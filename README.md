# HIRI

**HIRI** is a smart-home **bridge + farmware** stack optimized for **Home Assistant** and multi-ecosystem bridging.

| Package | Role |
| --- | --- |
| **HIRI-bridge** | Central bridge: HA MQTT discovery, device registry, REST API |
| **HIRI-firmware** | ESP32 / ESP8266 farmware (PlatformIO) → MQTT → HA |
| **HIRI-web** | User dashboard |
| **HIRI-admin** | Admin console (devices, adapters, logs) |
| **HIRI-android** | Android client scaffold |
| **HIRI-ios** | iOS client scaffold |

Org: [mergeos-bounties](https://github.com/mergeos-bounties) · Funded via MergeOS MRG bounties.


## Screenshots

Real captures from running the product demo (HIRI).

![Device registry](docs/screenshots/demo-devices.png)

*Device registry*

![HA discovery export](docs/screenshots/demo-discovery.png)

*HA discovery export*

## Quick start (bridge — runnable offline)

```bash
cd HIRI/packages/bridge
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -e ".[dev]"

hiri-bridge demo
hiri-bridge devices list
hiri-bridge adapters list
hiri-bridge adapters import z2m
hiri-bridge adapters import tuya
hiri-bridge mqtt publish --dry-run
hiri-bridge ha discovery --out data/out/discovery.json
hiri-bridge serve --port 8780
```

Optional API auth (protects POST): `set HIRI_API_TOKEN=your-secret` then send `Authorization: Bearer your-secret`.

MQTT live publish (optional): `pip install -e ".[mqtt]"` and `hiri-bridge mqtt publish --live`.

Open:
- Dashboard: `packages/web/public/index.html` (or serve static)
- Admin: `packages/admin/public/index.html`
- API health: `http://127.0.0.1:8780/health`

## Firmware (ESP32 / ESP8266)

```bash
cd packages/firmware
# Install PlatformIO CLI, then:
pio run -e esp32dev
pio run -e esp8266
# Flash (device connected):
pio run -e esp32dev -t upload
```

Farmware publishes HA MQTT discovery + state for onboard switch/sensor simulation.

## Packages layout

```
packages/
  bridge/          # Python 3.11+ CLI + API
  firmware/        # PlatformIO C++ farmware
  web/             # Static web UI
  admin/           # Static admin UI
  android/         # Kotlin scaffold
  ios/             # Swift scaffold
docs/BOUNTY.md
```

## MergeOS bounties

1. Star this repo + [mergeos](https://github.com/mergeos-bounties/mergeos)
2. Claim a `bounty` issue
3. Claim on MergeOS [issue #1](https://github.com/mergeos-bounties/mergeos/issues/1)
4. PR to **HIRI** `master` with tests/evidence
5. Credit MRG 25/50/100/200

See [docs/BOUNTY.md](docs/BOUNTY.md).

## License

MIT
