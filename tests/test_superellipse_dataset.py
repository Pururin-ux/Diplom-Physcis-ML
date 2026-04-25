"""Minimal tests for deterministic superellipse pilot dataset generation."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("kwant")

from src import dataset as dataset_module


def _fake_superellipse_levels_and_site_count(a: float, b: float, n: float) -> tuple[np.ndarray, int]:
    """Deterministic stand-in for fast dataset tests."""
    base = 0.01 * a + 0.02 * b + 0.03 * n
    levels = np.array([base, base + 0.4, base + 0.9, base + 1.5], dtype=float)
    n_sites = int(round(a * b))
    return levels, n_sites


def test_generate_superellipse_pilot_dataset_structure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pilot dataset has expected count, keys, and aligned array lengths."""
    monkeypatch.setattr(
        dataset_module,
        "_superellipse_levels_and_site_count",
        _fake_superellipse_levels_and_site_count,
    )

    data = dataset_module.generate_superellipse_pilot_dataset()
    expected_n = 3 * 5 * 9
    expected_keys = {
        "a",
        "b",
        "aspect_ratio",
        "n",
        "N_sites",
        "E0",
        "E1",
        "E2",
        "E3",
        "dE1",
        "dE2",
        "dE3",
    }

    assert len(data["a"]) == expected_n
    assert set(data.keys()) == expected_keys

    lengths = [len(data[k]) for k in expected_keys]
    assert all(length == expected_n for length in lengths)


def test_generate_superellipse_pilot_dataset_energy_sanity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Generated energies are finite and sorted for all samples."""
    monkeypatch.setattr(
        dataset_module,
        "_superellipse_levels_and_site_count",
        _fake_superellipse_levels_and_site_count,
    )

    data = dataset_module.generate_superellipse_pilot_dataset()
    e0, e1, e2, e3 = data["E0"], data["E1"], data["E2"], data["E3"]

    assert np.all(np.isfinite(e0))
    assert np.all(np.isfinite(e1))
    assert np.all(np.isfinite(e2))
    assert np.all(np.isfinite(e3))
    assert np.all(e0 <= e1)
    assert np.all(e1 <= e2)
    assert np.all(e2 <= e3)


def test_generate_superellipse_pilot_dataset_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two runs with same fixed grid should match exactly."""
    monkeypatch.setattr(
        dataset_module,
        "_superellipse_levels_and_site_count",
        _fake_superellipse_levels_and_site_count,
    )

    d1 = dataset_module.generate_superellipse_pilot_dataset()
    d2 = dataset_module.generate_superellipse_pilot_dataset()

    for key in d1:
        assert np.array_equal(d1[key], d2[key])


def test_generate_superellipse_discrete_n_pilot_dataset_structure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Discrete-n pilot dataset has expected count, keys, and array lengths."""
    monkeypatch.setattr(
        dataset_module,
        "_superellipse_levels_and_site_count",
        _fake_superellipse_levels_and_site_count,
    )

    data = dataset_module.generate_superellipse_discrete_n_pilot_dataset()
    expected_n = 3 * 5 * 4
    expected_keys = {
        "a",
        "b",
        "aspect_ratio",
        "n",
        "N_sites",
        "E0",
        "E1",
        "E2",
        "E3",
        "dE1",
        "dE2",
        "dE3",
    }

    assert len(data["a"]) == expected_n
    assert set(data.keys()) == expected_keys
    assert all(len(data[k]) == expected_n for k in expected_keys)


def test_generate_superellipse_discrete_n_pilot_dataset_energy_sanity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Discrete-n pilot energies are finite and sorted for all samples."""
    monkeypatch.setattr(
        dataset_module,
        "_superellipse_levels_and_site_count",
        _fake_superellipse_levels_and_site_count,
    )

    data = dataset_module.generate_superellipse_discrete_n_pilot_dataset()
    e0, e1, e2, e3 = data["E0"], data["E1"], data["E2"], data["E3"]

    assert np.all(np.isfinite(e0))
    assert np.all(np.isfinite(e1))
    assert np.all(np.isfinite(e2))
    assert np.all(np.isfinite(e3))
    assert np.all(e0 <= e1)
    assert np.all(e1 <= e2)
    assert np.all(e2 <= e3)


def test_generate_superellipse_discrete_n_pilot_dataset_deterministic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Discrete-n pilot generation is deterministic across repeated calls."""
    monkeypatch.setattr(
        dataset_module,
        "_superellipse_levels_and_site_count",
        _fake_superellipse_levels_and_site_count,
    )

    d1 = dataset_module.generate_superellipse_discrete_n_pilot_dataset()
    d2 = dataset_module.generate_superellipse_discrete_n_pilot_dataset()

    for key in d1:
        assert np.array_equal(d1[key], d2[key])


def test_generate_superellipse_discrete_n_dense_dataset_structure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Dense discrete-n dataset has expected count, keys, and array lengths."""
    monkeypatch.setattr(
        dataset_module,
        "_superellipse_levels_and_site_count",
        _fake_superellipse_levels_and_site_count,
    )

    data = dataset_module.generate_superellipse_discrete_n_dense_dataset()
    expected_n = 5 * 7 * 4
    expected_keys = {
        "a",
        "b",
        "aspect_ratio",
        "n",
        "N_sites",
        "E0",
        "E1",
        "E2",
        "E3",
        "dE1",
        "dE2",
        "dE3",
    }

    assert len(data["a"]) == expected_n
    assert set(data.keys()) == expected_keys
    assert all(len(data[k]) == expected_n for k in expected_keys)


def test_generate_superellipse_discrete_n_dense_dataset_energy_sanity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Dense discrete-n energies are finite and sorted for all samples."""
    monkeypatch.setattr(
        dataset_module,
        "_superellipse_levels_and_site_count",
        _fake_superellipse_levels_and_site_count,
    )

    data = dataset_module.generate_superellipse_discrete_n_dense_dataset()
    e0, e1, e2, e3 = data["E0"], data["E1"], data["E2"], data["E3"]

    assert np.all(np.isfinite(e0))
    assert np.all(np.isfinite(e1))
    assert np.all(np.isfinite(e2))
    assert np.all(np.isfinite(e3))
    assert np.all(e0 <= e1)
    assert np.all(e1 <= e2)
    assert np.all(e2 <= e3)


def test_generate_superellipse_discrete_n_dense_dataset_deterministic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Dense discrete-n generation is deterministic across repeated calls."""
    monkeypatch.setattr(
        dataset_module,
        "_superellipse_levels_and_site_count",
        _fake_superellipse_levels_and_site_count,
    )

    d1 = dataset_module.generate_superellipse_discrete_n_dense_dataset()
    d2 = dataset_module.generate_superellipse_discrete_n_dense_dataset()

    for key in d1:
        assert np.array_equal(d1[key], d2[key])
