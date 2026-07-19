# HIRI-firmware (Firmware)

PlatformIO project for **ESP32** and **ESP8266**.

## Build

```bash
pio run -e esp32dev
pio run -e esp8266
```

## Configure

Edit `include/hiri_config.h` (WiFi + MQTT broker = Home Assistant Mosquitto).

Sensor hardware is configurable in `include/hiri_config.h` or PlatformIO
`build_flags`:

- `HIRI_DHT_ENABLED=1`, `HIRI_DHT_PIN`, and `HIRI_DHT_TYPE` enable DHT22
  temperature readings.
- `HIRI_SOIL_ADC_ENABLED=1`, `HIRI_SOIL_ADC_PIN`, `HIRI_SOIL_ADC_DRY`, and
  `HIRI_SOIL_ADC_WET` enable calibrated soil ADC readings.

Defaults keep simulated telemetry enabled when hardware is disabled, missing, or
returns an invalid reading.

## Features

- HA MQTT discovery for switch + soil + temperature
- Optional DHT22 temperature and soil ADC moisture drivers
- Compact telemetry loop (10s)
- Command topic for relay

## Bounties

Real sensors, OTA, deep sleep, TLS MQTT — see monorepo issues labeled `firmware`.
