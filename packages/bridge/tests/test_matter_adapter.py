from __future__ import annotations

from typing import Any

from hiri_bridge.adapters import import_from_adapter, list_adapters
from hiri_bridge.adapters.matter import MatterAdapter, matter_node_to_device


class FakeMatterProvider:
    def list_nodes(self) -> list[dict[str, Any]]:
        return [
            {
                "node_id": 42,
                "endpoint_id": 2,
                "device_type": "door_lock",
                "name": "Test lock",
                "vendor": "Fixture vendor",
                "product": "lock-v1",
                "reachable": False,
                "attributes": {"lock_state": "locked"},
            }
        ]


def test_fixture_maps_matter_endpoints_to_hiri_devices() -> None:
    devices = MatterAdapter().list_remote()

    assert {device.domain for device in devices} == {"light", "binary_sensor", "climate"}
    assert all(device.adapter == "matter" for device in devices)
    assert devices[0].attributes["matter_node_id"] == 1001
    assert devices[0].state == {"state": "on", "brightness": 180}


def test_provider_boundary_is_injectable_and_offline() -> None:
    devices = MatterAdapter(provider=FakeMatterProvider()).list_remote()

    assert len(devices) == 1
    assert devices[0].id == "lock.matter_42_2"
    assert devices[0].online is False
    assert devices[0].state == {"state": "locked"}


def test_unknown_matter_device_type_falls_back_to_sensor() -> None:
    device = matter_node_to_device(
        {
            "node_id": 88,
            "device_type": "future_device",
            "attributes": {"measured_value": 7},
        }
    )

    assert device.domain == "sensor"
    assert device.state == {"value": 7}


def test_matter_adapter_is_available_from_catalog() -> None:
    row = next(adapter for adapter in list_adapters() if adapter["name"] == "matter")

    assert row["status"] == "fixture ready"
    assert row["live"] is False
    assert import_from_adapter("matter")
