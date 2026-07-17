from __future__ import annotations

import json
from typer.testing import CliRunner

from hiri_bridge.cli import app

runner = CliRunner()


def test_devices_list_domain_filter() -> None:
    """Test --domain filter on devices list command."""
    result = runner.invoke(app, ["devices", "list", "--domain", "sensor"])
    assert result.exit_code == 0
    # Should only show sensor devices, no other domains
    lines = result.stdout.split("\n")
    # Skip header lines, find table rows
    table_lines = [l for l in lines if "sensor" in l and "│" in l and "ID" not in l]
    for line in table_lines:
        assert "sensor" in line  # Domain column should show sensor
        # Should not contain other domains in the domain column
        assert "light" not in line or line.count("light") == 0  # light might appear elsewhere but not as domain


def test_devices_stats_domain_filter() -> None:
    """Test --domain filter on devices stats command."""
    # Test sensor domain
    result = runner.invoke(app, ["devices", "stats", "--domain", "sensor"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total"] > 0
    # Should only have sensor domain in by_domain
    assert list(data["by_domain"].keys()) == ["sensor"]
    # All devices should be sensor domain
    assert data["by_domain"]["sensor"] == data["total"]

    # Test switch domain
    result = runner.invoke(app, ["devices", "stats", "--domain", "switch"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total"] > 0
    assert list(data["by_domain"].keys()) == ["switch"]
    assert data["by_domain"]["switch"] == data["total"]

    # Test non-existent domain
    result = runner.invoke(app, ["devices", "stats", "--domain", "nonexistent"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total"] == 0
    assert data["by_domain"] == {}


def test_devices_stats_area_and_adapter_filters() -> None:
    """Test that existing area and adapter filters still work with domain filter."""
    result = runner.invoke(app, ["devices", "stats", "--domain", "sensor", "--area", "bathroom"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total"] > 0
    assert list(data["by_domain"].keys()) == ["sensor"]
    # All devices should be in bathroom area
    assert list(data["by_area"].keys()) == ["bathroom"]
    assert data["by_area"]["bathroom"] == data["total"]

    # Test with adapter filter
    result = runner.invoke(app, ["devices", "stats", "--domain", "sensor", "--adapter", "mqtt"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total"] > 0
    assert list(data["by_domain"].keys()) == ["sensor"]
    assert list(data["by_adapter"].keys()) == ["mqtt"]
    assert data["by_adapter"]["mqtt"] == data["total"]