"""Known bridge adapters and offline status."""

from __future__ import annotations

from typing import Any

from hiri_bridge.adapters.ha_rest import HomeAssistantRestAdapter
from hiri_bridge.adapters.ha_ws import HomeAssistantWebSocketAdapter
from hiri_bridge.adapters.local import LocalAdapter
from hiri_bridge.adapters.matter import MatterAdapter
from hiri_bridge.adapters.mqtt_pub import MqttDiscoveryPublisher
from hiri_bridge.adapters.tuya import TuyaAdapter
from hiri_bridge.adapters.z2m import Zigbee2MqttAdapter


def list_adapters() -> list[dict[str, Any]]:
    rows = [
        {
            "name": "local",
            "kind": "builtin",
            "live": False,
            "description": "In-memory registry (default seed devices)",
            "status": "ready",
        },
        {
            "name": "mqtt",
            "kind": "mqtt",
            "live": True,
            "description": "HA MQTT discovery publish (optional paho-mqtt)",
            "status": MqttDiscoveryPublisher().status(),
        },
        {
            "name": "ha_rest",
            "kind": "http",
            "live": True,
            "description": "Home Assistant REST /api/states import",
            "status": "token required for live" if not HomeAssistantRestAdapter().token else "configured",
        },
        {
            "name": "ha_ws",
            "kind": "websocket",
            "live": True,
            "description": "Home Assistant WebSocket state_changed event sync",
            "status": HomeAssistantWebSocketAdapter().status(),
        },
        {
            "name": "z2m",
            "kind": "mqtt_http",
            "live": True,
            "description": "Zigbee2MQTT device import (fixture offline)",
            "status": "fixture ready",
        },
        {
            "name": "tuya",
            "kind": "cloud_local",
            "live": True,
            "description": "Tuya cloud/local mapping stub",
            "status": "stub ready",
        },
        {
            "name": "matter",
            "kind": "scaffold",
            "live": False,
            "description": "Matter device-type mapping + fixture import (no controller yet)",
            "status": MatterAdapter().status(),
        },
    ]
    return rows


def import_from_adapter(name: str) -> list:
    key = (name or "").strip().lower()
    if key in {"local", ""}:
        return LocalAdapter().list_remote()
    if key in {"z2m", "zigbee2mqtt"}:
        return Zigbee2MqttAdapter().list_remote()
    if key == "tuya":
        return TuyaAdapter().list_remote()
    if key == "matter":
        return MatterAdapter().list_remote()
    if key in {"ha_rest", "ha"}:
        return HomeAssistantRestAdapter().list_remote()
    if key in {"ha_ws", "ha_websocket"}:
        return HomeAssistantWebSocketAdapter().list_remote()
    if key == "mqtt":
        return []  # mqtt is publish path, not import
    raise ValueError(f"unknown adapter: {name}")
