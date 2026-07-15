# HA MQTT Discovery Setup Guide

This guide explains how to set up MQTT discovery for Home Assistant integration.

## Prerequisites

- Home Assistant instance (2024.6+)
- MQTT broker (Mosquitto recommended)
- Network connectivity between HA and MQTT broker

## Configuration

### 1. MQTT Broker Setup

```yaml
# configuration.yaml
mqtt:
  broker: 192.168.1.100
  port: 1883
  discovery: true
  discovery_prefix: homeassistant
```

### 2. Discovery Message Format

MQTT discovery uses the following topic structure:

```
<discovery_prefix>/<component>/<node_id>/<object_id>/config
```

Example for a sensor:

```json
{
  "name": "Temperature Sensor",
  "state_topic": "home/sensor/temperature",
  "unit_of_measurement": "°C",
  "device_class": "temperature"
}
```

### 3. Supported Components

- `sensor` — readings and measurements
- `binary_sensor` — on/off states
- `switch` — controllable relays
- `light` — dimmable and RGB lights
- `cover` — blinds and curtains
- `climate` — thermostats and HVAC

### 4. Testing Discovery

Publish a test discovery message:

```bash
mosquitto_pub -h 192.168.1.100 \
  -t "homeassistant/sensor/test/config" \
  -m '{"name":"Test","state_topic":"test/state"}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Device not discovered | Check `discovery: true` in MQTT config |
| Wrong prefix | Verify `discovery_prefix` matches device configuration |
| No MQTT connection | Test with `mosquitto_pub` from HA server |
