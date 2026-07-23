"""Matter adapter scaffold — offline device-type mapping, no controller yet.

The catalog has advertised a `matter` adapter as "planned" since the adapters package
was introduced, but there was no module behind it, so `import_from_adapter("matter")`
raised. This scaffold fills that seam: the part of Matter that HIRI actually needs to
own — the device type → HIRI domain mapping and the shape of a commissioned node — is
implemented and tested offline, while the parts that need a real fabric (commissioning,
subscriptions, writes) are explicit, documented no-ops instead of silent failures.

See docs/MATTER.md for the direction and the steps to make this live.
"""

from __future__ import annotations

from typing import Any

from hiri_bridge.devices.types import Device

# Matter device type IDs (Matter 1.x Device Library) → HIRI/HA domain.
# Keys are the numeric device type of an *endpoint*, which is what a controller reports.
MATTER_DEVICE_TYPE_MAP: dict[int, str] = {
    0x0100: "light",  # On/Off Light
    0x0101: "light",  # Dimmable Light
    0x010C: "light",  # Color Temperature Light
    0x010D: "light",  # Extended Color Light
    0x010A: "switch",  # On/Off Plug-in Unit
    0x010B: "switch",  # Dimmable Plug-in Unit
    0x0103: "switch",  # On/Off Light Switch
    0x000A: "lock",  # Door Lock
    0x0202: "cover",  # Window Covering
    0x0301: "climate",  # Thermostat
    0x002B: "fan",  # Fan
    0x0015: "binary_sensor",  # Contact Sensor
    0x0107: "binary_sensor",  # Occupancy Sensor
    0x0076: "binary_sensor",  # Smoke CO Alarm
    0x0302: "sensor",  # Temperature Sensor
    0x0305: "sensor",  # Pressure Sensor
    0x0306: "sensor",  # Flow Sensor
    0x0307: "sensor",  # Humidity Sensor
    0x0106: "sensor",  # Light Sensor
}

# Endpoint device types that describe the node itself rather than a controllable thing.
MATTER_UTILITY_DEVICE_TYPES: frozenset[int] = frozenset(
    {
        0x0016,  # Root Node
        0x000E,  # Aggregator
        0x0013,  # Bridged Node
        0x0011,  # Power Source
        0x0012,  # OTA Requestor
        0x0014,  # OTA Provider
    }
)

MATTER_DEVICE_TYPE_NAMES: dict[int, str] = {
    0x0100: "On/Off Light",
    0x0101: "Dimmable Light",
    0x010C: "Color Temperature Light",
    0x010D: "Extended Color Light",
    0x010A: "On/Off Plug-in Unit",
    0x010B: "Dimmable Plug-in Unit",
    0x0103: "On/Off Light Switch",
    0x000A: "Door Lock",
    0x0202: "Window Covering",
    0x0301: "Thermostat",
    0x002B: "Fan",
    0x0015: "Contact Sensor",
    0x0107: "Occupancy Sensor",
    0x0076: "Smoke CO Alarm",
    0x0302: "Temperature Sensor",
    0x0305: "Pressure Sensor",
    0x0306: "Flow Sensor",
    0x0307: "Humidity Sensor",
    0x0106: "Light Sensor",
    0x0016: "Root Node",
    0x000E: "Aggregator",
    0x0013: "Bridged Node",
    0x0011: "Power Source",
    0x0012: "OTA Requestor",
    0x0014: "OTA Provider",
}

# Offline fixture shaped like what python-matter-server reports per commissioned node:
# a node id, basic information (vendor/product/serial) and endpoints carrying device types.
MATTER_FIXTURE: list[dict[str, Any]] = [
    {
        "node_id": 4,
        "available": True,
        "vendor_id": 0x1349,
        "product_id": 0x0002,
        "vendor_name": "Apple",
        "product_name": "Matter Bulb",
        "serial_number": "MTR-0004",
        "area": "living",
        "endpoints": [
            {"endpoint_id": 0, "device_types": [0x0016]},
            {"endpoint_id": 1, "device_types": [0x010D], "name": "Living lamp"},
        ],
    },
    {
        "node_id": 7,
        "available": True,
        "vendor_id": 0x1217,
        "product_id": 0x1001,
        "vendor_name": "Eve",
        "product_name": "Eve Energy",
        "serial_number": "MTR-0007",
        "area": "kitchen",
        "endpoints": [
            {"endpoint_id": 0, "device_types": [0x0016]},
            {"endpoint_id": 1, "device_types": [0x010A], "name": "Kettle plug"},
        ],
    },
    {
        "node_id": 11,
        "available": True,
        "vendor_id": 0x130A,
        "product_id": 0x0056,
        "vendor_name": "Aqara",
        "product_name": "Matter Sensor Hub",
        "serial_number": "MTR-0011",
        "area": "hall",
        "endpoints": [
            {"endpoint_id": 0, "device_types": [0x0016, 0x000E]},
            {"endpoint_id": 2, "device_types": [0x0013, 0x0015], "name": "Front door"},
            {"endpoint_id": 3, "device_types": [0x0013, 0x0302], "name": "Hall temperature"},
        ],
    },
    {
        "node_id": 19,
        "available": False,
        "vendor_id": 0x1209,
        "product_id": 0x8005,
        "vendor_name": "Generic",
        "product_name": "Unknown gadget",
        "serial_number": "MTR-0019",
        "area": "garage",
        "endpoints": [
            {"endpoint_id": 0, "device_types": [0x0016]},
            {"endpoint_id": 1, "device_types": [0xFFF1], "name": "Vendor thing"},
        ],
    },
]

