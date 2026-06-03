"""Finite-difference continuum reference for Article Path B.

This module builds a unit-domain Dirichlet Laplacian reference for selected
superellipse domains. It does not compute tight-binding spectra, run shape
contrast, fit effective radii, use ML, or use Q/S objectives.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy import sparse as sp
from scipy.sparse.linalg import eigsh
from scipy.special import jn_zeros


N_VALUES = (1.2, 2.0, 4.0)
ASPECT_RATIO = 1.0
GRID_VALUES = (101, 151, 201, 251)
N_LEVELS = 6


@dataclass(frozen=True)
class FDLaplacian:
    """Sparse finite-difference Dirichlet Laplacian and grid metadata."""

    matrix: sp.csr_matrix
    mask: np.ndarray
    h: float
    num_interior_points: int


@dataclass(frozen=True)
class BesselLevel:
    """Exact unit-disk Bessel eigenvalue with degeneracy metadata."""

    level_index: int
    m: int
    s: int
    lambda_value: float
    degeneracy_group: str


def grid_spacing(n_grid: int, aspect_ratio: float = ASPECT_RATIO) -> float:
    """Return the uniform grid spacing for the square/circular box."""
    if int(n_grid) < 5:
        raise ValueError("n_grid must be at least 5.")
    if not np.isclose(float(aspect_ratio), 1.0):
        raise ValueError("This FD reference step uses rAR=1.0 only.")
    return 2.0 / (int(n_grid) - 1)


def superellipse_mask(n_value: float, aspect_ratio: float, n_grid: int) -> tuple[np.ndarray, float]:
    """Return strict interior mask for the unit-scaled superellipse domain."""
    if float(n_value) <= 0.0 or float(aspect_ratio) <= 0.0:
        raise ValueError("n_value and aspect_ratio must be positive.")
    h = grid_spacing(int(n_grid), float(aspect_ratio))
    x = np.linspace(-1.0, 1.0, int(n_grid))
    y = np.linspace(-float(aspect_ratio), float(aspect_ratio), int(n_grid))
    xx, yy = np.meshgrid(x, y, indexing="ij")
    values = np.abs(xx) ** float(n_value) + np.abs(yy / float(aspect_ratio)) ** float(n_value)
    # Strict interior: grid points exactly on the continuum boundary are
    # Dirichlet boundary points, not unknowns.
    mask = values < 1.0
    return mask, h


def build_dirichlet_laplacian(n_value: float, aspect_ratio: float, n_grid: int) -> FDLaplacian:
    """Build the positive 5-point finite-difference Dirichlet Laplacian."""
    mask, h = superellipse_mask(n_value, aspect_ratio, n_grid)
    index = -np.ones(mask.shape, dtype=int)
    interior = np.argwhere(mask)
    for row_index, (i, j) in enumerate(interior):
        index[int(i), int(j)] = row_index

    n_unknowns = int(interior.shape[0])
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    inv_h2 = 1.0 / (h * h)

    for row_index, (i_raw, j_raw) in enumerate(interior):
        i = int(i_raw)
        j = int(j_raw)
        rows.append(row_index)
        cols.append(row_index)
        data.append(4.0 * inv_h2)
        for ni, nj in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
            if 0 <= ni < mask.shape[0] and 0 <= nj < mask.shape[1] and mask[ni, nj]:
                rows.append(row_index)
                cols.append(int(index[ni, nj]))
                data.append(-inv_h2)

    matrix = sp.coo_matrix((data, (rows, cols)), shape=(n_unknowns, n_unknowns)).tocsr()
    return FDLaplacian(matrix=matrix, mask=mask, h=h, num_interior_points=n_unknowns)


def lowest_fd_eigenvalues(n_value: float, aspect_ratio: float, n_grid: int, n_levels: int = N_LEVELS) -> tuple[np.ndarray, FDLaplacian]:
    """Return the lowest finite-difference eigenvalues and matrix metadata."""
    fd = build_dirichlet_laplacian(n_value, aspect_ratio, n_grid)
    if fd.matrix.shape[0] <= n_levels:
        raise ValueError(f"Need more than {n_levels} interior points.")
    values, _ = eigsh(
        fd.matrix,
        k=int(n_levels),
        which="SA",
        tol=1e-9,
        ncv=max(4 * int(n_levels) + 20, 50),
        maxiter=max(1000, 10 * fd.matrix.shape[0]),
    )
    values = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("FD eigenvalues must be finite.")
    values.sort()
    if np.any(values <= 0.0):
        raise ValueError("FD eigenvalues must be positive.")
    if np.any(np.diff(values) < -1e-10):
        raise ValueError("FD eigenvalues must be sorted.")
    return values, fd


def first_bessel_disk_levels(n_levels: int = N_LEVELS) -> list[BesselLevel]:
    """Return the first unit-disk Dirichlet eigenvalues including degeneracies."""
    candidates: list[tuple[float, int, int, int]] = []
    for m_value in range(8):
        for s_index, zero in enumerate(jn_zeros(m_value, 8), start=1):
            degeneracy = 1 if m_value == 0 else 2
            candidates.append((float(zero * zero), m_value, s_index, degeneracy))
    candidates.sort(key=lambda item: item[0])
    levels: list[BesselLevel] = []
    for lambda_value, m_value, s_index, degeneracy in candidates:
        group = f"m{m_value}_s{s_index}"
        for _ in range(degeneracy):
            levels.append(
                BesselLevel(
                    level_index=len(levels),
                    m=m_value,
                    s=s_index,
                    lambda_value=lambda_value,
                    degeneracy_group=group,
                )
            )
            if len(levels) == n_levels:
                return levels
    raise RuntimeError(f"Could not generate {n_levels} Bessel levels.")


def grid_convergence_rows(
    n_values: Sequence[float] = N_VALUES,
    grid_values: Sequence[int] = GRID_VALUES,
    aspect_ratio: float = ASPECT_RATIO,
) -> list[dict[str, object]]:
    """Compute FD convergence rows for all requested domains."""
    bessel = first_bessel_disk_levels(N_LEVELS)
    rows: list[dict[str, object]] = []
    for n_value in n_values:
        for n_grid in grid_values:
            values, fd = lowest_fd_eigenvalues(float(n_value), float(aspect_ratio), int(n_grid), N_LEVELS)
            for level_index, lambda_fd in enumerate(values):
                bessel_level = bessel[level_index] if np.isclose(float(n_value), 2.0) else None
                lambda_bessel = "" if bessel_level is None else bessel_level.lambda_value
                abs_error = "" if bessel_level is None else abs(float(lambda_fd) - bessel_level.lambda_value)
                rel_error = (
                    ""
                    if bessel_level is None
                    else abs(float(lambda_fd) - bessel_level.lambda_value) / bessel_level.lambda_value
                )
                rows.append(
                    {
                        "n": float(n_value),
                        "rAR": float(aspect_ratio),
                        "N_grid": int(n_grid),
                        "h": fd.h,
                        "num_interior_points": fd.num_interior_points,
                        "level_index": int(level_index),
                        "lambda_fd_unit": float(lambda_fd),
                        "lambda_bessel_unit_if_available": lambda_bessel,
                        "abs_error_vs_bessel_if_available": abs_error,
                        "rel_error_vs_bessel_if_available": rel_error,
                        "degeneracy_group_if_available": "" if bessel_level is None else bessel_level.degeneracy_group,
                    }
                )
    return rows


def selected_reference_rows(rows: Sequence[dict[str, object]], selected_grid: int | None = None) -> list[dict[str, object]]:
    """Select the highest-grid reference values for each geometry."""
    out: list[dict[str, object]] = []
    for n_value in sorted({float(row["n"]) for row in rows}):
        available = sorted({int(row["N_grid"]) for row in rows if np.isclose(float(row["n"]), n_value)})
        n_grid = int(selected_grid) if selected_grid is not None else available[-1]
        selected = [
            row
            for row in rows
            if np.isclose(float(row["n"]), n_value) and int(row["N_grid"]) == n_grid
        ]
        for row in sorted(selected, key=lambda item: int(item["level_index"])):
            out.append(
                {
                    "n": float(row["n"]),
                    "rAR": float(row["rAR"]),
                    "N_grid_selected": int(row["N_grid"]),
                    "h": float(row["h"]),
                    "level_index": int(row["level_index"]),
                    "lambda_fd_unit": float(row["lambda_fd_unit"]),
                    "degeneracy_group_if_available": row["degeneracy_group_if_available"],
                    "validation_status": "selected_reference",
                }
            )
    return out


def _rows_for(rows: Sequence[dict[str, object]], n_value: float, n_grid: int) -> list[dict[str, object]]:
    """Filter rows by n and grid."""
    return [
        row
        for row in rows
        if np.isclose(float(row["n"]), float(n_value)) and int(row["N_grid"]) == int(n_grid)
    ]


def circle_error_summary(rows: Sequence[dict[str, object]], selected_grid: int | None = None) -> dict[str, float]:
    """Return selected-grid Bessel validation errors for the circle."""
    grids = sorted({int(row["N_grid"]) for row in rows if np.isclose(float(row["n"]), 2.0)})
    n_grid = int(selected_grid) if selected_grid is not None else grids[-1]
    selected = _rows_for(rows, 2.0, n_grid)
    rel_errors = [float(row["rel_error_vs_bessel_if_available"]) for row in selected]
    abs_errors = [float(row["abs_error_vs_bessel_if_available"]) for row in selected]
    return {
        "N_grid": float(n_grid),
        "ground_rel_error": rel_errors[0],
        "max_low_level_rel_error": max(rel_errors),
        "max_low_level_abs_error": max(abs_errors),
    }


def bessel_group_splitting(rows: Sequence[dict[str, object]], selected_grid: int | None = None) -> dict[str, float]:
    """Return FD splitting for degenerate Bessel groups at selected grid."""
    grids = sorted({int(row["N_grid"]) for row in rows if np.isclose(float(row["n"]), 2.0)})
    n_grid = int(selected_grid) if selected_grid is not None else grids[-1]
    selected = _rows_for(rows, 2.0, n_grid)
    out: dict[str, float] = {}
    for group in sorted({str(row["degeneracy_group_if_available"]) for row in selected if row["degeneracy_group_if_available"]}):
        group_rows = [row for row in selected if str(row["degeneracy_group_if_available"]) == group]
        if len(group_rows) <= 1:
            continue
        values = [float(row["lambda_fd_unit"]) for row in group_rows]
        out[group] = max(values) - min(values)
    return out


def two_finest_stability(rows: Sequence[dict[str, object]]) -> dict[float, float]:
    """Return max relative level change between the two finest grids by n."""
    out: dict[float, float] = {}
    for n_value in sorted({float(row["n"]) for row in rows}):
        grids = sorted({int(row["N_grid"]) for row in rows if np.isclose(float(row["n"]), n_value)})
        if len(grids) < 2:
            out[n_value] = float("inf")
            continue
        prev_grid, final_grid = grids[-2], grids[-1]
        prev = sorted(_rows_for(rows, n_value, prev_grid), key=lambda item: int(item["level_index"]))
        final = sorted(_rows_for(rows, n_value, final_grid), key=lambda item: int(item["level_index"]))
        rel = [
            abs(float(final_row["lambda_fd_unit"]) - float(prev_row["lambda_fd_unit"]))
            / abs(float(final_row["lambda_fd_unit"]))
            for prev_row, final_row in zip(prev, final)
        ]
        out[n_value] = max(rel)
    return out


def circle_converges_to_bessel(rows: Sequence[dict[str, object]]) -> bool:
    """Return whether circle ground-state error decreases with grid refinement."""
    circle_ground = [
        row
        for row in rows
        if np.isclose(float(row["n"]), 2.0) and int(row["level_index"]) == 0
    ]
    circle_ground.sort(key=lambda row: int(row["N_grid"]))
    errors = [float(row["rel_error_vs_bessel_if_available"]) for row in circle_ground]
    return bool(errors[-1] < errors[0] and errors[-1] < errors[-2])


def validate_fd_reference(rows: Sequence[dict[str, object]]) -> tuple[str, list[str]]:
    """Classify the FD reference validation result."""
    reasons: list[str] = []
    finite_positive_sorted = True
    for n_value in sorted({float(row["n"]) for row in rows}):
        for n_grid in sorted({int(row["N_grid"]) for row in rows if np.isclose(float(row["n"]), n_value)}):
            values = [
                float(row["lambda_fd_unit"])
                for row in sorted(_rows_for(rows, n_value, n_grid), key=lambda item: int(item["level_index"]))
            ]
            finite_positive_sorted = finite_positive_sorted and bool(
                np.all(np.isfinite(values)) and np.all(np.array(values) > 0.0) and np.all(np.diff(values) >= -1e-10)
            )
    if not finite_positive_sorted:
        return "FD_REFERENCE_VALIDATION_FAILED", ["FD eigenvalues are not finite, positive, and sorted."]

    error_summary = circle_error_summary(rows)
    stability = two_finest_stability(rows)
    split = bessel_group_splitting(rows)
    circle_converges = circle_converges_to_bessel(rows)
    noncircle_stable = stability[1.2] < 0.01 and stability[4.0] < 0.01
    ground_ok = error_summary["ground_rel_error"] < 0.01
    low_level_ok = error_summary["max_low_level_rel_error"] < 0.05
    splitting_reported = bool(split)

    if circle_converges and ground_ok and low_level_ok and noncircle_stable and splitting_reported:
        return (
            "FD_REFERENCE_VALIDATION_PASSED",
            [
                f"Circle ground-state relative error at selected grid is {error_summary['ground_rel_error']:.6g}.",
                "Non-circle reference values are finite, sorted, and stable across the two finest grids.",
                "Degeneracy splitting is reported rather than hidden.",
            ],
        )

    if not circle_converges:
        return "FD_REFERENCE_VALIDATION_FAILED", ["Circle FD eigenvalues do not converge toward Bessel values."]

    if not ground_ok:
        reasons.append(f"Circle ground-state relative error is {error_summary['ground_rel_error']:.6g}, above 1%.")
    if not low_level_ok:
        reasons.append(f"Max low-level circle relative error is {error_summary['max_low_level_rel_error']:.6g}, above 5%.")
    if not noncircle_stable:
        reasons.append(f"Two-finest-grid stability by n is {stability}.")
    if not splitting_reported:
        reasons.append("Degeneracy splitting was not reported.")
    return "FD_REFERENCE_VALIDATION_INCONCLUSIVE", reasons


def run_fd_reference() -> dict[str, object]:
    """Run the FD-reference-only computation in memory."""
    rows = grid_convergence_rows()
    selected = selected_reference_rows(rows)
    verdict, reasons = validate_fd_reference(rows)
    return {
        "grid_convergence_rows": rows,
        "selected_reference_rows": selected,
        "verdict": verdict,
        "verdict_reasons": reasons,
        "circle_error_summary": circle_error_summary(rows),
        "bessel_group_splitting": bessel_group_splitting(rows),
        "two_finest_stability": two_finest_stability(rows),
    }
