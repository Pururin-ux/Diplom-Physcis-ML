"""Article-G: signed, baseline-subtracted, branch-tracked shape response.

Implements the frozen protocol
`reports/article_g_signed_response/protocol.md` (commit 0fa6cbe):

- area-preserving (and legacy control) placed superellipse geometry;
- baseline and deformed low-energy solves with eigenvectors;
- union-site-space embedding and 2x2 doublet overlap/assignment;
- point-group classification and C4v symmetry-adapted baseline pairing;
- signed observables chi_minus, chi_plus, chi_center, chi_split, plus the
  legacy raw and sorted-baseline-corrected comparison metrics;
- reliability (subspace singular values, assignment margin, branch_status).

Kwant is the source of truth for the Hamiltonian; this module only assembles
placed domains and post-processes spectra.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.sparse import lil_matrix, csc_matrix
from scipy.sparse.linalg import eigsh

NEIGHBORS = ((1, 0), (0, 1))
SV_MIN_OK = 0.90
MARGIN_OK = 0.10
_HALF_TOL = 1e-9

# Frozen pilot grid constants (protocol.md section 5). Imported by the pilot
# script and asserted by tests so they cannot drift from the frozen protocol.
FROZEN_SHAPES = (2.0, 4.0)
FROZEN_SCALES = (24.3, 33.7, 48.2)
FROZEN_MODE_A_XI = (0.05, 0.10, 0.20, 0.40, 0.80)
FROZEN_MODE_B_DELTA = (0.001, 0.002, 0.004, 0.008)
FROZEN_PLACEMENT_GRID = 16
FROZEN_CONV_GRID = 32
FROZEN_THETA = 0.0
# Pre-registered 32x32 convergence points: (n, a0, mode, kind, value)
FROZEN_CONV_POINTS = (
    (2.0, 33.7, "area_preserving", "xi", 0.10),
    (2.0, 33.7, "area_preserving", "xi", 0.40),
    (4.0, 33.7, "area_preserving", "xi", 0.10),
    (4.0, 33.7, "area_preserving", "xi", 0.40),
    (4.0, 33.7, "area_preserving", "delta", 0.004),
)


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------

def area_factor(n: float) -> float:
    """Superellipse area factor f(n): analytic area = f(n) * a_x * a_y."""
    return 4.0 * math.gamma(1 + 1 / n) ** 2 / math.gamma(1 + 2 / n)


def semi_axes(a0: float, delta: float, mode: str) -> tuple[float, float]:
    """Return (a_x, a_y) for a deformation mode. r = 1 - delta.

    area_preserving:      a_x = a0/sqrt(r), a_y = a0*sqrt(r)  (a_x a_y = a0^2)
    legacy_fixed_major_axis: a_x = a0, a_y = a0*r  (control only, area ~ r)
    """
    r = 1.0 - delta
    if r <= 0.0:
        raise ValueError("delta must be < 1")
    if mode == "area_preserving":
        return a0 / math.sqrt(r), a0 * math.sqrt(r)
    if mode == "legacy_fixed_major_axis":
        return a0, a0 * r
    raise ValueError(f"unknown deformation mode: {mode}")


def placed_sites(
    a_x: float, a_y: float, n: float, x0: float, y0: float, theta_deg: float
) -> list[tuple[int, int]]:
    """Sorted integer lattice sites inside a placed superellipse.

    A point (x, y) is inside when, after translating by -(x0, y0) and rotating
    by -theta, it satisfies |u/a_x|^n + |v/a_y|^n <= 1.
    """
    th = math.radians(theta_deg)
    ct, st = math.cos(th), math.sin(th)
    radius = int(math.ceil(math.hypot(a_x, a_y))) + 2
    cx, cy = int(round(x0)), int(round(y0))
    out = []
    for x in range(cx - radius, cx + radius + 1):
        for y in range(cy - radius, cy + radius + 1):
            dx, dy = x - x0, y - y0
            u = ct * dx + st * dy
            v = -st * dx + ct * dy
            if abs(u / a_x) ** n + abs(v / a_y) ** n <= 1.0:
                out.append((x, y))
    out.sort()
    return out


# --------------------------------------------------------------------------
# solver
# --------------------------------------------------------------------------

@dataclass
class Spectrum:
    sites: list[tuple[int, int]]
    index: dict[tuple[int, int], int]
    energies: np.ndarray  # lowest k, ascending
    vectors: np.ndarray  # (N, k), columns aligned with energies


def solve_sites(sites: list[tuple[int, int]], k: int = 4) -> Spectrum:
    """Lowest-k closed tight-binding spectrum (onsite 0, hopping -1)."""
    index = {s: i for i, s in enumerate(sites)}
    n = len(sites)
    h = lil_matrix((n, n))
    for (x, y), i in index.items():
        for dx, dy in NEIGHBORS:
            j = index.get((x + dx, y + dy))
            if j is not None:
                h[i, j] = -1.0
                h[j, i] = -1.0
    hc = csc_matrix(h)
    if n < k + 2:
        dense = hc.toarray()
        vals, vecs = np.linalg.eigh(dense)
        return Spectrum(sites, index, vals[:k], vecs[:, :k])
    vals, vecs = eigsh(hc, k=k, sigma=-4.2, which="LM")
    order = np.argsort(vals)
    return Spectrum(sites, index, vals[order], vecs[:, order])


# --------------------------------------------------------------------------
# symmetry classification
# --------------------------------------------------------------------------

def _is_half_integer(value: float) -> bool:
    return abs(2.0 * value - round(2.0 * value)) < _HALF_TOL


def symmetry_class(x0: float, y0: float, theta_deg: float) -> str:
    """Point-group class of a theta=0 placement from the center offset."""
    if theta_deg != 0.0:
        return "C1_theta"
    cx = x0 - math.floor(x0)
    cy = y0 - math.floor(y0)
    has_mx = _is_half_integer(cx)
    has_my = _is_half_integer(cy)
    is_c4_center = has_mx and has_my and (
        (abs(cx - cy) < _HALF_TOL) or (abs((cx + cy) - round(cx + cy)) < _HALF_TOL)
    )
    # C4 centers on the square lattice are (0,0) and (0.5,0.5): cx == cy.
    if has_mx and has_my and abs(cx - cy) < _HALF_TOL:
        return "C4v"
    if has_mx and has_my:
        return "C2v"
    if has_mx or has_my:
        return "Cs_axis"
    if abs(cx - cy) < _HALF_TOL or abs((cx + cy) - round(cx + cy)) < _HALF_TOL:
        return "Cs_diag"
    return "C1"


# --------------------------------------------------------------------------
# embedding and overlaps
# --------------------------------------------------------------------------

def embed_pair(
    spec_a: Spectrum, cols_a: tuple[int, int],
    spec_b: Spectrum, cols_b: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    """Embed two 2-column vector sets into the union site space and renorm.

    Returns (Va, Vb), each (|union|, 2), columns renormalized to unit norm.
    """
    union = sorted(set(spec_a.sites) | set(spec_b.sites))
    uindex = {s: i for i, s in enumerate(union)}
    m = len(union)

    def build(spec: Spectrum, cols: tuple[int, int]) -> np.ndarray:
        out = np.zeros((m, 2), dtype=float)
        for local_tag, local_i in spec.index.items():
            ui = uindex[local_tag]
            out[ui, 0] = spec.vectors[local_i, cols[0]]
            out[ui, 1] = spec.vectors[local_i, cols[1]]
        for c in (0, 1):
            nrm = np.linalg.norm(out[:, c])
            if nrm > 0:
                out[:, c] /= nrm
        return out

    return build(spec_a, cols_a), build(spec_b, cols_b)


def mx_reflection_projected(spec: Spectrum, cols: tuple[int, int], x0: float) -> np.ndarray:
    """2x2 matrix of the M_x reflection (x -> 2*x0 - x) in the doublet subspace.

    Requires 2*x0 to be integer (true for C4v/C2v centers).
    """
    two_x0 = round(2.0 * x0)
    v = spec.vectors[:, [cols[0], cols[1]]]
    # permuted vector: (Pv)[site] = v[reflected site]
    pv = np.zeros_like(v)
    for (x, y), i in spec.index.items():
        rx = two_x0 - x
        j = spec.index.get((rx, y))
        if j is None:
            # reflection maps outside domain: not exactly symmetric -> abort
            return np.full((2, 2), np.nan)
        pv[i, :] = v[j, :]
    return v.T @ pv


# --------------------------------------------------------------------------
# doublet baseline pairing and tracking
# --------------------------------------------------------------------------

def baseline_pair(spec0: Spectrum, sym_class: str, x0: float):
    """Return baseline (-, +) as (E_minus, E_plus, cols, adapted_vectors).

    Non-degenerate classes: - = lower level (col 1), + = higher level (col 2),
    using the raw eigenvectors.
    C4v: build symmetry-adapted basis via M_x; - = M_x-odd (p_x), + = M_x-even
    (p_y). Returns the adapted 2-column vector block (in the spec0 site space).
    """
    e1, e2 = spec0.energies[1], spec0.energies[2]
    if sym_class != "C4v":
        block = spec0.vectors[:, [1, 2]].copy()
        return e1, e2, ("raw", block)
    r = mx_reflection_projected(spec0, (1, 2), x0)
    if np.any(np.isnan(r)):
        block = spec0.vectors[:, [1, 2]].copy()
        return e1, e2, ("raw_fallback", block)
    r = 0.5 * (r + r.T)
    w, u = np.linalg.eigh(r)  # eigenvalues near -1 (odd) and +1 (even)
    raw = spec0.vectors[:, [1, 2]]
    adapted = raw @ u  # columns are M_x eigenvectors
    # order columns: odd (eigenvalue -1) first = minus, even (+1) = plus
    order = np.argsort(w)  # ascending: -1 then +1
    adapted = adapted[:, order]
    return e1, e2, ("c4v_adapted", adapted)


def track_and_observe(
    spec0: Spectrum, specd: Spectrum, sym_class: str, x0: float, delta: float,
) -> dict:
    """Compute signed observables and reliability for one (baseline, deformed)."""
    e_minus0, e_plus0, (kind, base_block) = baseline_pair(spec0, sym_class, x0)

    # embed baseline pair block and deformed doublet (cols 1,2) into union
    union = sorted(set(spec0.sites) | set(specd.sites))
    uindex = {s: i for i, s in enumerate(union)}
    m = len(union)
    Vb = np.zeros((m, 2))
    for tag, li in spec0.index.items():
        Vb[uindex[tag], 0] = base_block[li, 0]
        Vb[uindex[tag], 1] = base_block[li, 1]
    Vd = np.zeros((m, 2))
    for tag, li in specd.index.items():
        Vd[uindex[tag], 0] = specd.vectors[li, 1]
        Vd[uindex[tag], 1] = specd.vectors[li, 2]
    for c in (0, 1):
        for V in (Vb, Vd):
            nrm = np.linalg.norm(V[:, c])
            if nrm > 0:
                V[:, c] /= nrm

    M = Vb.T @ Vd  # 2x2 real overlap of baseline (-,+) vs deformed (lo,hi)
    O = M ** 2
    sv = np.linalg.svd(M, compute_uv=False)
    sv_min, sv_max = float(sv.min()), float(sv.max())

    score_identity = O[0, 0] + O[1, 1]
    score_swap = O[0, 1] + O[1, 0]
    if score_identity >= score_swap:
        assign = (1, 2)  # minus->deformed lo (col1), plus->deformed hi (col2)
        best, second = score_identity, score_swap
    else:
        assign = (2, 1)
        best, second = score_swap, score_identity
    margin = best - second

    ed_lo, ed_hi = specd.energies[1], specd.energies[2]
    deformed_levels = {1: ed_lo, 2: ed_hi}
    etil_minus = deformed_levels[assign[0]]
    etil_plus = deformed_levels[assign[1]]

    s0_sorted = spec0.energies[2] - spec0.energies[1]
    sd_sorted = specd.energies[2] - specd.energies[1]

    chi_minus = (etil_minus - e_minus0) / delta
    chi_plus = (etil_plus - e_plus0) / delta
    chi_center = (
        0.5 * (etil_plus + etil_minus) - 0.5 * (e_plus0 + e_minus0)
    ) / delta
    chi_split = ((etil_plus - etil_minus) - (e_plus0 - e_minus0)) / delta

    legacy_raw = sd_sorted / delta
    sorted_bc = (sd_sorted - s0_sorted) / delta

    status = "OK" if (sv_min >= SV_MIN_OK and margin >= MARGIN_OK) else "AMBIGUOUS"

    return {
        "Eminus_0": e_minus0,
        "Eplus_0": e_plus0,
        "E0_0": spec0.energies[0],
        "E0_delta": specd.energies[0],
        "Eminus_delta": etil_minus,
        "Eplus_delta": etil_plus,
        "S0_sorted": s0_sorted,
        "Sdelta_sorted": sd_sorted,
        "legacy_raw_ratio": legacy_raw,
        "sorted_baseline_corrected_ratio": sorted_bc,
        "chi_minus": chi_minus,
        "chi_plus": chi_plus,
        "chi_center": chi_center,
        "chi_split": chi_split,
        "overlap_11": O[0, 0],
        "overlap_12": O[0, 1],
        "overlap_21": O[1, 0],
        "overlap_22": O[1, 1],
        "assignment_score_best": best,
        "assignment_score_second": second,
        "assignment_margin": margin,
        "subspace_sv_min": sv_min,
        "subspace_sv_max": sv_max,
        "branch_status": status,
        "baseline_pair_kind": kind,
    }
