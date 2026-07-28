"""Tests for devices filter --domain CLI (Fixes #89)."""

from __future__ import annotations

import json

import pytest
from typer import Exit

from hiri_bridge.cli import devices_filter
from hiri_bridge.cli import _registry


class TestDevicesFilter:
    def test_filter_by_domain_light(self) -> None:
        reg = _registry()
        got = [d for d in reg.list() if d.domain == "light"]
        assert len(got) > 0
        assert all("light" in i.lower() for i in {d.id for d in got})

    def test_filter_by_domain_sensor(self) -> None:
        reg = _registry()
        got = [d for d in reg.list() if d.domain == "sensor"]
        assert len(got) > 0

    def test_filter_by_domain_subset_ok(self) -> None:
        reg = _registry()
        got = [d for d in reg.list() if d.domain == "water_heater"]
        for d in got:
            assert d.domain == "water_heater"

    def test_filter_sort_by_name(self) -> None:
        reg = _registry()
        got = [d for d in reg.list() if d.domain == "sensor"]
        got_sorted = sorted(got, key=lambda d: d.name.lower())
        assert len(got) == len(got_sorted)

    def test_filter_sort_by_id_desc(self) -> None:
        reg = _registry()
        got = [d for d in reg.list() if d.domain == "light"]
        got_sorted = sorted(got, key=lambda d: d.id, reverse=True)
        assert len(got) == len(got_sorted)

    def test_filter_sort_by_area(self) -> None:
        reg = _registry()
        got = [d for d in reg.list() if d.domain == "switch"]
        got_sorted = sorted(got, key=lambda d: str(getattr(d, "area", "") or ""))
        assert len(got) == len(got_sorted)

    def test_filter_limit(self) -> None:
        reg = _registry()
        got = [d for d in reg.list() if d.domain == "sensor"]
        lim = min(3, len(got))
        assert len(got[:lim]) == lim

    def test_filter_unknown_domain_exits(self, capsys) -> None:
        with pytest.raises(Exit) as exc:
            devices_filter(domain="nonexistent", sort_by="id", reverse=False, limit=0, json_out=False)
        assert exc.value.exit_code == 1
        out = capsys.readouterr()
        assert "unknown domain" in (out.out + out.err).lower()

    def test_filter_bad_sort_exits(self, capsys) -> None:
        with pytest.raises(Exit) as exc:
            devices_filter(domain="light", sort_by="foo", reverse=False, limit=0, json_out=False)
        assert exc.value.exit_code == 1
        out = capsys.readouterr()
        assert "unknown --sort" in (out.out + out.err).lower()

    def test_filter_domain_normalized(self, capsys) -> None:
        """Upper/mixed case domain is normalized and matched."""
        devices_filter(domain="SENSOR", sort_by="id", reverse=False, limit=2, json_out=True)
        out = capsys.readouterr()
        data = json.loads(out.out)
        assert data["domain"] == "sensor"
        assert data["count"] <= 2
        for d in data["devices"]:
            assert d["domain"] == "sensor"

    def test_filter_json_output_structure(self, capsys) -> None:
        devices_filter(domain="light", sort_by="id", reverse=False, limit=2, json_out=True)
        out = capsys.readouterr()
        data = json.loads(out.out)
        assert "domain" in data
        assert "count" in data
        assert "devices" in data
        assert isinstance(data["devices"], list)
        keys = set(data["devices"][0].keys()) if data["devices"] else set()
        for k in ("id", "name", "domain", "area", "adapter", "online", "state"):
            assert k in keys

    def test_filter_json_count_matches(self, capsys) -> None:
        devices_filter(domain="camera", sort_by="id", reverse=False, limit=0, json_out=True)
        out = capsys.readouterr()
        data = json.loads(out.out)
        assert data["count"] == len(data["devices"])
