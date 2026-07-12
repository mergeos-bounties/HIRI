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
