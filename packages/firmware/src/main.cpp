/**
 * HIRI Firmware — lightweight MQTT client for ESP32/ESP8266.
 * Publishes Home Assistant MQTT discovery + state for:
 *  - switch (relay)
 *  - sensor (fake soil moisture / temperature)
 *
 * Configure WiFi/MQTT in include/hiri_config.h or build_flags.
 */
#include <Arduino.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "hiri_config.h"

#if defined(ESP8266)
#include <ESP8266WiFi.h>
#else
#include <WiFi.h>
#endif
#if HIRI_DEEP_SLEEP_ENABLED && !defined(ESP8266)
#include <esp_sleep.h>
#endif

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

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
String stateTopicBatteryVoltage() {
  return String("hiri/state/") + HIRI_DEVICE_ID + "/battery_voltage";
}
String stateTopicBatteryPercent() {
  return String("hiri/state/") + HIRI_DEVICE_ID + "/battery_percent";
}

void addDevice(JsonDocument &doc) {
  JsonObject dev = doc["device"].to<JsonObject>();
  dev["identifiers"][0] = HIRI_DEVICE_ID;
  dev["manufacturer"] = "HIRI";
  dev["model"] = "HIRI Firmware";
  dev["name"] = HIRI_DEVICE_ID;
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
    addDevice(doc);
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
#if HIRI_BATTERY_REPORTING_ENABLED
  // Battery voltage sensor
  {
    String topic = String("homeassistant/sensor/hiri/") + HIRI_DEVICE_ID + "_battery_voltage/config";
    JsonDocument doc;
    doc["name"] = String(HIRI_DEVICE_ID) + " Battery Voltage";
    doc["unique_id"] = String(HIRI_DEVICE_ID) + "_battery_voltage";
    doc["state_topic"] = stateTopicBatteryVoltage();
    doc["unit_of_measurement"] = "V";
    doc["device_class"] = "voltage";
    doc["state_class"] = "measurement";
    doc["entity_category"] = "diagnostic";
    doc["availability_topic"] = STATUS_TOPIC;
    addDevice(doc);
    char buf[512];
    size_t n = serializeJson(doc, buf, sizeof(buf));
    mqtt.publish(topic.c_str(), (uint8_t *)buf, n, true);
  }
  // Battery percentage sensor
  {
    String topic = String("homeassistant/sensor/hiri/") + HIRI_DEVICE_ID + "_battery_percent/config";
    JsonDocument doc;
    doc["name"] = String(HIRI_DEVICE_ID) + " Battery";
    doc["unique_id"] = String(HIRI_DEVICE_ID) + "_battery_percent";
    doc["state_topic"] = stateTopicBatteryPercent();
    doc["unit_of_measurement"] = "%";
    doc["device_class"] = "battery";
    doc["state_class"] = "measurement";
    doc["entity_category"] = "diagnostic";
    doc["availability_topic"] = STATUS_TOPIC;
    addDevice(doc);
    char buf[512];
    size_t n = serializeJson(doc, buf, sizeof(buf));
    mqtt.publish(topic.c_str(), (uint8_t *)buf, n, true);
  }
#endif
}

void publishTelemetry() {
  if (!mqtt.connected()) return;

  // Simulated sensors — replace with real ADC/I2C in bounties
  unsigned long now = millis();
  float soil = 35.0f + (now % 2000) / 100.0f;
  float temp = 24.0f + (now % 1000) / 200.0f;
  char buf[16];
  dtostrf(soil, 0, 1, buf);
  mqtt.publish(stateTopicSoil().c_str(), buf, true);
  dtostrf(temp, 0, 1, buf);
  mqtt.publish(stateTopicTemp().c_str(), buf, true);

#if HIRI_BATTERY_REPORTING_ENABLED
  int raw = analogRead(HIRI_BATTERY_ADC_PIN);
  float voltage = (raw / HIRI_BATTERY_ADC_MAX) * HIRI_BATTERY_ADC_REF_V * HIRI_BATTERY_DIVIDER_RATIO;
  float percent = 0.0f;
  if (HIRI_BATTERY_MAX_V > HIRI_BATTERY_MIN_V) {
    percent = (voltage - HIRI_BATTERY_MIN_V) * 100.0f / (HIRI_BATTERY_MAX_V - HIRI_BATTERY_MIN_V);
    percent = constrain(percent, 0.0f, 100.0f);
  }
  dtostrf(voltage, 0, 2, buf);
  mqtt.publish(stateTopicBatteryVoltage().c_str(), buf, true);
  dtostrf(percent, 0, 0, buf);
  mqtt.publish(stateTopicBatteryPercent().c_str(), buf, true);
#endif
}

void enterDeepSleep() {
#if HIRI_DEEP_SLEEP_ENABLED
  if (mqtt.connected()) {
    mqtt.publish(STATUS_TOPIC, "offline", true);
    mqtt.loop();
    delay(HIRI_MQTT_FLUSH_DELAY_MS);
    mqtt.disconnect();
  }
  WiFi.disconnect(true);
  Serial.flush();
#if defined(ESP8266)
  ESP.deepSleep((uint64_t)HIRI_DEEP_SLEEP_INTERVAL_SECONDS * 1000000ULL);
#else
  esp_sleep_enable_timer_wakeup((uint64_t)HIRI_DEEP_SLEEP_INTERVAL_SECONDS * 1000000ULL);
  esp_deep_sleep_start();
#endif
#endif
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
  bool telemetryDue = now - lastTelemetry > HIRI_TELEMETRY_INTERVAL_MS;
#if HIRI_DEEP_SLEEP_ENABLED
  telemetryDue = telemetryDue || lastTelemetry == 0;
#endif
  if (telemetryDue) {
    lastTelemetry = now;
    publishTelemetry();
    enterDeepSleep();
  }
}
