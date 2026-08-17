from __future__ import annotations

from typer.testing import CliRunner

from hiri_bridge.cli import app

runner = CliRunner()


def test_devices_list_shows_all_by_default() -> None:
    """hiri-bridge devices list shows all devices if no domain filter is provided."""
    result = runner.invoke(app, ["devices", "list"])
    assert result.exit_code == 0
    assert "HIRI devices" in result.stdout
    assert "light" in result.stdout
    assert "sensor" in result.stdout
    assert "switch" in result.stdout


def test_devices_list_filter_domain_sensor() -> None:
    """hiri-bridge devices list --domain sensor should only show sensor devices."""
    result = runner.invoke(app, ["devices", "list", "--domain", "sensor"])
    assert result.exit_code == 0
    assert "HIRI devices" in result.stdout
    assert "sensor" in result.stdout
    
    # We should not see other domains like light or switch
    # NOTE: "light" might appear as a substring of something else, but let's check for standalone domain column
    lines = result.stdout.split("\n")
    data_lines = [line for line in lines if "│" in line and not line.startswith("├") and not line.startswith("┌") and not line.startswith("└")]
    
    # Skip the header row
    if len(data_lines) > 1:
        for row in data_lines[1:]:
            parts = [p.strip() for p in row.split("│")]
            if len(parts) > 2:
                domain = parts[2]
                if domain:  # Some rows might be empty framing
                    assert domain == "sensor", f"Expected domain 'sensor', found '{domain}' in row: {row}"


def test_devices_list_filter_domain_light() -> None:
    """hiri-bridge devices list --domain light should only show light devices."""
    result = runner.invoke(app, ["devices", "list", "--domain", "light"])
    assert result.exit_code == 0
    assert "HIRI devices" in result.stdout
    
    lines = result.stdout.split("\n")
    data_lines = [line for line in lines if "│" in line and not line.startswith("├") and not line.startswith("┌") and not line.startswith("└")]
    
    if len(data_lines) > 1:
        for row in data_lines[1:]:
            parts = [p.strip() for p in row.split("│")]
            if len(parts) > 2:
                domain = parts[2]
                if domain:
                    assert domain == "light", f"Expected domain 'light', found '{domain}' in row: {row}"
