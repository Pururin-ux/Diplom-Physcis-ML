"""Article-Ic discrepancy gate: Model 0 (bare geometry) vs Model 1
(geometry + eigenfunction-weighted marks), predicting the spectral marks with
leave-one-placement-out evaluation. Post-processing of event_rows.csv only.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np  # noqa: E402

OUT = PROJECT_ROOT / "reports" / "article_ic_event_shifts"

MODEL0 = ["added_count", "removed_count", "changed_edge_count", "event_rank",
          "max_row_length", "max_column_length", "flatness_proxy",
          "axis_aligned_normal"]
MODEL1_EXTRA = ["boundary_weight_mode1", "boundary_weight_mode2",
                "changed_bond_weight", "schur_predictor"]
TARGETS = ["eta_gap", "abs_eta_gap", "eta_center"]


def load():
    rows = list(csv.DictReader(open(OUT / "event_rows.csv")))
    for r in rows:
        r["abs_eta_gap"] = abs(float(r["eta_gap"]))
    return rows


def fnum(r, k):
    try:
        return float(r[k])
    except (ValueError, KeyError, TypeError):
        return 0.0


def design(rows, feats):
    X = np.array([[fnum(r, f) for f in feats] for r in rows], dtype=float)
    X = np.column_stack([np.ones(len(rows)), X])
    return X


def loplo_r2(rows, feats, target):
    """Leave-one-placement-out R^2 (ridge-regularized least squares)."""
    groups = {}
    for i, r in enumerate(rows):
        key = (r["shape_n"], r["scale_a0"], r["placement_x"], r["placement_y"])
        groups.setdefault(key, []).append(i)
    y = np.array([fnum(r, target) for r in rows])
    preds = np.full(len(rows), np.nan)
    for key, test_idx in groups.items():
        train_idx = [i for i in range(len(rows)) if i not in set(test_idx)]
        if len(train_idx) < len(feats) + 3:
            continue
        Xtr = design([rows[i] for i in train_idx], feats)
        Xte = design([rows[i] for i in test_idx], feats)
        # standardize columns (except intercept) using train stats
        mu = Xtr[:, 1:].mean(0)
        sd = Xtr[:, 1:].std(0) + 1e-12
        Xtr[:, 1:] = (Xtr[:, 1:] - mu) / sd
        Xte[:, 1:] = (Xte[:, 1:] - mu) / sd
        lam = 1e-2
        A = Xtr.T @ Xtr + lam * np.eye(Xtr.shape[1])
        beta = np.linalg.solve(A, Xtr.T @ y[train_idx])
        preds[test_idx] = Xte @ beta
    mask = np.isfinite(preds)
    yy = y[mask]
    pp = preds[mask]
    ss_res = float(np.sum((yy - pp) ** 2))
    ss_tot = float(np.sum((yy - yy.mean()) ** 2)) + 1e-30
    return 1.0 - ss_res / ss_tot, int(mask.sum())


def main():
    rows = load()
    lines = ["# Article-Ic discrepancy gate: Model 0 vs Model 1", "",
             "Leave-one-placement-out R^2 (ridge LS). Model 0 = bare geometry;",
             "Model 1 = geometry + eigenfunction-weighted marks.", "",
             "| target | shape | Model0 R2 | Model1 R2 | improvement | n |",
             "|---|---|---|---|---|---|"]
    records = []
    for shape in ("all", "2.0", "4.0"):
        sub = rows if shape == "all" else [r for r in rows if r["shape_n"] == shape]
        if len(sub) < 20:
            continue
        for tgt in TARGETS:
            r0, n0 = loplo_r2(sub, MODEL0, tgt)
            r1, n1 = loplo_r2(sub, MODEL0 + MODEL1_EXTRA, tgt)
            lines.append(f"| {tgt} | {shape} | {r0:.3f} | {r1:.3f} | {r1 - r0:+.3f} | {n0} |")
            records.append({"target": tgt, "shape": shape, "model0_r2": r0,
                            "model1_r2": r1, "improvement": r1 - r0, "n": n0})
    lines.append("")
    # verdict logic per protocol
    key_imp = [rec["improvement"] for rec in records
               if rec["target"] == "abs_eta_gap" and rec["shape"] == "all"]
    imp = key_imp[0] if key_imp else float("nan")
    lines.append("## Gate reading")
    lines.append(f"- Model 1 improvement on |eta_gap| (all shapes, LOPLO): {imp:+.3f}")
    if imp < 0.05:
        lines.append("- Eigenfunction weighting does NOT substantially beat bare counting "
                     "-> KNOWN DISCREPANCY EFFECT / STOP (Model 1 improvement < 0.05).")
    else:
        lines.append("- Eigenfunction weighting improves prediction on this micro-pilot "
                     "-> SPECTRAL MARK CANDIDATE / NOVELTY NOT ESTABLISHED (needs "
                     "independent sizes/placements).")
    with open(OUT / "discrepancy_model_comparison.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)
    (OUT / "discrepancy_model_comparison.md").write_text("\n".join(lines), encoding="utf-8")
    print("discrepancy gate done; |eta_gap| improvement =", imp)


if __name__ == "__main__":
    main()
