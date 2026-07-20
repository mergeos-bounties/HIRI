from __future__ import annotations

from pathlib import Path

from hiri_bridge.adapters import import_from_adapter, list_adapters
from hiri_bridge.adapters.mqtt_pub import MqttDiscoveryPublisher
from hiri_bridge.adapters.tuya import TuyaAdapter
from hiri_bridge.adapters.z2m import Zigbee2MqttAdapter
from hiri_bridge.devices.registry import DeviceRegistry


def test_list_adapters():
    rows = list_adapters()
    names = {r["name"] for r in rows}
    assert {"local", "mqtt", "ha_rest", "ha_ws", "z2m", "tuya"}.issubset(names)


def test_z2m_fixture_import():
    devices = Zigbee2MqttAdapter().list_remote()
    assert len(devices) >= 3
    assert all(d.adapter == "z2m" for d in devices)
    assert any(d.domain == "light" for d in devices)


def test_tuya_fixture_and_map():
    devices = TuyaAdapter().list_remote()
    assert len(devices) >= 3
    assert "dj" in TuyaAdapter.mapping_table()
    assert all(d.adapter == "tuya" for d in devices)


def test_import_into_registry(tmp_path: Path):
    reg = DeviceRegistry(path=tmp_path / "d.json")
    reg.seed()
    before = reg.stats()["total"]
    for d in import_from_adapter("z2m"):
        reg.upsert(d)
    assert reg.stats()["total"] > before


def test_ha_ws_import_is_offline_safe():
    assert import_from_adapter("ha_ws") == []


def test_mqtt_dry_run(tmp_path: Path):
    reg = DeviceRegistry(path=tmp_path / "d.json")
    reg.seed()
    pub = MqttDiscoveryPublisher()
    result = pub.publish(reg.list()[:3], dry_run=True)
    assert result["ok"] is True
    assert result["dry_run"] is True
    assert result["count"] >= 3
