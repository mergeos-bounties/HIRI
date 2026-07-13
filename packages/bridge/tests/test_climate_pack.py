"""Device pack tests: climate — thermostat presets (Fixes #25)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_climate_seed_present(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    stats = reg.stats()
    assert stats["by_domain"].get("climate", 0) >= 2
    thermo = reg.get("climate.living_thermostat")
    assert thermo is not None
    assert thermo.attributes["preset_modes"] == ["comfort", "eco", "away", "boost"]


def test_climate_command_sets_mode_temp_and_preset(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command(
        "climate.living_thermostat",
        "set_temperature",
        {"hvac_mode": "cool", "temperature": 23, "preset_mode": "eco"},
    )
    assert dev.state["hvac_mode"] == "cool"
    assert dev.state["temperature"] == 23
    assert dev.state["preset_mode"] == "eco"


def test_climate_discovery_includes_presets_and_topics(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    thermo = reg.get("climate.living_thermostat")
    assert thermo is not None
    payload = export_discovery([thermo])[0]["payload"]

    assert payload["modes"] == ["off", "heat", "cool", "auto"]
    assert payload["min_temp"] == 7
    assert payload["max_temp"] == 35
    assert payload["temp_step"] == 0.5
    # thermostat presets must be advertised for HA
    assert payload["preset_modes"] == ["comfort", "eco", "away", "boost"]
    assert payload["preset_mode_command_topic"].endswith("/cmd/climate/living_thermostat/preset")
    assert payload["preset_mode_state_topic"].endswith("/state/climate/living_thermostat/preset")
    assert payload["mode_command_topic"].endswith("/cmd/climate/living_thermostat/mode")
    assert payload["temperature_command_topic"].endswith("/cmd/climate/living_thermostat/temp")
