"""Device pack tests: media_player — source list (Fixes #29)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_tv_source_list_seed_present(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    tv = reg.get("media_player.tv_living")
    assert tv is not None
    assert tv.attributes["source_list"] == ["HDMI 1", "HDMI 2", "Netflix", "YouTube", "TV"]
    assert tv.state["source"] == "HDMI 1"


def test_media_player_discovery_emits_source_list(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    tv = reg.get("media_player.tv_living")
    assert tv is not None
    payload = export_discovery([tv])[0]["payload"]

    assert payload["source_list"] == ["HDMI 1", "HDMI 2", "Netflix", "YouTube", "TV"]
    assert "source_command_topic" in payload
    assert "volume_set" in payload["supported_features"]


def test_select_source_validated(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("media_player.tv_living", "select_source", {"source": "Netflix"})
    assert dev.state["source"] == "Netflix"


def test_select_source_rejects_invalid(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("media_player.tv_living", "select_source", {"source": "Nonexistent"})
    assert dev.state["source"] == "HDMI 1"  # unchanged
