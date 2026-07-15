# Devices.json Append-Only Policy

> **CRITICAL**: `packages/bridge/data/devices.json` is an **append-only** registry. Device packs and automated
> cycles MUST append entries — never replace or overwrite the entire file.

## Why Append-Only?

`devices.json` is the canonical device registry for the HIRI bridge. Every commit that writes device
data **must preserve all existing devices** and only add new ones. Replacing the entire file would:

- **Destroy device history** — previously registered devices would disappear from the registry
- **Break MQTT discovery** — Home Assistant entities would lose their source definitions
- **Cause duplicate re-registration** — re-imported devices get new internal IDs, breaking automations
- **Corrupt the seed** — the seed data used for offline demos and CI would be incomplete

## Correct: Append-Only Pattern

When adding devices via a device pack or automated cycle, always **read first, then append**:

```python
import json
from pathlib import Path

DEVICES_PATH = Path("packages/bridge/data/devices.json")

# ✅ CORRECT: Read existing, append new, write back
existing = json.loads(DEVICES_PATH.read_text())
new_devices = [
    {"id": "sensor.new_sensor", "name": "New Sensor", "domain": "sensor"}
]
all_devices = existing + new_devices  # APPEND, do NOT replace
DEVICES_PATH.write_text(json.dumps(all_devices, indent=2) + "\n")
```

```javascript
// ✅ CORRECT: Read-modify-write with append
const fs = require("fs");
const existing = JSON.parse(fs.readFileSync("packages/bridge/data/devices.json", "utf8"));
const newDevices = [
  { id: "sensor.new_sensor", name: "New Sensor", domain: "sensor" }
];
const allDevices = [...existing, ...newDevices]; // APPEND, do NOT replace
fs.writeFileSync("packages/bridge/data/devices.json", JSON.stringify(allDevices, null, 2) + "\n");
```

## Wrong: Replace / Overwrite

```python
# ❌ WRONG: Overwrites the entire file — all existing devices are LOST
DEVICES_PATH.write_text(json.dumps(new_devices, indent=2))
```

```javascript
// ❌ WRONG: Replaces the array — all existing devices are LOST
fs.writeFileSync("packages/bridge/data/devices.json", JSON.stringify(newDevices, null, 2));
```

## Seed Merge-Only Behavior

The HIRI bridge ships with a **seed device set** in `devices.json` (living room lights, farm pump,
climate devices, sensors, etc.). When the bridge starts:

1. It loads the seed from `devices.json`
2. Additional adapters (z2m, tuya, ha_rest) **merge** their devices into the in-memory registry
3. The on-disk file is never overwritten — it only grows through append operations

This merge-only model ensures that:
- The seed is always intact for offline/demo mode
- Adapter-imported devices are layered on top without modifying the seed
- Rollbacks are safe — the seed anchors the registry

## Device Pack Guidelines

When creating a device pack (e.g., `devices_climate.json`, `devices_energy.json`):

1. **Keep pack files separate** — do not merge packs into `devices.json` manually
2. **Append to `devices.json`** — use the append-only pattern above
3. **One device per line entry** in the JSON array, maintaining existing formatting
4. **Never reorder existing entries** — only add to the end of the array
5. **Validate JSON** after appending — malformed JSON breaks the entire registry
6. **Test with `hiri-bridge demo`** — verify devices appear in discovery output

## Commit Message Convention

When committing device additions, use the MergeOS cycle format to make intent clear:

```
Improve HIRI: <device description> (cycle <id>)

- Append <device.id> (append-only)
```

The `(append-only)` tag in the commit body confirms compliance with this policy.

## CI / Automated Checks

CI will reject PRs that:
- Replace or overwrite the `devices.json` array (file shrinks substantially)
- Remove existing device entries without explicit approval
- Reorder existing device entries
- Contain malformed JSON

## Recovery

If `devices.json` is accidentally overwritten:
1. Restore from the last known-good commit: `git checkout HEAD~1 -- packages/bridge/data/devices.json`
2. Re-apply any legitimate additions that were lost
3. Never force-push to rewrite history — use reverts instead

---

**Remember: append, never replace. The registry grows — it does not get rewritten.**
