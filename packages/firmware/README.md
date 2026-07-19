# HIRI-firmware (Firmware)

PlatformIO project for **ESP32** and **ESP8266**.

## Build

```bash
pio run -e esp32dev
pio run -e esp8266
```

## Configure

Edit `include/hiri_config.h` (WiFi + MQTT broker = Home Assistant Mosquitto).

## Features

- HA MQTT discovery for switch + soil + temperature
- MQTT-triggered HTTP OTA updates with status telemetry
- Compact telemetry loop (10s)
- Command topic for relay

## OTA update flow

1. Build a firmware binary for the target board:

```bash
pio run -e esp32dev
pio run -e esp8266
```

2. Host the generated binary on an HTTP endpoint reachable from the ESP board:

```bash
python3 -m http.server 8080 -d .pio/build/esp32dev
```

3. Publish an OTA command over MQTT. JSON payloads may include an optional
`version` for traceability and must include `token` when `HIRI_OTA_TOKEN` is set:

```bash
mosquitto_pub -h homeassistant.local \
  -t hiri/cmd/hiri_node_01/ota \
  -m '{"url":"http://192.168.1.10:8080/firmware.bin","version":"2026.07.19","token":"change-me"}'
```

The device publishes progress to `hiri/state/<device_id>/ota` as JSON states
such as `idle`, `downloading`, `rebooting`, or `error`. Home Assistant discovers
this as an OTA status sensor.

Use OTA only on a trusted broker/network. Set MQTT credentials and override
`HIRI_OTA_TOKEN` with a non-empty value through build flags for shared
deployments.

## Bounties

Real sensors, OTA, deep sleep, TLS MQTT — see monorepo issues labeled `firmware`.
