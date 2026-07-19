from __future__ import annotations

from hiri_bridge import __version__
from hiri_bridge.adapters import import_from_adapter, list_adapters
from hiri_bridge.adapters.ha_ws import sync_event_to_registry
from hiri_bridge.adapters.mqtt_pub import MqttDiscoveryPublisher
from hiri_bridge.auth import OptionalTokenMiddleware, api_token
from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import DOMAINS, Device
from hiri_bridge.ha.discovery import export_discovery

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except ImportError as exc:  # pragma: no cover
    raise ImportError('pip install -e ".[api]"') from exc

app = FastAPI(title="HIRI Bridge", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(OptionalTokenMiddleware)

_reg = DeviceRegistry()
_reg.load_or_seed()


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "service": "hiri-bridge",
        "version": __version__,
        "domains": DOMAINS,
        "auth_required": bool(api_token()),
        "adapters": [a["name"] for a in list_adapters()],
    }


@app.get("/stats")
def stats() -> dict:
    return _reg.stats()


@app.get("/devices")
def list_devices(domain: str | None = None, area: str | None = None) -> list[dict]:
    devices = _reg.list()
    if domain:
        devices = [d for d in devices if d.domain == domain]
    if area:
        devices = [d for d in devices if d.area == area]
    return [d.model_dump() for d in devices]


@app.get("/devices/{device_id}")
def get_device(device_id: str) -> dict:
    d = _reg.get(device_id)
    if not d:
        raise HTTPException(404, "device not found")
    return d.model_dump()


@app.post("/devices/{device_id}/command")
def command_device(device_id: str, body: dict) -> dict:
    action = body.get("action") or body.get("service") or "turn_on"
    data = body.get("data") or {}
    try:
        dev = _reg.apply_command(device_id, action, data)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return dev.model_dump()


@app.post("/devices")
def upsert_device(device: Device) -> dict:
    return _reg.upsert(device).model_dump()


@app.get("/ha/discovery")
def ha_discovery() -> list[dict]:
    return export_discovery(_reg.list())


@app.post("/devices/seed")
def seed() -> dict:
    _reg.seed()
    return _reg.stats()


@app.get("/adapters")
def adapters() -> list[dict]:
    return list_adapters()


@app.post("/adapters/{name}/import")
def adapters_import(name: str) -> dict:
    try:
        devices = import_from_adapter(name)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    for d in devices:
        _reg.upsert(d)
    return {"imported": len(devices), "adapter": name, "stats": _reg.stats()}


@app.post("/adapters/ha_ws/events")
def ha_ws_event(body: dict) -> dict:
    device = sync_event_to_registry(_reg, body)
    if not device:
        raise HTTPException(400, "unsupported Home Assistant state_changed event")
    return {
        "synced": 1,
        "adapter": "ha_ws",
        "device": device.model_dump(),
        "stats": _reg.stats(),
    }


@app.post("/mqtt/publish")
def mqtt_publish(body: dict | None = None) -> dict:
    body = body or {}
    dry = body.get("dry_run", True)
    pub = MqttDiscoveryPublisher(
        host=body.get("host"),
        port=body.get("port"),
    )
    return pub.publish(_reg.list(), dry_run=bool(dry))


@app.get("/areas")
def areas() -> dict:
    by_area: dict[str, int] = {}
    for d in _reg.list():
        by_area[d.area] = by_area.get(d.area, 0) + 1
    return {"areas": by_area}
