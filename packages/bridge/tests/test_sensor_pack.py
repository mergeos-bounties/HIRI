"""Device pack tests: sensor — PM2.5 / CO2 / energy (Fixes #24)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def _payload(reg: DeviceRegistry, device_id: str) -> dict:
    dev = reg.get(device_id)
    assert dev is not None
    return export_discovery([dev])[0]["payload"]


def test_energy_sensor_seed_present(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    energy = reg.get("sensor.panel_energy")
    assert energy is not None
    assert energy.attributes["device_class"] == "energy"
    assert energy.attributes["unit_of_measurement"] == "kWh"


def test_energy_sensor_uses_total_increasing(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    payload = _payload(reg, "sensor.panel_energy")
    # Cumulative meter must be total_increasing for HA statistics / energy dash
    assert payload["state_class"] == "total_increasing"
    assert payload["device_class"] == "energy"


def test_instant_sensor_stays_measurement(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    power = _payload(reg, "sensor.power_panel")
    assert power["state_class"] == "measurement"  # instantaneous reading


def test_air_quality_sensors_present(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    classes = {
        d.attributes.get("device_class")
        for d in reg.list()
        if d.domain == "sensor"
    }
    assert "pm25" in classes
    assert "carbon_dioxide" in classes
    assert "energy" in classes
