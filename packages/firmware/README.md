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
- Compact telemetry loop (10s)
- Command topic for relay

## Bounties

Real sensors, OTA, deep sleep, TLS MQTT — see monorepo issues labeled `firmware`.
