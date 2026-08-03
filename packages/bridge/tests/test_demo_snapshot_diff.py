from __future__ import annotations

from pathlib import Path

from hiri_bridge.devices.registry import DeviceRegistry


def test_seed_append_only_invariant(tmp_path: Path) -> None:
    """Pytest that loading seed + appends never shrinks device count (anti-truncate).

    This test enforces the append-only invariant for the registry seed() method.
    After calling seed() multiple times, the total device count must not decrease.
    """
    reg = DeviceRegistry(path=tmp_path / "devices.json")

    # Initial seed
    reg.seed()
    initial_count = reg.stats()["total"]
    assert initial_count >= 15

    # Append another seed (should not truncate)
    reg.seed()
    after_second_seed = reg.stats()["total"]
    assert after_second_seed >= initial_count, (
        f"Device count decreased after second seed: {initial_count} -> {after_second_seed}"
    )

    # Append once more to be sure
    reg.seed()
    after_third_seed = reg.stats()["total"]
    assert after_third_seed >= after_second_seed, (
        f"Device count decreased after third seed: {after_second_seed} -> {after_third_seed}"
    )
