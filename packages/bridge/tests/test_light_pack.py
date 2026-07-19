"""Device pack tests: light - porch sconce brightness (Fixes #92)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_porch_sconce_seed_present(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    sconce = reg.get("light.porch_sconce")
    assert sconce is not None
    assert sconce.domain == "light"
    assert sconce.area == "porch"
    assert sconce.state["brightness"] == 0
    assert sconce.attributes["supported_color_modes"] == ["brightness"]


def test_porch_sconce_discovery_supports_brightness(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    sconce = reg.get("light.porch_sconce")
    assert sconce is not None

    payload = export_discovery([sconce])[0]["payload"]

    assert payload["brightness"] is True
    assert payload["brightness_scale"] == 255
    assert payload["command_topic"].endswith("/cmd/light/porch_sconce")
