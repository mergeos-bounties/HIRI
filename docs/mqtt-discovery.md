# HA MQTT Discovery Setup Guide

## Prerequisites

- Home Assistant running
- MQTT broker configured (e.g., Mosquitto)
- HIRI device connected to network

## Docker Desktop smoke test on Windows

The repository includes an anonymous broker configuration for local development
only. It binds the published Docker port to loopback so the broker is not exposed
to the LAN.

From the repository root in PowerShell:

```powershell
$repoRoot = (Get-Location).Path
docker run --rm --name hiri-mosquitto `
  -p 127.0.0.1:1883:1883 `
  --mount "type=bind,source=$repoRoot\docs\mosquitto-dev.conf,target=/mosquitto/config/mosquitto.conf,readonly" `
  eclipse-mosquitto:2
```

In a second PowerShell terminal:

```powershell
cd packages\bridge
pip install -e ".[mqtt]"
hiri-bridge mqtt publish --live --host 127.0.0.1 --port 1883
```

The command publishes retained Home Assistant discovery, state, and HIRI
availability messages at QoS 1. It waits for every Paho publish receipt before
disconnecting.

Verify a retained discovery message:

```powershell
docker exec hiri-mosquitto mosquitto_sub `
  -t "homeassistant/#" -C 1 -v
```

Stop the foreground broker with `Ctrl+C`. Replace the anonymous development
configuration with authentication and TLS before using any non-loopback broker.

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

## References

- [Eclipse Paho Python network loop and publish receipts](https://eclipse.dev/paho/files/paho.mqtt.python/html/index.html)
- [Eclipse Mosquitto documentation](https://mosquitto.org/documentation/)