DEFAULT_DOMAIN = "sensor"


def domain_for_device_types(device_types: list[int] | tuple[int, ...]) -> str | None:
    """Pick the HIRI domain for an endpoint from its Matter device types.

    Utility types (Root Node, Bridged Node, Aggregator, …) never produce a device on
    their own — an endpoint that carries nothing else is skipped. An endpoint with a
    device type we do not know yet still becomes a device, in the fallback domain, so a
    new gadget shows up in the registry instead of disappearing silently.
    """
    controllable = [dt for dt in device_types if dt not in MATTER_UTILITY_DEVICE_TYPES]
    if not controllable:
        return None
    for dt in controllable:
        if dt in MATTER_DEVICE_TYPE_MAP:
            return MATTER_DEVICE_TYPE_MAP[dt]
    return DEFAULT_DOMAIN


def device_type_name(device_type: int) -> str:
    return MATTER_DEVICE_TYPE_NAMES.get(device_type, f"Unknown (0x{device_type:04X})")


class MatterAdapter:
    """Read-only Matter scaffold.

    `use_fixture=True` (the default) walks the bundled fixture so the mapping, the entity
    ids and the registry import are exercised with no fabric, no SDK and no network. A
    real controller is only used when `server_url` is set *and* `use_fixture=False`; that
    path is not implemented yet and returns nothing rather than pretending.
    """

    name = "matter"

    def __init__(self, server_url: str = "", fabric_id: int = 1, use_fixture: bool = True):
        self.server_url = (server_url or "").rstrip("/")
        self.fabric_id = int(fabric_id)
        self.use_fixture = use_fixture

    def status(self) -> str:
        if self.use_fixture:
            return "scaffold ready (fixture)"
        if not self.server_url:
            return "controller not configured (set server_url)"
        return "controller configured, live path not implemented"

    def list_remote(self) -> list[Device]:
        if not self.use_fixture:
            # Live path: a python-matter-server websocket client would fill this in.
            # See docs/MATTER.md — until then we import nothing rather than guessing.
            return []
        devices: list[Device] = []
        for node in MATTER_FIXTURE:
            devices.extend(self._devices_for_node(node))
        return devices

    def _devices_for_node(self, node: dict[str, Any]) -> list[Device]:
        node_id = int(node["node_id"])
        vendor = str(node.get("vendor_name") or "Matter")
        product = str(node.get("product_name") or "matter node")
        online = bool(node.get("available", True))
        out: list[Device] = []
        for endpoint in node.get("endpoints") or []:
            device_types = [int(dt) for dt in endpoint.get("device_types") or []]
            domain = domain_for_device_types(device_types)
            if domain is None:
                continue  # root/bridged/aggregator endpoint — nothing controllable on it
            endpoint_id = int(endpoint.get("endpoint_id", 0))
            primary = next(
                (dt for dt in device_types if dt not in MATTER_UTILITY_DEVICE_TYPES),
                device_types[0] if device_types else 0,
            )
            label = str(endpoint.get("name") or f"{product} {endpoint_id}")
            out.append(
                Device(
                    id=f"{domain}.matter_{node_id}_{endpoint_id}",
                    name=label,
                    domain=domain,
                    manufacturer=vendor,
                    model=product,
                    area=str(node.get("area") or "home"),
                    online=online,
                    state={"state": "0" if domain == "sensor" else "off"},
                    attributes={
                        "via": "matter",
                        "node_id": node_id,
                        "endpoint_id": endpoint_id,
                        "fabric_id": self.fabric_id,
                        "device_type": f"0x{primary:04X}",
                        "device_type_name": device_type_name(primary),
                        "vendor_id": f"0x{int(node.get('vendor_id', 0)):04X}",
                        "product_id": f"0x{int(node.get('product_id', 0)):04X}",
                        "serial_number": node.get("serial_number"),
                        "bridged": 0x0013 in device_types,
                    },
                    adapter="matter",
                )
            )
        return out

    def push_state(self, device: Device) -> None:
        """Writes need a commissioned fabric — intentionally a no-op in the scaffold."""

    def commission(self, setup_code: str = "") -> dict[str, Any]:
        """Report what commissioning would need instead of half-doing it."""
        return {
            "ok": False,
            "error": "commissioning requires a Matter controller (python-matter-server or chip SDK)",
            "setup_code_received": bool(setup_code),
            "next_steps": [
                "run python-matter-server with a Thread/Wi-Fi capable host",
                "set HIRI_MATTER_SERVER_URL and construct MatterAdapter(use_fixture=False)",
                "pair with the 11-digit manual code or the QR payload, then store the node id",
            ],
            "docs": "docs/MATTER.md",
        }

    @staticmethod
    def mapping_table() -> dict[str, str]:
        """Human-readable device type → domain table (hex keys, like the spec prints them)."""
        return {
            f"0x{dt:04X} {device_type_name(dt)}": domain
            for dt, domain in MATTER_DEVICE_TYPE_MAP.items()
        }
