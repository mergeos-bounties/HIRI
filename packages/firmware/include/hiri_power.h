#pragma once

#include <Arduino.h>

#include "hiri_config.h"

inline float hiri_battery_voltage() {
#if HIRI_BATTERY_ENABLED
  const int raw = analogRead(HIRI_BATTERY_ADC_PIN);
  return (raw / (float)HIRI_BATTERY_ADC_MAX) * HIRI_BATTERY_DIVIDER_RATIO * 3.3f;
#else
  return 0.0f;
#endif
}

inline int hiri_battery_percent() {
#if HIRI_BATTERY_ENABLED
  const float voltage = hiri_battery_voltage();
  const float span = HIRI_BATTERY_MAX_VOLTAGE - HIRI_BATTERY_MIN_VOLTAGE;
  if (span <= 0.0f) {
    return 0;
  }
  const float pct = ((voltage - HIRI_BATTERY_MIN_VOLTAGE) / span) * 100.0f;
  if (pct <= 0.0f) {
    return 0;
  }
  if (pct >= 100.0f) {
    return 100;
  }
  return (int)pct;
#else
  return 0;
#endif
}

inline void hiri_deep_sleep_now() {
#if HIRI_DEEP_SLEEP_ENABLED
#if defined(ESP8266)
  ESP.deepSleep((uint64_t)HIRI_DEEP_SLEEP_SECONDS * 1000000ULL);
#elif defined(ESP32)
  esp_sleep_enable_timer_wakeup((uint64_t)HIRI_DEEP_SLEEP_SECONDS * 1000000ULL);
  esp_deep_sleep_start();
#endif
#endif
}
