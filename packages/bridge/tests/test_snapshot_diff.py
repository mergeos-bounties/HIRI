from __future__ import annotations
from pathlib import Path
import pytest
from hiri_bridge.devices.registry import DeviceRegistry

def test_load_seed_and_append_never_shrinks(tmp_path: Path) -> None:
    reg = DeviceRegistry(path=tmp_path / "devices.json")
    reg.seed()

    initial_stats = reg.stats()
    initial_count = initial_stats["total"]

    reg.apply_command("light.living_main", "turn_on", {"brightness": 255})

    post_action_stats = reg.stats()
    post_action_count = post_action_stats["total"]

    assert post_action_count >= initial_count, f"Anti-truncate failure: count dropped from {initial_count} to {post_action_count}"

