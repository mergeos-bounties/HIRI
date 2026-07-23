# Matter on HIRI — direction and scaffold

Status: **scaffold**. The mapping and the device shape are implemented and tested
offline (`packages/bridge/src/hiri_bridge/adapters/matter.py`); commissioning and live
subscriptions are not, and say so instead of failing quietly.

## Why HIRI wants Matter

Every other adapter in the bridge speaks one vendor's dialect: Zigbee2MQTT talks z2m
JSON, Tuya talks category codes, HA talks entity ids. Matter is the one protocol where
the device itself declares what it is, in a way that is the same across vendors. For HIRI
that means the mapping layer — the thing that is fragile in every other adapter — becomes
a lookup table published in a spec, which is exactly the piece this scaffold implements.

Two roles are possible, and they are not the same job:

| Role | What it means | Where HIRI sits |
| --- | --- | --- |
| Matter **controller** | HIRI commissions nodes onto its own fabric and drives them | the direction below |
| Matter **bridge** (Bridged Node) | HIRI exposes its non-Matter devices *to* Apple/Google/Alexa | later, needs a certified stack |

Being a controller first is the cheaper half: it makes Matter devices appear in the HIRI
registry next to z2m and Tuya ones, and it reuses the HA MQTT discovery path that already
exists. Being a bridge means shipping a commissionable Matter device, which drags in
certification, attestation certificates and a Thread/Wi-Fi provisioning story. Not now.

## What the scaffold does today

* `MATTER_DEVICE_TYPE_MAP` — endpoint device type → HIRI domain, straight from the Matter
  1.x Device Library:

  | Device type | Name | HIRI domain |
  | --- | --- | --- |
  | `0x0100` / `0x0101` / `0x010C` / `0x010D` | On/Off, Dimmable, Color Temperature, Extended Color Light | `light` |
  | `0x010A` / `0x010B` / `0x0103` | On/Off & Dimmable Plug-in Unit, On/Off Light Switch | `switch` |
  | `0x000A` | Door Lock | `lock` |
  | `0x0202` | Window Covering | `cover` |
  | `0x0301` | Thermostat | `climate` |
  | `0x002B` | Fan | `fan` |
  | `0x0015` / `0x0107` / `0x0076` | Contact, Occupancy, Smoke CO Alarm | `binary_sensor` |
  | `0x0302` / `0x0305` / `0x0306` / `0x0307` / `0x0106` | Temperature, Pressure, Flow, Humidity, Light Sensor | `sensor` |

* `MATTER_UTILITY_DEVICE_TYPES` — Root Node `0x0016`, Aggregator `0x000E`, Bridged Node
  `0x0013`, Power Source `0x0011`, OTA `0x0012`/`0x0014`. An endpoint that carries only
  these is *not* a device; endpoint 0 of every node is skipped for this reason.
* Unknown device types still produce a device, in the `sensor` fallback domain, tagged
  `device_type: 0xFFF1` — a new gadget shows up in the registry instead of disappearing.
* One HIRI device per **(node, endpoint)** pair, id `<domain>.matter_<node>_<endpoint>`.
  A Matter node is not one device: a sensor hub reports contact on endpoint 2 and
  temperature on endpoint 3, and both must land separately.
* Attributes keep the identity a controller would need later: `node_id`, `endpoint_id`,
  `fabric_id`, `vendor_id`, `product_id`, `serial_number`, `bridged`.

```bash
hiri-bridge adapters list                # matter: scaffold ready (fixture)
hiri-bridge adapters import matter       # 5 devices from 4 fixture nodes
```

## Making it live

The intended controller is **python-matter-server** (the same one Home Assistant uses):
it runs the CHIP SDK in its own container and exposes a WebSocket API, which keeps the
SDK's native build out of the bridge package. The alternative — linking `chip-repl`
directly — pulls a large native toolchain into HIRI's install and is not worth it.

1. Run the controller next to the bridge:
   ```bash
   docker run -d --name matter-server --network=host \
     -v $(pwd)/matter-data:/data ghcr.io/home-assistant-libs/python-matter-server:stable
   ```
   Host networking is not optional — commissioning needs mDNS and IPv6 on the LAN.
2. Point the adapter at it and turn the fixture off:
   ```python
   MatterAdapter(server_url="ws://127.0.0.1:5580/ws", use_fixture=False)
   ```
3. Implement `list_remote()` over the WebSocket API: `start_listening` returns all
   commissioned nodes; each node carries `attributes` keyed `"<endpoint>/<cluster>/<attr>"`.
   Device types come from the Descriptor cluster (`0x001D`) attribute `DeviceTypeList`,
   which is what `domain_for_device_types()` already consumes.
4. Commissioning (`commission()`): `commission_with_code` with the 11-digit manual code or
   the QR payload. This is the security-sensitive part — PASE with the setup passcode,
   then CASE on operational credentials, and the node joins **HIRI's fabric**. Store the
   returned node id; the fabric's operational credentials live in the controller's data
   volume and must be backed up with it, or every device has to be re-paired.
5. State follow: subscribe rather than poll — the controller pushes attribute updates, and
   they map onto the existing registry `upsert` + MQTT discovery publish path.
6. Writes (`push_state()`): cluster commands (On/Off `0x0006`, Level Control `0x0008`,
   Color Control `0x0300`) per endpoint. Keep them behind the same allowlist the other
   adapters use before anything can drive a lock.

## Testing approach

`packages/bridge/tests/test_matter_adapter.py` covers the mapping table, utility-endpoint
skipping, the unknown-type fallback, id uniqueness, bridged flagging, offline nodes, the
registry import, and that both live paths import nothing while reporting *why*. All of it
runs with no fabric, no SDK and no network. When the WebSocket client lands, the fixture
becomes a recorded `start_listening` payload and the same assertions keep working.
