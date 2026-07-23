from __future__ import annotations

from pathlib import Path

import pytest

from hiri_bridge.adapters import import_from_adapter, list_adapters
from hiri_bridge.adapters.matter import (
    MATTER_DEVICE_TYPE_MAP,
    MATTER_UTILITY_DEVICE_TYPES,
    MatterAdapter,
    domain_for_device_types,
)
from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import DOMAINS


def test_matter_is_in_the_catalog_and_importable():
    row = next(r for r in list_adapters() if r["name"] == "matter")
    assert row["status"] == "scaffold ready (fixture)"
    # Used to raise ValueError("unknown adapter: matter") — the catalog advertised it
    # while no module existed.
    assert len(import_from_adapter("matter")) >= 3


def test_fixture_devices_carry_matter_identity():
    devices = MatterAdapter().list_remote()
    assert all(d.adapter == "matter" for d in devices)
    assert all(d.domain in DOMAINS for d in devices)
    assert len({d.id for d in devices}) == len(devices)  # node+endpoint keeps ids unique
    lamp = next(d for d in devices if d.id == "light.matter_4_1")
    assert lamp.attributes["device_type"] == "0x010D"
    assert lamp.attributes["device_type_name"] == "Extended Color Light"
    assert lamp.attributes["node_id"] == 4
    assert lamp.attributes["endpoint_id"] == 1
    assert lamp.attributes["vendor_id"] == "0x1349"
    assert lamp.manufacturer == "Apple"


def test_device_types_map_to_expected_domains():
    devices = {d.id: d for d in MatterAdapter().list_remote()}
    assert devices["switch.matter_7_1"].domain == "switch"  # On/Off Plug-in Unit
    assert devices["binary_sensor.matter_11_2"].domain == "binary_sensor"  # Contact Sensor
    assert devices["sensor.matter_11_3"].domain == "sensor"  # Temperature Sensor


def test_bridged_endpoints_are_flagged_and_root_endpoints_skipped():
    devices = MatterAdapter().list_remote()
    ids = {d.id for d in devices}
    # endpoint 0 of every node is a Root Node — it is not a device
    assert not any(i.endswith("_0") for i in ids)
    hub_contact = next(d for d in devices if d.id == "binary_sensor.matter_11_2")
    assert hub_contact.attributes["bridged"] is True
    assert next(d for d in devices if d.id == "light.matter_4_1").attributes["bridged"] is False


def test_offline_node_keeps_online_false():
    garage = next(d for d in MatterAdapter().list_remote() if d.attributes["node_id"] == 19)
    assert garage.online is False


def test_unknown_device_type_falls_back_instead_of_vanishing():
    garage = next(d for d in MatterAdapter().list_remote() if d.attributes["node_id"] == 19)
    assert garage.domain == "sensor"
    assert garage.attributes["device_type"] == "0xFFF1"
    assert "Unknown" in garage.attributes["device_type_name"]


@pytest.mark.parametrize(
    ("device_types", "expected"),
    [
        ([0x0016], None),  # Root Node only
        ([0x000E], None),  # Aggregator only
        ([0x0016, 0x0100], "light"),
        ([0x0013, 0x0301], "climate"),
        ([0x0202], "cover"),
        ([0x000A], "lock"),
        ([0x002B], "fan"),
        ([0x1234], "sensor"),  # unknown -> fallback
        ([], None),
    ],
)
def test_domain_for_device_types(device_types, expected):
    assert domain_for_device_types(device_types) == expected


def test_mapping_table_is_consistent():
    assert set(MATTER_DEVICE_TYPE_MAP).isdisjoint(MATTER_UTILITY_DEVICE_TYPES)
    assert set(MATTER_DEVICE_TYPE_MAP.values()) <= set(DOMAINS)
    table = MatterAdapter.mapping_table()
    assert len(table) == len(MATTER_DEVICE_TYPE_MAP)
    assert table["0x0100 On/Off Light"] == "light"


def test_live_mode_imports_nothing_and_says_why():
    unconfigured = MatterAdapter(use_fixture=False)
    assert unconfigured.list_remote() == []
    assert "not configured" in unconfigured.status()
    configured = MatterAdapter(server_url="ws://matter:5580/ws", use_fixture=False)
    assert configured.list_remote() == []
    assert "not implemented" in configured.status()


def test_commission_reports_requirements_instead_of_failing_silently():
    result = MatterAdapter().commission("34970112332")
    assert result["ok"] is False
    assert result["setup_code_received"] is True
    assert result["next_steps"]
    assert result["docs"] == "docs/MATTER.md"


def test_push_state_is_a_noop_for_now():
    devices = MatterAdapter().list_remote()
    assert MatterAdapter().push_state(devices[0]) is None


def test_matter_devices_import_into_registry(tmp_path: Path):
    reg = DeviceRegistry(path=tmp_path / "d.json")
    reg.seed()
    before = reg.stats()["total"]
    for d in import_from_adapter("matter"):
        reg.upsert(d)
    after = reg.stats()["total"]
    assert after > before
    assert any(d.adapter == "matter" for d in reg.list())


def test_matter_docs_exist():
    docs = Path(__file__).resolve().parents[3] / "docs" / "MATTER.md"
    assert docs.is_file()
    body = docs.read_text(encoding="utf-8")
    assert "python-matter-server" in body
    assert "0x010D" in body  # the mapping table is documented, not just coded
