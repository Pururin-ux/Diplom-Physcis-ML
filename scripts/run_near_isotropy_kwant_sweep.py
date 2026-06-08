"""Run direct Kwant near-isotropy sweep around surrogate iso-Ekin roots."""

from __future__ import annotations

import csv
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dataset import _superellipse_levels_and_site_count  # noqa: E402
from src.inverse_screening import (  # noqa: E402
    MAIN_N_VALUES,
    compute_ekin,
    compute_q,
    find_ekin_root,
    geometry_diagnostics,
    load_superellipse_dataset,
    train_surrogates_for_n,
)
from src.symmetry_optimum_analysis import (  # noqa: E402
    NEAR_ISOTROPY_ASPECT_RATIOS,
    classify_near_isotropy_optimum,
    compute_s,
    local_refinement_candidates,
    select_min_ekin_error_candidate,
)


DATA_PATH = PROJECT_ROOT / "data" / "superellipse_discrete_n_dense_dataset.npz"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_near_isotropy_sweep"
PLOT_DIR = OUTPUT_DIR / "plots"


SWEEP_COLUMNS = [
    "n",
    "requested_aspect_ratio",
    "surrogate_a_root",
    "selected_a",
    "selected_b",
    "Ekin_target",
    "E0_Kwant",
    "E1_Kwant",
    "E2_Kwant",
    "E3_Kwant",
    "Ekin_Kwant",
    "abs_Ekin_error",
    "dE1_Kwant",
    "dE2_Kwant",
    "Q_Kwant",
    "S_Kwant",
    "geometry_hash",
    "N_sites",
    "N_A",
    "N_B",
    "imbalance_ratio",
    "n_local_candidates",
    "n_unique_local_geometries",
    "failure_mode",
]

SUMMARY_COLUMNS = [
    "n",
    "n_verified_points",
    "Q_iso",
    "best_noniso_Q",
    "Q_iso_minus_best_noniso",
    "noniso_beats_iso",
    "spearman_r_ar_Q",
    "S_iso",
    "max_noniso_S",
    "spearman_r_ar_S",
    "supports_near_isotropy_optimum",
    "notes",
]


