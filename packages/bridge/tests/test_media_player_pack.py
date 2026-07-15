"""Device pack tests: media_player — source list (Fixes #29)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


EXPECTED_MEDIA_PLAYER_PACK = {
    "media_player.family_room_tv": {
        "model": "HIRI-TV",
        "area": "family_room",
        "source": "HDMI 1",
        "source_list": ["HDMI 1", "HDMI 2", "Disney+", "Game Console", "Antenna"],
    },
    "media_player.patio_speaker": {
        "model": "HIRI-SPK",
        "area": "patio",
        "source": "Bluetooth",
        "source_list": ["Bluetooth", "AirPlay", "Line-in"],
    },
    "media_player.den_streamer": {
        "model": "HIRI-STREAM",
        "area": "den",
        "source": "Plex",
        "source_list": ["Plex", "Spotify", "YouTube", "Internet Radio"],
    },
}

EXPECTED_SUPPORTED_FEATURES = [
    "turn_on",
    "turn_off",
    "play",
    "pause",
    "volume_set",
    "select_source",
]


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


def test_media_player_pack_adds_tv_speaker_and_streamer(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()

    for device_id, expected in EXPECTED_MEDIA_PLAYER_PACK.items():
        dev = reg.get(device_id)
        assert dev is not None
        assert dev.domain == "media_player"
        assert dev.model == expected["model"]
        assert dev.area == expected["area"]
        assert dev.state["source"] == expected["source"]
        assert dev.attributes["source_list"] == expected["source_list"]
        assert dev.attributes["supported_features"] == EXPECTED_SUPPORTED_FEATURES


def test_media_player_pack_discovery_emits_source_controls(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()

    for device_id, expected in EXPECTED_MEDIA_PLAYER_PACK.items():
        dev = reg.get(device_id)
        assert dev is not None
        payload = export_discovery([dev])[0]["payload"]

        assert payload["source_list"] == expected["source_list"]
        assert payload["source_command_topic"].endswith(
            f"/cmd/media_player/{device_id.rsplit('.', 1)[1]}/source"
        )
        assert payload["supported_features"] == EXPECTED_SUPPORTED_FEATURES


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
