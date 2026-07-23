# Matter adapter direction

HIRI's Matter integration starts as an offline, transport-neutral scaffold. It
maps controller-provided Matter endpoint snapshots into the existing HIRI
`Device` registry without commissioning devices, storing fabric credentials, or
opening a network connection.

Matter is an IP-based application-layer standard with a shared data and
interaction model. The Connectivity Standards Alliance released Matter 1.6 in
June 2026, so HIRI keeps the adapter boundary version-neutral instead of binding
the bridge to one generated SDK revision.

## Architecture

```text
Matter device
    |
    | commissioning, fabric security, subscriptions
    v
Matter controller server
    |
    | normalized node/endpoint snapshots
    v
MatterNodeProvider -> MatterAdapter -> HIRI DeviceRegistry
                                      |-> REST API
                                      `-> Home Assistant MQTT discovery
```

The controller server owns commissioning, certificates, fabric storage, device
attestation, and attribute subscriptions. HIRI owns only the conversion from a
normalized endpoint snapshot to its local device model.

The initial implementation in
`packages/bridge/src/hiri_bridge/adapters/matter.py` includes:

- `MatterNodeProvider`, the future live-client boundary;
- `MatterAdapter`, which consumes provider snapshots or an offline fixture;
- a conservative Matter device-type to HIRI domain map;
- normalized node, endpoint, device type, and attribute metadata on every
  imported device.

No Matter SDK, controller, hardware, account, or network access is required for
the scaffold:

```powershell
cd packages\bridge
hiri-bridge adapters list
hiri-bridge adapters import matter
pytest -q tests\test_matter_adapter.py
```

## Snapshot contract

A provider returns one dictionary per Matter endpoint:

```json
{
  "node_id": 1001,
  "endpoint_id": 1,
  "device_type": "dimmable_light",
  "name": "Living-room lamp",
  "vendor": "Example vendor",
  "product": "Example lamp",
  "area": "living_room",
  "reachable": true,
  "attributes": {
    "on_off": true,
    "current_level": 180
  }
}
```

Transport implementations normalize SDK-specific numeric device types,
clusters, and attribute names into this contract. Unknown future device types
fall back to the HIRI `sensor` domain while retaining their original Matter
metadata.

## Initial mapping

| Matter device type | HIRI domain |
| --- | --- |
| On/Off, dimmable, color-temperature, extended-color light | `light` |
| On/Off or dimmable plug-in unit | `switch` |
| Contact sensor | `binary_sensor` |
| Temperature sensor | `sensor` |
| Door lock | `lock` |
| Thermostat | `climate` |
| Window covering | `cover` |
| Fan | `fan` |

## Live upgrade path

1. Implement `MatterNodeProvider` as a client for a dedicated Matter controller
   server. Prefer its WebSocket API over embedding a platform-specific Matter
   SDK in HIRI.
2. Normalize nodes, endpoints, device types, clusters, and attributes at the
   provider boundary, then reuse `MatterAdapter` unchanged.
3. Add reconnect and attribute-subscription handling. Reconcile snapshots into
   `DeviceRegistry` using stable `node_id + endpoint_id` identifiers.
4. Add command writes only after an explicit device-type allowlist and tests for
   every cluster mapping.
5. Keep commissioning in the controller server. Never log setup codes or store
   fabric keys in `devices.json`.

The current Python Matter Server provides a certified controller component and a
WebSocket client/server API, but is in maintenance mode while its successor is
being built on Matter.js. HIRI's provider boundary avoids coupling to either
implementation.

## Primary references

- [Connectivity Standards Alliance: Matter 1.6 release](https://csa-iot.org/newsroom/matter-1-6-enables-more-intuitive-setup-multi-ecosystem-experiences-and-context-driven-control/)
- [Official Matter SDK: connectedhomeip](https://github.com/project-chip/connectedhomeip)
- [Open Home Foundation Python Matter Server](https://github.com/matter-js/python-matter-server)
- [Matter.js Server successor](https://github.com/matter-js/matterjs-server)

## Security boundaries

- Offline fixture mode is the default.
- HIRI does not commission devices or create a Matter fabric.
- HIRI does not persist setup codes, fabric credentials, or controller tokens.
- Live network access must be explicitly configured in a future provider.
- State-changing commands remain disabled until they have an allowlist and
  device-type-specific tests.
