"""Optional MQTT publisher for HA discovery (offline dry-run without paho)."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any, Protocol

from hiri_bridge.devices.types import Device
from hiri_bridge.ha.discovery import discovery_payload, discovery_topic, state_topic


class MqttPublishReceipt(Protocol):
    def wait_for_publish(self, timeout: float | None = None) -> Any: ...


class MqttClient(Protocol):
    def username_pw_set(self, username: str, password: str) -> Any: ...

    def connect(self, host: str, port: int, keepalive: int) -> Any: ...

    def loop_start(self) -> Any: ...

    def publish(
        self, topic: str, payload: str, qos: int = 0, retain: bool = False
    ) -> MqttPublishReceipt: ...

    def disconnect(self) -> Any: ...

    def loop_stop(self) -> Any: ...


class MqttDiscoveryPublisher:
    name = "mqtt"

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        client_factory: Callable[[], MqttClient] | None = None,
        publish_timeout: float = 5.0,
        qos: int = 1,
    ):
        self.host = host or os.environ.get("HIRI_MQTT_HOST", "127.0.0.1")
        self.port = int(port or os.environ.get("HIRI_MQTT_PORT", "1883"))
        self.username = username or os.environ.get("HIRI_MQTT_USER") or ""
        self.password = password or os.environ.get("HIRI_MQTT_PASSWORD") or ""
        self.client_factory = client_factory
        self.publish_timeout = publish_timeout
        self.qos = qos

    def status(self) -> str:
        if self.client_factory is not None:
            return f"client ready → {self.host}:{self.port}"
        try:
            import paho.mqtt.client  # noqa: F401

            return f"paho ready → {self.host}:{self.port}"
        except ImportError:
            return "offline dry-run (pip install -e '.[mqtt]')"

    def list_remote(self) -> list[Device]:
        return []

    def push_state(self, device: Device) -> None:
        return None

    def build_messages(self, devices: list[Device]) -> list[dict[str, Any]]:
        """Build discovery + state messages without connecting."""
        msgs: list[dict[str, Any]] = []
        for d in devices:
            msgs.append(
                {
                    "topic": discovery_topic(d),
                    "payload": discovery_payload(d),
                    "retain": True,
                    "qos": self.qos,
                    "kind": "discovery",
                }
            )
            msgs.append(
                {
                    "topic": state_topic(d),
                    "payload": d.state if d.state else {"state": "unknown"},
                    "retain": True,
                    "qos": self.qos,
                    "kind": "state",
                }
            )
        msgs.append(
            {
                "topic": "hiri/status",
                "payload": "online",
                "retain": True,
                "qos": self.qos,
                "kind": "availability",
            }
        )
        return msgs

    def publish(self, devices: list[Device], dry_run: bool = True) -> dict[str, Any]:
        messages = self.build_messages(devices)
        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "broker": f"{self.host}:{self.port}",
                "count": len(messages),
                "messages": messages[:40],
                "truncated": len(messages) > 40,
            }
        try:
            client = self._new_client()
        except RuntimeError as exc:
            return {
                "ok": False,
                "error": str(exc),
                "detail": str(exc),
            }

        published = 0
        connected = False
        loop_started = False
        try:
            if self.username:
                client.username_pw_set(self.username, self.password)
            client.connect(self.host, self.port, 30)
            connected = True
            client.loop_start()
            loop_started = True
            for message in messages:
                payload = message["payload"]
                body = payload if isinstance(payload, str) else json.dumps(payload)
                receipt = client.publish(
                    message["topic"],
                    body,
                    qos=int(message.get("qos", self.qos)),
                    retain=bool(message.get("retain")),
                )
                receipt.wait_for_publish(timeout=self.publish_timeout)
                published += 1
            return {
                "ok": True,
                "dry_run": False,
                "broker": f"{self.host}:{self.port}",
                "published": published,
                "qos": self.qos,
            }
        except Exception as exc:
            return {
                "ok": False,
                "dry_run": False,
                "broker": f"{self.host}:{self.port}",
                "published": published,
                "error": f"MQTT publish failed: {exc}",
            }
        finally:
            if connected:
                client.disconnect()
            if loop_started:
                client.loop_stop()

    def _new_client(self) -> MqttClient:
        if self.client_factory is not None:
            return self.client_factory()
        try:
            import paho.mqtt.client as mqtt
        except ImportError as exc:
            raise RuntimeError(
                'paho-mqtt not installed; pip install -e ".[mqtt]" or use dry_run'
            ) from exc
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
