"""Minimal tests for dataset generation and NPZ saving."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("kwant")

from src import dataset as dataset_module


def _fake_lowest_four_energies(lx: int, ly: int) -> np.ndarray:
    """Deterministic stand-in for fast dataset tests."""
    base = float(lx + ly)
    return np.array([base, base + 1.0, base + 2.0, base + 3.0], dtype=float)


def test_generate_rectangular_dot_dataset_grid_shape_and_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Small regular grid should produce expected sample count and fields."""
    monkeypatch.setattr(dataset_module, "lowest_four_energies", _fake_lowest_four_energies)

    lx_values = [10, 12]
    ly_values = [8, 9, 10]
    data = dataset_module.generate_rectangular_dot_dataset(lx_values, ly_values)

    expected_keys = {"Lx", "Ly", "E0", "E1", "E2", "E3"}
    assert set(data.keys()) == expected_keys

    expected_n = len(lx_values) * len(ly_values)
    assert len(data["Lx"]) == expected_n

    lengths = [len(data[key]) for key in ("Lx", "Ly", "E0", "E1", "E2", "E3")]
    assert all(length == expected_n for length in lengths)


def test_save_dataset_npz_writes_readable_file(tmp_path) -> None:
    """Saved NPZ should be readable with expected arrays."""
    dataset = {
        "Lx": np.array([10, 12], dtype=int),
        "Ly": np.array([8, 8], dtype=int),
        "E0": np.array([1.0, 2.0], dtype=float),
        "E1": np.array([2.0, 3.0], dtype=float),
        "E2": np.array([3.0, 4.0], dtype=float),
        "E3": np.array([4.0, 5.0], dtype=float),
    }
    out_path = tmp_path / "small_dataset.npz"

    dataset_module.save_dataset_npz(dataset, out_path)

    loaded = np.load(out_path)
    assert set(loaded.files) == {"Lx", "Ly", "E0", "E1", "E2", "E3"}
    for key, values in dataset.items():
        assert np.array_equal(loaded[key], values)


def test_superellipse_levels_and_site_count_returns_sorted_finite_four_levels() -> None:
    """Representative superellipse spectrum path should validate four sorted energies."""
    levels, n_sites = dataset_module._superellipse_levels_and_site_count(a=8.0, b=6.0, n=2.0)

    assert n_sites >= 5
    assert levels.shape == (4,)
    assert np.all(np.isfinite(levels))
    assert np.all(np.diff(levels) >= 0.0)
