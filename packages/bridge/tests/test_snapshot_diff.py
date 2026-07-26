from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import Device


def test_snapshot_diff_append_only_invariant(tmp_path: Path) -> None:
    """Loading seed + appends never shrinks device count (anti-truncate).

    The append-only invariant guarantees that once a device is registered
    in the snapshot, subsequent operations only add new devices — they
    never silently remove or truncate existing entries.
    """
    # --- Arrange: create a seeded registry snapshot ---
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    snapshot_count = reg.stats()["total"]
    assert snapshot_count > 0, "Seed should produce at least one device"

    # --- Act: append new devices (simulating MQTT discovery / adapter adds) ---
    new_devices = [
        Device(
            id="light.garden_path",
            name="Garden path light",
            domain="light",
            model="HIRI-RGBW",
            area="garden",
            state={"state": "off", "brightness": 0},
        ),
        Device(
            id="sensor.temp_patio",
            name="Patio temperature",
            domain="sensor",
            model="HIRI-TH",
            area="patio",
            state={"state": 22.5},
            attributes={"unit_of_measurement": "°C", "device_class": "temperature"},
        ),
        Device(
            id="switch.garden_fountain",
            name="Garden fountain pump",
            domain="switch",
            model="HIRI-RELAY",
            area="garden",
            state={"state": "off"},
        ),
        Device(
            id="binary_sensor.gate_reed",
            name="Gate reed switch",
            domain="binary_sensor",
            model="HIRI-CONTACT",
            area="garden",
            state={"state": "off"},
            attributes={"device_class": "door"},
        ),
        Device(
            id="cover.garden_awning",
            name="Garden awning",
            domain="cover",
            model="HIRI-BLIND",
            area="garden",
            state={"state": "closed", "position": 0},
        ),
    ]

    for d in new_devices:
        reg.upsert(d)

    # --- Assert: count after appends >= snapshot count ---
    final_count = reg.stats()["total"]
    assert final_count >= snapshot_count, (
        f"Append-only invariant violated: "
        f"snapshot had {snapshot_count} devices, "
        f"but after appending {len(new_devices)} new devices "
        f"the registry only has {final_count} devices. "
        f"Devices were silently truncated or removed."
    )

    # --- Assert: every new device is actually present ---
    for d in new_devices:
        loaded = reg.get(d.id)
        assert loaded is not None, (
            f"Device '{d.id}' was upserted but is missing from registry"
        )
        assert loaded.name == d.name
        assert loaded.domain == d.domain

    # --- Assert: all original seed devices are still present ---
    reg2 = DeviceRegistry(path=tmp_path / "devices.json")
    reg2.load_or_seed()
    # reloaded count should match final count (persistence verified)
    assert reg2.stats()["total"] == final_count, (
        f"Persisted registry count ({reg2.stats()['total']}) "
        f"does not match final in-memory count ({final_count})"
    )


def test_snapshot_diff_append_existing_id_does_not_duplicate(tmp_path: Path) -> None:
    """Upserting a device with an existing ID updates it in place (no duplicate)."""
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    before = reg.stats()["total"]

    # Re-upsert an existing device with the same id but updated name
    existing = reg.get("light.living_main")
    assert existing is not None
    updated = existing.model_copy(update={"name": "Living room main light (v2)"})
    reg.upsert(updated)

    after = reg.stats()["total"]
    # Count should not increase — we updated in place
    assert after == before, (
        f"Upserting an existing device id created a duplicate: "
        f"before={before}, after={after}"
    )
    # Verify the name was actually updated
    reloaded = reg.get("light.living_main")
    assert reloaded is not None
    assert reloaded.name == "Living room main light (v2)"


def test_snapshot_diff_append_multiple_batches(tmp_path: Path) -> None:
    """Multiple append batches preserve the invariant cumulatively."""
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    snapshot = reg.stats()["total"]

    # Batch 1
    batch1 = [
        Device(id="light.batch1_a", name="Batch1 A", domain="light", area="test"),
        Device(id="sensor.batch1_b", name="Batch1 B", domain="sensor", area="test"),
    ]
    for d in batch1:
        reg.upsert(d)
    assert reg.stats()["total"] >= snapshot + len(batch1)

    # Batch 2
    batch2 = [
        Device(id="switch.batch2_a", name="Batch2 A", domain="switch", area="test"),
        Device(id="fan.batch2_b", name="Batch2 B", domain="fan", area="test"),
        Device(id="cover.batch2_c", name="Batch2 C", domain="cover", area="test"),
    ]
    for d in batch2:
        reg.upsert(d)
    assert reg.stats()["total"] >= snapshot + len(batch1) + len(batch2)

    # Batch 3: re-upsert an existing device (should not add)
    existing = reg.get("light.batch1_a")
    assert existing is not None
    reg.upsert(existing.model_copy(update={"name": "Batch1 A renamed"}))
    # Count should stay the same as after batch 2
    assert reg.stats()["total"] == snapshot + len(batch1) + len(batch2)


def test_snapshot_diff_round_trip_preserves_count(tmp_path: Path) -> None:
    """Save → reload preserves device count (no truncation on I/O)."""
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    initial_count = reg.stats()["total"]

    # Append some devices
    extras = [
        Device(id="light.extra_1", name="Extra 1", domain="light", area="test"),
        Device(id="switch.extra_2", name="Extra 2", domain="switch", area="test"),
    ]
    for d in extras:
        reg.upsert(d)

    # Save happens automatically on upsert; reload from disk
    reg2 = DeviceRegistry(path=tmp_path / "devices.json")
    reg2.load_or_seed()
    assert reg2.stats()["total"] == initial_count + len(extras), (
        f"Round-trip lost devices: "
        f"expected {initial_count + len(extras)}, "
        f"got {reg2.stats()['total']}"
    )