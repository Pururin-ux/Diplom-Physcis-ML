"""Article-H dimensionless reanalysis (frozen protocol
reports/article_h_dimensionless_response/protocol.md).

Reads the Article-G pilot CSVs (read-only), restores the E0+4 normalization,
and writes the derived table plus statistics, conditional, convergence,
scaling, and n2-vs-n4 reports. No eigensolves.
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
from scipy.stats import wasserstein_distance  # noqa: E402

from src.article_h_dimensionless import (  # noqa: E402
    DERIVED_FIELDS, derived_row, dimless_split_under_swap,
)

G_DIR = PROJECT_ROOT / "reports" / "article_g_signed_response"
H_DIR = PROJECT_ROOT / "reports" / "article_h_dimensionless_response"
SHAPES = (2.0, 4.0)
SCALES = (24.3, 33.7, 48.2)
XIS = (0.05, 0.10, 0.20, 0.40, 0.80)
DELTAS = (0.001, 0.002, 0.004, 0.008)
CONV_ANCHORS = [
    (2.0, 33.7, "xi", 0.10), (2.0, 33.7, "xi", 0.40),
    (4.0, 33.7, "xi", 0.10), (4.0, 33.7, "xi", 0.40),
    (4.0, 33.7, "delta", 0.004),
]


def load(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def build_derived():
    rows = load(G_DIR / "pilot_main_rows.csv") + load(G_DIR / "pilot_conv_rows.csv")
    derived = [derived_row(r) for r in rows if r.get("solve_status") == "OK"]
    H_DIR.mkdir(parents=True, exist_ok=True)
    with open(H_DIR / "article_h_dimensionless_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(DERIVED_FIELDS))
        w.writeheader()
        w.writerows(derived)
    return derived


def sel(derived, n, a0, mode, path, val, grid=16):
    out = []
    for d in derived:
        if float(d["shape_n"]) != n or float(d["scale_a0"]) != a0:
            continue
        if d["deformation_mode"] != mode or int(float(d["grid"])) != grid:
            continue
        if path == "xi":
            # mode A rows: xi is a round frozen value AND delta = xi/a0
            if abs(d["xi"] - val) > 1e-9:
                continue
            if abs(d["delta"] - val / a0) > 1e-9:
                continue
        else:
            if abs(d["delta"] - val) > 1e-9:
                continue
            # exclude mode-A rows that happen to share a delta
            if abs(d["xi"] - val * a0) > 1e-6:
                continue
        out.append(d)
    return out


def arr(rows, key, ok_only=True):
    v = [r[key] for r in rows if (not ok_only or r["branch_status"] == "OK")]
    return np.array([x for x in v if np.isfinite(x)], dtype=float)


def stat_block(values):
    v = values[np.isfinite(values)]
    if v.size == 0:
        return {k: math.nan for k in
                ("mean", "std", "median", "min", "max", "q05", "q25", "q75",
                 "q95", "iqr", "frac_neg", "frac_pos", "frac_zero", "count")}
    return {
        "mean": float(np.mean(v)), "std": float(np.std(v)),
        "median": float(np.median(v)), "min": float(v.min()), "max": float(v.max()),
        "q05": float(np.percentile(v, 5)), "q25": float(np.percentile(v, 25)),
        "q75": float(np.percentile(v, 75)), "q95": float(np.percentile(v, 95)),
        "iqr": float(np.percentile(v, 75) - np.percentile(v, 25)),
        "frac_neg": float(np.mean(v < 0)), "frac_pos": float(np.mean(v > 0)),
        "frac_zero": float(np.mean(v == 0)), "count": int(v.size),
    }


def ambiguity_bounds(rows):
    """Mean of dimless_chi_split: OK-only, all-row, and worst-case ambiguous."""
    ok = arr(rows, "dimless_chi_split", ok_only=True)
    allv = arr(rows, "dimless_chi_split", ok_only=False)
    amb = [r for r in rows if r["branch_status"] == "AMBIGUOUS"]
    non_amb = [r["dimless_chi_split"] for r in rows if r["branch_status"] != "AMBIGUOUS"]
    amb_id = [r["dimless_chi_split"] for r in amb]
    amb_sw = [dimless_split_under_swap(r) for r in amb]
    lo = np.array(non_amb + [min(a, b) for a, b in zip(amb_id, amb_sw)])
    hi = np.array(non_amb + [max(a, b) for a, b in zip(amb_id, amb_sw)])
    med_id = np.median(np.array(non_amb + amb_id)) if (non_amb + amb_id) else math.nan
    med_sw = np.median(np.array(non_amb + amb_sw)) if (non_amb + amb_sw) else math.nan
    return {
        "mean_ok": float(ok.mean()) if ok.size else math.nan,
        "mean_all": float(allv.mean()) if allv.size else math.nan,
        "mean_amb_lo": float(lo.mean()) if lo.size else math.nan,
        "mean_amb_hi": float(hi.mean()) if hi.size else math.nan,
        "median_id": float(med_id), "median_swap": float(med_sw),
        "n_amb": len(amb), "n_total": len(rows),
    }


def main():
    derived = build_derived()
    assert len(derived) == 20224, f"expected 20224 derived rows, got {len(derived)}"

    # ---- primary statistics (chih_split) and aux, both paths, OK-only ----
    stat_records = []
    for n in SHAPES:
        for a0 in SCALES:
            for path, vals in (("xi", XIS), ("delta", DELTAS)):
                for val in vals:
                    rows = sel(derived, n, a0, "area_preserving", path, val)
                    if not rows:
                        continue
                    amb = ambiguity_bounds(rows)
                    for key in ("dimless_chi_split", "dimless_chi_minus",
                                "dimless_chi_plus", "dimless_chi_center"):
                        s = stat_block(arr(rows, key))
                        rec = {"n": n, "a0": a0, "path": path, "value": val,
                               "metric": key, "n_total": len(rows),
                               "n_ambiguous": amb["n_amb"], **s}
                        if key == "dimless_chi_split":
                            rec.update({"mean_all": amb["mean_all"],
                                        "mean_amb_lo": amb["mean_amb_lo"],
                                        "mean_amb_hi": amb["mean_amb_hi"],
                                        "median_id": amb["median_id"],
                                        "median_swap": amb["median_swap"]})
                        stat_records.append(rec)
    with open(H_DIR / "dimensionless_statistics.csv", "w", newline="") as fh:
        keys = sorted({k for r in stat_records for k in r})
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(stat_records)

    # ---- conditional by baseline symmetry class (chih_split) ----
    cond_records = []
    for n in SHAPES:
        for a0 in SCALES:
            rows = sel(derived, n, a0, "area_preserving", "xi", 0.40)
            classes = {}
            for r in rows:
                classes.setdefault(r["symmetry_class_0"], []).append(r)
            for cls, crows in sorted(classes.items()):
                v = arr(crows, "dimless_chi_split", ok_only=True)
                namb = sum(1 for r in crows if r["branch_status"] == "AMBIGUOUS")
                cond_records.append({
                    "n": n, "a0": a0, "xi": 0.40, "symmetry_class_0": cls,
                    "count": len(crows), "count_ok": int(v.size),
                    "mean": float(v.mean()) if v.size else math.nan,
                    "median": float(np.median(v)) if v.size else math.nan,
                    "std": float(v.std()) if v.size else math.nan,
                    "frac_neg": float(np.mean(v < 0)) if v.size else math.nan,
                    "frac_ambiguous": namb / len(crows) if crows else math.nan,
                    "enough_points": len(crows) >= 16,
                })
    with open(H_DIR / "dimensionless_conditional.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cond_records[0].keys()))
        w.writeheader()
        w.writerows(cond_records)

    # ---- convergence 16 -> 32 on dimensionless chih_split ----
    conv_records = []
    for n, a0, path, val in CONV_ANCHORS:
        r16 = sel(derived, n, a0, "area_preserving", path, val, grid=16)
        r32 = sel(derived, n, a0, "area_preserving", path, val, grid=32)
        v16 = arr(r16, "dimless_chi_split"); v32 = arr(r32, "dimless_chi_split")
        s16, s32 = stat_block(v16), stat_block(v32)
        pooled = np.concatenate([v16, v32])
        sig = float(pooled.std()); iqr = float(np.percentile(pooled, 75) - np.percentile(pooled, 25))
        d_mean = abs(s32["mean"] - s16["mean"])
        d_med = abs(s32["median"] - s16["median"])
        dq = max(abs(s32[q] - s16[q]) for q in ("q05", "q25", "q75", "q95"))
        # ECDF D
        alls = np.sort(pooled)
        cdf16 = np.searchsorted(np.sort(v16), alls, "right") / v16.size
        cdf32 = np.searchsorted(np.sort(v32), alls, "right") / v32.size
        ecdf_d = float(np.max(np.abs(cdf16 - cdf32)))
        w1 = float(wasserstein_distance(v16, v32))
        famb16 = np.mean([r["branch_status"] == "AMBIGUOUS" for r in r16])
        famb32 = np.mean([r["branch_status"] == "AMBIGUOUS" for r in r32])
        crit = {
            "mean_over_sigma": d_mean / sig if sig else math.nan,
            "median_over_iqr": d_med / iqr if iqr else math.nan,
            "maxq_over_iqr": dq / iqr if iqr else math.nan,
            "ecdf_D": ecdf_d, "w1_over_iqr": w1 / iqr if iqr else math.nan,
            "d_fneg": abs(s32["frac_neg"] - s16["frac_neg"]),
            "d_famb": abs(famb32 - famb16),
        }
        passed = (crit["mean_over_sigma"] <= 0.05 and crit["median_over_iqr"] <= 0.05
                  and crit["maxq_over_iqr"] <= 0.10 and crit["ecdf_D"] <= 0.05
                  and crit["w1_over_iqr"] <= 0.05 and crit["d_fneg"] <= 0.03
                  and crit["d_famb"] <= 0.03)
        conv_records.append({
            "n": n, "a0": a0, "path": path, "value": val,
            "mean16": s16["mean"], "mean32": s32["mean"],
            "median16": s16["median"], "median32": s32["median"], **crit,
            "status": "RESOLVED" if passed else "GRID_UNRESOLVED",
        })
    with open(H_DIR / "dimensionless_convergence.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(conv_records[0].keys()))
        w.writeheader()
        w.writerows(conv_records)

    # ---- n=2 vs n=4 distances (ECDF, Wasserstein), no iid p ----
    n2n4 = []
    for a0 in SCALES:
        for xi in XIS:
            v2 = arr(sel(derived, 2.0, a0, "area_preserving", "xi", xi), "dimless_chi_split")
            v4 = arr(sel(derived, 4.0, a0, "area_preserving", "xi", xi), "dimless_chi_split")
            alls = np.sort(np.concatenate([v2, v4]))
            c2 = np.searchsorted(np.sort(v2), alls, "right") / v2.size
            c4 = np.searchsorted(np.sort(v4), alls, "right") / v4.size
            n2n4.append({
                "a0": a0, "xi": xi, "ecdf_D": float(np.max(np.abs(c2 - c4))),
                "w1": float(wasserstein_distance(v2, v4)),
                "mean2": float(v2.mean()), "mean4": float(v4.mean()),
                "median2": float(np.median(v2)), "median4": float(np.median(v4)),
                "q05_2": float(np.percentile(v2, 5)), "q05_4": float(np.percentile(v4, 5)),
            })
    with open(H_DIR / "dimensionless_n2_vs_n4.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(n2n4[0].keys()))
        w.writeheader()
        w.writerows(n2n4)

    # ---- scaling: raw and dimensionless mean/std/iqr exponents ----
    scaling = []
    for n in SHAPES:
        for path, vals in (("xi", XIS), ("delta", DELTAS)):
            for val in vals:
                for metric, key in (("raw", "raw_chi_split"),
                                    ("dimless", "dimless_chi_split")):
                    means, stds, iqrs = [], [], []
                    for a0 in SCALES:
                        v = arr(sel(derived, n, a0, "area_preserving", path, val), key)
                        means.append(v.mean()); stds.append(v.std())
                        iqrs.append(np.percentile(v, 75) - np.percentile(v, 25))
                    la = np.log(np.array(SCALES))
                    def expo(y):
                        y = np.array(y)
                        if np.any(y <= 0):
                            return math.nan
                        p = np.polyfit(la, np.log(y), 1)
                        return -p[0]
                    scaling.append({
                        "n": n, "path": path, "value": val, "metric": metric,
                        "mean_24.3": means[0], "mean_33.7": means[1], "mean_48.2": means[2],
                        "std_exponent": expo(stds), "iqr_exponent": expo(iqrs),
                        "std_24.3": stds[0], "std_48.2": stds[2],
                    })
    with open(H_DIR / "dimensionless_scaling.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(scaling[0].keys()))
        w.writeheader()
        w.writerows(scaling)

    # ---- legacy control (n=4, a0=33.7): F-metric decomposition vs signed ----
    legacy = []
    for xi in XIS:
        rows = sel(derived, 4.0, 33.7, "legacy_fixed_major_axis", "xi", xi)
        if not rows:
            continue
        legacy.append({
            "xi": xi, "n_ok": int(arr(rows, "dimless_chi_split").size),
            "L_old_mean": float(arr(rows, "normalized_sorted_raw").mean()),
            "B_baseline_mean": float(arr(rows, "normalized_baseline_term").mean()),
            "C_sorted_bc_mean": float(arr(rows, "normalized_sorted_bc").mean()),
            "signed_chih_split_mean": float(arr(rows, "dimless_chi_split").mean()),
            "signed_chih_split_median": float(np.median(arr(rows, "dimless_chi_split"))),
        })
    with open(H_DIR / "dimensionless_legacy_control.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(legacy[0].keys()))
        w.writeheader()
        w.writerows(legacy)

    print("article-H analysis done:", len(derived), "derived rows")


if __name__ == "__main__":
    main()
