"""Device pack tests: switch — multi-gang relay (Fixes #22)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_switch_multigang_seed_present(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    stats = reg.stats()
    assert stats["by_domain"].get("switch", 0) >= 2
    panel = reg.get("switch.wall_panel")
    assert panel is not None
    assert panel.attributes["gangs"] == ["gang1", "gang2", "gang3"]


def test_switch_set_gang_updates_aggregate_state(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("switch.wall_panel", "set_gang", {"gang": "gang2", "state": "on"})
    assert dev.state["gang2"] == "on"
    assert dev.state["state"] == "on"  # aggregate reflects any-on
    dev = reg.apply_command("switch.wall_panel", "set_gang", {"gang": "gang2", "state": "off"})
    assert dev.state["gang2"] == "off"
    assert dev.state["state"] == "off"  # all gangs off


def test_switch_discovery_includes_gang_topics(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    panel = reg.get("switch.wall_panel")
    assert panel is not None
    payload = export_discovery([panel])[0]["payload"]

    assert payload["payload_on"] == "ON"
    assert payload["device_class"] == "outlet"
    assert payload["gang_count"] == 3
    assert payload["gang_command_topics"]["gang1"].endswith("/cmd/switch/wall_panel/gang1")
    assert payload["gang_state_topics"]["gang3"].endswith("/state/switch/wall_panel/gang3")


def test_single_switch_omits_gang_topics(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    pump = reg.get("switch.pump_a")
    assert pump is not None
    payload = export_discovery([pump])[0]["payload"]
    assert "gang_count" not in payload
    assert payload["device_class"] == "switch"
