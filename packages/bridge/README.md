# HIRI-bridge

Runnable Home Assistant–oriented bridge with a broad device type registry.

```bash
pip install -e ".[dev,api]"
hiri-bridge demo
hiri-bridge serve --port 8780
hiri-bridge mqtt publish --dry-run
```

For a local live publish smoke test with Docker Desktop and Mosquitto, see
[`../../docs/mqtt-discovery.md`](../../docs/mqtt-discovery.md).
