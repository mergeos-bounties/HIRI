"""Device pack tests: cover — tilt blinds (Fixes #26)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_cover_tilt_seed_present(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    stats = reg.stats()
    assert stats["by_domain"].get("cover", 0) >= 2
    blinds = reg.get("cover.living_blinds")
    assert blinds is not None
    assert blinds.attributes["tilt"] is True


def test_cover_command_set_tilt_and_position(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("cover.living_blinds", "set_tilt", {"tilt": 30})
    assert dev.state["tilt"] == 30
    dev = reg.apply_command("cover.living_blinds", "set_position", {"position": 75})
    assert dev.state["position"] == 75
    assert dev.state["state"] == "open"


def test_cover_discovery_includes_tilt_topics(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    blinds = reg.get("cover.living_blinds")
    assert blinds is not None
    payload = export_discovery([blinds])[0]["payload"]

    assert payload["position_topic"].endswith("/state/cover/living_blinds/position")
    assert payload["tilt_status_topic"].endswith("/state/cover/living_blinds/tilt")
    assert payload["tilt_command_topic"].endswith("/cmd/cover/living_blinds/tilt")
    assert payload["tilt_min"] == 0
    assert payload["tilt_max"] == 100


def test_cover_without_tilt_omits_tilt_topics(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    garage = reg.get("cover.garage")
    assert garage is not None
    payload = export_discovery([garage])[0]["payload"]
    assert "tilt_command_topic" not in payload
