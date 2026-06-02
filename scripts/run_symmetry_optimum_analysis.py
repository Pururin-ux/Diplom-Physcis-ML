"""Run symmetry-optimum explanation analysis for the negative screening result."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.inverse_screening import MAIN_N_VALUES, load_superellipse_dataset  # noqa: E402
from src.symmetry_optimum_analysis import (  # noqa: E402
    classify_doublet_splitting,
    classify_symmetry_optimum,
    generate_isoenergy_curve_for_n,
    jaccard_overlap,
    select_representative_points,
    site_coordinates_for_superellipse,
    verify_isoenergy_point,
)


DATA_PATH = PROJECT_ROOT / "data" / "superellipse_discrete_n_dense_dataset.npz"
PREVIOUS_MAIN_PATH = PROJECT_ROOT / "reports" / "article_inverse_screening" / "main_candidates_verified.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_symmetry_optimum"
PLOT_DIR = OUTPUT_DIR / "plots"


CURVE_COLUMNS = [
    "n",
    "aspect_ratio",
    "a_root",
    "b_root",
    "Ekin_target",
    "Ekin_pred",
    "dE1_pred",
    "dE2_pred",
    "Q_pred",
    "geometry_hash",
    "N_sites",
    "N_A",
    "N_B",
    "imbalance_ratio",
    "is_kwant_verified",
    "requested_aspect_ratio",
    "E0_Kwant",
    "E1_Kwant",
    "E2_Kwant",
    "E3_Kwant",
    "Ekin_Kwant",
    "dE1_Kwant",
    "dE2_Kwant",
    "Q_Kwant",
    "S_Kwant",
    "failure_mode",
]

SUMMARY_COLUMNS = [
    "n",
    "n_feasible_roots",
    "n_unique_geometries",
    "n_kwant_verified_points",
    "Q_iso_Kwant",
    "best_noniso_Q_Kwant",
    "Q_iso_minus_best_noniso",
    "spearman_r_ar_Q",
    "finite_difference_sign_pattern_Q",
    "supports_symmetry_optimum",
    "S_iso_Kwant",
    "max_noniso_S_Kwant",
    "spearman_r_ar_S",
    "finite_difference_sign_pattern_S",
    "doublet_splitting_interpretation",
    "notes",
]

GEOMETRY_COLUMNS = [
    "n",
    "candidate_geometry_hash",
    "isotropic_geometry_hash",
    "hashes_match",
    "candidate_a",
    "isotropic_a",
    "candidate_aspect_ratio",
    "isotropic_aspect_ratio",
    "candidate_N_sites",
    "isotropic_N_sites",
    "N_sites_difference",
    "jaccard_overlap",
    "candidate_Q_Kwant",
    "isotropic_Q_Kwant",
    "Q_difference_candidate_minus_isotropic",
    "interpretation",
]


def _write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    """Write deterministic CSV output."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _read_previous_main_rows() -> list[dict[str, str]]:
    """Read previous inverse-screening verified rows."""
    with PREVIOUS_MAIN_PATH.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _float_or_nan(value: str) -> float:
    """Parse a CSV float, returning NaN for empty fields."""
    if value == "":
        return np.nan
    return float(value)


def _selected_previous_pair(rows: list[dict[str, str]], n_value: float) -> tuple[dict[str, str], dict[str, str]]:
    """Return previous best candidate and isotropic baseline rows for one n."""
    n_rows = [row for row in rows if np.isclose(float(row["n"]), n_value)]
    candidate = next(
        row
        for row in n_rows
        if row["candidate_type"] == "inverse_candidate" and row["candidate_rank"] == "1"
    )
    isotropic = next(row for row in n_rows if row["candidate_type"] == "isotropic_same_n_baseline")
    return candidate, isotropic


