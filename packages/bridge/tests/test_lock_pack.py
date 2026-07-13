"""Device pack tests: lock — PIN / door codes stub (Fixes #27)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_lock_keypad_seed_present(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    stats = reg.stats()
    assert stats["by_domain"].get("lock", 0) >= 2
    gate = reg.get("lock.side_gate")
    assert gate is not None
    assert gate.attributes["code_required"] is True


def test_lock_command_lock_unlock_and_code(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("lock.side_gate", "unlock", {"code": "1234"})
    assert dev.state["state"] == "unlocked"
    assert dev.state["code_set"] is True
    dev = reg.apply_command("lock.side_gate", "lock")
    assert dev.state["state"] == "locked"


def test_lock_keypad_discovery_includes_code_format(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    gate = reg.get("lock.side_gate")
    assert gate is not None
    payload = export_discovery([gate])[0]["payload"]

    assert payload["payload_lock"] == "LOCK"
    assert payload["payload_unlock"] == "UNLOCK"
    assert payload["code_format"] == "^[0-9]{4,6}$"
    assert payload["code_state_topic"].endswith("/state/lock/side_gate/code")


def test_lock_without_code_omits_code_format(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    front = reg.get("lock.front")
    assert front is not None
    payload = export_discovery([front])[0]["payload"]
    assert "code_format" not in payload
