# Contributing to HIRI

Thank you for your interest in contributing to HIRI — the Home Assistant bridge + ESP32/ESP8266 farmware + web/admin/mobile smart-home stack.

## Monorepo Structure

This repository is organized as a monorepo with the following packages:

| Package   | Path               | Description                                      |
|-----------|--------------------|--------------------------------------------------|
| `bridge`  | `packages/bridge/` | Python Home Assistant bridge (MQTT, discovery)   |
| `admin`   | `packages/admin/`  | Web admin interface                              |
| `web`     | `packages/web/`    | Main web frontend                                |
| `android` | `packages/android/`| Android mobile app                               |
| `ios`     | `packages/ios/`    | iOS mobile app                                   |
| `firmware`| `packages/firmware/`| ESP32/ESP8266 firmware (PlatformIO)             |

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/HIRI.git
   cd HIRI
   ```
3. **Set up your environment** per the package you want to contribute to (see each package's README).

## How to Contribute

- **Report bugs** by opening a GitHub Issue.
- **Suggest features** by opening a GitHub Issue with the `enhancement` label.
- **Submit code** via a Pull Request (see below).

## Pull Request Process

1. Create a feature branch from `master`:
   ```bash
   git checkout -b feat/my-feature
   ```
2. Make your changes, keeping them focused on a single concern.
3. Run existing tests for the affected package(s).
4. Commit with a clear message:
   ```
   feat(bridge): add MQTT auto-reconnect
   ```
5. Push to your fork and open a Pull Request against `master`.
6. Link any related issues in the PR description using `Closes #N`.

## Code Style

- **Python** (bridge): follows PEP 8 — run `ruff check` before committing.
- **C++** (firmware): follows the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html).
- **JavaScript/TypeScript** (web/admin): follows the project's ESLint configuration.

## Need Help?

Open a [Discussion](https://github.com/mergeos-bounties/HIRI/discussions) or ask in the relevant issue. We're happy to guide new contributors!
