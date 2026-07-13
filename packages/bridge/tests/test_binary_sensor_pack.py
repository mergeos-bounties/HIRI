"""Device pack tests: binary_sensor — door/window/battery (Fixes #23)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_battery_window_seed_present(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    win = reg.get("binary_sensor.window_bedroom")
    assert win is not None
    assert win.attributes["battery"] is True
    assert win.state["battery"] == 87


def test_motion_sensor_has_off_delay(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    motion = next(
        d for d in reg.list() if d.domain == "binary_sensor" and d.attributes.get("device_class") == "motion"
    )
    assert motion.attributes["off_delay"] == 30


def test_battery_sensor_discovery_has_attributes_topic(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    win = reg.get("binary_sensor.window_bedroom")
    assert win is not None
    payload = export_discovery([win])[0]["payload"]

    assert payload["device_class"] == "window"
    assert payload["expire_after"] == 3600
    assert payload["json_attributes_topic"].endswith("/attributes")


def test_plain_door_sensor_omits_battery_fields(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    door = reg.get("binary_sensor.door_front")
    assert door is not None
    payload = export_discovery([door])[0]["payload"]

    assert payload["device_class"] == "door"
    assert "json_attributes_topic" not in payload
    assert "off_delay" not in payload
