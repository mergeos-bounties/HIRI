"""Device pack tests: vacuum — room map + fan speed (Fixes #30)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_vacuum_seed_has_rooms_and_fan_speed(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    bot = reg.get("vacuum.bot_1")
    assert bot is not None
    assert bot.attributes["rooms"] == ["living", "kitchen", "bedroom", "hallway"]
    assert bot.attributes["fan_speed_list"] == ["quiet", "balanced", "turbo", "max"]


def test_vacuum_discovery_emits_fan_speed_list(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    bot = reg.get("vacuum.bot_1")
    assert bot is not None
    payload = export_discovery([bot])[0]["payload"]

    assert payload["fan_speed_list"] == ["quiet", "balanced", "turbo", "max"]
    assert "fan_speed" in payload["supported_features"]
    assert "json_attributes_topic" in payload


def test_vacuum_set_fan_speed_validated(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("vacuum.bot_1", "set_fan_speed", {"fan_speed": "turbo"})
    assert dev.state["fan_speed"] == "turbo"


def test_vacuum_set_fan_speed_rejects_invalid(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("vacuum.bot_1", "set_fan_speed", {"fan_speed": "warp9"})
    assert dev.state["fan_speed"] == "balanced"  # unchanged


def test_vacuum_clean_room(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("vacuum.bot_1", "clean_room", {"room": "kitchen"})
    assert dev.state["state"] == "cleaning"
    assert dev.state["current_room"] == "kitchen"


def test_vacuum_clean_room_rejects_unknown(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("vacuum.bot_1", "clean_room", {"room": "garage"})
    assert dev.state["state"] == "docked"  # unchanged
    assert "current_room" not in dev.state
