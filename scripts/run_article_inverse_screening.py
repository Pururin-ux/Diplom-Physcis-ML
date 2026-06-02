"""Run the article-extension inverse-screening falsification experiment."""

from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.inverse_screening import (  # noqa: E402
    MAIN_N_VALUES,
    generate_candidate_pool_for_n,
    best_training_baseline,
    isotropic_same_n_baseline,
    load_error_scales,
    load_superellipse_dataset,
    random_feasible_candidates,
    select_diverse_top_candidates,
    verify_candidate,
)


DATA_PATH = PROJECT_ROOT / "data" / "superellipse_discrete_n_dense_dataset.npz"
ERROR_SCALE_PATH = PROJECT_ROOT / "reports" / "model_error_physical_scale.csv"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_inverse_screening"


MAIN_COLUMNS = [
    "n",
    "candidate_rank",
    "candidate_type",
    "a",
    "b",
    "aspect_ratio",
    "Ekin_target",
    "Ekin_pred",
    "dE1_pred",
    "Q_pred",
    "E0_Kwant",
    "E1_Kwant",
    "E2_Kwant",
    "E3_Kwant",
    "Ekin_Kwant",
    "dE1_Kwant",
    "Q_Kwant",
    "Ekin_error",
    "dE1_error",
    "Q_error",
    "passes_Ekin_constraint_pred",
    "passes_Ekin_constraint_Kwant",
    "geometry_hash",
    "N_sites",
    "N_A",
    "N_B",
    "imbalance_ratio",
    "Q_gain_vs_isotropic_same_n",
    "Q_gain_vs_best_training",
    "Q_gain_vs_random_best_of_5",
    "beats_isotropic_same_n",
    "beats_best_training",
    "beats_random_best_of_5",
    "meaningful_gain_vs_isotropic",
    "meaningful_gain_vs_best_training",
    "meaningful_gain_vs_random_best_of_5",
    "failure_mode",
]

SUMMARY_COLUMNS = [
    "n",
    "n_feasible_roots",
    "n_unique_geometries",
    "n_selected_candidates",
    "best_candidate_Q_Kwant",
    "isotropic_same_n_Q_Kwant",
    "best_training_Q_Kwant",
    "random_best_of_5_Q_Kwant",
    "best_gain_vs_isotropic_percent",
    "best_gain_vs_training_percent",
    "best_gain_vs_random_percent",
    "main_success_bool",
    "notes",
]


def _verified_to_row(row, baseline_q: dict[str, float], delta_q: dict[str, float]) -> dict[str, object]:
    """Convert a verified row to the required report schema."""
    gains = {
        "isotropic_same_n": row.q_kwant - baseline_q["isotropic_same_n"],
        "best_training": row.q_kwant - baseline_q["best_training"],
        "random_best_of_5": row.q_kwant - baseline_q["random_best_of_5"],
    }
    is_candidate = row.candidate_type == "inverse_candidate"
    failure_mode = row.failure_mode
    if is_candidate and failure_mode == "ok":
        if gains["isotropic_same_n"] <= 0.0:
            failure_mode = "candidate_not_better_than_isotropic"
        elif gains["best_training"] <= 0.0:
            failure_mode = "candidate_not_better_than_best_training"
        elif any(gains[name] <= delta_q[name] for name in gains):
            failure_mode = "candidate_gain_within_noise_floor"

    return {
        "n": row.n,
        "candidate_rank": "" if row.candidate_rank is None else row.candidate_rank,
        "candidate_type": row.candidate_type,
        "a": row.a,
        "b": row.b,
        "aspect_ratio": row.aspect_ratio,
        "Ekin_target": row.ekin_target,
        "Ekin_pred": row.ekin_pred,
        "dE1_pred": row.de1_pred,
        "Q_pred": row.q_pred,
        "E0_Kwant": row.e0_kwant,
        "E1_Kwant": row.e1_kwant,
        "E2_Kwant": row.e2_kwant,
        "E3_Kwant": row.e3_kwant,
        "Ekin_Kwant": row.ekin_kwant,
        "dE1_Kwant": row.de1_kwant,
        "Q_Kwant": row.q_kwant,
        "Ekin_error": row.ekin_error,
        "dE1_error": row.de1_error,
        "Q_error": row.q_error,
        "passes_Ekin_constraint_pred": row.passes_ekin_constraint_pred,
        "passes_Ekin_constraint_Kwant": row.passes_ekin_constraint_kwant,
        "geometry_hash": row.geometry_hash,
        "N_sites": row.n_sites,
        "N_A": row.n_a,
        "N_B": row.n_b,
        "imbalance_ratio": row.imbalance_ratio,
        "Q_gain_vs_isotropic_same_n": gains["isotropic_same_n"],
        "Q_gain_vs_best_training": gains["best_training"],
        "Q_gain_vs_random_best_of_5": gains["random_best_of_5"],
        "beats_isotropic_same_n": is_candidate and gains["isotropic_same_n"] > 0.0,
        "beats_best_training": is_candidate and gains["best_training"] > 0.0,
        "beats_random_best_of_5": is_candidate and gains["random_best_of_5"] > 0.0,
        "meaningful_gain_vs_isotropic": is_candidate and gains["isotropic_same_n"] > delta_q["isotropic_same_n"],
        "meaningful_gain_vs_best_training": is_candidate and gains["best_training"] > delta_q["best_training"],
        "meaningful_gain_vs_random_best_of_5": is_candidate and gains["random_best_of_5"] > delta_q["random_best_of_5"],
        "failure_mode": failure_mode,
    }


