"""Device pack tests: button — single/double/long press (Fixes #32)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_button_seed_has_event_types(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    btn = reg.get("button.panic")
    assert btn is not None
    assert btn.attributes["event_types"] == ["single", "double", "long"]


def test_button_discovery_emits_event_types(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    btn = reg.get("button.panic")
    assert btn is not None
    payload = export_discovery([btn])[0]["payload"]

    assert payload["event_types"] == ["single", "double", "long"]
    assert "event_topic" in payload


def test_button_double_press_recorded(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("button.panic", "press", {"press_type": "double"})
    assert dev.state["last_pressed"] == "double"


def test_button_long_press_recorded(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("button.panic", "press", {"press_type": "long"})
    assert dev.state["last_pressed"] == "long"


def test_button_invalid_press_falls_back_to_single(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("button.panic", "press", {"press_type": "triple"})
    assert dev.state["last_pressed"] == "single"
