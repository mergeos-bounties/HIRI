from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from hiri_bridge import api
from hiri_bridge.api import app
from hiri_bridge.devices.registry import DeviceRegistry

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_devices_and_command() -> None:
    r = client.get("/devices")
    assert r.status_code == 200
    assert len(r.json()) >= 10
    r2 = client.post("/devices/light.living_main/command", json={"action": "turn_on", "data": {"brightness": 100}})
    assert r2.status_code == 200
    assert r2.json()["state"]["state"] == "on"


def test_ha_ws_event_updates_registry(tmp_path) -> None:
    old_reg = api._reg
    api._reg = DeviceRegistry(path=tmp_path / "devices.json")
    try:
        event = {
            "event_type": "state_changed",
            "data": {
                "entity_id": "sensor.office_temperature",
                "new_state": {
                    "entity_id": "sensor.office_temperature",
                    "state": "23.4",
                    "attributes": {
                        "friendly_name": "Office temperature",
                        "device_class": "temperature",
                        "unit_of_measurement": "C",
                    },
                },
            },
        }

        r = client.post("/adapters/ha_ws/events", json=event)
        assert r.status_code == 200
        assert r.json()["synced"] == 1

        detail = client.get("/devices/sensor.office_temperature")
        assert detail.status_code == 200
        assert detail.json()["state"]["state"] == "23.4"
        assert detail.json()["adapter"] == "ha_ws"
    finally:
        api._reg = old_reg
