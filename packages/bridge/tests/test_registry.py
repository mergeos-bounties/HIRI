from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_seed_covers_many_domains(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    stats = reg.stats()
    assert stats["total"] >= 15
    assert "light" in stats["by_domain"]
    assert "sensor" in stats["by_domain"]
    assert "climate" in stats["by_domain"]


def test_command_light(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command(
        "light.living_main",
        "turn_on",
        {"brightness": 200, "effect": "colorloop"},
    )
    assert dev.state["state"] == "on"
    assert dev.state["brightness"] == 200
    assert dev.state["effect"] == "colorloop"


def test_cover_tilt_and_fan_preset(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    cover = reg.apply_command("cover.garage", "set_tilt", {"tilt": 40})
    assert cover.state["tilt"] == 40
    fan = reg.apply_command("fan.ceiling_lr", "set_preset_mode", {"preset_mode": "breeze"})
    assert fan.state["preset_mode"] == "breeze"
    assert fan.state["state"] == "on"


def test_fan_discovery_includes_preset_controls(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    fan = reg.get("fan.ceiling_lr")
    assert fan is not None
    payload = export_discovery([fan])[0]["payload"]
    assert payload["preset_modes"] == ["low", "medium", "high", "breeze"]
    assert payload["percentage_command_topic"].endswith("/cmd/fan/ceiling_lr")
    assert payload["preset_mode_command_topic"].endswith("/cmd/fan/ceiling_lr/preset")
    assert payload["preset_mode_state_topic"].endswith("/state/fan/ceiling_lr/preset")


def test_discovery_export(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    disc = export_discovery(reg.list())
    assert len(disc) == reg.stats()["total"]
    assert all("topic" in x and "payload" in x for x in disc)


def test_snapshot_append_only_invariant(tmp_path: Path) -> None:
    """Seed + append must never shrink device count (anti-truncate).

    This verifies the append-only invariant of the registry JSON on disk.
    A seed (or re-seed) must not wipe previously upserted devices, and
    a sequence of seed then upsert then save then load must never produce
    fewer devices than the original seed count.
    """
    from hiri_bridge.devices.types import Device

    # 1. Fresh seed → record baseline count
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    seed_count = reg.stats()["total"]
    assert seed_count > 0, "seed must produce at least one device"

    # 2. Append a new device (simulate runtime import/addition)
    custom = Device(
        id="sensor.custom_test_1",
        name="Custom test sensor",
        domain="sensor",
        model="HIRI-TEST",
        area="test",
        state={"state": 99.9},
        attributes={"unit_of_measurement": "test"},
    )
    reg.upsert(custom)
    after_append = reg.stats()["total"]
    assert after_append >= seed_count + 1, (
        f"append must increase total: {after_append} >= {seed_count + 1}"
    )

    # 3. Save + reload from disk → count must not shrink
    reg.save()
    reg2 = DeviceRegistry(path=tmp_path / "devices.json")
    reg2.load_or_seed()
    reload_count = reg2.stats()["total"]
    assert reload_count >= seed_count, (
        f"reload must not shrink count: {reload_count} >= {seed_count}"
    )
    assert reload_count >= after_append, (
        f"reload must preserve appended device: {reload_count} >= {after_append}"
    )

    # 4. Re-seed on the reloaded registry (simulate zero-touch idempotent seed)
    reg2.seed()
    re_seed_count = reg2.stats()["total"]
    assert re_seed_count >= reload_count, (
        f"re-seed must be idempotent append: {re_seed_count} >= {reload_count}"
    )

    # 5. Verify the appended device survived all operations
    custom_loaded = reg2.get("sensor.custom_test_1")
    assert custom_loaded is not None, "appended device must survive seed+save+reload cycle"
    assert custom_loaded.model == "HIRI-TEST"


def test_snapshot_truncate_is_caught(tmp_path: Path) -> None:
    """A truncated JSON file must be detectable — anti-regression guard.

    If save() were to overwrite with fewer devices (truncation bug),
    the append-only invariant would break. This test writes a deliberately
    short file and verifies the registry detects the anomaly.
    """
    from hiri_bridge.devices.types import Device

    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    original_count = reg.stats()["total"]

    # Simulate truncation: write a file with only 1 device
    truncated = [Device(
        id="light.only_one",
        name="Only one left",
        domain="light",
        model="HIRI-TRUNC",
        area="test",
    ).model_dump()]
    import json
    reg.path.write_text(json.dumps(truncated, indent=2) + "\n", encoding="utf-8")

    # Load the truncated file
    reg2 = DeviceRegistry(path=tmp_path / "devices.json")
    reg2.load_or_seed()
    truncated_count = reg2.stats()["total"]
    assert truncated_count < original_count, (
        f"truncated file must have fewer devices: {truncated_count} < {original_count}"
    )

    # After re-seed, count should be restored (anti-truncate safety net)
    reg2.seed()
    restored_count = reg2.stats()["total"]
    assert restored_count >= original_count, (
        f"re-seed after truncation must restore count: {restored_count} >= {original_count}"
    )
    # The truncated device is still there, seeds were added back
    assert reg2.get("light.only_one") is not None
    assert reg2.get("light.living_main") is not None, "seed device must be restored"
