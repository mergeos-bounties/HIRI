"""Offline Matter adapter scaffold with a transport-neutral node snapshot contract."""

from __future__ import annotations

from typing import Any, Iterable, Protocol

from hiri_bridge.devices.types import Device


MATTER_DEVICE_TYPE_MAP: dict[str, str] = {
    "on_off_light": "light",
    "dimmable_light": "light",
    "color_temperature_light": "light",
    "extended_color_light": "light",
    "on_off_plug_in_unit": "switch",
    "dimmable_plug_in_unit": "switch",
    "contact_sensor": "binary_sensor",
    "temperature_sensor": "sensor",
    "door_lock": "lock",
    "thermostat": "climate",
    "window_covering": "cover",
    "fan": "fan",
}

MATTER_NODE_FIXTURE: list[dict[str, Any]] = [
    {
        "node_id": 1001,
        "endpoint_id": 1,
        "device_type": "dimmable_light",
        "name": "Matter living-room lamp",
        "vendor": "HIRI fixture",
        "product": "dimmable-light",
        "area": "living_room",
        "reachable": True,
        "attributes": {"on_off": True, "current_level": 180},
    },
    {
        "node_id": 1002,
        "endpoint_id": 1,
        "device_type": "contact_sensor",
        "name": "Matter front-door contact",
        "vendor": "HIRI fixture",
        "product": "contact-sensor",
        "area": "entry",
        "reachable": True,
        "attributes": {"contact": False},
    },
    {
        "node_id": 1003,
        "endpoint_id": 1,
        "device_type": "thermostat",
        "name": "Matter hallway thermostat",
        "vendor": "HIRI fixture",
        "product": "thermostat",
        "area": "hallway",
        "reachable": True,
        "attributes": {"local_temperature": 21.4, "occupied_heating_setpoint": 22.0},
    },
]


class MatterNodeProvider(Protocol):
    """Boundary implemented later by a Matter Server WebSocket client."""

    def list_nodes(self) -> list[dict[str, Any]]:
        """Return normalized Matter endpoint snapshots."""
        ...


class MatterAdapter:
    name = "matter"

    def __init__(
        self,
        provider: MatterNodeProvider | None = None,
        fixture_nodes: Iterable[dict[str, Any]] | None = None,
    ):
        self.provider = provider
        self.fixture_nodes = (
            list(fixture_nodes) if fixture_nodes is not None else MATTER_NODE_FIXTURE
        )

    def status(self) -> str:
        return "provider configured" if self.provider is not None else "fixture ready"

    def list_remote(self) -> list[Device]:
        rows = self.provider.list_nodes() if self.provider is not None else self.fixture_nodes
        return [matter_node_to_device(row) for row in rows]

    def push_state(self, device: Device) -> None:
        """Command writes remain out of scope until a live controller provider is added."""
        return None


def matter_node_to_device(node: dict[str, Any]) -> Device:
    """Map one normalized Matter endpoint snapshot to the HIRI device contract."""
    node_id = int(node["node_id"])
    endpoint_id = int(node.get("endpoint_id", 0))
    device_type = str(node.get("device_type") or "unknown").strip().lower()
    domain = MATTER_DEVICE_TYPE_MAP.get(device_type, "sensor")
    attributes = dict(node.get("attributes") or {})

    return Device(
        id=f"{domain}.matter_{node_id}_{endpoint_id}",
        name=str(node.get("name") or f"Matter {node_id}/{endpoint_id}"),
        domain=domain,
        manufacturer=str(node.get("vendor") or "Matter"),
        model=str(node.get("product") or device_type),
        area=str(node.get("area") or "home"),
        online=bool(node.get("reachable", True)),
        state=_state_for_domain(domain, attributes),
        attributes={
            "matter_node_id": node_id,
            "matter_endpoint_id": endpoint_id,
            "matter_device_type": device_type,
            "matter_attributes": attributes,
        },
        adapter="matter",
    )


def _state_for_domain(domain: str, attributes: dict[str, Any]) -> dict[str, Any]:
    if domain in {"light", "switch"}:
        state = {"state": "on" if attributes.get("on_off") else "off"}
        if "current_level" in attributes:
            state["brightness"] = attributes["current_level"]
        return state
    if domain == "binary_sensor":
        return {"state": "on" if attributes.get("contact") else "off"}
    if domain == "climate":
        return {
            "temperature": attributes.get("local_temperature"),
            "target_temperature": attributes.get("occupied_heating_setpoint"),
        }
    if domain == "lock":
        return {"state": attributes.get("lock_state", "unknown")}
    if domain == "cover":
        return {"position": attributes.get("current_position")}
    if domain == "fan":
        return {"state": "on" if attributes.get("fan_mode") else "off"}
    return {"value": attributes.get("measured_value")}
