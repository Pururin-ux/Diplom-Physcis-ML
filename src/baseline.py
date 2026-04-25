"""Analytical reference levels for the rectangular benchmark case."""

from __future__ import annotations

import numpy as np


def exact_rectangular_tb_levels(nx: int, ny: int, num_levels: int = 4, t: float = 1.0) -> np.ndarray:
    """Return the exact lowest levels for a discrete rectangular TB box.

    This uses the closed-form spectrum of a 2D nearest-neighbor tight-binding
    rectangle with open boundaries, zero onsite energy, and hopping ``-t``:

    ``E(m, n) = -2 t [cos(pi m / (nx + 1)) + cos(pi n / (ny + 1))]``.

    Parameters
    ----------
    nx, ny
        Number of lattice sites along x and y.
    num_levels
        Number of lowest energies to return.
    t
        Hopping magnitude (must be positive for the sign convention above).

    Returns
    -------
    numpy.ndarray
        Lowest ``num_levels`` energies sorted in nondecreasing order.
    """
    if nx < 1 or ny < 1:
        raise ValueError("nx and ny must be positive integers.")
    if num_levels < 1:
        raise ValueError("num_levels must be >= 1.")
    if t <= 0:
        raise ValueError("t must be positive.")

    mx = np.arange(1, nx + 1, dtype=float)
    my = np.arange(1, ny + 1, dtype=float)

    cos_x = np.cos(np.pi * mx / (nx + 1.0))
    cos_y = np.cos(np.pi * my / (ny + 1.0))
    levels = -2.0 * t * (cos_x[:, None] + cos_y[None, :])

    flat_sorted = np.sort(levels.ravel())
    return flat_sorted[: min(num_levels, flat_sorted.size)]


def continuum_box_levels(nx: int, ny: int, num_levels: int = 4, t: float = 1.0) -> np.ndarray:
    """Return a low-energy continuum approximation for the same rectangle.

    This is an approximation obtained from the small-wavevector expansion of
    the discrete TB spectrum (``cos k ≈ 1 - k^2 / 2``), giving:

    ``E(m, n) ≈ -4 t + t pi^2 [m^2/(nx+1)^2 + n^2/(ny+1)^2]``.

    It is generally better for larger ``nx, ny`` and lower modes, and is not an
    exact representation of the lattice spectrum.
    """
    if nx < 1 or ny < 1:
        raise ValueError("nx and ny must be positive integers.")
    if num_levels < 1:
        raise ValueError("num_levels must be >= 1.")
    if t <= 0:
        raise ValueError("t must be positive.")

    mx = np.arange(1, nx + 1, dtype=float)
    my = np.arange(1, ny + 1, dtype=float)

    term_x = (mx / (nx + 1.0)) ** 2
    term_y = (my / (ny + 1.0)) ** 2
    levels = -4.0 * t + t * np.pi**2 * (term_x[:, None] + term_y[None, :])

    flat_sorted = np.sort(levels.ravel())
    return flat_sorted[: min(num_levels, flat_sorted.size)]
