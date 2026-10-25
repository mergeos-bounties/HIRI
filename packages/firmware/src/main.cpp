#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "hiri_config.h"

#if HIRI_MQTT_TLS
#include <WiFiClientSecure.h>
#endif

#if HIRI_DHT_ENABLED
#include <DHT.h>
DHT dht(HIRI_DHT_PIN, HIRI_DHT_TYPE);
#endif

#if HIRI_MQTT_TLS
WiFiClientSecure netClient;
#else
WiFiClient netClient;
#endif

PubSubClient mqtt(netClient);

bool relayOn = false;
unsigned long lastTelemetry = 0;
unsigned long lastReconnect = 0;

void topic(char *out, size_t len, const char *suffix) {
  snprintf(out, len, "hiri/%s/%s", HIRI_DEVICE_ID, suffix);
}

int readSoil() {
#if HIRI_SOIL_ADC_ENABLED
  int raw = analogRead(HIRI_SOIL_ADC_PIN);
  int pct = map(raw, HIRI_SOIL_ADC_DRY, HIRI_SOIL_ADC_WET, 0, 100);
  return constrain(pct, 0, 100);
#else
  return random(300, 700) / 10;
#endif
}

float readTemperature() {
#if HIRI_DHT_ENABLED
  float t = dht.readTemperature();
  if (!isnan(t)) return t;
#endif
  return 20.0 + (random(-20, 21) / 10.0);
}

void publishState() {
  char t[96];
  topic(t, sizeof(t), "switch/state");
  mqtt.publish(t, relayOn ? "ON" : "OFF", true);
}

void publishTelemetry() {
  char t[96];
  char payload[32];

  topic(t, sizeof(t), "soil");
  snprintf(payload, sizeof(payload), "%d", readSoil());
  mqtt.publish(t, payload, true);

  topic(t, sizeof(t), "temperature");
  snprintf(payload, sizeof(payload), "%.1f", readTemperature());
  mqtt.publish(t, payload, true);

  publishState();
}

void setRelay(bool on) {
  relayOn = on;
  digitalWrite(HIRI_RELAY_PIN, on ? HIGH : LOW);
  publishState();
}

void publishDiscovery() {
  char t[96];
  char payload[512];
  char avail[96];
  topic(avail, sizeof(avail), "availability");

  snprintf(t, sizeof(t), "homeassistant/switch/%s/config", HIRI_DEVICE_ID);
  snprintf(payload, sizeof(payload),
           "{\"name\":\"HIRI Switch\",\"uniq_id\":\"%s_switch\",\"stat_t\":\"hiri/%s/switch/state\",\"cmd_t\":\"hiri/%s/switch/set\",\"avty_t\":\"%s\",\"pl_avail\":\"online\",\"pl_not_avail\":\"offline\"}",
           HIRI_DEVICE_ID, HIRI_DEVICE_ID, HIRI_DEVICE_ID, avail);
  mqtt.publish(t, payload, true);

  snprintf(t, sizeof(t), "homeassistant/sensor/%s_soil/config", HIRI_DEVICE_ID);
  snprintf(payload, sizeof(payload),
           "{\"name\":\"HIRI Soil\",\"uniq_id\":\"%s_soil\",\"stat_t\":\"hiri/%s/soil\",\"unit_of_meas\":\"%%\",\"dev_cla\":\"moisture\",\"avty_t\":\"%s\",\"pl_avail\":\"online\",\"pl_not_avail\":\"offline\"}",
           HIRI_DEVICE_ID, HIRI_DEVICE_ID, avail);
  mqtt.publish(t, payload, true);

  snprintf(t, sizeof(t), "homeassistant/sensor/%s_temperature/config", HIRI_DEVICE_ID);
  snprintf(payload, sizeof(payload),
           "{\"name\":\"HIRI Temperature\",\"uniq_id\":\"%s_temperature\",\"stat_t\":\"hiri/%s/temperature\",\"unit_of_meas\":\"\\u00b0C\",\"dev_cla\":\"temperature\",\"avty_t\":\"%s\",\"pl_avail\":\"online\",\"pl_not_avail\":\"offline\"}",
           HIRI_DEVICE_ID, HIRI_DEVICE_ID, avail);
  mqtt.publish(t, payload, true);
}

void callback(char *t, byte *payload, unsigned int length) {
  char cmd[96];
  topic(cmd, sizeof(cmd), "switch/set");
  if (strcmp(t, cmd) != 0) return;

  char msg[16];
  unsigned int n = length < sizeof(msg) - 1 ? length : sizeof(msg) - 1;
  memcpy(msg, payload, n);
  msg[n] = '\0';

  if (!strcmp(msg, "ON") || !strcmp(msg, "on") || !strcmp(msg, "1")) {
    setRelay(true);
  } else if (!strcmp(msg, "OFF") || !strcmp(msg, "off") || !strcmp(msg, "0")) {
    setRelay(false);
  }
}

void connectWifi() {
  if (WiFi.status() == WL_CONNECTED) return;
  WiFi.mode(WIFI_STA);
  WiFi.begin(HIRI_WIFI_SSID, HIRI_WIFI_PASS);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
    delay(250);
  }
}

bool connectMqtt() {
  char avail[96];
  topic(avail, sizeof(avail), "availability");
  if (!mqtt.connect(HIRI_DEVICE_ID, HIRI_MQTT_USER, HIRI_MQTT_PASS, avail, 0, true, "offline")) {
    return false;
  }
  mqtt.publish(avail, "online", true);
  publishDiscovery();
  publishState();
  publishTelemetry();
  return true;
}

void setup() {
  Serial.begin(115200);
  pinMode(HIRI_RELAY_PIN, OUTPUT);
  digitalWrite(HIRI_RELAY_PIN, LOW);

#if HIRI_DHT_ENABLED
  dht.begin();
#endif

#if HIRI_MQTT_TLS
#if HIRI_MQTT_TLS_INSECURE
  netClient.setInsecure();
#else
  netClient.setCACert(HIRI_MQTT_CA_CERT);
#endif
#endif

  mqtt.setServer(HIRI_MQTT_HOST, HIRI_MQTT_PORT);
  mqtt.setCallback(callback);
  mqtt.setKeepAlive(30);
  mqtt.setSocketTimeout(10);
  mqtt.setBufferSize(1024);

  connectWifi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWifi();
  }

  if (!mqtt.connected()) {
    if (millis() - lastReconnect > 5000) {
      lastReconnect = millis();
      connectMqtt();
    }
  } else {
    mqtt.loop();
    if (millis() - lastTelemetry > 10000) {
      lastTelemetry = millis();
      publishTelemetry();
    }
  }

  delay(10);
}
