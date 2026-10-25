# Low-power farm node mode

These settings are opt-in. Defaults keep the existing always-on firmware
behavior, so existing nodes do not need changes.

## Config flags

Set flags in `platformio.ini` `build_flags` or a local override.

| Flag | Default | Purpose |
| --- | --- | --- |
| `HIRI_DEEP_SLEEP_ENABLED` | `0` | Enter deep sleep after a publish cycle. |
| `HIRI_DEEP_SLEEP_SECONDS` | `300` | Sleep duration between wake cycles. |
| `HIRI_BATTERY_ENABLED` | `0` | Read and report battery voltage/percent. |
| `HIRI_BATTERY_ADC_PIN` | `A0` / `35` | ADC pin connected to the battery divider. |
| `HIRI_BATTERY_ADC_MAX` | `1023` / `4095` | ADC full-scale value for the board. |
| `HIRI_BATTERY_DIVIDER_RATIO` | `2.0` | Full resistor-divider ratio. |
| `HIRI_BATTERY_MIN_VOLTAGE` | `3.0` | Voltage mapped to 0%. |
| `HIRI_BATTERY_MAX_VOLTAGE` | `4.2` | Voltage mapped to 100%. |

Example:

```ini
build_flags =
  -DHIRI_DEEP_SLEEP_ENABLED=1
  -DHIRI_DEEP_SLEEP_SECONDS=600
  -DHIRI_BATTERY_ENABLED=1
  -DHIRI_BATTERY_ADC_PIN=35
  -DHIRI_BATTERY_DIVIDER_RATIO=2.0
```

## Usage

Include the helper and publish battery values before sleeping:

```cpp
#include "hiri_power.h"

const float battery_v = hiri_battery_voltage();
const int battery_pct = hiri_battery_percent();
// Publish battery_v / battery_pct with the normal telemetry payload.

hiri_deep_sleep_now();
```

On ESP8266, connect `D0`/`GPIO16` to `RST` for timer wake. On ESP32, use an
RTC-capable ADC pin and keep the divider powered only while sampling if the
board supports it.

## Notes

- Battery reporting uses a simple linear voltage-to-percent mapping. Adjust
  `HIRI_BATTERY_MIN_VOLTAGE` / `HIRI_BATTERY_MAX_VOLTAGE` for the cell chemistry.
- Deep sleep resets RAM. Publish telemetry and flush MQTT before calling
  `hiri_deep_sleep_now()`.
- Keep the ADC input below the board's safe voltage; most boards expect at most
  3.3 V on the pin.
