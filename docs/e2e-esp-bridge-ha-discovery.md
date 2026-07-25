# End-to-End: ESP Farmware → Bridge → Home Assistant MQTT Discovery

> **E2E evidence for [HIRI #16](https://github.com/mergeos-bounties/HIRI/issues/16)**
> 200 MRG — Documented E2E path with screenshots and reproducible steps.

---

## Architecture

```
┌─────────────────────┐     MQTT      ┌──────────────────┐     MQTT       ┌──────────────────────┐
│   ESP32 / ESP8266   │ ─────────────→│   MQTT Broker    │ ─────────────→│  Home Assistant      │
│   (HIRI Firmware)   │   state/cmd   │  (Mosquitto)     │   discovery   │  (Auto-discovery)    │
│                     │               │  127.0.0.1:1883  │               │                      │
│  • Switch (relay)   │               │                  │               │  • Switch entity     │
│  • Soil sensor      │               │                  │               │  • Soil sensor       │
│  • Temperature      │               │                  │               │  • Temperature       │
│  • HA discovery     │               │                  │               │  • Online status     │
└─────────────────────┘               └──────────────────┘               └──────────────────────┘
                                              ↕
                                      ┌──────────────────┐
                                      │  HIRI Bridge      │
                                      │  (hiri-bridge)    │
                                      │                   │
                                      │  • Device registry │
                                      │  • Web dashboard  │
                                      │  • Admin console  │
                                      │  • Adapters       │
                                      └──────────────────┘
```

### Data Flow

1. **ESP32 firmware** connects to WiFi and MQTT broker
2. **Firmware publishes HA MQTT discovery configs** to `homeassistant/<domain>/hiri/<device_id>/config`
3. **Home Assistant receives discovery messages** and auto-creates entities
4. **Firmware publishes telemetry** (soil moisture, temperature) every 10s
5. **HA displays entities** in the dashboard with real-time updates
6. **User can control devices** (e.g., toggle relay) via HA → MQTT → firmware
7. **HIRI bridge** maintains device registry, adapters, and optional web/admin UI

---

## Hardware Requirements

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| MCU | ESP32-DevKitC | ESP8266 (NodeMCU v2) |
| Relay | 1-channel 5V relay module | Any GPIO-controlled relay |
| Soil sensor | Capacitive soil moisture sensor v1.2 | Resistive sensor + ADC |
| Temp/humidity | DHT22 (AM2302) | DHT11 (less accurate) |
| Power | 5V USB power supply | Battery + deep sleep |
| MQTT broker | Mosquitto (HA add-on) | Any MQTT 3.1.1 broker |

---

## Step 1: Build and Flash ESP Firmware

### Prerequisites

```bash
# Install PlatformIO
pip install platformio

# Navigate to firmware directory
cd packages/firmware
```

### Configure WiFi and MQTT

Edit `include/hiri_config.h`:

```c
#define HIRI_WIFI_SSID    "YourWiFiSSID"
#define HIRI_WIFI_PASS    "YourWiFiPassword"
#define HIRI_MQTT_HOST    "192.168.1.100"         // Your MQTT broker IP
#define HIRI_MQTT_PORT    1883
#define HIRI_DEVICE_ID    "hiri_node_01"           // Unique device ID

// Enable sensors
#define HIRI_DHT_ENABLED     1                     // Enable DHT22
#define HIRI_DHT_PIN         4                     // GPIO pin for DHT22
#define HIRI_DHT_TYPE        DHT22

#define HIRI_SOIL_ADC_ENABLED 1                   // Enable soil sensor
#define HIRI_SOIL_ADC_PIN     34                   // ADC pin for soil
```

### Build and Flash

```bash
# Build for ESP32
pio run -e esp32dev

# Flash to device
pio run -e esp32dev --target upload

# Monitor serial output
pio device monitor --baud 115200
```

### Expected Serial Output

```
Connecting to WiFi...
WiFi connected, IP: 192.168.1.42
Connecting to MQTT broker...
MQTT connected
Publishing HA discovery: switch, sensor (soil), sensor (temp)
Telemetry loop started (10s interval)
```

---

## Step 2: Configure MQTT Broker

### Home Assistant Mosquitto Add-on

```yaml
# configuration.yaml
mqtt:
  broker: core-mosquitto
  discovery: true
  birth_message:
    topic: "hiri/status"
    payload: "online"
  will_message:
    topic: "hiri/status"
    payload: "offline"
```

### Standalone Mosquitto

```bash
# Install
brew install mosquitto   # macOS
apt install mosquitto     # Linux

# Test broker
mosquitto_sub -h localhost -t "#" -v
```

---

## Step 3: Run the HIRI Bridge

### Install

```bash
cd packages/bridge
pip install -e ".[dev,api,mqtt]"
```

### Demo Mode (Offline, No Hardware Required)

```bash
hiri-bridge demo
```

**Expected output:**
```
{
  "total": 100,
  "online": 99,
  "by_domain": {
    "light": 7,
    "switch": 12,
    "binary_sensor": 13,
    "sensor": 36,
    "climate": 3,
    ...
  }
}
discovery data/out/discovery.json (100 entities)
command demo light.living_main → {state: on, brightness: 180}
mqtt dry-run 11 msgs · 127.0.0.1:1883 · offline
```

### Export HA Discovery

```bash
hiri-bridge ha discovery --out data/out/discovery.json
```

### Serve API

```bash
hiri-bridge serve --host 0.0.0.0 --port 8780
# Health check: http://localhost:8780/health
```

### Live MQTT Discovery Publish

```bash
# Install MQTT extras first
pip install -e ".[mqtt]"

# Dry-run (no broker needed)
hiri-bridge mqtt publish --dry-run

# Live publish (requires MQTT broker)
hiri-bridge mqtt publish --live --host 192.168.1.100
```

---

## Step 4: Expected MQTT Topics

### Discovery Topics (Published Once on Connect)

| Topic | Payload | Description |
|-------|---------|-------------|
| `homeassistant/switch/hiri/hiri_node_01/config` | `{"name": "hiri_node_01 Relay", ...}` | Switch entity config |
| `homeassistant/sensor/hiri/hiri_node_01_soil/config` | `{"name": "hiri_node_01 Soil", "unit_of_measurement": "%", ...}` | Soil moisture sensor config |
| `homeassistant/sensor/hiri/hiri_node_01_temp/config` | `{"name": "hiri_node_01 Temp", "unit_of_measurement": "°C", ...}` | Temperature sensor config |

### State Topics (Published Every 10s)

| Topic | Payload | Description |
|-------|---------|-------------|
| `hiri/state/hiri_node_01/switch` | `ON` / `OFF` | Relay state |
| `hiri/state/hiri_node_01/soil` | `42.5` | Soil moisture % |
| `hiri/state/hiri_node_01/temp` | `24.3` | Temperature °C |
| `hiri/status` | `online` / `offline` | Device availability |

### Command Topics (Subscribed by Firmware)

| Topic | Payload | Description |
|-------|---------|-------------|
| `hiri/cmd/hiri_node_01/switch` | `ON` / `OFF` | Toggle relay |

### Sample Discovery Payload (from firmware)

```json
{
  "topic": "homeassistant/switch/hiri/hiri_node_01/config",
  "payload": {
    "name": "hiri_node_01 Relay",
    "unique_id": "hiri_node_01_switch",
    "state_topic": "hiri/state/hiri_node_01/switch",
    "command_topic": "hiri/cmd/hiri_node_01/switch",
    "payload_on": "ON",
    "payload_off": "OFF",
    "availability_topic": "hiri/status",
    "payload_available": "online",
    "payload_not_available": "offline",
    "device": {
      "identifiers": ["hiri_node_01"],
      "manufacturer": "HIRI",
      "model": "HIRI Firmware",
      "name": "hiri_node_01"
    }
  }
}
```

### Sample Discovery Payload (from bridge — sensor)

```json
{
  "topic": "homeassistant/sensor/hiri/sensor_soil_moisture_planter/config",
  "payload": {
    "name": "Planter soil moisture",
    "unique_id": "hiri_sensor_soil_moisture_planter",
    "state_topic": "hiri/state/sensor/soil_moisture_planter",
    "unit_of_measurement": "%",
    "device_class": "moisture",
    "state_class": "measurement",
    "availability_topic": "hiri/status",
    "device": {
      "identifiers": ["hiri_sensor.soil_moisture_planter"],
      "manufacturer": "HIRI",
      "model": "HIRI-SOIL",
      "name": "Planter soil moisture",
      "suggested_area": "living_room"
    }
  }
}
```

---

## Step 5: Home Assistant Auto-Discovery Results

### HA Entities Created

After the firmware connects and publishes discovery, Home Assistant automatically creates the following entities:

| Entity ID | Name | Domain | Device Class |
|-----------|------|--------|-------------|
| `switch.hiri_node_01_relay` | hiri_node_01 Relay | switch | switch |
| `sensor.hiri_node_01_soil` | hiri_node_01 Soil | sensor | moisture |
| `sensor.hiri_node_01_temp` | hiri_node_01 Temp | sensor | temperature |

### Verification in HA

1. **Check MQTT broker**: `mosquitto_sub -h localhost -t "homeassistant/+/hiri/#" -v`
2. **Check HA entities**: Settings → Devices & Services → MQTT → HIRI devices
3. **Check dashboard**: Add entities to Lovelace dashboard

### Screenshots

![HIRI bridge demo — MQTT discovery dry-run output](screenshots/demo-discovery.png)
*Figure 1: HIRI bridge demo showing MQTT discovery dry-run with 11 discovery messages published to `homeassistant/<domain>/hiri/<id>/config` topics.*

![HIRI bridge demo — device list](screenshots/demo-devices.png)
*Figure 2: HIRI bridge demo showing 100 devices across 18 domains (light, switch, sensor, binary_sensor, climate, cover, lock, fan, etc.) with states, areas, and adapter sources.*

![HIRI bridge admin — floorplan view](screenshots/admin-area-floorplan.png)
*Figure 3: HIRI admin area floorplan showing devices grouped by room/area.*

![HIRI bridge admin — mobile floorplan](screenshots/admin-area-floorplan-mobile.png)
*Figure 4: HIRI admin area floorplan responsive mobile view.*

---

## Step 6: End-to-End Verification

### Verify MQTT Communication

```bash
# Terminal 1: Subscribe to all HIRI topics
mosquitto_sub -h localhost -t "hiri/#" -v

# Terminal 2: Subscribe to HA discovery topics
mosquitto_sub -h localhost -t "homeassistant/+/hiri/#" -v
```

**Expected output after firmware connects:**
```
hiri/status online
homeassistant/switch/hiri/hiri_node_01/config {"name": "hiri_node_01 Relay", ...}
homeassistant/sensor/hiri/hiri_node_01_soil/config {"name": "hiri_node_01 Soil", ...}
homeassistant/sensor/hiri/hiri_node_01_temp/config {"name": "hiri_node_01 Temp", ...}
hiri/state/hiri_node_01/switch OFF
hiri/state/hiri_node_01/soil 42.5
hiri/state/hiri_node_01/temp 24.3
```

### Verify HA Integration

1. Open Home Assistant web UI
2. Navigate to Settings → Devices & Services → MQTT
3. Confirm HIRI devices appear under "Discovered devices"
4. Add entities to dashboard
5. Verify live sensor readings update every 10 seconds
6. Toggle relay switch — confirm state changes in HA

### Test Relay Control

```bash
# Turn relay ON via MQTT
mosquitto_pub -h localhost -t "hiri/cmd/hiri_node_01/switch" -m "ON"

# Verify state change
# → hiri/state/hiri_node_01/switch should publish "ON"
# → HA sensor should reflect "on" state
```

---

## Bridge-Only Mode (Without ESP Hardware)

The HIRI bridge can run standalone with simulated sensors:

```bash
# Install bridge
cd packages/bridge
pip install -e ".[dev,api,mqtt]"

# Seed demo devices
hiri-bridge devices seed

# List devices
hiri-bridge devices list

# Export HA discovery JSON
hiri-bridge ha discovery --out data/out/discovery.json

# Run MQTT discovery publish (dry-run)
hiri-bridge mqtt publish --dry-run

# Simulate sensor readings
hiri-bridge devices sim-tick

# View sensor history
hiri-bridge devices sim-history --id sensor.soil_moisture_planter

# Start API server
hiri-bridge serve --host 0.0.0.0 --port 8780
```

### Full Discovery Export (Bridge)

The bridge registers **100 devices** across **18 domains**:

| Domain | Count | Examples |
|--------|-------|---------|
| sensor | 36 | Soil moisture, temperature, PM2.5, humidity |
| binary_sensor | 13 | Door contact, leak, motion, occupancy |
| switch | 12 | Irrigation, relay, pump |
| light | 7 | RGB, dimmable, color temp |
| media_player | 6 | TV, speakers |
| fan | 5 | Ceiling, exhaust |
| climate | 3 | Thermostat |
| cover | 3 | Garage door, blind |
| lock | 3 | Front door, deadbolt |
| vacuum | 2 | Robot cleaner |
| select | 2 | Mode selector |
| humidifier | 2 | Humidifier |
| siren | 1 | Alarm siren |
| camera | 1 | IP camera |
| button | 1 | Doorbell |
| number | 1 | Dimmer value |
| water_heater | 1 | Water heater |
| alarm_control_panel | 1 | Home alarm |

Each device publishes a `homeassistant/<domain>/hiri/<id>/config` discovery message with the full MQTT discovery payload described in [docs/mqtt-discovery.md](mqtt-discovery.md) and [docs/ha-entity-mapping-export.md](ha-entity-mapping-export.md).

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| ESP not connecting to WiFi | Wrong SSID/password | Check `hiri_config.h` — SSID must be exact (case-sensitive) |
| ESP not connecting to MQTT | Wrong broker IP/port | Verify MQTT broker is running: `mosquitto -v` |
| No HA entities appearing | MQTT discovery disabled | Add `discovery: true` to HA `mqtt:` config |
| Entities show "Unavailable" | No status topic | Check firmware `hiri/status` publishes "online" |
| Sensor values not updating | Sensor hardware issue | Check wiring; firmware falls back to simulated values |
| Bridge demo fails | Missing dependencies | `pip install -e ".[dev,api,mqtt]"` |

---

## Evidence Summary

| Item | Status | Location |
|------|--------|----------|
| Firmware source code | ✅ Implemented | `packages/firmware/src/main.cpp` |
| HA MQTT discovery | ✅ Implemented | `packages/firmware/src/main.cpp` (lines 44-97) |
| Bridge device registry | ✅ Implemented | `packages/bridge/src/hiri_bridge/devices/` |
| Bridge HA discovery export | ✅ Implemented | `packages/bridge/src/hiri_bridge/ha/discovery.py` |
| Bridge MQTT publish | ✅ Implemented | `packages/bridge/src/hiri_bridge/adapters/mqtt_pub.py` |
| Bridge demo (offline) | ✅ Verified | `hiri-bridge demo` — 100 devices, 18 domains |
| Discovery JSON export | ✅ Verified | `data/out/discovery.json` — 100 entities |
| MQTT dry-run output | ✅ Verified | 11 discovery messages published |
| Architecture diagrams | ✅ Available | `docs/diagrams/architecture.svg` |
| Screenshots | ✅ Available | `docs/screenshots/demo-discovery.png`, `demo-devices.png` |
| E2E documentation | ✅ This document | `docs/e2e-esp-bridge-ha-discovery.md` |

---

## Reproducible Steps

To reproduce this E2E path:

1. Clone HIRI: `git clone https://github.com/mergeos-bounties/HIRI.git`
2. Install bridge: `cd packages/bridge && pip install -e ".[dev,api,mqtt]"`
3. Run demo: `hiri-bridge demo`
4. Export discovery: `hiri-bridge ha discovery --out data/out/discovery.json`
5. [Optional] Flash ESP32: `cd packages/firmware && pio run -e esp32dev --target upload`
6. [Optional] Subscribe to MQTT: `mosquitto_sub -h localhost -t "homeassistant/+/hiri/#" -v`
7. Verify HA entities appear in Home Assistant → Settings → Devices & Services → MQTT