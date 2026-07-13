"""Device pack tests: water_heater — away mode + temp clamping (Fixes #37)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_boiler_seed_has_modes(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    boiler = reg.get("water_heater.boiler")
    assert boiler is not None
    assert boiler.attributes["modes"] == ["off", "eco", "performance", "away"]
    assert boiler.state["mode"] == "eco"


def test_water_heater_discovery_emits_modes(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    boiler = reg.get("water_heater.boiler")
    assert boiler is not None
    payload = export_discovery([boiler])[0]["payload"]

    assert payload["modes"] == ["off", "eco", "performance", "away"]
    assert payload["min_temp"] == 30
    assert payload["max_temp"] == 70
    assert "mode_command_topic" in payload


def test_water_heater_set_away_mode(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("water_heater.boiler", "set_mode", {"mode": "away"})
    assert dev.state["mode"] == "away"
    assert dev.state["state"] == "on"


def test_water_heater_off_mode_sets_state_off(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("water_heater.boiler", "set_mode", {"mode": "off"})
    assert dev.state["state"] == "off"


def test_water_heater_temperature_clamped(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("water_heater.boiler", "set_temperature", {"temperature": 999})
    assert dev.state["temperature"] == 70
    dev = reg.apply_command("water_heater.boiler", "set_temperature", {"temperature": -5})
    assert dev.state["temperature"] == 30


def test_water_heater_invalid_mode_ignored(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("water_heater.boiler", "set_mode", {"mode": "turbo"})
    assert dev.state["mode"] == "eco"  # unchanged
