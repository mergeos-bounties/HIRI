from __future__ import annotations

import json
from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import Device


def _count_devices(reg: DeviceRegistry) -> int:
    return len(reg.list())


def _make_extra_device(suffix: str) -> Device:
    return Device(
        id=f"switch.extra_{suffix}",
        name=f"Extra device {suffix}",
        domain="switch",
        model="HIRI-RELAY",
        area="test",
        state={"state": "off"},
    )


def test_seed_append_never_truncates(tmp_path: Path) -> None:
    """Loading seed + appending devices never shrinks device count.

    The append-only invariant means:
    - Seeding the same registry again must not shrink the count.
    - Explicitly adding new devices must increase or keep the count.
    - Any operation that would truncate the registry should be detected.
    """
    reg = DeviceRegistry(path=tmp_path / "devices.json")

    # --- Seed baseline ---
    reg.seed()
    baseline = _count_devices(reg)
    assert baseline >= 15, f"Expected at least 15 seeded devices, got {baseline}"

    # --- Re-seed: must NOT shrink ---
    reg.seed()
    after_reseed = _count_devices(reg)
    assert after_reseed >= baseline, (
        f"Re-seed truncated device count: {baseline} -> {after_reseed}"
    )

    # --- Append one device ---
    reg.upsert(_make_extra_device("a"))
    after_append_1 = _count_devices(reg)
    assert after_append_1 > after_reseed, (
        f"Append did not increase count: {after_reseed} -> {after_append_1}"
    )

    # --- Append more devices ---
    for label in ("b", "c", "d", "e"):
        reg.upsert(_make_extra_device(label))
    after_append_many = _count_devices(reg)
    assert after_append_many > after_append_1, (
        f"Multiple appends did not increase count: {after_append_1} -> {after_append_many}"
    )

    # --- Verify total growth ---
    total_growth = after_append_many - baseline
    assert total_growth == 5, (
        f"Expected 5 new devices, got {total_growth} "
        f"(baseline={baseline}, final={after_append_many})"
    )


def test_snapshot_load_roundtrip_preserves_count(tmp_path: Path) -> None:
    """Exporting a snapshot and re-importing it preserves device count."""
    import json

    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    original_count = _count_devices(reg)

    # --- Snapshot export (simulate via model_dump) ---
    snapshot = [d.model_dump() for d in reg.list()]

    # --- Re-import into a fresh registry ---
    fresh = DeviceRegistry(path=tmp_path / "devices_reloaded.json")
    for data in snapshot:
        fresh.upsert(Device.model_validate(data))

    reloaded_count = _count_devices(fresh)
    assert reloaded_count == original_count, (
        f"Snapshot round-trip changed count: {original_count} -> {reloaded_count}"
    )


def test_append_after_snapshot_never_truncates(tmp_path: Path) -> None:
    """Appending devices after a snapshot never reduces the count."""
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    baseline = _count_devices(reg)

    # --- Simulate a snapshot write (export) ---
    snapshot = [d.model_dump() for d in reg.list()]
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2))

    # --- Append devices to the live registry ---
    for label in ("post_snap_1", "post_snap_2"):
        reg.upsert(_make_extra_device(label))
    after_append = _count_devices(reg)
    assert after_append > baseline, (
        f"Append after snapshot truncated count: {baseline} -> {after_append}"
    )

    # --- Verify snapshot file is still intact (not mutated) ---
    loaded = json.loads(snapshot_path.read_text())
    assert len(loaded) == baseline, (
        f"Snapshot file was mutated: expected {baseline} devices, got {len(loaded)}"
    )