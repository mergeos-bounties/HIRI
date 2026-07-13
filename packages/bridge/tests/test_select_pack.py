"""Device pack tests: select — scene modes (Fixes #34)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_scene_select_seed_present(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    scene = reg.get("select.scene_living")
    assert scene is not None
    assert scene.attributes["options"] == ["day", "night", "movie", "party", "away"]
    assert scene.state["option"] == "day"


def test_select_option_change_validated(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("select.scene_living", "select_option", {"option": "movie"})
    assert dev.state["option"] == "movie"


def test_select_rejects_invalid_option(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("select.scene_living", "select_option", {"option": "nonexistent"})
    assert dev.state["option"] == "day"  # unchanged, invalid option ignored


def test_select_discovery_has_value_template(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    scene = reg.get("select.scene_living")
    assert scene is not None
    payload = export_discovery([scene])[0]["payload"]

    assert payload["options"] == ["day", "night", "movie", "party", "away"]
    assert payload["value_template"] == "{{ value_json.option }}"
