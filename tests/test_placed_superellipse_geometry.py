"""Tests for placed (translated/rotated) superellipse domains and the generic solver."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("kwant")

from src.geometry import (
    build_superellipse_dot,
    build_superellipse_dot_placed,
    placed_superellipse_sites,
)
from src.kwant_solver import lowest_energies_of_system, shift_invert_consistency_error


def test_placed_default_matches_original_builder() -> None:
    """With zero offset and angle the placed builder reproduces the original site set."""
    fsys_orig = build_superellipse_dot(a=9.0, b=7.0, n=3.0)
    fsys_placed = build_superellipse_dot_placed(a=9.0, b=7.0, n=3.0)
    sites_orig = sorted(site.tag for site in fsys_orig.sites)
    sites_placed = sorted(site.tag for site in fsys_placed.sites)
    assert sites_orig == sites_placed


def test_integer_translation_is_a_lattice_symmetry() -> None:
    """Shifting the center by whole lattice vectors translates the site set rigidly."""
    base = placed_superellipse_sites(a=8.0, b=8.0, n=4.0)
    shifted = placed_superellipse_sites(a=8.0, b=8.0, n=4.0, x0=3.0, y0=-2.0)
    assert sorted((x - 3, y + 2) for x, y in shifted) == base


def test_rotation_by_90_degrees_is_a_lattice_symmetry() -> None:
    """theta=90 deg maps the isotropic discrete domain onto itself."""
    base = set(placed_superellipse_sites(a=8.0, b=8.0, n=1.2))
    rot = set(placed_superellipse_sites(a=8.0, b=8.0, n=1.2, theta_deg=90.0))
    assert base == rot


def test_site_centered_isotropic_domain_has_exact_c4_symmetry() -> None:
    """The site-centered isotropic domain is invariant under (x, y) -> (-y, x)."""
    base = set(placed_superellipse_sites(a=8.0, b=8.0, n=4.0))
    assert {(-y, x) for x, y in base} == base


def test_bond_centered_placement_changes_site_set() -> None:
    """A half-step offset produces a genuinely different discrete domain."""
    base = set(placed_superellipse_sites(a=8.0, b=8.0, n=4.0))
    offset = set(placed_superellipse_sites(a=8.0, b=8.0, n=4.0, x0=0.5))
    assert base != offset


def test_shift_invert_matches_sa_on_moderate_system() -> None:
    """Shift-invert around the band bottom agrees with which='SA' to solver accuracy."""
    fsys = build_superellipse_dot_placed(a=12.0, b=10.0, n=2.0)
    assert shift_invert_consistency_error(fsys, k=4) < 1e-9


def test_lowest_energies_above_band_bottom() -> None:
    """All returned levels must lie above the infinite-lattice band bottom -4."""
    fsys = build_superellipse_dot_placed(a=10.0, b=10.0, n=4.0, x0=0.5, y0=0.25)
    vals = lowest_energies_of_system(fsys, k=4)
    assert np.all(vals > -4.0)
    assert np.all(np.diff(vals) >= -1e-12)
