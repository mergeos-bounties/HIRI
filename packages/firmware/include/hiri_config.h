#pragma once

// Override via build flags or local secrets (do not commit real WiFi passwords).
#ifndef HIRI_WIFI_SSID
#define HIRI_WIFI_SSID "YOUR_WIFI"
#endif
#ifndef HIRI_WIFI_PASS
#define HIRI_WIFI_PASS "YOUR_PASSWORD"
#endif
#ifndef HIRI_MQTT_HOST
#define HIRI_MQTT_HOST "homeassistant.local"
#endif
#ifndef HIRI_MQTT_PORT
#define HIRI_MQTT_PORT 1883
#endif
#ifndef HIRI_MQTT_USER
#define HIRI_MQTT_USER ""
#endif
#ifndef HIRI_MQTT_PASS
#define HIRI_MQTT_PASS ""
#endif
#ifndef HIRI_DEVICE_ID
#define HIRI_DEVICE_ID "hiri_node_01"
#endif

// Telemetry cadence for normal continuous mode and each deep-sleep wake cycle.
#ifndef HIRI_TELEMETRY_INTERVAL_MS
#define HIRI_TELEMETRY_INTERVAL_MS 10000UL
#endif

// Keep deep sleep disabled by default so command/relay behavior stays continuous.
#ifndef HIRI_DEEP_SLEEP_ENABLED
#define HIRI_DEEP_SLEEP_ENABLED 0
#endif
#ifndef HIRI_DEEP_SLEEP_INTERVAL_SECONDS
#define HIRI_DEEP_SLEEP_INTERVAL_SECONDS 300UL
#endif
#ifndef HIRI_MQTT_FLUSH_DELAY_MS
#define HIRI_MQTT_FLUSH_DELAY_MS 250UL
#endif

// Battery reporting is opt-in because boards need a wired and calibrated divider.
#ifndef HIRI_BATTERY_REPORTING_ENABLED
#define HIRI_BATTERY_REPORTING_ENABLED 0
#endif
#ifndef HIRI_BATTERY_ADC_PIN
#if defined(HIRI_BOARD_ESP8266)
#define HIRI_BATTERY_ADC_PIN A0
#else
#define HIRI_BATTERY_ADC_PIN 34
#endif
#endif
#ifndef HIRI_BATTERY_ADC_MAX
#if defined(HIRI_BOARD_ESP8266)
#define HIRI_BATTERY_ADC_MAX 1023.0f
#else
#define HIRI_BATTERY_ADC_MAX 4095.0f
#endif
#endif
#ifndef HIRI_BATTERY_ADC_REF_V
#define HIRI_BATTERY_ADC_REF_V 3.3f
#endif
#ifndef HIRI_BATTERY_DIVIDER_RATIO
#define HIRI_BATTERY_DIVIDER_RATIO 2.0f
#endif
#ifndef HIRI_BATTERY_MIN_V
#define HIRI_BATTERY_MIN_V 3.0f
#endif
#ifndef HIRI_BATTERY_MAX_V
#define HIRI_BATTERY_MAX_V 4.2f
#endif
