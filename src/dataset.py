"""Dataset utilities for rectangular and superellipse quantum-dot energies."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.sparse.linalg import eigsh

from .geometry import build_superellipse_dot
from .kwant_solver import lowest_four_energies


DatasetDict = dict[str, np.ndarray]


def generate_rectangular_dot_dataset(
    lx_values: Iterable[int],
    ly_values: Iterable[int],
    save_path: str | Path | None = None,
) -> DatasetDict:
    """Generate a regular-grid dataset of the first four energies.

    Parameters
    ----------
    lx_values
        Iterable of integer `Lx` values (lattice units).
    ly_values
        Iterable of integer `Ly` values (lattice units).
    save_path
        Optional output path for `.npz` saving. If provided, the dataset is saved.

    Returns
    -------
    dict[str, numpy.ndarray]
        Flat arrays with one row per `(Lx, Ly)` pair:
        `Lx`, `Ly`, `E0`, `E1`, `E2`, `E3`.
    """
    lx_arr = np.asarray(list(lx_values), dtype=int)
    ly_arr = np.asarray(list(ly_values), dtype=int)

    if lx_arr.size == 0 or ly_arr.size == 0:
        raise ValueError("lx_values and ly_values must be non-empty.")

    n_points = lx_arr.size * ly_arr.size
    lx_flat = np.empty(n_points, dtype=int)
    ly_flat = np.empty(n_points, dtype=int)
    energies = np.empty((n_points, 4), dtype=float)

    idx = 0
    for lx in lx_arr:
        for ly in ly_arr:
            vals = lowest_four_energies(int(lx), int(ly))
            if vals.shape != (4,):
                raise ValueError(
                    f"Expected exactly 4 energies, got shape {vals.shape} for Lx={lx}, Ly={ly}."
                )
            lx_flat[idx] = int(lx)
            ly_flat[idx] = int(ly)
            energies[idx] = vals
            idx += 1

    dataset: DatasetDict = {
        "Lx": lx_flat,
        "Ly": ly_flat,
        "E0": energies[:, 0],
        "E1": energies[:, 1],
        "E2": energies[:, 2],
        "E3": energies[:, 3],
    }

    if save_path is not None:
        save_dataset_npz(dataset, save_path)

    return dataset


def save_dataset_npz(dataset: DatasetDict, path: str | Path) -> None:
    """Save a generated dataset dictionary to a NumPy `.npz` file."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(output_path, **dataset)


def _superellipse_levels_and_site_count(a: float, b: float, n: float) -> tuple[np.ndarray, int]:
    """Return first four energies and site count for one superellipse geometry."""
    fsys = build_superellipse_dot(a=a, b=b, n=n)
    n_sites = len(fsys.sites)
    h = fsys.hamiltonian_submatrix(sparse=True).tocsr()

    if n_sites < 5:
        vals = np.linalg.eigvalsh(h.toarray())[: min(4, n_sites)]
    else:
        vals, _ = eigsh(h, k=4, which="SA")
    vals = np.sort(np.asarray(vals, dtype=float))
    if vals.shape != (4,):
        raise ValueError(f"Expected exactly 4 energies, got shape {vals.shape}.")
    return vals, n_sites


def generate_superellipse_pilot_dataset(save_path: str | Path | None = None) -> DatasetDict:
    """Generate a deterministic superellipse pilot dataset on a fixed 3D grid.

    Grid definition (pilot-v2):
    - ``a`` in [24, 30, 36]
    - ``aspect_ratio = b/a`` in [0.67, 0.75, 0.83, 0.92, 1.0]
    - ``n`` in [1.2, 1.5, 1.8, 2.1, 2.4, 2.8, 3.2, 3.6, 4.0]

    For each sample, ``b`` is computed deterministically as ``b = aspect_ratio * a``.
    """
    a_values = np.array([24.0, 30.0, 36.0], dtype=float)
    ratio_values = np.array([0.67, 0.75, 0.83, 0.92, 1.0], dtype=float)
    n_values = np.array([1.2, 1.5, 1.8, 2.1, 2.4, 2.8, 3.2, 3.6, 4.0], dtype=float)

    n_points = a_values.size * ratio_values.size * n_values.size
    a_flat = np.empty(n_points, dtype=float)
    b_flat = np.empty(n_points, dtype=float)
    ratio_flat = np.empty(n_points, dtype=float)
    n_flat = np.empty(n_points, dtype=float)
    n_sites_flat = np.empty(n_points, dtype=int)
    energies = np.empty((n_points, 4), dtype=float)

    idx = 0
    for a in a_values:
        for ratio in ratio_values:
            b = ratio * a
            for n in n_values:
                vals, n_sites = _superellipse_levels_and_site_count(a=a, b=b, n=n)
                a_flat[idx] = a
                b_flat[idx] = b
                ratio_flat[idx] = ratio
                n_flat[idx] = n
                n_sites_flat[idx] = n_sites
                energies[idx] = vals
                idx += 1

    dE1 = energies[:, 1] - energies[:, 0]
    dE2 = energies[:, 2] - energies[:, 1]
    dE3 = energies[:, 3] - energies[:, 2]

    dataset: DatasetDict = {
        "a": a_flat,
        "b": b_flat,
        "aspect_ratio": ratio_flat,
        "n": n_flat,
        "N_sites": n_sites_flat,
        "E0": energies[:, 0],
        "E1": energies[:, 1],
        "E2": energies[:, 2],
        "E3": energies[:, 3],
        "dE1": dE1,
        "dE2": dE2,
        "dE3": dE3,
    }

    if save_path is not None:
        save_dataset_npz(dataset, save_path)
    return dataset


