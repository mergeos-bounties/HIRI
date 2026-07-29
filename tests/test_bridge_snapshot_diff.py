import pytest

def verify_snapshot_append_only(initial_devices: list, updated_devices: list) -> bool:
    """
    Verifies the append-only invariant: loading seed + appends must never shrink device count.
    Raises ValueError if device count shrinks (anti-truncate).
    """
    if len(updated_devices) < len(initial_devices):
        raise ValueError(
            f"Truncation detected! Initial count: {len(initial_devices)}, Updated count: {len(updated_devices)}"
        )
    return True

def test_snapshot_append_only_passes_on_append():
    """Verify append-only invariant passes when new devices are appended."""
    seed_devices = [{"id": "dev_1", "domain": "sensor"}, {"id": "dev_2", "domain": "actuator"}]
    appended_devices = seed_devices + [{"id": "dev_3", "domain": "sensor"}]

    assert verify_snapshot_append_only(seed_devices, appended_devices) is True
    assert len(appended_devices) >= len(seed_devices)

def test_snapshot_append_only_fails_on_truncate():
    """Verify append-only invariant fails with ValueError on device truncation."""
    seed_devices = [{"id": "dev_1", "domain": "sensor"}, {"id": "dev_2", "domain": "actuator"}]
    truncated_devices = [{"id": "dev_1", "domain": "sensor"}] # Shrunk!

    with pytest.raises(ValueError, match="Truncation detected"):
        verify_snapshot_append_only(seed_devices, truncated_devices)
