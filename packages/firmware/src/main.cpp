/**
 * HIRI Firmware — lightweight MQTT client for ESP32/ESP8266.
 * Publishes Home Assistant MQTT discovery + state for:
 *  - switch (relay)
 *  - sensor (DHT22 temperature + soil ADC, with simulated fallback)
 *
 * Configure WiFi/MQTT in include/hiri_config.h or build_flags.
 */
#include <Arduino.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <PubSubClient.h>
#include "hiri_config.h"

#if defined(ESP8266)
#include <ESP8266WiFi.h>
#else
#include <WiFi.h>
#endif

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
#if HIRI_DHT_ENABLED
DHT dht(HIRI_DHT_PIN, HIRI_DHT_TYPE);
#endif

const char *STATUS_TOPIC = "hiri/status";
bool relayOn = false;
unsigned long lastTelemetry = 0;

String stateTopicSwitch() {
  return String("hiri/state/") + HIRI_DEVICE_ID + "/switch";
}
String cmdTopicSwitch() {
  return String("hiri/cmd/") + HIRI_DEVICE_ID + "/switch";
}
String stateTopicSoil() {
  return String("hiri/state/") + HIRI_DEVICE_ID + "/soil";
}
String stateTopicTemp() {
  return String("hiri/state/") + HIRI_DEVICE_ID + "/temp";
}

void publishDiscovery() {
  // Switch
  {
    String topic = String("homeassistant/switch/hiri/") + HIRI_DEVICE_ID + "/config";
    JsonDocument doc;
    doc["name"] = String(HIRI_DEVICE_ID) + " Relay";
    doc["unique_id"] = String(HIRI_DEVICE_ID) + "_switch";
    doc["state_topic"] = stateTopicSwitch();
    doc["command_topic"] = cmdTopicSwitch();
    doc["payload_on"] = "ON";
    doc["payload_off"] = "OFF";
    doc["availability_topic"] = STATUS_TOPIC;
    doc["payload_available"] = "online";
    doc["payload_not_available"] = "offline";
    JsonObject dev = doc["device"].to<JsonObject>();
    dev["identifiers"][0] = HIRI_DEVICE_ID;
    dev["manufacturer"] = "HIRI";
    dev["model"] = "HIRI Firmware";
    dev["name"] = HIRI_DEVICE_ID;
    char buf[512];
    size_t n = serializeJson(doc, buf, sizeof(buf));
    mqtt.publish(topic.c_str(), (uint8_t *)buf, n, true);
  }
  // Soil sensor
  {
    String topic = String("homeassistant/sensor/hiri/") + HIRI_DEVICE_ID + "_soil/config";
    JsonDocument doc;
    doc["name"] = String(HIRI_DEVICE_ID) + " Soil";
    doc["unique_id"] = String(HIRI_DEVICE_ID) + "_soil";
    doc["state_topic"] = stateTopicSoil();
    doc["unit_of_measurement"] = "%";
    doc["device_class"] = "moisture";
    doc["state_class"] = "measurement";
    doc["availability_topic"] = STATUS_TOPIC;
    char buf[512];
    size_t n = serializeJson(doc, buf, sizeof(buf));
    mqtt.publish(topic.c_str(), (uint8_t *)buf, n, true);
  }
  // Temp sensor
  {
    String topic = String("homeassistant/sensor/hiri/") + HIRI_DEVICE_ID + "_temp/config";
    JsonDocument doc;
    doc["name"] = String(HIRI_DEVICE_ID) + " Temp";
    doc["unique_id"] = String(HIRI_DEVICE_ID) + "_temp";
    doc["state_topic"] = stateTopicTemp();
    doc["unit_of_measurement"] = "°C";
    doc["device_class"] = "temperature";
    doc["state_class"] = "measurement";
    doc["availability_topic"] = STATUS_TOPIC;
    char buf[512];
    size_t n = serializeJson(doc, buf, sizeof(buf));
    mqtt.publish(topic.c_str(), (uint8_t *)buf, n, true);
  }
}

float simulatedSoil(unsigned long now) {
  return 35.0f + (now % 2000) / 100.0f;
}

float simulatedTemp(unsigned long now) {
  return 24.0f + (now % 1000) / 200.0f;
}

float clampPercent(float value) {
  if (value < 0.0f) return 0.0f;
  if (value > 100.0f) return 100.0f;
  return value;
}

bool readSoil(float &value) {
#if HIRI_SOIL_ADC_ENABLED
  if (HIRI_SOIL_ADC_DRY == HIRI_SOIL_ADC_WET) {
    return false;
  }
  int raw = analogRead(HIRI_SOIL_ADC_PIN);
  value = clampPercent(((float)HIRI_SOIL_ADC_DRY - raw) * 100.0f /
                       ((float)HIRI_SOIL_ADC_DRY - HIRI_SOIL_ADC_WET));
  return true;
#else
  (void)value;
  return false;
#endif
}

bool readTemperature(float &value) {
#if HIRI_DHT_ENABLED
  float reading = dht.readTemperature();
  if (!isnan(reading)) {
    value = reading;
    return true;
  }
#else
  (void)value;
#endif
  return false;
}

void publishTelemetry(unsigned long now) {
  float soil;
  if (!readSoil(soil)) {
    soil = simulatedSoil(now);
  }

  float temp;
  if (!readTemperature(temp)) {
    temp = simulatedTemp(now);
  }

  char buf[16];
  dtostrf(soil, 0, 1, buf);
  mqtt.publish(stateTopicSoil().c_str(), buf, true);
  dtostrf(temp, 0, 1, buf);
  mqtt.publish(stateTopicTemp().c_str(), buf, true);
}

void onMqttMessage(char *topic, byte *payload, unsigned int length) {
  String t(topic);
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  if (t == cmdTopicSwitch()) {
    relayOn = (msg == "ON" || msg == "on" || msg == "1");
    mqtt.publish(stateTopicSwitch().c_str(), relayOn ? "ON" : "OFF", true);
  }
}

void ensureMqtt() {
  if (mqtt.connected()) return;
  String clientId = String("hiri-") + HIRI_DEVICE_ID;
  if (mqtt.connect(clientId.c_str(), HIRI_MQTT_USER, HIRI_MQTT_PASS, STATUS_TOPIC, 0, true, "offline")) {
    mqtt.publish(STATUS_TOPIC, "online", true);
    mqtt.subscribe(cmdTopicSwitch().c_str());
    publishDiscovery();
    mqtt.publish(stateTopicSwitch().c_str(), relayOn ? "ON" : "OFF", true);
  }
}

void setup() {
  Serial.begin(115200);
#if HIRI_DHT_ENABLED
  dht.begin();
#endif
  WiFi.mode(WIFI_STA);
  WiFi.begin(HIRI_WIFI_SSID, HIRI_WIFI_PASS);
  uint8_t tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 40) {
    delay(250);
    tries++;
  }
  mqtt.setServer(HIRI_MQTT_HOST, HIRI_MQTT_PORT);
  mqtt.setCallback(onMqttMessage);
  mqtt.setBufferSize(1024);
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    ensureMqtt();
    mqtt.loop();
  }
  unsigned long now = millis();
  if (now - lastTelemetry > 10000) {
    lastTelemetry = now;
    if (mqtt.connected()) {
      publishTelemetry(now);
    }
  }
}
