"""Device pack tests: camera — snapshot URL (Fixes #31)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_camera_seed_has_snapshot_url(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    cam = reg.get("camera.yard")
    assert cam is not None
    assert cam.attributes["snapshot_url"] == "http://192.0.2.10/snapshot.jpg"
    assert cam.attributes["stream_url"] == "rtsp://192.0.2.10/stream"


def test_camera_discovery_emits_snapshot_and_stream(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    cam = reg.get("camera.yard")
    assert cam is not None
    payload = export_discovery([cam])[0]["payload"]

    assert payload["still_image_url"] == "http://192.0.2.10/snapshot.jpg"
    assert payload["stream_source"] == "rtsp://192.0.2.10/stream"


def test_camera_discovery_omits_snapshot_when_absent(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    cam = reg.get("camera.yard")
    assert cam is not None
    cam.attributes.pop("snapshot_url", None)
    payload = export_discovery([cam])[0]["payload"]

    assert "still_image_url" not in payload
    assert payload["stream_source"] == "rtsp://192.0.2.10/stream"
