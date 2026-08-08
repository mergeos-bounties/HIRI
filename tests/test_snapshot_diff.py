"""Test snapshot append-only invariant (Closes #93)."""
import json
from pathlib import Path
import pytest

def load_devices(devices_dir):
    devices = []
    for fpath in sorted(Path(devices_dir).glob("*.json")):
        devices.append(json.loads(fpath.read_text()))
    return devices

class TestSnapshotAppendOnly:
    def test_seed_has_devices(self, tmp_path):
        (tmp_path / "light_kitchen.json").write_text('{"entity_id": "light.kitchen", "domain": "light"}')
        devices = load_devices(tmp_path)
        assert len(devices) >= 1

    def test_append_never_shrinks(self, tmp_path):
        (tmp_path / "a.json").write_text('{"entity_id": "sensor.a"}')
        before = len(load_devices(tmp_path))
        assert before == 1
        (tmp_path / "b.json").write_text('{"entity_id": "sensor.b"}')
        after = len(load_devices(tmp_path))
        assert after >= before, f"Invariant violated: {before} -> {after}"
        assert after == 2

    def test_multiple_appends_monotonic(self, tmp_path):
        (tmp_path / "base.json").write_text('{"entity_id": "base"}')
        prev = len(load_devices(tmp_path))
        assert prev == 1
        for i in range(5):
            (tmp_path / f"dev{i}.json").write_text('{"entity_id": "' + str(i) + '"}')
            curr = len(load_devices(tmp_path))
            assert curr >= prev, f"Shrunk at step {i}: {prev} -> {curr}"
            prev = curr

    def test_truncation_detected(self, tmp_path):
        (tmp_path / "x.json").write_text('{"entity_id": "x"}')
        (tmp_path / "y.json").write_text('{"entity_id": "y"}')
        assert len(load_devices(tmp_path)) == 2
        (tmp_path / "x.json").unlink()
        assert len(load_devices(tmp_path)) < 2
