# Append-Only devices.json Policy

## Overview

All device packs and integrations **MUST** append to `devices.json` and **NEVER** replace or truncate the entire file. This ensures that device registrations from multiple sources coexist without conflict.

## Policy

### ✅ DO: Append new entries

python
import json
from pathlib import Path

def register_device(device_id: str, device_data: dict) -> None:
    """Register a new device by appending to devices.json."""
    devices_file = Path("devices.json")
    
    # Load existing devices
    if devices_file.exists():
        with open(devices_file, "r") as f:
            devices = json.load(f)
    else:
        devices = {}
    
    # Append/update the new device
    devices[device_id] = device_data
    
    # Write back
    with open(devices_file, "w") as f:
        json.dump(devices, f, indent=2)


### ❌ DON'T: Replace the entire file

python
# BAD - This will erase all other devices!
def bad_register_device(device_id: str, device_data: dict) -> None:
    with open("devices.json", "w") as f:
        json.dump({device_id: device_data}, f)  # ⚠️ WRONG!


## Seed Merge-Only Behavior

When initializing from seed data:

1. **Read** existing `devices.json` if present
2. **Merge** seed devices with existing entries
3. **Preserve** all existing device IDs not in the seed
4. **Only update** devices that exist in both (merge semantics)

### Example: Seed merge implementation

python
def merge_seed_devices(seed_devices: dict) -> None:
    """Merge seed devices without removing existing entries."""
    devices_file = Path("devices.json")
    
    # Load existing devices
    existing = {}
    if devices_file.exists():
        with open(devices_file, "r") as f:
            existing = json.load(f)
    
    # Merge: existing takes precedence, seed fills gaps
    merged = {**seed_devices, **existing}
    
    # Write merged result
    with open(devices_file, "w") as f:
        json.dump(merged, f, indent=2)


## Rationale

- **Multi-source support**: Different device packs may contribute devices independently
- **Data integrity**: Prevents accidental loss of device configurations
- **Idempotency**: Re-running device pack installations won't break existing setups
- **Version control**: Easier to track incremental changes in git history

## Enforcement

- All PRs adding device pack code **MUST** demonstrate append-only behavior
- Integration tests should verify multi-device scenarios
- Code reviews will reject truncating writes to `devices.json`

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md) - General contribution guidelines
- [README.md](../README.md) - Project overview and quick start
- Device pack development guide (if applicable)

---

**Questions?** Open an issue or ask in discussions.