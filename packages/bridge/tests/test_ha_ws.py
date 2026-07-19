from __future__ import annotations

import asyncio
from pathlib import Path

from hiri_bridge.adapters.ha_ws import HomeAssistantWebSocketAdapter, sync_event_to_registry
from hiri_bridge.devices.registry import DeviceRegistry


def _state_changed_event() -> dict:
    return {
        "event_type": "state_changed",
        "data": {
            "entity_id": "light.kitchen",
            "new_state": {
                "entity_id": "light.kitchen",
                "state": "on",
                "attributes": {
                    "friendly_name": "Kitchen light",
                    "brightness": 128,
                    "supported_color_modes": ["brightness"],
                },
            },
        },
    }


def test_ha_ws_state_changed_event_maps_to_device() -> None:
    device = HomeAssistantWebSocketAdapter().device_from_event(_state_changed_event())

    assert device is not None
    assert device.id == "light.kitchen"
    assert device.name == "Kitchen light"
    assert device.domain == "light"
    assert device.state == {"state": "on"}
    assert device.attributes["brightness"] == 128
    assert device.adapter == "ha_ws"


def test_ha_ws_event_syncs_registry(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")

    device = sync_event_to_registry(reg, _state_changed_event())

    assert device is not None
    assert reg.get("light.kitchen") == device
    assert reg.get("light.kitchen").state["state"] == "on"  # type: ignore[union-attr]


def test_ha_ws_live_subscribe_is_offline_safe_without_token(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    adapter = HomeAssistantWebSocketAdapter(token="")

    synced = asyncio.run(adapter.subscribe_events(reg, max_events=1))

    assert synced == 0
    assert reg.list() == []
