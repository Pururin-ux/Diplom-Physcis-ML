"""Kwant geometry builders for rectangular and superellipse quantum dots."""

from __future__ import annotations

import kwant
from kwant.builder import Builder


def build_rectangular_dot(Lx: int, Ly: int) -> kwant.system.FiniteSystem:
    """Build a finalized closed rectangular dot parameterized only by ``Lx`` and ``Ly``.

    The model uses a square lattice with lattice constant 1, zero onsite potential,
    and nearest-neighbor hopping -1. Sites exist only for integer coordinates
    ``(x, y)`` with ``0 <= x < Lx`` and ``0 <= y < Ly``; missing neighbors at the
    boundary implement hard-wall confinement.

    Parameters
    ----------
    Lx
        Number of lattice sites along x (width), in lattice units.
    Ly
        Number of lattice sites along y (height), in lattice units.

    Returns
    -------
    kwant.system.FiniteSystem
        Finalized finite tight-binding system.
    """
    if Lx < 1 or Ly < 1:
        raise ValueError("Lx and Ly must be positive integers.")

    lat = kwant.lattice.square(a=1, norbs=1)

    def in_rectangle(pos: tuple[float, float]) -> bool:
        x, y = pos
        return 0 <= x < Lx and 0 <= y < Ly

    syst = Builder()
    syst[lat.shape(in_rectangle, (0, 0))] = 0
    syst[lat.neighbors()] = -1
    return syst.finalized()


def build_superellipse_dot(a: float, b: float, n: float) -> kwant.system.FiniteSystem:
    """Build a finalized closed superellipse dot centered at ``(0, 0)``.

    The shape is defined by
    ``|x / a|**n + |y / b|**n <= 1``
    on a square lattice with zero onsite potential and nearest-neighbor
    hopping ``-1``.

    Parameters
    ----------
    a
        Semi-axis scale along x (lattice units), must be positive.
    b
        Semi-axis scale along y (lattice units), must be positive.
    n
        Superellipse exponent, must be positive.

    Returns
    -------
    kwant.system.FiniteSystem
        Finalized finite tight-binding system.
    """
    if a <= 0 or b <= 0 or n <= 0:
        raise ValueError("a, b, and n must be positive.")

    lat = kwant.lattice.square(a=1, norbs=1)

    def in_superellipse(pos: tuple[float, float]) -> bool:
        x, y = pos
        return abs(x / a) ** n + abs(y / b) ** n <= 1.0

    syst = Builder()
    syst[lat.shape(in_superellipse, (0, 0))] = 0
    syst[lat.neighbors()] = -1
    return syst.finalized()
