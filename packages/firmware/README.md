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

## TLS MQTT (optional)

Production HA brokers should use TLS. Enable it with a build flag; the default
broker port becomes `8883` when TLS is enabled:

```bash
PLATFORMIO_BUILD_FLAGS="-D HIRI_MQTT_TLS=1" pio run -e esp32dev
```

Or add `-D HIRI_MQTT_TLS=1` to `build_flags` in `platformio.ini`.

By default TLS uses `setInsecure()` so a self-signed/unknown broker works
without extra setup. For verified TLS set `HIRI_MQTT_TLS_INSECURE=0` and provide
the broker CA PEM in `HIRI_MQTT_CA_CERT` (build flag or `hiri_config.h`).

```bash
PLATFORMIO_BUILD_FLAGS="-D HIRI_MQTT_TLS=1 -D HIRI_MQTT_TLS_INSECURE=0 -D HIRI_MQTT_CA_CERT='\"-----BEGIN CERTIFICATE-----...\"'" pio run -e esp32dev
```

## Features

- HA MQTT discovery for switch + soil + temperature
- Optional DHT22 temperature and soil ADC moisture drivers
- Optional TLS MQTT (`HIRI_MQTT_TLS=1`)
- Compact telemetry loop (10s)
- Command topic for relay

## Bounties

Real sensors, OTA, deep sleep — see monorepo issues labeled `firmware`.