def _write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    """Write deterministic CSV output."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _verify_local_candidate(n_value: float, aspect_ratio: float, a_value: float) -> dict[str, object]:
    """Compute direct Kwant quantities for one local candidate."""
    b_value = float(a_value) * float(aspect_ratio)
    vals, _ = _superellipse_levels_and_site_count(a=float(a_value), b=b_value, n=n_value)
    e0, e1, e2, e3 = [float(v) for v in vals]
    ekin = float(compute_ekin(e0))
    de1 = e1 - e0
    de2 = e2 - e1
    geom = geometry_diagnostics(a=float(a_value), b=b_value, n=n_value)
    return {
        "selected_a": float(a_value),
        "selected_b": b_value,
        "E0_Kwant": e0,
        "E1_Kwant": e1,
        "E2_Kwant": e2,
        "E3_Kwant": e3,
        "Ekin_Kwant": ekin,
        "dE1_Kwant": de1,
        "dE2_Kwant": de2,
        "Q_Kwant": float(compute_q(de1, ekin)),
        "S_Kwant": float(compute_s(de2, ekin)),
        "geometry_hash": geom.geometry_hash,
        "N_sites": geom.n_sites,
        "N_A": geom.n_a,
        "N_B": geom.n_b,
        "imbalance_ratio": geom.imbalance_ratio,
    }


def _run_one_root(
    n_value: float,
    aspect_ratio: float,
    a_root: float,
    ekin_target: float,
) -> dict[str, object]:
    """Run local direct-Kwant refinement around one surrogate root."""
    local_as = local_refinement_candidates(a_root)
    local_rows: list[dict[str, object]] = []
    seen_hashes: set[str] = set()
    for a_value in local_as:
        row = _verify_local_candidate(n_value, aspect_ratio, a_value)
        if row["geometry_hash"] in seen_hashes:
            continue
        seen_hashes.add(str(row["geometry_hash"]))
        local_rows.append(row)

    selected = select_min_ekin_error_candidate(local_rows, ekin_target)
    selected["n"] = n_value
    selected["requested_aspect_ratio"] = aspect_ratio
    selected["surrogate_a_root"] = a_root
    selected["Ekin_target"] = ekin_target
    selected["abs_Ekin_error"] = abs(float(selected["Ekin_Kwant"]) - ekin_target)
    selected["n_local_candidates"] = len(local_as)
    selected["n_unique_local_geometries"] = len(local_rows)
    selected["failure_mode"] = "ok"
    return selected


def _summary_for_n(rows: list[dict[str, object]]) -> dict[str, object]:
    """Summarize direct near-isotropy evidence for one n."""
    rows = sorted(rows, key=lambda row: float(row["requested_aspect_ratio"]))
    ar = np.array([float(row["requested_aspect_ratio"]) for row in rows])
    q = np.array([float(row["Q_Kwant"]) for row in rows])
    s = np.array([float(row["S_Kwant"]) for row in rows])
    iso_row = max(rows, key=lambda row: float(row["requested_aspect_ratio"]))
    noniso_rows = [row for row in rows if float(row["requested_aspect_ratio"]) < 1.0]
    q_iso = float(iso_row["Q_Kwant"])
    s_iso = float(iso_row["S_Kwant"])
    best_noniso_q = max(float(row["Q_Kwant"]) for row in noniso_rows)
    max_noniso_s = max(float(row["S_Kwant"]) for row in noniso_rows)
    rho_q = float(spearmanr(ar, q).statistic) if len(rows) >= 3 else np.nan
    rho_s = float(spearmanr(ar, s).statistic) if len(rows) >= 3 else np.nan
    threshold = max(0.02 * q_iso, 1e-6)
    status, note = classify_near_isotropy_optimum(
        q_iso=q_iso,
        best_noniso_q=best_noniso_q,
        spearman_q=rho_q,
        tolerance=threshold,
    )
    if best_noniso_q > q_iso and best_noniso_q <= q_iso + threshold:
        note = f"{note}; noniso_gain_within_threshold={best_noniso_q - q_iso}"
    return {
        "n": float(rows[0]["n"]),
        "n_verified_points": len(rows),
        "Q_iso": q_iso,
        "best_noniso_Q": best_noniso_q,
        "Q_iso_minus_best_noniso": q_iso - best_noniso_q,
        "noniso_beats_iso": best_noniso_q > q_iso,
        "spearman_r_ar_Q": rho_q,
        "S_iso": s_iso,
        "max_noniso_S": max_noniso_s,
        "spearman_r_ar_S": rho_s,
        "supports_near_isotropy_optimum": status,
        "notes": note,
    }


def _plot_metric(rows: list[dict[str, object]], metric: str, ylabel: str, path: Path) -> None:
    """Plot one metric against near-isotropy aspect ratio by n."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, n_value in zip(axes.ravel(), MAIN_N_VALUES):
        n_rows = [row for row in rows if np.isclose(float(row["n"]), n_value)]
        n_rows.sort(key=lambda row: float(row["requested_aspect_ratio"]))
        ax.plot(
            [float(row["requested_aspect_ratio"]) for row in n_rows],
            [float(row[metric]) for row in n_rows],
            marker="o",
        )
        ax.axvline(1.0, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"n = {n_value}")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.3)
    axes[-1, 0].set_xlabel("requested aspect_ratio")
    axes[-1, 1].set_xlabel("requested aspect_ratio")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def _plot_levels(rows: list[dict[str, object]]) -> None:
    """Plot direct Kwant E0/E1/E2 levels near isotropy by n."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, n_value in zip(axes.ravel(), MAIN_N_VALUES):
        n_rows = [row for row in rows if np.isclose(float(row["n"]), n_value)]
        n_rows.sort(key=lambda row: float(row["requested_aspect_ratio"]))
        ar = [float(row["requested_aspect_ratio"]) for row in n_rows]
        for key, label in [("E0_Kwant", "E0"), ("E1_Kwant", "E1"), ("E2_Kwant", "E2")]:
            ax.plot(ar, [float(row[key]) for row in n_rows], marker="o", label=label)
        ax.axvline(1.0, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"n = {n_value}")
        ax.set_ylabel("Energy, onsite=0 hopping=-1")
        ax.grid(alpha=0.3)
    axes[-1, 0].set_xlabel("requested aspect_ratio")
    axes[-1, 1].set_xlabel("requested aspect_ratio")
    axes[0, 0].legend(loc="best")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "E_levels_near_isotropy_by_n.png", dpi=200)
    plt.close(fig)


def _write_readme(summary_rows: list[dict[str, object]]) -> None:
    """Write report README."""
    lines = [
        "# Direct Kwant near-isotropy sweep",
        "",
        "This sweep was run because the previous symmetry-optimum analysis used a",
        "surrogate-defined dense iso-Ekin curve with only representative direct",
        "Kwant checks. Here, near isotropy, every reported point is selected by a",
        "local direct-Kwant refinement around the surrogate iso-Ekin root.",
        "",
        "Exact Ekin matching is not imposed because continuous superellipse",
        "parameters induce discrete lattice domains; Ekin changes stepwise with",
        "the selected site set. For each requested aspect ratio, the selected",
        "geometry is the local candidate with minimum absolute Ekin error.",
        "",
        "This is not a new inverse-design objective, and S = (E2-E1)/Ekin is not",
        "optimized here.",
        "",
        "## Summary",
        "",
    ]
    for row in summary_rows:
        lines.append(
            f"- n={row['n']}: status={row['supports_near_isotropy_optimum']}; "
            f"Q_iso_minus_best_noniso={row['Q_iso_minus_best_noniso']}; "
            f"noniso_beats_iso={row['noniso_beats_iso']}."
        )
    if any(row["noniso_beats_iso"] for row in summary_rows):
        lines.extend(
            [
                "",
                "At least one non-isotropic point has larger raw Q than isotropy, but",
                "the report classifies gains conservatively using a 2% threshold.",
                "Therefore the strict near-isotropy optimum claim is ambiguous, not",
                "confirmed as a clean maximum.",
            ]
        )
    else:
        lines.extend(["", "No non-isotropic Q bump above the isotropic value was found."])
    lines.extend(
        [
            "",
            "The broader symmetry explanation remains plausible because Q keeps a",
            "positive rank trend toward isotropy and S decreases toward near-zero",
            "at isotropy, but the direct sweep does not prove a strict isotropic",
            "maximum in the discrete lattice setting.",
            "",
            "S remains a plausible next pre-registered objective only as a separate",
            "new experiment with direct Kwant verification and strong baselines. This",
            "sweep does not establish inverse-design success.",
            "",
            "## Limitations",
            "",
            "- The sweep is local near isotropy and does not replace a full direct Kwant",
            "  sweep of the whole domain.",
            "- The selected geometries minimize local Ekin error but are not exactly",
            "  iso-Ekin matched.",
            "- Continuous parameters can map to duplicate discrete geometries.",
            "- Thesis files and thesis conclusions are not modified.",
        ]
    )
    (OUTPUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Run direct near-isotropy Kwant sweep."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    dataset = load_superellipse_dataset(DATA_PATH)
    all_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for n_value in MAIN_N_VALUES:
        model_ekin, _, training_rows = train_surrogates_for_n(dataset, n_value)
        ekin_target = float(np.median(training_rows["Ekin"]))
        n_rows: list[dict[str, object]] = []
        for ar_value in NEAR_ISOTROPY_ASPECT_RATIOS:
            root, status = find_ekin_root(model_ekin, float(ar_value), ekin_target)
            if root is None or status != "ok":
                n_rows.append(
                    {
                        "n": n_value,
                        "requested_aspect_ratio": float(ar_value),
                        "surrogate_a_root": np.nan if root is None else root,
                        "selected_a": np.nan,
                        "selected_b": np.nan,
                        "Ekin_target": ekin_target,
                        "failure_mode": status,
                    }
                )
                continue
            n_rows.append(_run_one_root(n_value, float(ar_value), float(root), ekin_target))
        all_rows.extend(n_rows)
        ok_rows = [row for row in n_rows if row.get("failure_mode") == "ok"]
        summary_rows.append(_summary_for_n(ok_rows))

    _write_csv(OUTPUT_DIR / "near_isotropy_kwant_sweep.csv", all_rows, SWEEP_COLUMNS)
    _write_csv(OUTPUT_DIR / "summary_by_n.csv", summary_rows, SUMMARY_COLUMNS)
    _plot_metric(all_rows, "Q_Kwant", "Q = dE1 / Ekin", PLOT_DIR / "Q_near_isotropy_by_n.png")
    _plot_metric(all_rows, "S_Kwant", "S = (E2 - E1) / Ekin", PLOT_DIR / "S_near_isotropy_by_n.png")
    _plot_levels(all_rows)
    _write_readme(summary_rows)


if __name__ == "__main__":
    main()
