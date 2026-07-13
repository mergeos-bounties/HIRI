"""Device pack tests: number — calibration min/max (Fixes #33)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_number_emits_unit_and_mode(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dose = reg.get("number.feed_dose")
    assert dose is not None
    payload = export_discovery([dose])[0]["payload"]

    assert payload["unit_of_measurement"] == "ml"
    assert payload["min"] == 0
    assert payload["max"] == 500
    assert payload["step"] == 10
    assert payload["mode"] == "auto"


def test_number_value_clamped_to_max(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("number.feed_dose", "set_value", {"value": 9999})
    assert dev.state["value"] == 500  # clamped to max


def test_number_value_clamped_to_min(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("number.feed_dose", "set_value", {"value": -50})
    assert dev.state["value"] == 0  # clamped to min


def test_number_value_within_range_kept(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("number.feed_dose", "set_value", {"value": 120})
    assert dev.state["value"] == 120
