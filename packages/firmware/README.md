# HIRI-firmware (Firmware)

PlatformIO project for **ESP32** and **ESP8266**.

## Build

```bash
pio run -e esp32dev
pio run -e esp8266
pio run -e esp32dev_tls
pio run -e esp8266_tls
```

## Configure

Edit `include/hiri_config.h` (WiFi + MQTT broker = Home Assistant Mosquitto).

MQTT uses plaintext port `1883` by default. Enable TLS at build time when your
broker exposes secure MQTT:

```ini
build_flags =
  -DHIRI_MQTT_TLS=1
  -DHIRI_MQTT_CA_CERT="\"-----BEGIN CERTIFICATE-----\\n...\\n-----END CERTIFICATE-----\\n\""
```

When `HIRI_MQTT_TLS=1`, the default MQTT port becomes `8883`. Override
`HIRI_MQTT_PORT` if your broker uses a different TLS port.

For local development with a self-signed broker certificate, you can compile
with `-DHIRI_MQTT_TLS_INSECURE=1` to skip certificate validation. Do not use
that mode for production Home Assistant installs.

## Features

- HA MQTT discovery for switch + soil + temperature
- Compact telemetry loop (10s)
- Command topic for relay

## Bounties

Real sensors, OTA, deep sleep, TLS MQTT — see monorepo issues labeled `firmware`.
