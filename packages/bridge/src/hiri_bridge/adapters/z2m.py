"""Zigbee2MQTT device import through the frontend WebSocket API."""

from __future__ import annotations

import json
import os
import re
import time
from collections.abc import Callable, Iterable, Mapping
from contextlib import AbstractContextManager
from typing import Any, Protocol
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from hiri_bridge.devices.types import Device

# Minimal offline sample shaped like the retained ``bridge/devices`` payload.
Z2M_FIXTURE: list[dict[str, Any]] = [
    {
        "friendly_name": "kitchen/motion",
        "type": "EndDevice",
        "definition": {"model": "SNZB-03", "vendor": "SONOFF", "description": "Motion"},
        "exposes": [{"type": "binary", "name": "occupancy"}],
    },
    {
        "friendly_name": "hall/contact",
        "type": "EndDevice",
        "definition": {"model": "MCCGQ11LM", "vendor": "Xiaomi", "description": "Door"},
        "exposes": [{"type": "binary", "name": "contact"}],
    },
    {
        "friendly_name": "living/bulb",
        "type": "Router",
        "definition": {"model": "LED1623G12", "vendor": "IKEA", "description": "Bulb"},
        "exposes": [{"type": "light", "features": [{"name": "state"}, {"name": "brightness"}]}],
    },
]

_DOMAIN_BY_EXPOSE_TYPE = {
    "light": "light",
    "switch": "switch",
    "climate": "climate",
    "cover": "cover",
    "lock": "lock",
    "fan": "fan",
}
_BINARY_DEVICE_CLASSES = {
    "contact": "door",
    "gas": "gas",
    "motion": "motion",
    "occupancy": "motion",
    "presence": "presence",
    "smoke": "smoke",
    "tamper": "tamper",
    "vibration": "vibration",
    "water_leak": "moisture",
}


class Z2mConnection(Protocol):
    def recv(self, timeout: float | None = None) -> str | bytes: ...


ConnectionFactory = Callable[..., AbstractContextManager[Z2mConnection]]


class Zigbee2MqttAdapter:
    name = "z2m"

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        use_fixture: bool | None = None,
        *,
        timeout: float = 5.0,
        connection_factory: ConnectionFactory | None = None,
    ):
        configured_url = base_url if base_url is not None else os.environ.get("HIRI_Z2M_URL", "")
        self.base_url = configured_url.rstrip("/")
        self.token = token if token is not None else os.environ.get("HIRI_Z2M_TOKEN", "")
        self.use_fixture = not self.base_url if use_fixture is None else use_fixture
        self.timeout = timeout
        self.connection_factory = connection_factory

    def status(self) -> str:
        if self.use_fixture:
            return "fixture ready"
        if not self.base_url:
            return "HIRI_Z2M_URL required for live import"
        if self.connection_factory is not None:
            return f"configured -> {_display_host(self.base_url)}"
        try:
            import websockets.sync.client  # noqa: F401
        except ImportError:
            return 'configured (pip install -e ".[z2m]" for live import)'
        return f"configured -> {_display_host(self.base_url)}"

    @property
    def websocket_url(self) -> str:
        if not self.base_url:
            raise ValueError("HIRI_Z2M_URL is required for live import")

        parsed = urlsplit(self.base_url)
        if parsed.scheme in {"http", "ws"}:
            scheme = "ws"
        elif parsed.scheme in {"https", "wss"}:
            scheme = "wss"
        else:
            raise ValueError("Zigbee2MQTT URL must use http, https, ws, or wss")

        path = parsed.path.rstrip("/")
        if not path.endswith("/api"):
            path = f"{path}/api"
        query = parse_qsl(parsed.query, keep_blank_values=True)
        if self.token:
            query = [(key, value) for key, value in query if key != "token"]
            query.append(("token", self.token))
        return urlunsplit((scheme, parsed.netloc, path, urlencode(query), ""))

    def list_remote(self) -> list[Device]:
        if self.use_fixture:
            return devices_from_payload(Z2M_FIXTURE)
        if not self.base_url:
            return []
        try:
            return devices_from_payload(self._read_live_payload())
        except Exception:
            return []

    def push_state(self, device: Device) -> None:
        return None

    def _read_live_payload(self) -> list[Mapping[str, Any]]:
        factory = self.connection_factory
        if factory is None:
            try:
                from websockets.sync.client import connect
            except ImportError as exc:
                raise RuntimeError(
                    'websockets not installed; pip install -e ".[z2m]"'
                ) from exc
            factory = connect

        deadline = time.monotonic() + self.timeout
        with factory(
            self.websocket_url,
            open_timeout=self.timeout,
            close_timeout=self.timeout,
        ) as connection:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("timed out waiting for Zigbee2MQTT bridge/devices")
                raw = connection.recv(timeout=remaining)
                message = json.loads(raw)
                if not isinstance(message, dict) or message.get("topic") != "bridge/devices":
                    continue
                payload = message.get("payload")
                if isinstance(payload, str):
                    payload = json.loads(payload)
                if not isinstance(payload, list):
                    raise ValueError("Zigbee2MQTT bridge/devices payload must be a list")
                return payload


