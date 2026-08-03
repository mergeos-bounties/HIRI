from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from hiri_bridge.cli import filter_devices
from hiri_bridge.devices.registry import DeviceRegistry
from hiri_bridge.devices.types import Device


def _run_list(*args: str, data_dir: Path) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "HIRI_DATA_DIR": str(data_dir),
        "COLUMNS": "200",
        "TERM": "dumb",
    }
    return subprocess.run(
        [sys.executable, "-m", "hiri_bridge.cli", "devices", "list", *args],
        capture_output=True,
        text=True,
        env=env,
    )


def test_filter_devices_by_domain_case_insensitive() -> None:
    devices = [
        Device(id="sensor.a", name="A", domain="sensor"),
        Device(id="light.b", name="B", domain="light"),
        Device(id="sensor.c", name="C", domain="sensor"),
    ]
    rows = filter_devices(devices, domain="Sensor")
    assert [d.id for d in rows] == ["sensor.a", "sensor.c"]


def test_filter_devices_unknown_domain_empty() -> None:
    devices = [Device(id="light.a", name="A", domain="light")]
    assert filter_devices(devices, domain="vacuum") == []


def test_filter_devices_combines_domain_and_area() -> None:
    devices = [
        Device(id="sensor.farm", name="Farm", domain="sensor", area="farm"),
        Device(id="sensor.home", name="Home", domain="sensor", area="home"),
        Device(id="light.farm", name="Lamp", domain="light", area="farm"),
    ]
    rows = filter_devices(devices, domain="sensor", area="farm")
    assert [d.id for d in rows] == ["sensor.farm"]


def test_devices_list_domain_cli(tmp_path: Path) -> None:
    """hiri-bridge devices list --domain sensor filters registry (no tokens)."""
    data_dir = tmp_path / "data"
    reg = DeviceRegistry(path=data_dir / "devices.json")
    reg.seed()
    expected = [d.id for d in reg.list() if d.domain == "sensor"]
    assert expected, "seed should include sensors"

    result = _run_list("--domain", "sensor", data_dir=data_dir)
    assert result.returncode == 0, f"stdout={result.stdout} stderr={result.stderr}"
    assert "domain=sensor" in result.stdout
    assert f"shown={len(expected)}" in result.stdout
    # Rich may ellipsize long cells; match stable ID prefixes instead.
    assert "sensor.soil" in result.stdout
    assert "sensor.temp" in result.stdout
    assert "light.living" not in result.stdout
    assert "switch.pump" not in result.stdout
    # Alarm PIN lives in attributes — list must not print it
    assert "1234" not in result.stdout
    assert "access_token" not in result.stdout.lower()


def test_devices_list_domain_short_flag_and_case(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    DeviceRegistry(path=data_dir / "devices.json").seed()

    result = _run_list("-d", "Light", data_dir=data_dir)
    assert result.returncode == 0, f"stdout={result.stdout} stderr={result.stderr}"
    assert "domain=light" in result.stdout
    assert "light.living" in result.stdout
    assert "sensor.soil" not in result.stdout
    assert "shown=4" in result.stdout


def test_devices_list_domain_help_mentions_filter() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "hiri_bridge.cli", "devices", "list", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--domain" in result.stdout
    assert "domain" in result.stdout.lower()
