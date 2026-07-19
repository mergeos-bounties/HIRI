# HIRI-firmware (Firmware)

PlatformIO project for **ESP32** and **ESP8266**.

## Build

```bash
pio run -e esp32dev
pio run -e esp8266
```

## Configure

Edit `include/hiri_config.h` (WiFi + MQTT broker = Home Assistant Mosquitto).

### Battery and deep sleep

Battery reporting and deep sleep are opt-in so the default firmware keeps the
relay command topic online continuously.

Set these flags in `include/hiri_config.h` or PlatformIO `build_flags`:

- `HIRI_BATTERY_REPORTING_ENABLED=1` publishes retained voltage and percent
  states plus Home Assistant discovery sensors.
- `HIRI_BATTERY_ADC_PIN` selects the ADC pin. Defaults are `A0` on ESP8266 and
  GPIO 34 on ESP32.
- `HIRI_BATTERY_ADC_REF_V`, `HIRI_BATTERY_DIVIDER_RATIO`,
  `HIRI_BATTERY_MIN_V`, and `HIRI_BATTERY_MAX_V` calibrate the voltage divider
  and percentage estimate. Use a resistor divider that keeps the ADC input below
  the board limit.
- `HIRI_DEEP_SLEEP_ENABLED=1` publishes one telemetry sample, flushes MQTT, and
  enters timer deep sleep.
- `HIRI_DEEP_SLEEP_INTERVAL_SECONDS` controls the wake interval. ESP8266 boards
  must wire the wake pin as required by the board.

When deep sleep is enabled, MQTT commands are only available while the device is
awake. Leave it disabled for relay nodes that need always-on command handling.

## Features

- HA MQTT discovery for switch + soil + temperature
- Optional battery voltage/percent reporting
- Optional timer deep sleep after telemetry publish
- Compact telemetry loop (10s)
- Command topic for relay

## Bounties

Real sensors, OTA, deep sleep, TLS MQTT — see monorepo issues labeled `firmware`.
