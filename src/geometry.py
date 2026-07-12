"""Kwant geometry builders for rectangular and superellipse quantum dots."""

from __future__ import annotations

import math

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


def in_placed_superellipse(
    x: float,
    y: float,
    a: float,
    b: float,
    n: float,
    x0: float = 0.0,
    y0: float = 0.0,
    theta_deg: float = 0.0,
) -> bool:
    """Return whether lattice point ``(x, y)`` lies in a placed superellipse.

    The continuum superellipse ``|u/a|**n + |v/b|**n <= 1`` is placed with its
    center at ``(x0, y0)`` and rotated by ``theta_deg`` degrees relative to the
    lattice axes. A lattice point belongs to the discrete domain when its
    coordinates, translated by ``-(x0, y0)`` and rotated by ``-theta_deg``,
    satisfy the superellipse inequality.

    This is the single geometric predicate shared by the placed builder and by
    site-set diagnostics (site counts, symmetric differences), so that all
    placement studies use exactly one definition of the discrete domain.
    """
    th = math.radians(theta_deg)
    dx = x - x0
    dy = y - y0
    u = math.cos(th) * dx + math.sin(th) * dy
    v = -math.sin(th) * dx + math.cos(th) * dy
    return abs(u / a) ** n + abs(v / b) ** n <= 1.0


def placed_superellipse_sites(
    a: float,
    b: float,
    n: float,
    x0: float = 0.0,
    y0: float = 0.0,
    theta_deg: float = 0.0,
) -> list[tuple[int, int]]:
    """Return sorted integer lattice sites of a placed superellipse domain.

    Parameters mirror :func:`in_placed_superellipse`. The scan window is chosen
    from the circumscribed radius ``hypot(a, b)`` plus the center offset, so it
    is valid for any rotation angle.
    """
    if a <= 0 or b <= 0 or n <= 0:
        raise ValueError("a, b, and n must be positive.")
    radius = int(math.ceil(math.hypot(a, b))) + 2
    cx = int(round(x0))
    cy = int(round(y0))
    sites = [
        (x, y)
        for x in range(cx - radius, cx + radius + 1)
        for y in range(cy - radius, cy + radius + 1)
        if in_placed_superellipse(x, y, a, b, n, x0, y0, theta_deg)
    ]
    sites.sort()
    return sites


def build_superellipse_dot_placed(
    a: float,
    b: float,
    n: float,
    x0: float = 0.0,
    y0: float = 0.0,
    theta_deg: float = 0.0,
) -> kwant.system.FiniteSystem:
    """Build a finalized closed superellipse dot with explicit lattice placement.

    Same tight-binding convention as :func:`build_superellipse_dot` (zero onsite
    potential, nearest-neighbor hopping ``-1``, hard-wall open boundary), but the
    continuum shape is translated by ``(x0, y0)`` and rotated by ``theta_deg``
    degrees relative to the square lattice before discretization. With
    ``x0 = y0 = theta_deg = 0`` the realized site set is identical to
    :func:`build_superellipse_dot`.
    """
    sites = placed_superellipse_sites(a, b, n, x0, y0, theta_deg)
    if not sites:
        raise ValueError("Placed superellipse contains no lattice sites.")

    lat = kwant.lattice.square(a=1, norbs=1)
    syst = Builder()
    for x, y in sites:
        syst[lat(x, y)] = 0
    site_set = set(sites)
    for x, y in sites:
        if (x + 1, y) in site_set:
            syst[lat(x, y), lat(x + 1, y)] = -1
        if (x, y + 1) in site_set:
            syst[lat(x, y), lat(x, y + 1)] = -1
    return syst.finalized()
