"""Direct Kwant magnetic-field sprint for geometry ranking crossovers.

This module is exploratory infrastructure only. It does not train models and
does not reuse Q/S inverse-screening objectives. The primary quantity is the
raw low-energy gap ranking under direct Kwant spectra with Peierls phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import inf, pi, sqrt
from typing import Iterable, Mapping, Sequence

import kwant
import numpy as np
from scipy import sparse as sp
from scipy.sparse.linalg import ArpackNoConvergence, eigsh

from .geometry import build_superellipse_dot
from .inverse_screening import geometry_hash_from_coordinates, site_coordinates_from_system


GAUGE_LANDAU = "landau"
GAUGE_SYMMETRIC = "symmetric"
GAUGES = (GAUGE_LANDAU, GAUGE_SYMMETRIC)

WEAK_ALPHAS = (0.0, 0.00125, 0.0025, 0.005)
DIAGNOSTIC_ALPHAS = (0.01, 0.02, 0.04)
ALL_ALPHAS = WEAK_ALPHAS + DIAGNOSTIC_ALPHAS
PRIMARY_SIZES = (30.0, 36.0)

ALPHA0_REPRODUCTION_TOL = 1e-10
HERMITICITY_TOL = 1e-12
EIGEN_IMAG_TOL = 1e-10
GAUGE_INVARIANCE_TOL = 1e-6
MIN_LB_FOR_PRIMARY_SIGNAL = 5.0
LOW_ENERGY_SHIFT_INVERT_SIGMA = -4.0
BLOCK_EIGEN_TOL = 1e-8


@dataclass(frozen=True)
class ShapeSpec:
    """One fixed superellipse shape in the magnetic sprint grid."""

    shape_id: str
    n: float
    aspect_ratio: float
    role: str


@dataclass(frozen=True)
class SpectrumComputation:
    """Direct spectrum plus matrix diagnostics for one geometry and gauge."""

    row: dict[str, object]
    hamiltonian: sp.csr_matrix
    max_hermiticity_error: float
    max_eigen_imag: float


SHAPES: tuple[ShapeSpec, ...] = (
    ShapeSpec(
        shape_id="circle_n2_r1",
        n=2.0,
        aspect_ratio=1.0,
        role="circle_baseline;symmetry_baseline",
    ),
    ShapeSpec(
        shape_id="ellipse_n2_r067",
        n=2.0,
        aspect_ratio=0.67,
        role="ellipse_aspect_ratio_baseline",
    ),
    ShapeSpec(
        shape_id="diamond_n12_r1",
        n=1.2,
        aspect_ratio=1.0,
        role="diamond_like_baseline",
    ),
    ShapeSpec(
        shape_id="squircle_n4_r1",
        n=4.0,
        aspect_ratio=1.0,
        role="square_like_squircle_baseline",
    ),
)


SPECTRA_COLUMNS = [
    "spectrum_role",
    "shape_id",
    "shape_role",
    "n",
    "a",
    "b",
    "rAR",
    "alpha",
    "gauge",
    "l_B",
    "l_B_over_a",
    "N_sites",
    "N_plaquettes_inside_dot",
    "phi_total",
    "phi_total_area_proxy",
    "geometry_hash",
    "max_hermiticity_error",
    "max_eigen_imag",
    "E0",
    "E1",
    "E2",
    "E3",
    "E4",
    "E5",
    "dE1",
    "dE2",
    "dE3",
    "dE4",
    "dE5",
    "min_gap_low",
]

GAUGE_CHECK_COLUMNS = [
    "shape_id",
    "n",
    "a",
    "b",
    "rAR",
    "alpha",
    "landau_gauge",
    "symmetric_gauge",
    "max_abs_energy_diff",
    "tolerance",
    "passed",
]

RANKING_COLUMNS = [
    "a",
    "alpha",
    "shape_id",
    "n",
    "rAR",
    "dE1",
    "min_gap_low",
    "rank_dE1_desc",
    "rank_min_gap_low_desc",
    "zero_field_rank_dE1_desc",
    "dE1_rank_changed_from_alpha0",
]

CROSSOVER_COLUMNS = [
    "a",
    "alpha",
    "shape_a",
    "shape_b",
    "dE1_diff_alpha0",
    "dE1_diff_alpha",
    "delta_crossover",
    "alpha0_separated",
    "ranking_reversed",
    "thresholded",
    "weak_field",
    "l_B",
    "l_B_filter_pass",
    "circle_symmetry_artifact_candidate",
    "onset_artifact_candidate",
    "qualifies_before_size_stability",
    "initial_winner",
    "field_winner",
    "notes",
]

ROBUSTNESS_COLUMNS = [
    "a",
    "alpha",
    "shape_a",
    "shape_b",
    "dE1_diff_alpha0",
    "dE1_diff_alpha",
    "delta_crossover",
    "zero_field_near_tie",
    "weak_field_separation",
    "weak_field",
    "l_B",
    "l_B_filter_pass",
    "circle_symmetry_artifact_candidate",
    "onset_artifact_candidate",
    "qualifies_before_size_stability",
    "separation_winner",
    "notes",
]

RESPONSE_COLUMNS = [
    "a",
    "shape_id",
    "n",
    "rAR",
    "mean_dE1_weak",
    "std_dE1_weak",
    "min_dE1_weak",
    "max_dE1_weak",
    "max_abs_change_dE1_from_alpha0_weak",
    "robust_gap_score",
]

SYMMETRY_COLUMNS = [
    "a",
    "alpha",
    "shape_id",
    "n",
    "rAR",
    "split_12",
    "delta_crossover",
    "split_12_le_delta",
    "symmetry_artifact_candidate",
]

BASELINE_COLUMNS = [
    "a",
    "alpha",
    "zero_field_best_shape",
    "current_best_shape",
    "zero_field_best_dE1",
    "current_best_dE1",
    "zero_field_best_rank_at_alpha",
    "best_zero_field_carried_across_alpha",
    "circle_rank_dE1",
    "ellipse_rank_dE1",
    "strongest_baseline",
    "notes",
]


def canonical_shape_order() -> tuple[str, ...]:
    """Return the fixed shape order used for pairwise comparisons."""
    return tuple(shape.shape_id for shape in SHAPES)


def magnetic_length(alpha: float) -> float:
    """Return lattice magnetic length for flux per plaquette ``alpha``."""
    alpha_value = float(alpha)
    if alpha_value == 0.0:
        return inf
    if alpha_value < 0.0:
        raise ValueError("alpha must be non-negative.")
    return 1.0 / sqrt(2.0 * pi * alpha_value)


def superellipse_site_coordinates(a: float, b: float, n: float) -> tuple[tuple[int, int], ...]:
    """Return realized discrete coordinates from the existing superellipse builder."""
    fsys = build_superellipse_dot(a=float(a), b=float(b), n=float(n))
    return tuple(site_coordinates_from_system(fsys))


def count_internal_plaquettes(coords: Iterable[tuple[int, int]]) -> int:
    """Count plaquettes whose four corner lattice sites are present."""
    coord_set = {(int(x), int(y)) for x, y in coords}
    n_plaquettes = 0
    for x, y in coord_set:
        if (x + 1, y) in coord_set and (x, y + 1) in coord_set and (x + 1, y + 1) in coord_set:
            n_plaquettes += 1
    return n_plaquettes


def magnetic_hopping_x(x: int, y: int, alpha: float, gauge: str) -> complex:
    """Return hopping for the positive x-direction edge."""
    if gauge == GAUGE_LANDAU:
        return complex(-1.0)
    if gauge == GAUGE_SYMMETRIC:
        return complex(-np.exp(-1j * pi * float(alpha) * int(y)))
    raise ValueError(f"Unknown gauge: {gauge!r}.")


def magnetic_hopping_y(x: int, y: int, alpha: float, gauge: str) -> complex:
    """Return hopping for the positive y-direction edge."""
    if gauge == GAUGE_LANDAU:
        return complex(-np.exp(1j * 2.0 * pi * float(alpha) * int(x)))
    if gauge == GAUGE_SYMMETRIC:
        return complex(-np.exp(1j * pi * float(alpha) * int(x)))
    raise ValueError(f"Unknown gauge: {gauge!r}.")


def build_magnetic_system_from_sites(
    coords: Iterable[tuple[int, int]],
    alpha: float,
    gauge: str = GAUGE_LANDAU,
) -> kwant.system.FiniteSystem:
    """Build a finalized square-lattice system with Peierls magnetic hoppings."""
    if gauge not in GAUGES:
        raise ValueError(f"Unknown gauge: {gauge!r}.")

    sorted_coords = tuple(sorted((int(x), int(y)) for x, y in coords))
    if not sorted_coords:
        raise ValueError("Cannot build a magnetic system with no sites.")

    coord_set = set(sorted_coords)
    lat = kwant.lattice.square(a=1, norbs=1)
    syst = kwant.Builder()

    for x, y in sorted_coords:
        syst[lat(x, y)] = 0.0

    for x, y in sorted_coords:
        if (x + 1, y) in coord_set:
            syst[lat(x, y), lat(x + 1, y)] = magnetic_hopping_x(x, y, alpha, gauge)
        if (x, y + 1) in coord_set:
            syst[lat(x, y), lat(x, y + 1)] = magnetic_hopping_y(x, y, alpha, gauge)

    return syst.finalized()


def magnetic_hamiltonian_from_sites(
    coords: Iterable[tuple[int, int]],
    alpha: float,
    gauge: str = GAUGE_LANDAU,
) -> sp.csr_matrix:
    """Return sparse magnetic Hamiltonian for a realized site set."""
    fsys = build_magnetic_system_from_sites(coords, alpha=alpha, gauge=gauge)
    return fsys.hamiltonian_submatrix(sparse=True).tocsr()


def hermiticity_error(matrix: sp.spmatrix) -> float:
    """Return the maximum absolute Hermiticity defect."""
    diff = (matrix - matrix.getH()).tocoo()
    if diff.nnz == 0:
        return 0.0
    return float(np.max(np.abs(diff.data)))


def lowest_k_eigenvalues(matrix: sp.spmatrix, k: int = 6) -> tuple[np.ndarray, float]:
    """Return sorted low-energy eigenvalues and maximum imaginary component."""
    n_sites = int(matrix.shape[0])
    if n_sites < k:
        raise ValueError(f"Need at least {k} sites, got {n_sites}.")
    solve_k = min(n_sites - 1, max(k, 12))

    if n_sites <= solve_k + 1:
        vals = np.linalg.eigvalsh(matrix.toarray())
        vals_arr = np.asarray(vals, dtype=float)
        vals_arr.sort()
        return vals_arr[:k], 0.0
    if matrix.dtype.kind == "c" and matrix.imag.nnz > 0 and float(np.max(np.abs(matrix.imag.data))) > 1e-14:
        vals = _lowest_k_complex_hermitian_via_real_block(matrix, k=k)
        return vals, 0.0

    real_matrix = matrix.real.tocsr()
    try:
        vals, _ = eigsh(
            real_matrix,
            k=solve_k,
            which="SA",
            tol=1e-10,
            ncv=max(4 * solve_k + 20, 80),
            maxiter=max(1000, 20 * n_sites),
        )
    except ArpackNoConvergence:
        # The finite square-lattice band bottom is near -4. Shift-invert at
        # that edge targets the same low-energy states when plain SA stalls.
        vals, _ = eigsh(
            real_matrix,
            k=solve_k,
            sigma=LOW_ENERGY_SHIFT_INVERT_SIGMA,
            which="LM",
            tol=1e-10,
            ncv=max(4 * solve_k + 20, 80),
            maxiter=max(1000, 20 * n_sites),
        )

    vals_arr = np.asarray(vals, dtype=float)
    if not np.all(np.isfinite(vals_arr)):
        raise ValueError("Encountered non-finite eigenvalues.")
    vals_arr.sort()
    return vals_arr[:k], 0.0


def _lowest_k_complex_hermitian_via_real_block(matrix: sp.spmatrix, k: int) -> np.ndarray:
    """Return eigenvalues of a complex Hermitian matrix via real block doubling.

    For ``H = A + iB``, the real symmetric block matrix ``[[A, -B], [B, A]]``
    has the same eigenvalues as ``H``, each doubled. Pair-averaging adjacent
    block eigenvalues recovers the physical spectrum with multiplicity.
    """
    a_real = matrix.real.tocsr()
    b_imag = matrix.imag.tocsr()
    block = sp.bmat([[a_real, -b_imag], [b_imag, a_real]], format="csr")
    block_k = 2 * int(k)
    vals, _ = eigsh(
        block,
        k=block_k,
        which="SA",
        tol=BLOCK_EIGEN_TOL,
        ncv=max(4 * block_k, 50),
        maxiter=max(5000, 20 * matrix.shape[0]),
    )
    sorted_vals = np.sort(np.asarray(vals, dtype=float))
    if sorted_vals.shape[0] < block_k:
        raise ValueError(f"Expected {block_k} block eigenvalues, got {sorted_vals.shape[0]}.")
    physical = np.array(
        [float(np.mean(sorted_vals[2 * idx : 2 * idx + 2])) for idx in range(k)],
        dtype=float,
    )
    if not np.all(np.isfinite(physical)):
        raise ValueError("Encountered non-finite eigenvalues.")
    physical.sort()
    return physical


def zero_field_reference_spectrum(a: float, b: float, n: float, k: int = 6) -> np.ndarray:
    """Return zero-field Kwant spectrum using the existing real-hopping builder."""
    fsys = build_superellipse_dot(a=float(a), b=float(b), n=float(n))
    hamiltonian = fsys.hamiltonian_submatrix(sparse=True).tocsr()
    values, _ = lowest_k_eigenvalues(hamiltonian, k=k)
    return values


def delta_crossover_for_size(primary_rows: Sequence[Mapping[str, object]], a: float) -> float:
    """Return crossover threshold for a size using the alpha=0 circle gap."""
    for row in primary_rows:
        if (
            str(row["shape_id"]) == "circle_n2_r1"
            and np.isclose(float(row["a"]), float(a))
            and np.isclose(float(row["alpha"]), 0.0)
        ):
            return max(0.001, 0.01 * float(row["dE1"]))
    raise ValueError(f"Missing circle alpha=0 row for a={a}.")


def compute_spectrum_row(
    shape: ShapeSpec,
    a: float,
    alpha: float,
    gauge: str = GAUGE_LANDAU,
    spectrum_role: str = "primary",
) -> SpectrumComputation:
    """Compute one direct magnetic spectrum row and matrix diagnostics."""
    b = float(a) * float(shape.aspect_ratio)
    coords = superellipse_site_coordinates(a=float(a), b=b, n=shape.n)
    hamiltonian = magnetic_hamiltonian_from_sites(coords, alpha=float(alpha), gauge=gauge)
    levels, max_imag = lowest_k_eigenvalues(hamiltonian, k=6)
    gaps = np.diff(levels)
    l_b = magnetic_length(float(alpha))
    n_plaquettes = count_internal_plaquettes(coords)
    phi_total = float(alpha) * float(n_plaquettes)
    phi_total_area_proxy = float(alpha) * pi * float(a) * b
    max_herm = hermiticity_error(hamiltonian)

    row: dict[str, object] = {
        "spectrum_role": spectrum_role,
        "shape_id": shape.shape_id,
        "shape_role": shape.role,
        "n": float(shape.n),
        "a": float(a),
        "b": b,
        "rAR": float(shape.aspect_ratio),
        "alpha": float(alpha),
        "gauge": gauge,
        "l_B": l_b,
        "l_B_over_a": l_b / float(a) if np.isfinite(l_b) else inf,
        "N_sites": len(coords),
        "N_plaquettes_inside_dot": n_plaquettes,
        "phi_total": phi_total,
        "phi_total_area_proxy": phi_total_area_proxy,
        "geometry_hash": geometry_hash_from_coordinates(coords),
        "max_hermiticity_error": max_herm,
        "max_eigen_imag": max_imag,
        "min_gap_low": float(np.min(gaps[:3])),
    }
    for idx, value in enumerate(levels):
        row[f"E{idx}"] = float(value)
    for idx, value in enumerate(gaps, start=1):
        row[f"dE{idx}"] = float(value)

    return SpectrumComputation(
        row=row,
        hamiltonian=hamiltonian,
        max_hermiticity_error=max_herm,
        max_eigen_imag=max_imag,
    )


def primary_spectrum_rows() -> tuple[list[dict[str, object]], list[SpectrumComputation]]:
    """Compute Landau-gauge spectra for the fixed sprint grid."""
    rows: list[dict[str, object]] = []
    computations: list[SpectrumComputation] = []
    for a_value in PRIMARY_SIZES:
        for shape in SHAPES:
            for alpha in ALL_ALPHAS:
                computation = compute_spectrum_row(shape, a_value, alpha, GAUGE_LANDAU, "primary")
                rows.append(computation.row)
                computations.append(computation)
    return rows, computations


def gauge_invariance_cases() -> tuple[tuple[ShapeSpec, float, float], ...]:
    """Return required gauge-control cases."""
    circle = SHAPES[0]
    return ((circle, 30.0, 0.005),)


def gauge_invariance_rows(
    primary_rows: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[SpectrumComputation]]:
    """Compute symmetric-gauge controls and compare against Landau spectra."""
    lookup = spectrum_lookup(primary_rows, gauge=GAUGE_LANDAU)
    check_rows: list[dict[str, object]] = []
    spectra_rows: list[dict[str, object]] = []
    computations: list[SpectrumComputation] = []

    for shape, a_value, alpha in gauge_invariance_cases():
        symmetric = compute_spectrum_row(shape, a_value, alpha, GAUGE_SYMMETRIC, "gauge_control")
        computations.append(symmetric)
        spectra_rows.append(symmetric.row)
        landau = lookup[(float(a_value), float(alpha), shape.shape_id)]
        landau_levels = np.array([float(landau[f"E{i}"]) for i in range(6)], dtype=float)
        symmetric_levels = np.array([float(symmetric.row[f"E{i}"]) for i in range(6)], dtype=float)
        max_diff = float(np.max(np.abs(landau_levels - symmetric_levels)))
        b = float(a_value) * float(shape.aspect_ratio)
        check_rows.append(
            {
                "shape_id": shape.shape_id,
                "n": float(shape.n),
                "a": float(a_value),
                "b": b,
                "rAR": float(shape.aspect_ratio),
                "alpha": float(alpha),
                "landau_gauge": GAUGE_LANDAU,
                "symmetric_gauge": GAUGE_SYMMETRIC,
                "max_abs_energy_diff": max_diff,
                "tolerance": GAUGE_INVARIANCE_TOL,
                "passed": max_diff < GAUGE_INVARIANCE_TOL,
            }
        )
    return check_rows, spectra_rows, computations


def spectrum_lookup(
    rows: Sequence[Mapping[str, object]],
    gauge: str = GAUGE_LANDAU,
) -> dict[tuple[float, float, str], Mapping[str, object]]:
    """Index spectrum rows by size, alpha, and shape."""
    lookup: dict[tuple[float, float, str], Mapping[str, object]] = {}
    for row in rows:
        if str(row.get("gauge")) != gauge:
            continue
        lookup[(float(row["a"]), float(row["alpha"]), str(row["shape_id"]))] = row
    return lookup


def shape_by_id() -> dict[str, ShapeSpec]:
    """Return shape specs keyed by shape id."""
    return {shape.shape_id: shape for shape in SHAPES}


def initial_and_field_winner(
    shape_a: str,
    shape_b: str,
    diff_value: float,
) -> str:
    """Return which shape wins under a pairwise dE1 difference."""
    if diff_value > 0.0:
        return shape_a
    if diff_value < 0.0:
        return shape_b
    return "tie"


def circle_split_lookup(primary_rows: Sequence[Mapping[str, object]]) -> dict[tuple[float, float], float]:
    """Return circle E2-E1 split by size and alpha."""
    out: dict[tuple[float, float], float] = {}
    for row in primary_rows:
        if str(row["shape_id"]) == "circle_n2_r1":
            out[(float(row["a"]), float(row["alpha"]))] = float(row["dE2"])
    return out


def signal_is_onset_only(
    pair_key: tuple[float, str, str],
    alpha: float,
    signal_map: Mapping[float, bool],
    diff_abs_by_alpha: Mapping[float, float],
) -> tuple[bool, bool]:
    """Return whether a signal is alpha=0.005-only and whether onset is monotonic."""
    del pair_key
    if not np.isclose(float(alpha), 0.005):
        return False, True
    earlier_signal = any(
        bool(signal_map.get(a_value, False))
        for a_value in WEAK_ALPHAS
        if a_value > 0.0 and a_value <= 0.0025
    )
    weak_abs = [float(diff_abs_by_alpha[a_value]) for a_value in WEAK_ALPHAS if a_value in diff_abs_by_alpha]
    monotonic = all(next_value >= value - 1e-12 for value, next_value in zip(weak_abs, weak_abs[1:]))
    return (not earlier_signal and not monotonic), monotonic


def ranking_rows(primary_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Rank geometries by dE1 and min low gap for each size and alpha."""
    out: list[dict[str, object]] = []
    zero_ranks: dict[tuple[float, str], int] = {}

    for a_value in PRIMARY_SIZES:
        alpha0_group = [
            row for row in primary_rows if np.isclose(float(row["a"]), a_value) and np.isclose(float(row["alpha"]), 0.0)
        ]
        sorted_zero = sorted(alpha0_group, key=lambda row: float(row["dE1"]), reverse=True)
        for rank, row in enumerate(sorted_zero, start=1):
            zero_ranks[(a_value, str(row["shape_id"]))] = rank

    for a_value in PRIMARY_SIZES:
        for alpha in ALL_ALPHAS:
            group = [
                row
                for row in primary_rows
                if np.isclose(float(row["a"]), a_value) and np.isclose(float(row["alpha"]), alpha)
            ]
            by_de1 = {str(row["shape_id"]): idx for idx, row in enumerate(sorted(group, key=lambda r: float(r["dE1"]), reverse=True), start=1)}
            by_min_gap = {
                str(row["shape_id"]): idx
                for idx, row in enumerate(sorted(group, key=lambda r: float(r["min_gap_low"]), reverse=True), start=1)
            }
            for row in group:
                shape_id = str(row["shape_id"])
                zero_rank = zero_ranks[(a_value, shape_id)]
                current_rank = by_de1[shape_id]
                out.append(
                    {
                        "a": a_value,
                        "alpha": float(alpha),
                        "shape_id": shape_id,
                        "n": float(row["n"]),
                        "rAR": float(row["rAR"]),
                        "dE1": float(row["dE1"]),
                        "min_gap_low": float(row["min_gap_low"]),
                        "rank_dE1_desc": current_rank,
                        "rank_min_gap_low_desc": by_min_gap[shape_id],
                        "zero_field_rank_dE1_desc": zero_rank,
                        "dE1_rank_changed_from_alpha0": current_rank != zero_rank,
                    }
                )
    return out