def _geometry_comparison_rows() -> list[dict[str, object]]:
    """Compare previous best candidates against isotropic same-n baselines."""
    previous_rows = _read_previous_main_rows()
    out: list[dict[str, object]] = []
    for n_value in MAIN_N_VALUES:
        candidate, isotropic = _selected_previous_pair(previous_rows, n_value)
        hashes_match = candidate["geometry_hash"] == isotropic["geometry_hash"]
        candidate_n_sites = int(candidate["N_sites"])
        isotropic_n_sites = int(isotropic["N_sites"])
        if hashes_match:
            overlap = 1.0
            interpretation = "same_discrete_geometry"
        else:
            cand_coords = site_coordinates_for_superellipse(
                a=float(candidate["a"]),
                b=float(candidate["b"]),
                n=n_value,
            )
            iso_coords = site_coordinates_for_superellipse(
                a=float(isotropic["a"]),
                b=float(isotropic["b"]),
                n=n_value,
            )
            overlap = jaccard_overlap(cand_coords, iso_coords)
            interpretation = "different_discrete_geometry"
        out.append(
            {
                "n": n_value,
                "candidate_geometry_hash": candidate["geometry_hash"],
                "isotropic_geometry_hash": isotropic["geometry_hash"],
                "hashes_match": hashes_match,
                "candidate_a": float(candidate["a"]),
                "isotropic_a": float(isotropic["a"]),
                "candidate_aspect_ratio": float(candidate["aspect_ratio"]),
                "isotropic_aspect_ratio": float(isotropic["aspect_ratio"]),
                "candidate_N_sites": candidate_n_sites,
                "isotropic_N_sites": isotropic_n_sites,
                "N_sites_difference": candidate_n_sites - isotropic_n_sites,
                "jaccard_overlap": overlap,
                "candidate_Q_Kwant": float(candidate["Q_Kwant"]),
                "isotropic_Q_Kwant": float(isotropic["Q_Kwant"]),
                "Q_difference_candidate_minus_isotropic": float(candidate["Q_Kwant"])
                - float(isotropic["Q_Kwant"]),
                "interpretation": interpretation,
            }
        )
    return out


def _curve_row(point, verification_by_hash: dict[str, object]) -> dict[str, object]:
    """Convert one curve point plus optional verification to a CSV row."""
    verification = verification_by_hash.get(point.geometry.geometry_hash)
    is_verified = verification is not None
    return {
        "n": point.n,
        "aspect_ratio": point.aspect_ratio,
        "a_root": point.a_root,
        "b_root": point.b_root,
        "Ekin_target": point.ekin_target,
        "Ekin_pred": point.ekin_pred,
        "dE1_pred": point.de1_pred,
        "dE2_pred": point.de2_pred,
        "Q_pred": point.q_pred,
        "geometry_hash": point.geometry.geometry_hash,
        "N_sites": point.geometry.n_sites,
        "N_A": point.geometry.n_a,
        "N_B": point.geometry.n_b,
        "imbalance_ratio": point.geometry.imbalance_ratio,
        "is_kwant_verified": is_verified,
        "requested_aspect_ratio": "" if not is_verified else verification["requested_aspect_ratio"],
        "E0_Kwant": np.nan if not is_verified else verification["verification"].e0,
        "E1_Kwant": np.nan if not is_verified else verification["verification"].e1,
        "E2_Kwant": np.nan if not is_verified else verification["verification"].e2,
        "E3_Kwant": np.nan if not is_verified else verification["verification"].e3,
        "Ekin_Kwant": np.nan if not is_verified else verification["verification"].ekin,
        "dE1_Kwant": np.nan if not is_verified else verification["verification"].de1,
        "dE2_Kwant": np.nan if not is_verified else verification["verification"].de2,
        "Q_Kwant": np.nan if not is_verified else verification["verification"].q,
        "S_Kwant": np.nan if not is_verified else verification["verification"].s,
        "failure_mode": point.failure_mode if not is_verified else verification["verification"].failure_mode,
    }


