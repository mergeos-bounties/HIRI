from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hiri_bridge.cli import device_export_snapshot
from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import Device


def _run_export(out: Path, data_dir: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "HIRI_DATA_DIR": str(data_dir)}
    return subprocess.run(
        [sys.executable, "-m", "hiri_bridge.cli", "devices", "export", "--out", str(out)],
        capture_output=True,
        text=True,
        env=env,
    )


def test_devices_export_writes_json(tmp_path: Path) -> None:
    """hiri-bridge devices export --out writes device registry snapshot."""
    data_dir = tmp_path / "data"
    out = tmp_path / "snapshot.json"
    result = _run_export(out, data_dir)
    assert result.returncode == 0, f"stdout={result.stdout} stderr={result.stderr}"
    assert out.exists(), f"Expected {out} to exist. stderr={result.stderr}"

    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) > 0, "Registry should contain seeded devices"

    d = data[0]
    for field in ("id", "name", "domain", "manufacturer", "model", "area", "online", "state", "adapter"):
        assert field in d, f"Device missing field: {field}"

    assert "devices=" in result.stdout and str(len(data)) in result.stdout


def test_devices_export_creates_parent_dirs(tmp_path: Path) -> None:
    """export --out creates parent directories if they don't exist."""
    data_dir = tmp_path / "data"
    out = tmp_path / "nested" / "deep" / "snapshot.json"
    assert not out.parent.exists()
    result = _run_export(out, data_dir)
    assert result.returncode == 0, f"stdout={result.stdout} stderr={result.stderr}"
    assert out.exists()


def test_devices_export_requires_out_option() -> None:
    """export command requires --out argument."""
    result = subprocess.run(
        [sys.executable, "-m", "hiri_bridge.cli", "devices", "export"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, "export without --out should fail"


def test_devices_export_strips_tokens_and_codes(tmp_path: Path) -> None:
    """Snapshot must not include tokens, secrets, or alarm PINs."""
    data_dir = tmp_path / "data"
    reg = DeviceRegistry(path=data_dir / "devices.json")
    reg.seed()
    alarm = reg.get("alarm_control_panel.home")
    assert alarm is not None
    assert alarm.attributes.get("code") == "1234"
    reg.upsert(
        Device(
            id="lock.secret_test",
            name="Secret lock",
            domain="lock",
            state={"state": "locked", "token": "leak-me"},
            attributes={
                "code": "9999",
                "access_token": "ha-token-xyz",
                "code_format": "^[0-9]{4}$",
                "password": "super-secret",
            },
        )
    )

    out = tmp_path / "safe.json"
    result = _run_export(out, data_dir)
    assert result.returncode == 0, f"stdout={result.stdout} stderr={result.stderr}"

    text = out.read_text(encoding="utf-8")
    data = json.loads(text)
    assert isinstance(data, list) and data

    assert "leak-me" not in text
    assert "ha-token-xyz" not in text
    assert "super-secret" not in text
    assert "9999" not in text
    assert "1234" not in text

    by_id = {row["id"]: row for row in data}
    secret_lock = by_id["lock.secret_test"]
    assert "token" not in secret_lock["state"]
    assert "code" not in secret_lock["attributes"]
    assert "access_token" not in secret_lock["attributes"]
    assert "password" not in secret_lock["attributes"]
    assert secret_lock["attributes"].get("code_format") == "^[0-9]{4}$"

    home_alarm = by_id["alarm_control_panel.home"]
    assert "code" not in home_alarm["attributes"]
    assert home_alarm["attributes"].get("code_arm_required") is True


def test_device_export_snapshot_unit() -> None:
    """Unit: device_export_snapshot redacts nested secret keys only."""
    dev = Device(
        id="sensor.demo",
        name="Demo",
        domain="sensor",
        state={"state": 1, "api_key": "k"},
        attributes={
            "unit_of_measurement": "%",
            "client_secret": "s",
            "nested": {"token": "t", "ok": 1},
            "items": [{"password": "x", "name": "a"}, "plain"],
        },
    )
    snap = device_export_snapshot(dev)
    assert snap["state"] == {"state": 1}
    assert snap["attributes"]["unit_of_measurement"] == "%"
    assert snap["attributes"]["nested"] == {"ok": 1}
    assert snap["attributes"]["items"] == [{"name": "a"}, "plain"]
    assert "api_key" not in snap["state"]
    assert "client_secret" not in snap["attributes"]
    assert "token" not in snap["attributes"]["nested"]
