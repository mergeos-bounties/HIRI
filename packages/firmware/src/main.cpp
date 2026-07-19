/**
 * HIRI Firmware — lightweight MQTT client for ESP32/ESP8266.
 * Publishes Home Assistant MQTT discovery + state for:
 *  - switch (relay)
 *  - sensor (fake soil moisture / temperature)
 *  - OTA status
 *
 * Configure WiFi/MQTT in include/hiri_config.h or build_flags.
 */
#include <Arduino.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "hiri_config.h"

#if defined(ESP8266)
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>
#include <ESP8266httpUpdate.h>
#else
#include <HTTPClient.h>
#include <HTTPUpdate.h>
#include <WiFi.h>
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
String cmdTopicOta() {
  return String("hiri/cmd/") + HIRI_DEVICE_ID + "/ota";
}
String stateTopicSoil() {
  return String("hiri/state/") + HIRI_DEVICE_ID + "/soil";
}
String stateTopicTemp() {
  return String("hiri/state/") + HIRI_DEVICE_ID + "/temp";
}
String stateTopicOta() {
  return String("hiri/state/") + HIRI_DEVICE_ID + "/ota";
}

struct OtaRequest {
  String url;
  String token;
  String version;
};

void publishOtaStatus(const char *state, const String &detail = "") {
  if (!mqtt.connected()) return;

  JsonDocument doc;
  doc["state"] = state;
  doc["device_id"] = HIRI_DEVICE_ID;
  doc["current_version"] = HIRI_FIRMWARE_VERSION;
  if (detail.length() > 0) {
    doc["detail"] = detail;
  }

  char buf[384];
  size_t n = serializeJson(doc, buf, sizeof(buf));
  mqtt.publish(stateTopicOta().c_str(), (uint8_t *)buf, n, false);
}

bool parseOtaRequest(const String &msg, OtaRequest &request) {
  request.url = "";
  request.token = "";
  request.version = "";

  String trimmed = msg;
  trimmed.trim();
  if (trimmed.length() == 0) return false;

  if (trimmed[0] == '{') {
    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, trimmed);
    if (err) return false;
    request.url = doc["url"] | "";
    request.token = doc["token"] | "";
    request.version = doc["version"] | "";
  } else {
    request.url = trimmed;
  }

  request.url.trim();
  return request.url.startsWith("http://");
}

bool isOtaAuthorized(const OtaRequest &request) {
  const String expectedToken = HIRI_OTA_TOKEN;
  return expectedToken.length() == 0 || request.token == expectedToken;
}

void performHttpOta(const OtaRequest &request) {
  if (!isOtaAuthorized(request)) {
    publishOtaStatus("error", "OTA token mismatch");
    return;
  }

  String detail = request.url;
  if (request.version.length() > 0) {
    detail += " version=" + request.version;
  }

  publishOtaStatus("downloading", detail);
  mqtt.publish(STATUS_TOPIC, "updating", true);
  mqtt.loop();

  WiFiClient otaClient;
#if defined(ESP8266)
  ESPhttpUpdate.rebootOnUpdate(false);
  t_httpUpdate_return result = ESPhttpUpdate.update(otaClient, request.url);
  String error = ESPhttpUpdate.getLastErrorString();
#else
  httpUpdate.rebootOnUpdate(false);
  t_httpUpdate_return result = httpUpdate.update(otaClient, request.url);
  String error = httpUpdate.getLastErrorString();
#endif

  if (result == HTTP_UPDATE_OK) {
    publishOtaStatus("rebooting", "OTA update applied");
    delay(250);
    ESP.restart();
  } else if (result == HTTP_UPDATE_NO_UPDATES) {
    publishOtaStatus("idle", "No update available");
    mqtt.publish(STATUS_TOPIC, "online", true);
  } else {
    publishOtaStatus("error", error.length() > 0 ? error : "HTTP OTA failed");
    mqtt.publish(STATUS_TOPIC, "online", true);
  }
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
  // OTA status sensor
  {
    String topic = String("homeassistant/sensor/hiri/") + HIRI_DEVICE_ID + "_ota/config";
    JsonDocument doc;
    doc["name"] = String(HIRI_DEVICE_ID) + " OTA Status";
    doc["unique_id"] = String(HIRI_DEVICE_ID) + "_ota";
    doc["state_topic"] = stateTopicOta();
    doc["value_template"] = "{{ value_json.state }}";
    doc["json_attributes_topic"] = stateTopicOta();
    doc["availability_topic"] = STATUS_TOPIC;
    doc["payload_available"] = "online";
    doc["payload_not_available"] = "offline";
    char buf[512];
    size_t n = serializeJson(doc, buf, sizeof(buf));
    mqtt.publish(topic.c_str(), (uint8_t *)buf, n, true);
  }
}

void onMqttMessage(char *topic, byte *payload, unsigned int length) {
  String t(topic);
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
  if (t == cmdTopicSwitch()) {
    relayOn = (msg == "ON" || msg == "on" || msg == "1");
    mqtt.publish(stateTopicSwitch().c_str(), relayOn ? "ON" : "OFF", true);
  }
  if (t == cmdTopicOta()) {
    OtaRequest request;
    if (parseOtaRequest(msg, request)) {
      performHttpOta(request);
    } else {
      publishOtaStatus("error", "Invalid OTA payload");
    }
  }
}

void ensureMqtt() {
  if (mqtt.connected()) return;
  String clientId = String("hiri-") + HIRI_DEVICE_ID;
  if (mqtt.connect(clientId.c_str(), HIRI_MQTT_USER, HIRI_MQTT_PASS, STATUS_TOPIC, 0, true, "offline")) {
    mqtt.publish(STATUS_TOPIC, "online", true);
    mqtt.subscribe(cmdTopicSwitch().c_str());
    mqtt.subscribe(cmdTopicOta().c_str());
    publishDiscovery();
    mqtt.publish(stateTopicSwitch().c_str(), relayOn ? "ON" : "OFF", true);
    publishOtaStatus("idle", "ready");
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
  if (now - lastTelemetry > 10000) {
    lastTelemetry = now;
    if (mqtt.connected()) {
      // Simulated sensors — replace with real ADC/I2C in bounties
      float soil = 35.0f + (now % 2000) / 100.0f;
      float temp = 24.0f + (now % 1000) / 200.0f;
      char buf[16];
      dtostrf(soil, 0, 1, buf);
      mqtt.publish(stateTopicSoil().c_str(), buf, true);
      dtostrf(temp, 0, 1, buf);
      mqtt.publish(stateTopicTemp().c_str(), buf, true);
    }
  }
}