def _plot_q(curve_rows: list[dict[str, object]]) -> None:
    """Plot predicted Q curves and Kwant-verified Q points by n."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, n_value in zip(axes.ravel(), MAIN_N_VALUES):
        rows = [row for row in curve_rows if np.isclose(float(row["n"]), n_value)]
        rows.sort(key=lambda row: float(row["aspect_ratio"]))
        ar = np.array([float(row["aspect_ratio"]) for row in rows])
        q_pred = np.array([float(row["Q_pred"]) for row in rows])
        ax.plot(ar, q_pred, color="tab:blue", label="Ridge Q_pred")
        verified = [row for row in rows if row["is_kwant_verified"]]
        ax.scatter(
            [float(row["aspect_ratio"]) for row in verified],
            [float(row["Q_Kwant"]) for row in verified],
            color="tab:orange",
            label="Kwant Q",
            zorder=3,
        )
        ax.axvline(1.0, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"n = {n_value}")
        ax.set_ylabel("Q = dE1 / Ekin")
        ax.grid(alpha=0.3)
    axes[-1, 0].set_xlabel("aspect_ratio")
    axes[-1, 1].set_xlabel("aspect_ratio")
    axes[0, 0].legend(loc="best")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "Q_vs_aspect_ratio_by_n.png", dpi=200)
    plt.close(fig)


def _plot_levels(curve_rows: list[dict[str, object]]) -> None:
    """Plot Kwant E0/E1/E2 levels by aspect ratio and n."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, n_value in zip(axes.ravel(), MAIN_N_VALUES):
        rows = [
            row
            for row in curve_rows
            if np.isclose(float(row["n"]), n_value) and row["is_kwant_verified"]
        ]
        rows.sort(key=lambda row: float(row["aspect_ratio"]))
        ar = np.array([float(row["aspect_ratio"]) for row in rows])
        for key, color in [("E0_Kwant", "tab:blue"), ("E1_Kwant", "tab:orange"), ("E2_Kwant", "tab:green")]:
            ax.plot(ar, [float(row[key]) for row in rows], marker="o", label=key.replace("_Kwant", ""), color=color)
        ax.axvline(1.0, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"n = {n_value}")
        ax.set_ylabel("Energy, onsite=0 hopping=-1")
        ax.grid(alpha=0.3)
    axes[-1, 0].set_xlabel("aspect_ratio")
    axes[-1, 1].set_xlabel("aspect_ratio")
    axes[0, 0].legend(loc="best")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "levels_vs_aspect_ratio_by_n.png", dpi=200)
    plt.close(fig)


