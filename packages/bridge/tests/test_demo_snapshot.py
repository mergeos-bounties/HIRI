from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import Device

def test_append_invariant(tmp_path: Path) -> None:
    """Loading seed + appends never shrinks device count (anti-truncate)."""
    db_path = tmp_path / "devices.json"
    
    # 1. Create and seed registry
    reg1 = DeviceRegistry(path=db_path)
    reg1.seed()
    reg1.save()
    
    seed_count = reg1.stats()["total"]
    
    # 2. Load registry from the saved file and append a new device
    reg2 = DeviceRegistry(path=db_path)
    reg2.load_or_seed()
    
    assert reg2.stats()["total"] == seed_count, "Loaded count should match seed count"
    
    new_device = Device(
        id="sensor.test_append_invariant",
        name="Test Sensor",
        domain="sensor",
        manufacturer="HIRI",
        model="Test",
        adapter="test",
        state={"temperature": 25.0}
    )
    reg2.upsert(new_device)
    reg2.save()
    
    appended_count = reg2.stats()["total"]
    assert appended_count == seed_count + 1, "Appended count should be seed count + 1"
    
    # 3. Load again to verify append persisted
    reg3 = DeviceRegistry(path=db_path)
    reg3.load_or_seed()
    final_count = reg3.stats()["total"]
    assert final_count == seed_count + 1, "Final loaded count should match appended count (no truncate)"
