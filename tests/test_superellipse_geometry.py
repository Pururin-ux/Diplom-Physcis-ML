"""Minimal geometry-only tests for the superellipse benchmark gate."""

from __future__ import annotations

import pytest

pytest.importorskip("kwant")

from src.geometry import build_superellipse_dot


def test_superellipse_builds_with_nonzero_finite_size() -> None:
    """A representative superellipse should build and contain sites."""
    fsys = build_superellipse_dot(a=8.0, b=6.0, n=2.0)
    n_sites = len(fsys.sites)
    assert n_sites > 0
    assert n_sites < 10_000


def test_superellipse_reproducible_for_same_parameters() -> None:
    """Building twice with same parameters should reproduce site set."""
    fsys_1 = build_superellipse_dot(a=9.0, b=7.0, n=3.0)
    fsys_2 = build_superellipse_dot(a=9.0, b=7.0, n=3.0)

    sites_1 = sorted(site.tag for site in fsys_1.sites)
    sites_2 = sorted(site.tag for site in fsys_2.sites)

    assert len(sites_1) == len(sites_2)
    assert sites_1 == sites_2
