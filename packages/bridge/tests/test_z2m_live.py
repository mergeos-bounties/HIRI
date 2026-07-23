from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hiri_bridge.adapters.z2m import Zigbee2MqttAdapter, devices_from_payload


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "z2m_devices.json"


class FakeConnection:
    def __init__(self, messages: list[dict[str, Any]]):
        self.messages = iter(messages)
        self.timeouts: list[float | None] = []
        self.closed = False

    def __enter__(self) -> FakeConnection:
        return self

    def __exit__(self, *args: object) -> None:
        self.closed = True

    def recv(self, timeout: float | None = None) -> str:
        self.timeouts.append(timeout)
        return json.dumps(next(self.messages))


def load_fixture() -> list[dict[str, Any]]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_maps_z2m_inventory_to_hiri_devices() -> None:
    devices = devices_from_payload(load_fixture())

    assert [device.id for device in devices] == [
        "light.z2m_living_main_bulb",
        "binary_sensor.z2m_hall_front_contact",
        "sensor.z2m_bedroom_temperature",
    ]
    light, contact, temperature = devices
    assert light.model == "LED1623G12"
    assert light.manufacturer == "IKEA"
    assert light.area == "living"
    assert light.attributes["ieee_address"] == "0x00124b0024c00002"
    assert contact.attributes["device_class"] == "door"
    assert contact.adapter == "z2m"
    assert temperature.online is False


def test_live_import_reads_retained_bridge_devices_message(monkeypatch: Any) -> None:
    fixture = load_fixture()
    connection = FakeConnection(
        [
            {"topic": "bridge/state", "payload": {"state": "online"}},
            {"topic": "bridge/devices", "payload": fixture},
        ]
    )
    calls: list[tuple[str, dict[str, Any]]] = []

    def connection_factory(url: str, **kwargs: Any) -> FakeConnection:
        calls.append((url, kwargs))
        return connection

    monkeypatch.setenv("HIRI_Z2M_URL", "https://z2m.example/panel?source=hiri")
    monkeypatch.setenv("HIRI_Z2M_TOKEN", "token with spaces")
    adapter = Zigbee2MqttAdapter(
        timeout=2.0,
        connection_factory=connection_factory,
    )

    devices = adapter.list_remote()

    assert len(devices) == 3
    assert calls == [
        (
            "wss://z2m.example/panel/api?source=hiri&token=token+with+spaces",
            {"open_timeout": 2.0, "close_timeout": 2.0},
        )
    ]
    assert len(connection.timeouts) == 2
    assert all(timeout is not None and 0 < timeout <= 2.0 for timeout in connection.timeouts)
    assert connection.closed is True


def test_live_import_is_offline_safe_on_invalid_payload() -> None:
    connection = FakeConnection(
        [{"topic": "bridge/devices", "payload": {"unexpected": "object"}}]
    )
    adapter = Zigbee2MqttAdapter(
        base_url="ws://127.0.0.1:8080/api",
        use_fixture=False,
        connection_factory=lambda *_args, **_kwargs: connection,
    )

    assert adapter.list_remote() == []
    assert connection.closed is True


def test_fixture_remains_default_without_live_url(monkeypatch: Any) -> None:
    monkeypatch.delenv("HIRI_Z2M_URL", raising=False)
    adapter = Zigbee2MqttAdapter()

    assert adapter.status() == "fixture ready"
    assert len(adapter.list_remote()) == 3