def generate_superellipse_discrete_n_pilot_dataset(
    save_path: str | Path | None = None,
) -> DatasetDict:
    """Generate a deterministic superellipse pilot dataset with discrete n values.

    Grid definition:
    - ``a`` in [24, 30, 36]
    - ``aspect_ratio = b/a`` in [0.67, 0.75, 0.83, 0.92, 1.0]
    - ``n`` in [1.2, 2.0, 3.0, 4.0]
    """
    a_values = np.array([24.0, 30.0, 36.0], dtype=float)
    ratio_values = np.array([0.67, 0.75, 0.83, 0.92, 1.0], dtype=float)
    n_values = np.array([1.2, 2.0, 3.0, 4.0], dtype=float)

    n_points = a_values.size * ratio_values.size * n_values.size
    a_flat = np.empty(n_points, dtype=float)
    b_flat = np.empty(n_points, dtype=float)
    ratio_flat = np.empty(n_points, dtype=float)
    n_flat = np.empty(n_points, dtype=float)
    n_sites_flat = np.empty(n_points, dtype=int)
    energies = np.empty((n_points, 4), dtype=float)

    idx = 0
    for a in a_values:
        for ratio in ratio_values:
            b = ratio * a
            for n in n_values:
                vals, n_sites = _superellipse_levels_and_site_count(a=a, b=b, n=n)
                a_flat[idx] = a
                b_flat[idx] = b
                ratio_flat[idx] = ratio
                n_flat[idx] = n
                n_sites_flat[idx] = n_sites
                energies[idx] = vals
                idx += 1

    dE1 = energies[:, 1] - energies[:, 0]
    dE2 = energies[:, 2] - energies[:, 1]
    dE3 = energies[:, 3] - energies[:, 2]

    dataset: DatasetDict = {
        "a": a_flat,
        "b": b_flat,
        "aspect_ratio": ratio_flat,
        "n": n_flat,
        "N_sites": n_sites_flat,
        "E0": energies[:, 0],
        "E1": energies[:, 1],
        "E2": energies[:, 2],
        "E3": energies[:, 3],
        "dE1": dE1,
        "dE2": dE2,
        "dE3": dE3,
    }

    if save_path is not None:
        save_dataset_npz(dataset, save_path)
    return dataset


def generate_superellipse_discrete_n_dense_dataset(
    save_path: str | Path | None = None,
) -> DatasetDict:
    """Generate a denser deterministic discrete-n superellipse dataset.

    Grid definition:
    - ``a`` in [24, 27, 30, 33, 36]
    - ``aspect_ratio = b/a`` in [0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0]
    - ``n`` in [1.2, 2.0, 3.0, 4.0]
    """
    a_values = np.array([24.0, 27.0, 30.0, 33.0, 36.0], dtype=float)
    ratio_values = np.array([0.67, 0.72, 0.78, 0.83, 0.89, 0.94, 1.0], dtype=float)
    n_values = np.array([1.2, 2.0, 3.0, 4.0], dtype=float)

    n_points = a_values.size * ratio_values.size * n_values.size
    a_flat = np.empty(n_points, dtype=float)
    b_flat = np.empty(n_points, dtype=float)
    ratio_flat = np.empty(n_points, dtype=float)
    n_flat = np.empty(n_points, dtype=float)
    n_sites_flat = np.empty(n_points, dtype=int)
    energies = np.empty((n_points, 4), dtype=float)

    idx = 0
    for a in a_values:
        for ratio in ratio_values:
            b = ratio * a
            for n in n_values:
                vals, n_sites = _superellipse_levels_and_site_count(a=a, b=b, n=n)
                a_flat[idx] = a
                b_flat[idx] = b
                ratio_flat[idx] = ratio
                n_flat[idx] = n
                n_sites_flat[idx] = n_sites
                energies[idx] = vals
                idx += 1

    dE1 = energies[:, 1] - energies[:, 0]
    dE2 = energies[:, 2] - energies[:, 1]
    dE3 = energies[:, 3] - energies[:, 2]

    dataset: DatasetDict = {
        "a": a_flat,
        "b": b_flat,
        "aspect_ratio": ratio_flat,
        "n": n_flat,
        "N_sites": n_sites_flat,
        "E0": energies[:, 0],
        "E1": energies[:, 1],
        "E2": energies[:, 2],
        "E3": energies[:, 3],
        "dE1": dE1,
        "dE2": dE2,
        "dE3": dE3,
    }

    if save_path is not None:
        save_dataset_npz(dataset, save_path)
    return dataset