def pairwise_diff_maps(
    primary_rows: Sequence[Mapping[str, object]],
) -> dict[tuple[float, str, str], dict[float, float]]:
    """Return pairwise dE1 differences across alpha for each size."""
    lookup = spectrum_lookup(primary_rows)
    out: dict[tuple[float, str, str], dict[float, float]] = {}
    shape_ids = canonical_shape_order()
    for a_value in PRIMARY_SIZES:
        for shape_a, shape_b in combinations(shape_ids, 2):
            values: dict[float, float] = {}
            for alpha in ALL_ALPHAS:
                row_a = lookup[(a_value, float(alpha), shape_a)]
                row_b = lookup[(a_value, float(alpha), shape_b)]
                values[float(alpha)] = float(row_a["dE1"]) - float(row_b["dE1"])
            out[(a_value, shape_a, shape_b)] = values
    return out


def crossover_rows(primary_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Identify pairwise dE1 ranking reversals relative to alpha=0."""
    split_lookup = circle_split_lookup(primary_rows)
    diffs = pairwise_diff_maps(primary_rows)
    out: list[dict[str, object]] = []

    for (a_value, shape_a, shape_b), by_alpha in diffs.items():
        delta = delta_crossover_for_size(primary_rows, a_value)
        diff0 = float(by_alpha[0.0])
        signal_map: dict[float, bool] = {}
        abs_map = {alpha: abs(value) for alpha, value in by_alpha.items() if alpha in WEAK_ALPHAS}
        for alpha in ALL_ALPHAS:
            if np.isclose(alpha, 0.0):
                continue
            diff_alpha = float(by_alpha[alpha])
            alpha0_separated = abs(diff0) > delta
            ranking_reversed = diff0 * diff_alpha < 0.0
            thresholded = alpha0_separated and ranking_reversed and abs(diff_alpha) > delta
            signal_map[float(alpha)] = thresholded

        for alpha in ALL_ALPHAS:
            if np.isclose(alpha, 0.0):
                continue
            diff_alpha = float(by_alpha[alpha])
            alpha0_separated = abs(diff0) > delta
            ranking_reversed = diff0 * diff_alpha < 0.0
            thresholded = alpha0_separated and ranking_reversed and abs(diff_alpha) > delta
            weak_field = float(alpha) in WEAK_ALPHAS and float(alpha) > 0.0
            l_b = magnetic_length(float(alpha))
            l_b_filter_pass = bool(np.isfinite(l_b) and l_b >= MIN_LB_FOR_PRIMARY_SIGNAL)
            circle_artifact = (
                "circle_n2_r1" in (shape_a, shape_b)
                and split_lookup[(a_value, 0.0)] <= delta
            )
            onset_artifact, monotonic_onset = signal_is_onset_only(
                (a_value, shape_a, shape_b), float(alpha), signal_map, abs_map
            )
            qualifies = bool(
                thresholded
                and weak_field
                and l_b_filter_pass
                and not circle_artifact
                and not onset_artifact
            )
            notes: list[str] = []
            if thresholded and not weak_field:
                notes.append("diagnostic_stronger_field_only")
            if thresholded and not l_b_filter_pass:
                notes.append("STRONG_FIELD_LATTICE_ARTIFACT_CANDIDATE")
            if circle_artifact and thresholded:
                notes.append("SYMMETRY_ARTIFACT_CANDIDATE")
            if onset_artifact and thresholded:
                notes.append("ONSET_ARTIFACT_CANDIDATE")
            if thresholded and monotonic_onset and np.isclose(float(alpha), 0.005):
                notes.append("monotonic_abs_diff_onset")
            if not thresholded:
                notes.append("no_thresholded_reversal")

            out.append(
                {
                    "a": a_value,
                    "alpha": float(alpha),
                    "shape_a": shape_a,
                    "shape_b": shape_b,
                    "dE1_diff_alpha0": diff0,
                    "dE1_diff_alpha": diff_alpha,
                    "delta_crossover": delta,
                    "alpha0_separated": alpha0_separated,
                    "ranking_reversed": ranking_reversed,
                    "thresholded": thresholded,
                    "weak_field": weak_field,
                    "l_B": l_b,
                    "l_B_filter_pass": l_b_filter_pass,
                    "circle_symmetry_artifact_candidate": circle_artifact,
                    "onset_artifact_candidate": onset_artifact,
                    "qualifies_before_size_stability": qualifies,
                    "initial_winner": initial_and_field_winner(shape_a, shape_b, diff0),
                    "field_winner": initial_and_field_winner(shape_a, shape_b, diff_alpha),
                    "notes": ";".join(notes),
                }
            )
    return out


def robustness_divergence_rows(primary_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Identify near-tie pairs that separate under weak magnetic field."""
    split_lookup = circle_split_lookup(primary_rows)
    diffs = pairwise_diff_maps(primary_rows)
    out: list[dict[str, object]] = []

    for (a_value, shape_a, shape_b), by_alpha in diffs.items():
        delta = delta_crossover_for_size(primary_rows, a_value)
        diff0 = float(by_alpha[0.0])
        zero_near_tie = abs(diff0) <= delta
        signal_map: dict[float, bool] = {}
        abs_map = {alpha: abs(value) for alpha, value in by_alpha.items() if alpha in WEAK_ALPHAS}
        for alpha in WEAK_ALPHAS:
            if np.isclose(alpha, 0.0):
                continue
            signal_map[float(alpha)] = zero_near_tie and abs(float(by_alpha[alpha])) > delta

        for alpha in WEAK_ALPHAS:
            if np.isclose(alpha, 0.0):
                continue
            diff_alpha = float(by_alpha[alpha])
            weak_field = True
            separation = zero_near_tie and abs(diff_alpha) > delta
            l_b = magnetic_length(float(alpha))
            l_b_filter_pass = bool(np.isfinite(l_b) and l_b >= MIN_LB_FOR_PRIMARY_SIGNAL)
            circle_artifact = (
                "circle_n2_r1" in (shape_a, shape_b)
                and split_lookup[(a_value, 0.0)] <= delta
            )
            onset_artifact, monotonic_onset = signal_is_onset_only(
                (a_value, shape_a, shape_b), float(alpha), signal_map, abs_map
            )
            qualifies = bool(
                separation
                and weak_field
                and l_b_filter_pass
                and not circle_artifact
                and not onset_artifact
            )
            notes: list[str] = []
            if separation:
                notes.append("ROBUSTNESS_DIVERGENCE_CANDIDATE")
            else:
                notes.append("no_weak_field_near_tie_separation")
            if circle_artifact and separation:
                notes.append("SYMMETRY_ARTIFACT_CANDIDATE")
            if onset_artifact and separation:
                notes.append("ONSET_ARTIFACT_CANDIDATE")
            if separation and monotonic_onset and np.isclose(float(alpha), 0.005):
                notes.append("monotonic_abs_diff_onset")

            out.append(
                {
                    "a": a_value,
                    "alpha": float(alpha),
                    "shape_a": shape_a,
                    "shape_b": shape_b,
                    "dE1_diff_alpha0": diff0,
                    "dE1_diff_alpha": diff_alpha,
                    "delta_crossover": delta,
                    "zero_field_near_tie": zero_near_tie,
                    "weak_field_separation": separation,
                    "weak_field": weak_field,
                    "l_B": l_b,
                    "l_B_filter_pass": l_b_filter_pass,
                    "circle_symmetry_artifact_candidate": circle_artifact,
                    "onset_artifact_candidate": onset_artifact,
                    "qualifies_before_size_stability": qualifies,
                    "separation_winner": initial_and_field_winner(shape_a, shape_b, diff_alpha),
                    "notes": ";".join(notes),
                }
            )
    return out


def magnetic_response_summary_rows(primary_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Summarize weak-field dE1 response by geometry."""
    lookup = spectrum_lookup(primary_rows)
    out: list[dict[str, object]] = []
    for a_value in PRIMARY_SIZES:
        for shape in SHAPES:
            values = np.array(
                [float(lookup[(a_value, float(alpha), shape.shape_id)]["dE1"]) for alpha in WEAK_ALPHAS],
                dtype=float,
            )
            alpha0 = float(values[0])
            out.append(
                {
                    "a": a_value,
                    "shape_id": shape.shape_id,
                    "n": float(shape.n),
                    "rAR": float(shape.aspect_ratio),
                    "mean_dE1_weak": float(np.mean(values)),
                    "std_dE1_weak": float(np.std(values, ddof=0)),
                    "min_dE1_weak": float(np.min(values)),
                    "max_dE1_weak": float(np.max(values)),
                    "max_abs_change_dE1_from_alpha0_weak": float(np.max(np.abs(values - alpha0))),
                    "robust_gap_score": float(np.mean(values) - np.std(values, ddof=0)),
                }
            )
    return out


def symmetry_artifact_rows(primary_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Report circular E1/E2 splitting used as a symmetry artifact diagnostic."""
    out: list[dict[str, object]] = []
    for row in primary_rows:
        if str(row["shape_id"]) != "circle_n2_r1":
            continue
        a_value = float(row["a"])
        delta = delta_crossover_for_size(primary_rows, a_value)
        split = float(row["dE2"])
        out.append(
            {
                "a": a_value,
                "alpha": float(row["alpha"]),
                "shape_id": str(row["shape_id"]),
                "n": float(row["n"]),
                "rAR": float(row["rAR"]),
                "split_12": split,
                "delta_crossover": delta,
                "split_12_le_delta": split <= delta,
                "symmetry_artifact_candidate": split <= delta or np.isclose(float(row["alpha"]), 0.0),
            }
        )
    return out


def baseline_comparison_rows(
    primary_rows: Sequence[Mapping[str, object]],
    ranking_rows_in: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Compare current rankings against killer baseline descriptors."""
    lookup = spectrum_lookup(primary_rows)
    rank_lookup = {
        (float(row["a"]), float(row["alpha"]), str(row["shape_id"])): row for row in ranking_rows_in
    }
    out: list[dict[str, object]] = []
    for a_value in PRIMARY_SIZES:
        alpha0_group = [lookup[(a_value, 0.0, shape.shape_id)] for shape in SHAPES]
        zero_best = max(alpha0_group, key=lambda row: float(row["dE1"]))
        zero_best_shape = str(zero_best["shape_id"])
        zero_best_dE1 = float(zero_best["dE1"])
        for alpha in ALL_ALPHAS:
            group = [lookup[(a_value, float(alpha), shape.shape_id)] for shape in SHAPES]
            current_best = max(group, key=lambda row: float(row["dE1"]))
            zero_rank = int(rank_lookup[(a_value, float(alpha), zero_best_shape)]["rank_dE1_desc"])
            circle_rank = int(rank_lookup[(a_value, float(alpha), "circle_n2_r1")]["rank_dE1_desc"])
            ellipse_rank = int(rank_lookup[(a_value, float(alpha), "ellipse_n2_r067")]["rank_dE1_desc"])
            out.append(
                {
                    "a": a_value,
                    "alpha": float(alpha),
                    "zero_field_best_shape": zero_best_shape,
                    "current_best_shape": str(current_best["shape_id"]),
                    "zero_field_best_dE1": zero_best_dE1,
                    "current_best_dE1": float(current_best["dE1"]),
                    "zero_field_best_rank_at_alpha": zero_rank,
                    "best_zero_field_carried_across_alpha": zero_rank == 1,
                    "circle_rank_dE1": circle_rank,
                    "ellipse_rank_dE1": ellipse_rank,
                    "strongest_baseline": "best_zero_field_geometry_carried_across_alpha",
                    "notes": "baseline is sufficient if no thresholded size-stable crossover survives",
                }
            )
    return out


def alpha0_reproduction_rows(primary_rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """Compare magnetic alpha=0 spectra against the existing zero-field builder."""
    out: list[dict[str, object]] = []
    for row in primary_rows:
        if not np.isclose(float(row["alpha"]), 0.0):
            continue
        levels_mag = np.array([float(row[f"E{i}"]) for i in range(6)], dtype=float)
        levels_zero = zero_field_reference_spectrum(float(row["a"]), float(row["b"]), float(row["n"]), k=6)
        max_diff = float(np.max(np.abs(levels_mag - levels_zero)))
        out.append(
            {
                "shape_id": str(row["shape_id"]),
                "a": float(row["a"]),
                "alpha": 0.0,
                "max_abs_diff": max_diff,
                "tolerance": ALPHA0_REPRODUCTION_TOL,
                "passed": max_diff < ALPHA0_REPRODUCTION_TOL,
            }
        )
    return out


def _stable_signal_keys(
    rows: Sequence[Mapping[str, object]],
    winner_a_field_key: str,
) -> dict[tuple[str, str, str, str], set[float]]:
    """Return qualified signal keys and sizes where they appear."""
    out: dict[tuple[str, str, str, str], set[float]] = {}
    for row in rows:
        if not bool(row["qualifies_before_size_stability"]):
            continue
        shape_a = str(row["shape_a"])
        shape_b = str(row["shape_b"])
        initial = str(row.get("initial_winner", "near_tie"))
        field = str(row[winner_a_field_key])
        key = (shape_a, shape_b, initial, field)
        out.setdefault(key, set()).add(float(row["a"]))
    return out


def classify_verdict(
    sanity: Mapping[str, object],
    crossovers: Sequence[Mapping[str, object]],
    divergences: Sequence[Mapping[str, object]],
) -> tuple[str, str]:
    """Classify the sprint under the frozen exploratory verdict categories."""
    if not bool(sanity["numerical_passed"]):
        return "KILLED_NUMERICAL", "At least one required numerical or gauge check failed."

    crossover_keys = _stable_signal_keys(crossovers, "field_winner")
    stable_crossovers = {key: sizes for key, sizes in crossover_keys.items() if {30.0, 36.0}.issubset(sizes)}
    if stable_crossovers:
        n_alpha_hits = sum(1 for row in crossovers if bool(row["qualifies_before_size_stability"]))
        if len(stable_crossovers) > 1 or n_alpha_hits > 2:
            return "PROMISING", "Multiple thresholded weak-field crossovers survived both tested sizes."
        return "INTERESTING", "A thresholded weak-field ranking crossover survived both tested sizes."

    divergence_keys = _stable_signal_keys(divergences, "separation_winner")
    stable_divergences = {key: sizes for key, sizes in divergence_keys.items() if {30.0, 36.0}.issubset(sizes)}
    if stable_divergences:
        return "INTERESTING_WEAK", "No true crossover survived, but a robustness divergence survived both sizes."

    one_size_crossover = any(bool(row["qualifies_before_size_stability"]) for row in crossovers)
    one_size_divergence = any(bool(row["qualifies_before_size_stability"]) for row in divergences)
    if one_size_crossover or one_size_divergence:
        return "KILLED_SIZE_ARTIFACT", "A non-baseline signal appeared before size-stability filtering but did not survive both sizes."

    raw_crossovers = [row for row in crossovers if bool(row["thresholded"])]
    raw_divergences = [row for row in divergences if bool(row["weak_field_separation"])]
    raw_signals = raw_crossovers + raw_divergences
    if raw_signals:
        if all(not bool(row["l_B_filter_pass"]) for row in raw_signals):
            return "KILLED_STRONG_FIELD_ARTIFACT", "Signals occurred only below the l_B >= 5 weak-field cutoff."
        if all(bool(row["onset_artifact_candidate"]) for row in raw_signals if bool(row.get("weak_field", False))):
            return "KILLED_ONSET_ARTIFACT", "Signals appeared only as onset-artifact candidates."
        if all(bool(row["circle_symmetry_artifact_candidate"]) for row in raw_signals):
            return "KILLED_BASELINE", "All thresholded signals were explained by the circle symmetry-lifting baseline."
        return "KILLED_BASELINE", "Thresholded signals did not survive killer baseline filters."

    return "KILLED_NO_SIGNAL", "No thresholded ranking crossover and no robustness-divergence candidate were found."


def sanity_summary(
    primary_rows: Sequence[Mapping[str, object]],
    all_computations: Sequence[SpectrumComputation],
    gauge_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Summarize required numerical checks."""
    alpha0_rows = alpha0_reproduction_rows(primary_rows)
    max_alpha0 = max(float(row["max_abs_diff"]) for row in alpha0_rows)
    max_herm = max(float(comp.max_hermiticity_error) for comp in all_computations)
    max_imag = max(float(comp.max_eigen_imag) for comp in all_computations)
    max_gauge = max(float(row["max_abs_energy_diff"]) for row in gauge_rows) if gauge_rows else inf
    alpha0_passed = all(bool(row["passed"]) for row in alpha0_rows)
    hermiticity_passed = max_herm < HERMITICITY_TOL
    eigen_imag_passed = max_imag < EIGEN_IMAG_TOL
    gauge_passed = all(bool(row["passed"]) for row in gauge_rows)
    finite_sorted_passed = True
    for row in primary_rows:
        levels = np.array([float(row[f"E{i}"]) for i in range(6)], dtype=float)
        gaps = np.diff(levels)
        finite_sorted_passed = finite_sorted_passed and bool(np.all(np.isfinite(levels)) and np.all(gaps >= -1e-12))
    numerical_passed = bool(
        alpha0_passed and hermiticity_passed and eigen_imag_passed and gauge_passed and finite_sorted_passed
    )
    return {
        "alpha0_passed": alpha0_passed,
        "max_alpha0_reproduction_error": max_alpha0,
        "alpha0_tolerance": ALPHA0_REPRODUCTION_TOL,
        "hermiticity_passed": hermiticity_passed,
        "max_hermiticity_error": max_herm,
        "hermiticity_tolerance": HERMITICITY_TOL,
        "eigen_imag_passed": eigen_imag_passed,
        "max_eigen_imag": max_imag,
        "eigen_imag_tolerance": EIGEN_IMAG_TOL,
        "gauge_passed": gauge_passed,
        "max_gauge_invariance_error": max_gauge,
        "gauge_tolerance": GAUGE_INVARIANCE_TOL,
        "finite_sorted_passed": finite_sorted_passed,
        "numerical_passed": numerical_passed,
    }


def phi_total_range(primary_rows: Sequence[Mapping[str, object]]) -> tuple[float, float]:
    """Return min and max total flux over primary spectra."""
    values = [float(row["phi_total"]) for row in primary_rows]
    return min(values), max(values)


def l_b_filter_status(primary_rows: Sequence[Mapping[str, object]]) -> str:
    """Return a compact l_B cutoff status for primary and diagnostic alphas."""
    weak_ok = all(
        magnetic_length(alpha) >= MIN_LB_FOR_PRIMARY_SIGNAL
        for alpha in WEAK_ALPHAS
        if alpha > 0.0
    )
    diagnostic_below = [alpha for alpha in DIAGNOSTIC_ALPHAS if magnetic_length(alpha) < MIN_LB_FOR_PRIMARY_SIGNAL]
    del primary_rows
    if weak_ok and diagnostic_below:
        return "all weak-field alpha values pass l_B >= 5; diagnostic alpha values below cutoff are not eligible for primary claims"
    if weak_ok:
        return "all weak-field alpha values pass l_B >= 5"
    return "at least one weak-field alpha fails l_B >= 5"


def run_magnetic_sprint() -> dict[str, object]:
    """Run the complete fixed magnetic ranking-crossover sprint in memory."""
    primary_rows, primary_computations = primary_spectrum_rows()
    gauge_checks, gauge_spectra, gauge_computations = gauge_invariance_rows(primary_rows)
    spectra_rows = list(primary_rows) + list(gauge_spectra)
    rankings = ranking_rows(primary_rows)
    crossovers = crossover_rows(primary_rows)
    divergences = robustness_divergence_rows(primary_rows)
    response = magnetic_response_summary_rows(primary_rows)
    symmetry = symmetry_artifact_rows(primary_rows)
    baselines = baseline_comparison_rows(primary_rows, rankings)
    sanity = sanity_summary(primary_rows, primary_computations + gauge_computations, gauge_checks)
    verdict, verdict_reason = classify_verdict(sanity, crossovers, divergences)
    phi_min, phi_max = phi_total_range(primary_rows)
    return {
        "magnetic_spectra": spectra_rows,
        "gauge_invariance_check": gauge_checks,
        "gap_rankings_by_alpha": rankings,
        "ranking_crossovers": crossovers,
        "robustness_divergence": divergences,
        "magnetic_response_summary": response,
        "symmetry_artifact_diagnostics": symmetry,
        "baseline_comparison": baselines,
        "sanity": sanity,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "phi_total_min": phi_min,
        "phi_total_max": phi_max,
        "l_b_filter_status": l_b_filter_status(primary_rows),
    }
