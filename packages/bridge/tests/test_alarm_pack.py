"""Device pack tests: alarm_control_panel — arm modes + code (Fixes #38)."""

from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.ha.discovery import export_discovery


def test_alarm_seed_requires_code(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    alarm = reg.get("alarm_control_panel.home")
    assert alarm is not None
    assert alarm.attributes["code_arm_required"] is True
    assert alarm.attributes["code_disarm_required"] is True


def test_alarm_discovery_emits_arm_modes(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    alarm = reg.get("alarm_control_panel.home")
    assert alarm is not None
    payload = export_discovery([alarm])[0]["payload"]

    assert "arm_night" in payload["supported_features"]
    assert "arm_vacation" in payload["supported_features"]
    assert payload["code_arm_required"] is True
    assert payload["code_disarm_required"] is True


def test_alarm_arm_night_with_code(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("alarm_control_panel.home", "arm_night", {"code": "1234"})
    assert dev.state["state"] == "armed_night"


def test_alarm_arm_vacation_with_code(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("alarm_control_panel.home", "arm_vacation", {"code": "1234"})
    assert dev.state["state"] == "armed_vacation"


def test_alarm_arm_rejected_without_code(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("alarm_control_panel.home", "arm_away", {"code": "0000"})
    assert dev.state["state"] == "disarmed"  # unchanged
    assert dev.state["last_error"] == "invalid_code"


def test_alarm_disarm_with_code_clears_error(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    reg.apply_command("alarm_control_panel.home", "arm_away", {"code": "0000"})  # sets error
    dev = reg.apply_command("alarm_control_panel.home", "disarm", {"code": "1234"})
    assert dev.state["state"] == "disarmed"
    assert "last_error" not in dev.state


def test_alarm_trigger_bypasses_code(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()
    dev = reg.apply_command("alarm_control_panel.home", "trigger", {})
    assert dev.state["state"] == "triggered"
