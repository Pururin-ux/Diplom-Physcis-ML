"""Closed 2D rectangular quantum dot on a square tight-binding lattice (Kwant)."""

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