def devices_from_payload(rows: Iterable[Mapping[str, Any]]) -> list[Device]:
    devices: list[Device] = []
    for row in rows:
        if str(row.get("type", "")).lower() == "coordinator":
            continue

        friendly_name = str(row.get("friendly_name") or row.get("ieee_address") or "").strip()
        if not friendly_name:
            continue

        exposes = row.get("exposes")
        if not isinstance(exposes, list):
            exposes = []
        domain, device_class = _classify_exposes(exposes)
        definition = row.get("definition")
        if not isinstance(definition, Mapping):
            definition = {}

        attributes: dict[str, Any] = {
            "via": "z2m",
            "zigbee_type": row.get("type"),
            "ieee_address": row.get("ieee_address"),
            "power_source": row.get("power_source"),
            "supported": row.get("supported", True),
        }
        if device_class:
            attributes["device_class"] = device_class
        attributes = {key: value for key, value in attributes.items() if value is not None}

        devices.append(
            Device(
                id=f"{domain}.z2m_{_slug(friendly_name)}",
                name=friendly_name,
                domain=domain,
                manufacturer=str(definition.get("vendor") or "Zigbee"),
                model=str(definition.get("model") or row.get("model_id") or "z2m"),
                area=friendly_name.split("/", 1)[0] if "/" in friendly_name else "home",
                online=bool(row.get("interview_completed", True))
                and not bool(row.get("disabled", False)),
                state={"state": "unknown"},
                attributes=attributes,
                adapter="z2m",
            )
        )
    return devices


def _classify_exposes(exposes: Iterable[Mapping[str, Any]]) -> tuple[str, str | None]:
    flattened = list(_flatten_exposes(exposes))
    expose_types = {str(expose.get("type", "")).lower() for expose in flattened}
    for expose_type, domain in _DOMAIN_BY_EXPOSE_TYPE.items():
        if expose_type in expose_types:
            return domain, None

    expose_names = {
        str(expose.get("name") or expose.get("property") or "").lower()
        for expose in flattened
    }
    for name, device_class in _BINARY_DEVICE_CLASSES.items():
        if name in expose_names:
            return "binary_sensor", device_class
    if "binary" in expose_types:
        return "binary_sensor", None
    return "sensor", None


def _flatten_exposes(exposes: Iterable[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
    for expose in exposes:
        if not isinstance(expose, Mapping):
            continue
        yield expose
        features = expose.get("features")
        if isinstance(features, list):
            yield from _flatten_exposes(features)


def _slug(value: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^\w]+", "_", value.lower())).strip("_") or "device"


def _display_host(url: str) -> str:
    parsed = urlsplit(url)
    return parsed.netloc or parsed.path.split("/", 1)[0]
