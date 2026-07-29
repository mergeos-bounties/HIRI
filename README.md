# HIRI Firmware - Secure TLS MQTT Setup

This firmware supports optional TLS/SSL encryption for MQTT communication to enable secure, high-availability (HA) deployment environments.

---

## 🔒 Enabling TLS for MQTT

MQTT TLS is disabled by default for low-overhead local development. Enable it via CMake build flags when compiling for production deployments.

### Build Flags

| Flag | Default | Description |
| :--- | :--- | :--- |
| `ENABLE_MQTT_TLS` | `OFF` | Enables TLS (MQTTS default port `8883`) and mbedTLS dependency linking |

### Building with TLS Enabled

