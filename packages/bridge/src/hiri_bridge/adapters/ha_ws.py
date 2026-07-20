"""Home Assistant WebSocket event stream adapter."""

from __future__ import annotations

import json
import os
from typing import Any

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import Device


class HomeAssistantWebSocketAdapter:
    name = "ha_ws"

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
    ):
        self.base_url = (base_url or os.environ.get("HIRI_HA_URL", "http://homeassistant.local:8123")).rstrip("/")
        self.token = token if token is not None else os.environ.get("HIRI_HA_TOKEN", "")

    def status(self) -> str:
        if not self.token:
            return "token required for live event stream"
        try:
            import websockets  # noqa: F401
        except ImportError:
            return 'offline mapper ready (pip install -e ".[ha-ws]" for live stream)'
        return f"configured -> {self.websocket_url}"

    @property
    def websocket_url(self) -> str:
        if self.base_url.startswith("wss://") or self.base_url.startswith("ws://"):
            url = self.base_url
        elif self.base_url.startswith("https://"):
            url = f"wss://{self.base_url.removeprefix('https://')}"
        elif self.base_url.startswith("http://"):
            url = f"ws://{self.base_url.removeprefix('http://')}"
        else:
            url = f"ws://{self.base_url}"
        if not url.endswith("/api/websocket"):
            url = f"{url}/api/websocket"
        return url

    def list_remote(self) -> list[Device]:
        return []

    def push_state(self, device: Device) -> None:
        return None

    def device_from_event(self, message: dict[str, Any]) -> Device | None:
        event = _unwrap_event(message)
        if event.get("event_type") != "state_changed":
            return None

        data = event.get("data") or {}
        new_state = data.get("new_state") or {}
        if not isinstance(new_state, dict):
            return None

        entity_id = new_state.get("entity_id") or data.get("entity_id")
        if not entity_id:
            return None

        attributes = new_state.get("attributes") or {}
        if not isinstance(attributes, dict):
            attributes = {}

        domain = entity_id.split(".", 1)[0] if "." in entity_id else "sensor"
        return Device(
            id=entity_id,
            name=attributes.get("friendly_name", entity_id),
            domain=domain,
            manufacturer="HomeAssistant",
            model="websocket",
            state={"state": new_state.get("state")},
            attributes=attributes,
            adapter=self.name,
        )

    async def subscribe_events(
        self,
        registry: DeviceRegistry,
        *,
        max_events: int | None = None,
    ) -> int:
        if not self.token:
            return 0
        try:
            import websockets
        except ImportError:
            return 0

        synced = 0
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                await websocket.recv()
                await websocket.send(json.dumps({"type": "auth", "access_token": self.token}))
                auth = json.loads(await websocket.recv())
                if auth.get("type") != "auth_ok":
                    return 0

                await websocket.send(
                    json.dumps({"id": 1, "type": "subscribe_events", "event_type": "state_changed"})
                )
                while max_events is None or synced < max_events:
                    raw = await websocket.recv()
                    message = json.loads(raw)
                    if sync_event_to_registry(registry, message, adapter=self):
                        synced += 1
        except Exception:
            return synced
        return synced


def sync_event_to_registry(
    registry: DeviceRegistry,
    event: dict[str, Any],
    *,
    adapter: HomeAssistantWebSocketAdapter | None = None,
) -> Device | None:
    device = (adapter or HomeAssistantWebSocketAdapter()).device_from_event(event)
    if not device:
        return None
    return registry.upsert(device)


def _unwrap_event(message: dict[str, Any]) -> dict[str, Any]:
    if message.get("type") == "event" and isinstance(message.get("event"), dict):
        return message["event"]
    return message
