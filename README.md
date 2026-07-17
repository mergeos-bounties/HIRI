# HIRI

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Bridge](https://img.shields.io/badge/hiri--bridge-0.2.15-0E8A16.svg)](packages/bridge/pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-MQTT%20discovery-41BDF5.svg)](https://www.home-assistant.io/)
[![MergeOS](https://img.shields.io/badge/MergeOS-bounties-5319E7.svg)](https://github.com/mergeos-bounties)

**HIRI** is a smart-home **bridge + firmware** stack for **Home Assistant** and multi-ecosystem device adapters — local registry, MQTT discovery, REST API, ESP firmware, and client scaffolds.

**Product:** [mergeos-bounties/HIRI](https://github.com/mergeos-bounties/HIRI)

---

## Table of contents

- [Monorepo packages](#monorepo-packages)
- [Highlights](#highlights)
- [Screenshots](#screenshots)
- [Quick start (bridge)](#quick-start-bridge)
- [CLI reference](#cli-reference)
- [Adapters](#adapters)
- [Diagrams](#diagrams)
- [Architecture](#architecture)
- [Safety](#safety)
- [Development](#development)
- [MergeOS bounties](#mergeos-bounties)
- [License](#license)

---

## Monorepo packages

| Package | Path | Role |
| --- | --- | --- |
| **HIRI-bridge** | `packages/bridge` | Device registry, adapters, HA MQTT discovery, FastAPI |
| **HIRI-firmware** | `packages/firmware` | ESP32 / ESP8266 firmware (PlatformIO) → MQTT → HA |
| **HIRI-web** | `packages/web` | User dashboard |
| **HIRI-admin** | `packages/admin` | Admin console (devices, adapters, logs) |
| **HIRI-android** / **ios** | `packages/…` | Mobile client scaffolds |

Primary offline path: **bridge** (`hiri-bridge demo`).

---

## Highlights

| Capability | Description |
| --- | --- |
| **Device registry** | Seed + import devices; domains (light, fan, sensor, …) |

---

## Development

```powershell
cd packages\bridge
pytest -q
ruff check src tests
hiri-bridge demo
```

### Device Entity ID Naming

When creating device packs, follow the [Device Entity ID Naming Conventions](docs/DEVICE_ENTITY_ID_NAMING.md) for consistent `domain.object_id` patterns.

---

## MergeOS bounties

Device packs, bridge adapters, firmware, web/admin UX.  
Star + claim → PR **master** → MRG **25–200**. Evidence: discovery JSON snippet, HA entity screenshots, or flash notes.

---

## License

MIT · MergeOS / ThanhTrucSolutions
