"""Tests for the Tuya adapter."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.adapters import import_from_adapter, list_adapters
from hiri_bridge.adapters.tuya import (
    TUYA_CATEGORY_MAP,
    TUYA_FIXTURE,
    TuyaAdapter,
)
from hiri_bridge.devices.registry import DeviceRegistry


def test_tuya_adapter_registered():
    """Tuya adapter is listed in the adapter catalog."""
    rows = list_adapters()
    names = {r["name"] for r in rows}
    assert "tuya" in names


def test_tuya_fixture_returns_devices():
    """Fixture mode returns the expected devices."""
    adapter = TuyaAdapter()
    devices = adapter.list_remote()
    assert len(devices) == len(TUYA_FIXTURE)
    assert all(d.adapter == "tuya" for d in devices)


def test_tuya_fixture_device_types():
    """Fixture devices cover multiple HA domains."""
    adapter = TuyaAdapter()
    devices = adapter.list_remote()
    domains = {d.domain for d in devices}
    expected = {"light", "switch", "sensor", "binary_sensor", "cover", "lock", "camera", "vacuum", "climate", "fan", "alarm"}
    covered = domains & expected
    assert len(covered) >= 5, f"Expected at least 5 domains, got {covered}"


def test_tuya_fixture_all_have_ids():
    """Every fixture device has a non-empty ID."""
    adapter = TuyaAdapter()
    for d in adapter.list_remote():
        assert d.id, f"Device {d.name} has empty id"


def test_tuya_mapping_table():
    """Mapping table contains all fixture categories."""
    mapping = TuyaAdapter.mapping_table()
    for fixture in TUYA_FIXTURE:
        assert fixture["category"] in mapping, f"Fixture category {fixture['category']} not in mapping"
    assert mapping["dj"] == "light"
    assert mapping["cz"] == "switch"
    assert mapping["wsdcg"] == "sensor"
    assert mapping["mcs"] == "binary_sensor"
    assert mapping["cl"] == "cover"
    assert mapping["sm"] == "lock"
    assert mapping["sp"] == "camera"
    assert mapping["sd"] == "vacuum"
    assert mapping["kt"] == "climate"
    assert mapping["fgn"] == "fan"
    assert mapping["jq"] == "alarm"


def test_tuya_full_mapping():
    """Full mapping table has descriptions."""
    full = TuyaAdapter.full_mapping_table()
    assert len(full) >= len(TUYA_CATEGORY_MAP)
    for cat, info in full.items():
        assert "domain" in info, f"Category {cat} missing domain"
        assert "description" in info, f"Category {cat} missing description"


def test_tuya_cloud_mode_offline_safe():
    """Cloud mode without credentials returns fixture."""
    adapter = TuyaAdapter(access_id="", access_secret="", use_fixture=False)
    devices = adapter.list_remote()
    assert len(devices) == len(TUYA_FIXTURE)


def test_tuya_push_state_noop_fixture():
    """push_state is a no-op in fixture mode."""
    adapter = TuyaAdapter()
    from hiri_bridge.devices.types import Device
    dummy = Device(
        id="test", name="test", domain="switch",
        state={"state": "on"}, adapter="tuya",
        manufacturer="Tuya", model="cz", area="home",
        online=True, attributes={"tuya_id": "test123"},
    )
    result = adapter.push_state(dummy)
    assert result is None


def test_tuya_import_into_registry(tmp_path: Path):
    """Importing Tuya devices into the registry works."""
    reg = DeviceRegistry(path=tmp_path / "tuya_test.json")
    reg.seed()
    before = reg.stats()["total"]
    for d in import_from_adapter("tuya"):
        reg.upsert(d)
    assert reg.stats()["total"] > before
    tuya_devices = [d for d in reg.list() if d.adapter == "tuya"]
    assert len(tuya_devices) == len(TUYA_FIXTURE)


def test_tuya_offline_device_online_status():
    """Offline fixture devices are marked correctly."""
    adapter = TuyaAdapter()
    devices = adapter.list_remote()
    online = [d for d in devices if d.online]
    offline = [d for d in devices if not d.online]
    assert len(online) >= len(offline)
    offline_ids = ["tuya_bf000door", "tuya_bf666ac"]
    for d in devices:
        if d.id.split(".")[-1] in offline_ids:
            assert not d.online, f"Expected {d.name} to be offline"
