# Zigbee2MQTT adapter

HIRI can import the device inventory exposed by the Zigbee2MQTT frontend
WebSocket API. With no URL configured, the existing offline sample remains the
default.

## Live import

Install the optional WebSocket dependency from `packages/bridge`:

```powershell
pip install -e ".[z2m]"
```

Set the URL of the Zigbee2MQTT frontend and, when frontend authentication is
enabled, its token:

```powershell
$env:HIRI_Z2M_URL = "http://127.0.0.1:8080"
$env:HIRI_Z2M_TOKEN = "replace-with-your-frontend-token"
hiri-bridge adapters import z2m
```

The adapter converts `http`/`https` URLs to `ws`/`wss`, connects to `/api`, and
waits for the retained `bridge/devices` message. Coordinator rows are ignored;
device capabilities are mapped to HIRI domains such as `light`, `switch`,
`binary_sensor`, and `sensor`.

Prefer an `https` frontend URL when traffic leaves the local machine so the
authentication token is protected by TLS.

## References

- [Zigbee2MQTT frontend WebSocket implementation](https://github.com/Koenkk/zigbee2mqtt/blob/master/lib/extension/frontend.ts)
- [Zigbee2MQTT exposes format](https://www.zigbee2mqtt.io/guide/usage/exposes.html)
