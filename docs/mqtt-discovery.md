# HA MQTT Discovery Setup Guide

## Prerequisites
- Home Assistant running
- MQTT broker configured (e.g., Mosquitto)
- HIRI device connected to network

## Setup Steps

1. Configure MQTT broker in HA
2. Enable MQTT discovery in configuration.yaml
3. Connect HIRI device to MQTT broker
4. Auto-discovery will detect the device

## Configuration Example

```yaml
mqtt:
  broker: core-mosquitto
  discovery: true
```

## Troubleshooting
- Check MQTT broker logs
- Verify device is publishing to discovery topic
- Ensure HA discovery is enabled