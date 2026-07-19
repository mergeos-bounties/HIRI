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
#ifndef HIRI_MQTT_TLS
#define HIRI_MQTT_TLS 0
#endif
#ifndef HIRI_MQTT_TLS_INSECURE
#define HIRI_MQTT_TLS_INSECURE 0
#endif
#ifndef HIRI_MQTT_CA_CERT
#define HIRI_MQTT_CA_CERT ""
#endif
#ifndef HIRI_MQTT_PORT
#if HIRI_MQTT_TLS
#define HIRI_MQTT_PORT 8883
#else
#define HIRI_MQTT_PORT 1883
#endif
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
