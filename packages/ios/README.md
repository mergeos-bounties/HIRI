# HIRI-ios

SwiftUI iOS client for HIRI bridge.

A native iOS app that connects to a local or remote [HIRI-bridge](https://github.com/mergeos-bounties/HIRI/tree/master/packages/bridge) instance to browse and control smart home devices.

## Features

- **Device list** — Browse all devices grouped by area, with search and filter
- **Device control** — Toggle power on/off for lights, switches, and fans
- **Brightness control** — Slider for light brightness (when device is on)
- **Area filtering** — Filter devices by room/area
- **Bridge discovery** — Configurable API endpoint in settings
- **Pull-to-refresh** — Refresh device states
- **Dark mode** — Native SwiftUI dark mode support

## Requirements

- iOS 17.0+
- Xcode 15.0+
- A running HIRI-bridge instance (default: `http://127.0.0.1:8780`)

## Build & Run

```bash
# Open in Xcode
open packages/ios/HIRI.xcodeproj

# Or build from command line
xcodebuild -project packages/ios/HIRI.xcodeproj \
  -scheme HIRI \
  -destination 'platform=iOS Simulator,name=iPhone 15,OS=17.0' \
  build
```

### Quick start (no Xcode project)

If you don't have an `.xcodeproj` file yet, create one in Xcode:

1. Open Xcode → File → New → Project
2. Select **iOS → App** template
3. Set Product Name: `HIRI`, Interface: **SwiftUI**, Language: **Swift**
4. Save the project to `packages/ios/`
5. Replace the auto-generated files with the Swift files in this directory
6. Add `NSAppTransportSecurity` → `NSAllowsArbitraryLoads = YES` in Info.plist
7. Build and run on simulator or device

## Architecture

```
HIRIApp.swift        — App entry point
ContentView.swift    — Device list with search, area filter, pull-to-refresh
DeviceDetailView.swift — Device detail with power toggle and brightness control
APIService.swift     — Network layer (URLSession) + Observable ViewModel
Models.swift         — Data models matching HIRI-bridge REST API
```

## API

Connects to the HIRI-bridge REST API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Bridge health check |
| `/devices` | GET | List all devices (optional `?domain=` & `?area=` filters) |
| `/devices/{id}` | GET | Single device details |
| `/devices/{id}/command` | POST | Send command (`turn_on`, `turn_off`, etc.) |
| `/stats` | GET | Bridge statistics |

## Bounty

Bounty: [HIRI #15 — iOS: SwiftUI device list + switch control](https://github.com/mergeos-bounties/HIRI/issues/15) — 100 MRG

## License

MIT · MergeOS / ThanhTrucSolutions