def _write_csv(path: Path, rows: list[dict[str, object]], columns: list[str] | None = None) -> None:
    """Write dictionaries to CSV with deterministic columns."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if columns is None:
        columns = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_readme(path: Path, summary_rows: list[dict[str, object]]) -> None:
    """Write a compact report README for the falsification run."""
    lines = [
        "# Article inverse screening report",
        "",
        "This report tests one-shot surrogate-guided inverse spectral screening.",
        "It is not closed-loop inverse design because no iterative retraining loop is used.",
        "",
        "The surrogate Ridge models generate candidates only. Final candidate and",
        "baseline values in `main_candidates_verified.csv` are direct Kwant",
        "calculations or already Kwant-computed training rows.",
        "",
        "Continuous parameters `(a, aspect_ratio)` induce discrete Kwant lattice",
        "domains, so candidate geometries are deduplicated by a stable hash of",
        "integer site coordinates.",
        "",
        "## How to rerun",
        "",
        "```powershell",
        "C:\\Users\\lalad\\miniforge3\\Scripts\\conda.exe run -n diplom-kwant python scripts\\run_article_inverse_screening.py",
        "```",
        "",
        "## Summary",
        "",
    ]
    for row in summary_rows:
        lines.append(
            f"- n={row['n']}: selected={row['n_selected_candidates']}, "
            f"best_Q={row['best_candidate_Q_Kwant']}, success={row['main_success_bool']}. "
            f"{row['notes']}"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- The search is restricted to the verified training-domain ranges.",
            "- Surrogate roots are off-grid candidate proposals, not physical truth.",
            "- The reported success criterion is conservative and first-pass.",
            "- No thesis chapter or thesis conclusion is modified by this report.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Execute the full one-shot screening run."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dataset = load_superellipse_dataset(DATA_PATH)
    error_scales = load_error_scales(ERROR_SCALE_PATH)
    aspect_grid = np.round(np.arange(0.67, 1.0001, 0.005), 3)

    main_rows: list[dict[str, object]] = []
    pool_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for n_value in MAIN_N_VALUES:
        pool, audit_rows, ekin_target, model_ekin, model_de1, training_rows = generate_candidate_pool_for_n(
            dataset=dataset,
            n_value=n_value,
            aspect_ratio_grid=aspect_grid,
        )
        pool_rows.extend(audit_rows)

        sigma_e = float(error_scales.get(n_value, {}).get("sigma_E", np.nan))
        if np.isfinite(sigma_e):
            epsilon_e = max(0.03 * ekin_target, 2.0 * sigma_e)
            sigma_note = "LOAO/LOARO Ridge error scale loaded"
        else:
            epsilon_e = 0.03 * ekin_target
            sigma_note = "sigma_E unavailable; used 3 percent target fallback"

        selected = select_diverse_top_candidates(pool, max_count=5)
        verified_candidates = [verify_candidate(cand, epsilon_e=epsilon_e) for cand in selected]

        iso_cand = isotropic_same_n_baseline(n_value, ekin_target, model_ekin, model_de1)
        verified_iso = (
            verify_candidate(iso_cand, epsilon_e=epsilon_e)
            if iso_cand is not None
            else None
        )
        verified_training = best_training_baseline(training_rows, n_value, ekin_target, epsilon_e)
        random_verified = [
            verify_candidate(cand, epsilon_e=epsilon_e)
            for cand in random_feasible_candidates(n_value, ekin_target, model_ekin, model_de1)
        ]

        random_best = max(random_verified, key=lambda item: item.q_kwant) if random_verified else None
        if verified_iso is None or random_best is None:
            raise RuntimeError(f"Baseline generation failed for n={n_value}.")

        baseline_q = {
            "isotropic_same_n": verified_iso.q_kwant,
            "best_training": verified_training.q_kwant,
            "random_best_of_5": random_best.q_kwant,
        }
        delta_q = {
            key: max(0.02 * value, 0.0) for key, value in baseline_q.items()
        }

        all_verified = verified_candidates + [verified_iso, verified_training] + random_verified
        for row in all_verified:
            main_rows.append(_verified_to_row(row, baseline_q=baseline_q, delta_q=delta_q))

        candidate_report_rows = [
            row for row in main_rows if row["n"] == n_value and row["candidate_type"] == "inverse_candidate"
        ]
        valid_candidate_rows = [
            row for row in candidate_report_rows if row["passes_Ekin_constraint_Kwant"]
        ]
        best_candidate_q = (
            max(float(row["Q_Kwant"]) for row in valid_candidate_rows)
            if valid_candidate_rows
            else np.nan
        )
        best_gain_iso_pct = (
            100.0 * (best_candidate_q - baseline_q["isotropic_same_n"]) / baseline_q["isotropic_same_n"]
            if np.isfinite(best_candidate_q)
            else np.nan
        )
        best_gain_training_pct = (
            100.0 * (best_candidate_q - baseline_q["best_training"]) / baseline_q["best_training"]
            if np.isfinite(best_candidate_q)
            else np.nan
        )
        best_gain_random_pct = (
            100.0 * (best_candidate_q - baseline_q["random_best_of_5"]) / baseline_q["random_best_of_5"]
            if np.isfinite(best_candidate_q)
            else np.nan
        )
        success = bool(
            np.isfinite(best_candidate_q)
            and best_candidate_q > baseline_q["isotropic_same_n"] + delta_q["isotropic_same_n"]
            and best_candidate_q > baseline_q["best_training"] + delta_q["best_training"]
            and best_candidate_q > baseline_q["random_best_of_5"] + delta_q["random_best_of_5"]
        )
        notes = (
            f"{sigma_note}; no_root={sum(1 for row in audit_rows if row['failure_mode'] == 'no_root')}; "
            f"duplicate_training={sum(1 for row in audit_rows if row['failure_mode'] == 'duplicate_training_geometry')}; "
            f"duplicate_candidate={sum(1 for row in audit_rows if row['failure_mode'] == 'duplicate_candidate_geometry')}"
        )
        summary_rows.append(
            {
                "n": n_value,
                "n_feasible_roots": sum(1 for row in audit_rows if row["failure_mode"] == "ok"),
                "n_unique_geometries": len({row.get("geometry_hash") for row in audit_rows if row.get("geometry_hash")}),
                "n_selected_candidates": len(selected),
                "best_candidate_Q_Kwant": best_candidate_q,
                "isotropic_same_n_Q_Kwant": baseline_q["isotropic_same_n"],
                "best_training_Q_Kwant": baseline_q["best_training"],
                "random_best_of_5_Q_Kwant": baseline_q["random_best_of_5"],
                "best_gain_vs_isotropic_percent": best_gain_iso_pct,
                "best_gain_vs_training_percent": best_gain_training_pct,
                "best_gain_vs_random_percent": best_gain_random_pct,
                "main_success_bool": success,
                "notes": notes,
            }
        )

    _write_csv(OUTPUT_DIR / "main_candidates_verified.csv", main_rows, MAIN_COLUMNS)
    _write_csv(OUTPUT_DIR / "summary_by_n.csv", summary_rows, SUMMARY_COLUMNS)
    _write_csv(OUTPUT_DIR / "candidate_pool.csv", pool_rows)
    _write_readme(OUTPUT_DIR / "README.md", summary_rows)


if __name__ == "__main__":
    main()
