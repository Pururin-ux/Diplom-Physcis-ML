"""Minimal dataset generation for rectangular quantum-dot energies."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np

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
