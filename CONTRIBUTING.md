# Contributing to HIRI

Welcome to HIRI! This guide explains how to work on the monorepo packages.

## Repository layout

HIRI is a monorepo with the following packages:

```
HIRI/
├── packages/
│   ├── bridge/        # Python bridge: Home Assistant ↔ MQTT ↔ firmware
│   ├── firmware/      # ESP32/ESP8266 firmware (Arduino/PlatformIO)
│   ├── web/           # Web admin panel
│   ├── admin/         # Admin dashboard
│   ├── android/       # Android companion app
│   └── ios/           # iOS companion app
├── docs/              # Documentation, diagrams, screenshots
├── scripts/           # Build & utility scripts
├── .github/workflows/ # CI pipelines
└── CONTRIBUTING.md    # This file
```

## Getting started

### Prerequisites

- **Python 3.11+** — for bridge, scripts, and admin
- **Node.js 18+** — for web admin panel
- **PlatformIO** — for ESP firmware builds
- **Home Assistant** — for bridge testing and MQTT discovery

### Bridge package

```bash
cd packages/bridge
pip install -e ".[dev]"
# Run tests
pytest -q
# Run linting
ruff check src/
```

### Web / Admin packages

```bash
cd packages/web
npm install
npm run dev      # dev server with hot reload
npm run build    # production build
npm test         # run tests
```

### Firmware package

```bash
cd packages/firmware
# Requires PlatformIO CLI
pio run          # compile for default platform
pio run -t clean # clean build artifacts
```

### Android / iOS

See the respective `README.md` inside `packages/android/` or `packages/ios/`.

## Making changes

### Branch naming

Use descriptive prefixes:

- `feat/<short-description>` — new features
- `fix/<short-description>` — bug fixes
- `docs/<short-description>` — documentation
- `ci/<short-description>` — CI/CD changes
- `refactor/<short-description>` — code restructuring

### Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(bridge): add Zigbee2MQTT device discovery
fix(firmware): correct WiFi reconnection timeout
docs(web): update admin panel setup guide
ci(bridge): add ruff linting to workflow
```

Format: `<type>(<scope>): <description>`

### Pull request process

1. Create a feature branch from `master`
2. Make your changes with tests where applicable
3. Ensure CI passes (lint + tests)
4. Open a PR with `Fixes #<issue-number>` in the description
5. Wait for maintainer review

### One issue per PR

Each PR must address **exactly one** GitHub issue. Do not combine multiple fixes into a single PR.

## Bounties

HIRI uses [MergeOS MRG bounties](docs/BOUNTY.md).

### Claim process

1. **Star** https://github.com/mergeos-bounties/HIRI and https://github.com/mergeos-bounties/mergeos
2. Comment on the issue: `I claim this bounty`
3. Comment on MergeOS [Claim Token #1](https://github.com/mergeos-bounties/mergeos/issues/1) with the issue link
4. Open a PR to HIRI with `Fixes #<n>`

### Bounty scale

| Scope | MRG |
| --- | ---: |
| Small (docs, CI, i18n) | 25 |
| Medium (features, UI) | 50 |
| Large (major features) | 100 |
| XL (end-to-end, platform) | 200 |

## Device packs

When creating device packs in `packages/bridge/data/packs/`, follow the **append-only policy**:

> ⚠️ **Important**: Device packs must **append** to the registry, never replace `devices.json`.  
> See [docs/devices-packs-policy.md](docs/devices-packs-policy.md) for the full policy.

## Code quality

- **Python**: `ruff check`, type hints encouraged, pytest for tests
- **TypeScript/JavaScript**: ESLint + Prettier
- **Firmware**: PlatformIO built-in checks
- All packages should have tests for new features

## Project architecture

HIRI follows a **bridge pattern**:

1. **Firmware** (ESP32) communicates via MQTT
2. **Bridge** translates between MQTT ↔ Home Assistant REST API
3. **Web/Admin** provide UI for configuration and monitoring
4. **Mobile apps** offer device control on the go

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full development roadmap.

## Questions?

Open a discussion or comment on the relevant issue.
