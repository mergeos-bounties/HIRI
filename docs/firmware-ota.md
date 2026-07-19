# Firmware OTA Flow

HIRI firmware listens for OTA commands on:

```text
hiri/cmd/<device_id>/ota
```

The update payload can be a plain HTTP URL:

```text
http://192.168.1.10:8080/firmware.bin
```

or a JSON document:

```json
{
  "url": "http://192.168.1.10:8080/firmware.bin",
  "version": "2026.07.19",
  "token": "change-me"
}
```

## Build And Host

Build the board-specific binary with PlatformIO:

```bash
cd packages/firmware
pio run -e esp32dev
pio run -e esp8266
```

Host the binary from a machine on the same trusted network:

```bash
python3 -m http.server 8080 -d .pio/build/esp32dev
```

For ESP8266, serve `.pio/build/esp8266/firmware.bin` instead.

## Trigger

Publish the MQTT command to the device-specific OTA topic:

```bash
mosquitto_pub -h homeassistant.local \
  -t hiri/cmd/hiri_node_01/ota \
  -m '{"url":"http://192.168.1.10:8080/firmware.bin","version":"2026.07.19","token":"change-me"}'
```

If `HIRI_OTA_TOKEN` is configured, the payload token must match before the
device downloads the binary.

## Status

The firmware publishes OTA state to:

```text
hiri/state/<device_id>/ota
```

Example status payload:

```json
{
  "state": "downloading",
  "device_id": "hiri_node_01",
  "current_version": "dev",
  "detail": "http://192.168.1.10:8080/firmware.bin version=2026.07.19"
}
```

Expected states are:

- `idle` when the device is ready
- `downloading` while the HTTP update is running
- `rebooting` after a successful update
- `error` when validation, authorization, or the HTTP update fails

## Safety Notes

- Use a trusted MQTT broker and authenticated MQTT credentials.
- Override `HIRI_OTA_TOKEN` with a non-empty per-deployment secret.
- Host binaries only on a trusted local network or protected endpoint.
- Match the binary to the physical board environment.
- Keep a USB flash recovery path for first rollout and failed OTA recovery.
