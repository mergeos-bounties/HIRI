"""Tests for append-only snapshot diff invariant.

Loading seed + appending devices must never shrink the device count
(anti-truncate). A truncation (replacing with fewer devices) should
cause the test to fail.
"""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import Device


def _make_device(device_id: str, domain: str = "sensor") -> Device:
    return Device(
        id=device_id,
        name=f"Test {device_id}",
        domain=domain,
        model="HIRI-TEST",
        area="test",
        state={"state": 0},
    )


def test_append_only_invariant_never_shrinks(tmp_path: Path) -> None:
    """Loading seed + appending never shrinks device count."""
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    count_before = len(reg.list())

    # Append several new devices
    for i in range(5):
        reg.upsert(_make_device(f"sensor.test_append_{i}", "sensor"))

    count_after = len(reg.list())
    assert count_after >= count_before + 5, (
        f"Device count shrank or didn't grow enough: "
        f"before={count_before} after={count_after}"
    )


def test_append_only_multiple_seeds(tmp_path: Path) -> None:
    """Repeated seeding should not shrink device count."""
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    count_first = len(reg.list())

    # Seed again — should not shrink
    reg.seed()
    count_second = len(reg.list())
    assert count_second >= count_first, (
        f"Device count shrank after second seed: "
        f"first={count_first} second={count_second}"
    )

    # Seed a third time
    reg.seed()
    count_third = len(reg.list())
    assert count_third >= count_second, (
        f"Device count shrank after third seed: "
        f"second={count_second} third={count_third}"
    )


def test_append_only_upsert_does_not_overwrite_new_devices(tmp_path: Path) -> None:
    """Upserting should not wipe out existing devices."""
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    count_before = len(reg.list())

    # Upsert an existing device (same id) — should not add or remove
    existing = reg.list()[0]
    reg.upsert(existing)
    count_after = len(reg.list())
    assert count_after == count_before, (
        f"Upserting existing device changed count: "
        f"before={count_before} after={count_after}"
    )


def test_append_only_load_and_append(tmp_path: Path) -> None:
    """Load from saved file, then append, count must not shrink."""
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    count_seed = len(reg.list())

    # Load from the same file (simulates restart)
    reg2 = DeviceRegistry(path=tmp_path / "devices.json")
    reg2.load_or_seed()
    count_load = len(reg2.list())
    assert count_load == count_seed, (
        f"Loaded count differs from seed: "
        f"seed={count_seed} load={count_load}"
    )

    # Append more
    reg2.upsert(_make_device("sensor.append_after_load", "sensor"))
    count_append = len(reg2.list())
    assert count_append == count_load + 1, (
        f"Count after append should be load+1: "
        f"load={count_load} append={count_append}"
    )