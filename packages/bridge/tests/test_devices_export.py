from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path



def test_devices_export_writes_json(tmp_path: Path) -> None:
    """hiri-bridge devices export --out writes device registry snapshot."""
    out = tmp_path / "snapshot.json"
    result = subprocess.run(
        [sys.executable, "-m", "hiri_bridge.cli", "devices", "export", "--out", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"stdout={result.stdout} stderr={result.stderr}"
    assert out.exists(), f"Expected {out} to exist. stderr={result.stderr}"

    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) > 0, "Registry should contain seeded devices"

    # Check structure of first device
    d = data[0]
    for field in ("id", "name", "domain", "manufacturer", "model", "area", "online", "state", "adapter"):
        assert field in d, f"Device missing field: {field}"

    # Verify no tokens/secrets leaked
    text = out.read_text(encoding="utf-8").lower()
    assert "token" not in text or "code" not in text, "Snapshot should not contain tokens/codes"

    # Verify output mentions device count
    assert "devices=" in result.stdout and str(len(data)) in result.stdout


def test_devices_export_creates_parent_dirs(tmp_path: Path) -> None:
    """export --out creates parent directories if they don't exist."""
    out = tmp_path / "nested" / "deep" / "snapshot.json"
    assert not out.parent.exists()
    result = subprocess.run(
        [sys.executable, "-m", "hiri_bridge.cli", "devices", "export", "--out", str(out)],
        capture_output=True,
        text=True,
    )
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