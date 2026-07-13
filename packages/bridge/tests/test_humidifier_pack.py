"""Device pack tests: humidifier — modes (Fixes #36)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_humidifier_seed_has_modes(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    hum = reg.get("humidifier.bedroom")
    assert hum is not None
    assert "eco" in hum.attributes["modes"]


def test_humidifier_set_humidity_clamped_to_range(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("humidifier.bedroom", "set_humidity", {"humidity": 95})
    assert dev.state["target_humidity"] == 80  # clamped to max_humidity
    assert dev.state["state"] == "on"


def test_humidifier_set_mode_validated(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("humidifier.bedroom", "set_mode", {"mode": "sleep"})
    assert dev.state["mode"] == "sleep"
    dev2 = reg.apply_command("humidifier.bedroom", "set_mode", {"mode": "bogus"})
    assert dev2.state["mode"] == "sleep"  # unchanged, invalid mode ignored


def test_humidifier_discovery_includes_modes_and_range(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    hum = reg.get("humidifier.bedroom")
    assert hum is not None
    payload = export_discovery([hum])[0]["payload"]

    assert payload["payload_on"] == "ON"
    assert payload["min_humidity"] == 30
    assert payload["max_humidity"] == 80
    assert payload["modes"] == ["normal", "eco", "away", "sleep", "boost"]