def _plot_split(curve_rows: list[dict[str, object]]) -> None:
    """Plot normalized doublet splitting by aspect ratio and n."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, n_value in zip(axes.ravel(), MAIN_N_VALUES):
        rows = [
            row
            for row in curve_rows
            if np.isclose(float(row["n"]), n_value) and row["is_kwant_verified"]
        ]
        rows.sort(key=lambda row: float(row["aspect_ratio"]))
        ax.plot(
            [float(row["aspect_ratio"]) for row in rows],
            [float(row["S_Kwant"]) for row in rows],
            marker="o",
            color="tab:red",
        )
        ax.axvline(1.0, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"n = {n_value}")
        ax.set_ylabel("S = (E2 - E1) / Ekin")
        ax.grid(alpha=0.3)
    axes[-1, 0].set_xlabel("aspect_ratio")
    axes[-1, 1].set_xlabel("aspect_ratio")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "normalized_split_vs_aspect_ratio_by_n.png", dpi=200)
    plt.close(fig)


def _write_readme(summary_rows: list[dict[str, object]], geometry_rows: list[dict[str, object]]) -> None:
    """Write a compact methodological README for the analysis."""
    lines = [
        "# Symmetry optimum analysis",
        "",
        "This report tests a physical explanation for the negative one-shot",
        "surrogate-guided inverse-screening result. The question is whether, along",
        "a surrogate iso-Ekin line, Q = dE1 / Ekin increases toward the isotropic",
        "same-n geometry and whether anisotropy splits the first excited doublet.",
        "",
        "This is a numerical test in the discrete square-lattice tight-binding",
        "superellipse model. Continuum PPW/Ashbaugh-Benguria intuition is only an",
        "analogy here, not proof for the lattice problem.",
        "",
        "No new inverse-design objective is implemented in this analysis.",
        "",
        "## Summary",
        "",
    ]
    for row in summary_rows:
        lines.append(
            f"- n={row['n']}: supports_symmetry_optimum={row['supports_symmetry_optimum']}; "
            f"Q_iso_minus_best_noniso={row['Q_iso_minus_best_noniso']}; "
            f"{row['doublet_splitting_interpretation']}"
        )

    if all(row["hashes_match"] for row in geometry_rows):
        lines.extend(
            [
                "",
                "The previous top inverse-screening candidate and the isotropic same-n",
                "baseline are the same discrete geometry for every tested n.",
            ]
        )

    lines.extend(
        [
            "",
            "## Implication for S = (E2 - E1) / Ekin",
            "",
            "The normalized doublet splitting S is diagnostic only in this report. If",
            "future work uses S as an objective, it must be pre-registered as a new",
            "question and directly Kwant-verified against strong baselines. The",
            "current analysis does not establish inverse-design success.",
            "",
            "## Limitations",
            "",
            "- Only representative points on the iso-Ekin line are Kwant-verified.",
            "- Surrogate roots define the iso-Ekin line; final spectral values are",
            "  direct Kwant values only at selected points.",
            "- Continuous parameters can map to identical discrete lattice domains.",
            "- Thesis chapters and thesis conclusions are not modified by this report.",
        ]
    )
    (OUTPUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Run the full symmetry-optimum analysis."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    dataset = load_superellipse_dataset(DATA_PATH)
    aspect_grid = np.round(np.arange(0.67, 1.0001, 0.005), 3)

    curve_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for n_value in MAIN_N_VALUES:
        points, audit_rows, _ = generate_isoenergy_curve_for_n(dataset, n_value, aspect_grid)
        selected = select_representative_points(points)
        verification_by_hash: dict[str, object] = {}
        for point in selected:
            verification_by_hash[point.geometry.geometry_hash] = {
                "verification": verify_isoenergy_point(point),
                "requested_aspect_ratio": point.requested_aspect_ratio,
            }

        n_curve_rows = [_curve_row(point, verification_by_hash) for point in points]
        curve_rows.extend(n_curve_rows)

        verified_rows = [row for row in n_curve_rows if row["is_kwant_verified"] and row["failure_mode"] == "ok"]
        verified_rows.sort(key=lambda row: float(row["aspect_ratio"]))
        ar = np.array([float(row["aspect_ratio"]) for row in verified_rows])
        q = np.array([float(row["Q_Kwant"]) for row in verified_rows])
        s = np.array([float(row["S_Kwant"]) for row in verified_rows])
        status, rho_q, q_signs, q_note = classify_symmetry_optimum(ar, q)
        split_note, rho_s, s_signs = classify_doublet_splitting(ar, s)
        iso_row = max(verified_rows, key=lambda row: float(row["aspect_ratio"]))
        noniso_rows = [row for row in verified_rows if float(row["aspect_ratio"]) < float(iso_row["aspect_ratio"])]
        best_noniso_q = max(float(row["Q_Kwant"]) for row in noniso_rows) if noniso_rows else np.nan
        max_noniso_s = max(float(row["S_Kwant"]) for row in noniso_rows) if noniso_rows else np.nan
        summary_rows.append(
            {
                "n": n_value,
                "n_feasible_roots": sum(1 for row in audit_rows if row["failure_mode"] == "ok"),
                "n_unique_geometries": len(points),
                "n_kwant_verified_points": len(verified_rows),
                "Q_iso_Kwant": float(iso_row["Q_Kwant"]),
                "best_noniso_Q_Kwant": best_noniso_q,
                "Q_iso_minus_best_noniso": float(iso_row["Q_Kwant"]) - best_noniso_q,
                "spearman_r_ar_Q": rho_q,
                "finite_difference_sign_pattern_Q": " ".join(str(sign) for sign in q_signs),
                "supports_symmetry_optimum": status,
                "S_iso_Kwant": float(iso_row["S_Kwant"]),
                "max_noniso_S_Kwant": max_noniso_s,
                "spearman_r_ar_S": rho_s,
                "finite_difference_sign_pattern_S": " ".join(str(sign) for sign in s_signs),
                "doublet_splitting_interpretation": split_note,
                "notes": q_note,
            }
        )

    geometry_rows = _geometry_comparison_rows()
    _write_csv(OUTPUT_DIR / "isoenergy_q_curve.csv", curve_rows, CURVE_COLUMNS)
    _write_csv(OUTPUT_DIR / "summary_by_n.csv", summary_rows, SUMMARY_COLUMNS)
    _write_csv(OUTPUT_DIR / "candidate_vs_isotropic_geometry_check.csv", geometry_rows, GEOMETRY_COLUMNS)
    _plot_q(curve_rows)
    _plot_levels(curve_rows)
    _plot_split(curve_rows)
    _write_readme(summary_rows, geometry_rows)


if __name__ == "__main__":
    main()
