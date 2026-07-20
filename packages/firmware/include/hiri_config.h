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

// Sensor hardware is opt-in so existing simulated telemetry still works without
// attached DHT22/soil probes. Override these from build_flags or this file.
#ifndef HIRI_DHT_ENABLED
#define HIRI_DHT_ENABLED 0
#endif
#ifndef HIRI_DHT_PIN
#define HIRI_DHT_PIN 4
#endif
#ifndef HIRI_DHT_TYPE
#define HIRI_DHT_TYPE DHT22
#endif

#ifndef HIRI_SOIL_ADC_ENABLED
#define HIRI_SOIL_ADC_ENABLED 0
#endif
#ifndef HIRI_SOIL_ADC_PIN
#if defined(HIRI_BOARD_ESP8266) || defined(ESP8266)
#define HIRI_SOIL_ADC_PIN A0
#else
#define HIRI_SOIL_ADC_PIN 34
#endif
#endif
#ifndef HIRI_SOIL_ADC_DRY
#if defined(HIRI_BOARD_ESP8266) || defined(ESP8266)
#define HIRI_SOIL_ADC_DRY 1023
#else
#define HIRI_SOIL_ADC_DRY 3200
#endif
#endif
#ifndef HIRI_SOIL_ADC_WET
#if defined(HIRI_BOARD_ESP8266) || defined(ESP8266)
#define HIRI_SOIL_ADC_WET 300
#else
#define HIRI_SOIL_ADC_WET 1200
#endif
#endif
