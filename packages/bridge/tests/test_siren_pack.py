"""Device pack tests: siren — tones (Fixes #35)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_siren_seed_has_tones(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    siren = reg.get("siren.alarm")
    assert siren is not None
    assert "fire" in siren.attributes["available_tones"]


def test_siren_set_tone_and_volume(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("siren.alarm", "set_tone", {"tone": "chime", "volume": 0.5})
    assert dev.state["tone"] == "chime"
    assert dev.state["state"] == "on"
    assert dev.state["volume"] == 0.5


def test_siren_rejects_unknown_tone(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("siren.alarm", "set_tone", {"tone": "nonexistent"})
    assert dev.state["tone"] is None  # unchanged, invalid tone ignored


def test_siren_discovery_includes_available_tones(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    siren = reg.get("siren.alarm")
    assert siren is not None
    payload = export_discovery([siren])[0]["payload"]

    assert payload["payload_on"] == "ON"
    assert payload["available_tones"] == ["alarm", "chime", "fire", "burglar"]
    assert payload["support_duration"] is True
    assert payload["support_volume_set"] is True
