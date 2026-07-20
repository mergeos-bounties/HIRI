# Home Assistant MQTT Discovery Setup Guide

This guide explains how to set up Home Assistant MQTT discovery for HIRI devices.

## Overview

Home Assistant can automatically discover MQTT devices and entities using the [MQTT Discovery protocol](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery). HIRI supports this protocol to enable seamless integration with Home Assistant.

## Prerequisites

- Home Assistant with MQTT integration configured
- MQTT broker (e.g., Mosquitto, EMQX) accessible from both Home Assistant and HIRI devices
- HIRI bridge running and connected to the same MQTT broker

## Configuration Steps

### 1. Configure HIRI Bridge MQTT Settings

Ensure your HIRI bridge is configured to connect to your MQTT broker:

```yaml
# hiRI bridge configuration (config.yaml or environment variables)
mqtt:
  broker: "your-mqtt-broker-address"
  port: 1883
  username: "your-username"  # if required
  password: "your-password"  # if required
  base_topic: "hiri"         # default base topic for HIRI
  discovery:
    enabled: true            # enable Home Assistant discovery
    prefix: "homeassistant"  # Home Assistant discovery prefix
```

### 2. Device Discovery Process

When a HIRI device connects, it will:

1. Announce its presence on the MQTT broker
2. Publish discovery messages to `homeassistant/<component>/<device_id>/<object_id>/config`
3. Home Assistant automatically creates entities based on these discovery messages

### 3. Supported Device Types

HIRI currently supports discovery for:
- **Binary Sensors** (motion, door/window, etc.)
- **Sensors** (temperature, humidity, pressure, etc.)
- **Switches** (relays, lights, etc.)
- **Lights** (RGB, dimmable, etc.)
- **Climate** (thermostats, HVAC)
- **Covers** (blinds, gates, etc.)

### 4. Device ID Format

Each HIRI device gets a unique ID based on:
```
<device-type>-<mac-address-last-3-bytes>
```

Example: `switch-a1b2c3`

### 5. Entity Naming

Entities are named using:
```
<device_id>_<function>
```

Example: `switch-a1b2c3_relay_1`

### 6. Verification in Home Assistant

After devices connect:

1. Go to **Settings > Devices & Services**
2. Look for discovered devices under the MQTT integration
3. Entities should appear automatically under:
   - **Entities** tab (filtered by MQTT integration)
   - **Entities** > **Devices & Services** > MQTT

### 7. Manual Configuration (if needed)

If auto-discovery doesn't work, you can manually configure MQTT entities:

```yaml
# configuration.yaml example
mqtt:
  sensor:
    - name: "Living Room Temperature"
      state_topic: "hiri/sensor-a1b2c3/temperature"
      unit_of_measurement: "°C"
      device_class: temperature
```

### 8. Troubleshooting

#### Discovery Messages Not Appearing
- Verify MQTT broker connectivity in HIRI logs
- Check that discovery is enabled in HIRI configuration
- Ensure base_topic matches between HIRI and discovery prefix

#### Entities Not Appearing in HA
- Check Home Assistant MQTT integration logs
- Verify discovery prefix matches (`homeassistant` by default)
- Restart Home Assistant after changing MQTT settings

#### Incorrect Entity Types
- Check device class in discovery message
- Ensure correct device type is reported by HIRI firmware

### 9. Example Discovery Message

For a temperature sensor:
```json
{
  "name": "Living Room Temp",
  "stat_t": "hiri/sensor-a1b2c3/temperature",
  "uniq_id": "sensor-a1b2c3_temperature",
  "dev_cla": "temperature",
  "unit_of_meas": "°C",
  "dev": {
    "ids": ["hiri-a1b2c3"],
    "name": "HIRI Sensor a1b2c3",
    "mdl": "HIRI Sensor",
    "sw": "1.0.0"
  }
}
```

### 10. Updating Discovery

When device configuration changes:
1. HIRI publishes new discovery messages with same `uniq_id`
2. Home Assistant updates existing entities
3. Restart may be required for some changes

## Advanced Configuration

### Custom Discovery Prefix
To use a custom discovery prefix (not `homeassistant`):
```yaml
discovery:
  prefix: "homeassistant_custom"
```

### Disabling Discovery
To disable discovery and use manual configuration only:
```yaml
discovery:
  enabled: false
```

### Birth and Last Will Messages
HIRI automatically sends:
- Birth message when connecting
- Last Will and Testament (LWT) when disconnecting unexpectedly

## References

- [Home Assistant MQTT Discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery)
- [MQTT Specification](http://mqtt.org/)
- [HIRI MQTT Protocol Documentation](../protocol/mqtt-spec.md)