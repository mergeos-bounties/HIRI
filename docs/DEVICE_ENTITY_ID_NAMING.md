# Device Entity ID Naming Conventions

This document defines the `domain.object_id` naming conventions for device packs in HIRI.

## Overview

Every device in HIRI is identified by a unique `entity_id` following the pattern:

```
<domain>.<object_id>
```

Where:
- **domain**: The Home Assistant domain (e.g., `light`, `switch`, `sensor`)
- **object_id**: A unique, descriptive identifier for the device

## Naming Rules

### 1. Use lowercase with underscores

```yaml
# ✅ Correct
light.living_room_ceiling
switch.kitchen_outlet_1
sensor.bedroom_temperature

# ❌ Incorrect
Light.LivingRoomCeiling
switch.KitchenOutlet1
SENSOR.BedroomTemperature
```

### 2. Be descriptive and specific

```yaml
# ✅ Correct - describes location and function
light.bedroom_bedside_lamp
switch.garage_door_opener
sensor.patio_humidity

# ❌ Incorrect - too generic
light.lamp
switch.door
sensor.humidity
```

### 3. Include location when applicable

```yaml
# ✅ Correct - includes room/location
light.kitchen_counter
switch.bathroom_fan
sensor.living_room_co2

# ❌ Incorrect - missing location context
light.counter
switch.fan
sensor.co2
```

### 4. Use numeric suffixes for multiple similar devices

```yaml
# ✅ Correct - numbered for multiple instances
switch.kitchen_outlet_1
switch.kitchen_outlet_2
switch.kitchen_outlet_3

# ❌ Incorrect - ambiguous
switch.kitchen_outlet
switch.kitchen_outlet_a
switch.kitchen_outlet_secondary
```

### 5. Avoid special characters

```yaml
# ✅ Correct - only lowercase, numbers, underscores
light.porch_motion_sensor
switch.pool_pump_relay

# ❌ Incorrect - contains special characters
light.porch-motion-sensor
switch.pool_pump_relay!
sensor.temperature@home
```

## Domain-Specific Guidelines

### Lights

```yaml
light.<location>_<fixture_type>
light.living_room_ceiling
light.bedroom_bedside_lamp
light.kitchen_under_cabinet
light.porch_motion_activated
```

### Switches

```yaml
switch.<location>_<device_type>
switch.garage_door_opener
switch.pool_pump_relay
switch.irrigation_zone_1
switch.smart_plug_tv
```

### Sensors

```yaml
sensor.<location>_<measurement>
sensor.bedroom_temperature
sensor.living_room_humidity
sensor.patio_air_quality
sensor.kitchen_smoke_detector
```

### Binary Sensors

```yaml
binary_sensor.<location>_<event>
binary_sensor.front_door_contact
binary_sensor.bedroom_motion
binary_sensor.garage_leak_detector
binary_sensor.window_kitchen
```

### Climate

```yaml
climate.<location>_<system>
climate.living_room_ac
climate.bedroom_heater
climate.office_thermostat
```

### Covers

```yaml
cover.<location>_<type>
cover.living_room_blinds
cover.bedroom_curtains
cover.garage_door
```

## Append-Only Policy

When adding new device packs, you must **append** to the registry, never replace `devices.json`.

### Correct approach

```json
{
  "devices": [
    // ... existing devices ...
    {
      "domain": "light",
      "object_id": "new_room_light",
      "name": "New Room Light",
      // ... other properties
    }
  ]
}
```

### Incorrect approach

```json
{
  "devices": [
    // ... ONLY new devices (existing ones removed!) ...
  ]
}
```

See [devices-packs-policy.md](devices-packs-policy.md) for the full append-only policy.

## Validation

Before submitting a device pack, verify:

1. **Unique object_ids**: No duplicate `domain.object_id` combinations
2. **Lowercase with underscores**: No spaces, hyphens, or uppercase
3. **Descriptive names**: Clear location and function
4. **Proper domain**: Correct Home Assistant domain
5. **Append-only**: Existing devices preserved

## Examples

### Good device pack

```json
{
  "domain": "light",
  "object_id": "bedroom_ceiling_fan_light",
  "name": "Bedroom Ceiling Fan Light",
  "state": "on",
  "attributes": {
    "brightness": 255,
    "color_temp": 400
  }
}
```

### Bad device pack

```json
{
  "domain": "light",
  "object_id": "Light1",
  "name": "My Light",
  "state": "ON",
  "attributes": {}
}
```

## References

- [Home Assistant Entity Naming](https://www.home-assistant.io/docs/configuration/templating/#entities)
- [HIRI Devices Packs Policy](devices-packs-policy.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
