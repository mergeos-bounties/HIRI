from __future__ import annotations

import json
from typing import Any

from hiri_bridge.adapters.mqtt_pub import MqttDiscoveryPublisher
from hiri_bridge.devices.types import Device


class FakePublishReceipt:
    def __init__(self, calls: list[tuple[Any, ...]]):
        self.calls = calls

    def wait_for_publish(self, timeout: float | None = None) -> None:
        self.calls.append(("wait_for_publish", timeout))


class FakeMqttClient:
    def __init__(self):
        self.calls: list[tuple[Any, ...]] = []

    def username_pw_set(self, username: str, password: str) -> None:
        self.calls.append(("username_pw_set", username, password))

    def connect(self, host: str, port: int, keepalive: int) -> None:
        self.calls.append(("connect", host, port, keepalive))

    def loop_start(self) -> None:
        self.calls.append(("loop_start",))

    def publish(
        self, topic: str, payload: str, qos: int = 0, retain: bool = False
    ) -> FakePublishReceipt:
        self.calls.append(("publish", topic, payload, qos, retain))
        return FakePublishReceipt(self.calls)

    def disconnect(self) -> None:
        self.calls.append(("disconnect",))

    def loop_stop(self) -> None:
        self.calls.append(("loop_stop",))


class FailingPublishReceipt(FakePublishReceipt):
    def wait_for_publish(self, timeout: float | None = None) -> None:
        self.calls.append(("wait_for_publish", timeout))
        raise TimeoutError("broker acknowledgement timed out")


class FailingMqttClient(FakeMqttClient):
    def publish(
        self, topic: str, payload: str, qos: int = 0, retain: bool = False
    ) -> FakePublishReceipt:
        self.calls.append(("publish", topic, payload, qos, retain))
        return FailingPublishReceipt(self.calls)


def test_live_publish_uses_network_loop_and_waits_for_delivery() -> None:
    client = FakeMqttClient()
    publisher = MqttDiscoveryPublisher(
        host="broker.test",
        port=1884,
        username="hiri",
        password="secret",
        client_factory=lambda: client,
        publish_timeout=2.5,
    )
    device = Device(
        id="light.test",
        name="Test light",
        domain="light",
        state={"state": "on"},
    )

    result = publisher.publish([device], dry_run=False)

    assert result == {
        "ok": True,
        "dry_run": False,
        "broker": "broker.test:1884",
        "published": 3,
        "qos": 1,
    }
    assert client.calls[:3] == [
        ("username_pw_set", "hiri", "secret"),
        ("connect", "broker.test", 1884, 30),
        ("loop_start",),
    ]
    published = [call for call in client.calls if call[0] == "publish"]
    assert [call[1] for call in published] == [
        "homeassistant/light/hiri/light_test/config",
        "hiri/state/light/test",
        "hiri/status",
    ]
    assert all(call[3:] == (1, True) for call in published)
    assert json.loads(published[0][2])["unique_id"] == "hiri_light_test"
    assert [call for call in client.calls if call[0] == "wait_for_publish"] == [
        ("wait_for_publish", 2.5),
        ("wait_for_publish", 2.5),
        ("wait_for_publish", 2.5),
    ]
    assert client.calls[-2:] == [("disconnect",), ("loop_stop",)]


def test_live_publish_reports_failure_and_closes_client() -> None:
    client = FailingMqttClient()
    publisher = MqttDiscoveryPublisher(client_factory=lambda: client)
    device = Device(id="switch.test", name="Test switch", domain="switch")

    result = publisher.publish([device], dry_run=False)

    assert result["ok"] is False
    assert result["published"] == 0
    assert "broker acknowledgement timed out" in result["error"]
    assert client.calls[-2:] == [("disconnect",), ("loop_stop",)]
