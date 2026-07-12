"""Article-G analysis (protocol.md sections 8-10): statistics, convergence,
outcome evidence. Post-processing only (no Kwant).

Reads pilot_main_rows.csv and pilot_conv_rows.csv; writes aggregates CSV,
convergence CSV, distribution arrays, and analysis_summary.md. The A/B/C
outcome evidence is emitted; the final verdict is stated against the frozen
qualitative criteria.
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

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_g_signed_response"
METRICS = [
    "chi_minus", "chi_plus", "chi_center", "chi_split",
    "legacy_raw_ratio", "sorted_baseline_corrected_ratio",
]
PRIMARY = ["chi_split", "chi_center"]


def load(path: Path) -> list[dict]:
    with open(path) as fh:
        return list(csv.DictReader(fh))


def fnum(row, key):
    try:
        return float(row[key])
    except (ValueError, KeyError, TypeError):
        return math.nan


def stats(values: np.ndarray) -> dict:
    v = values[np.isfinite(values)]
    if v.size == 0:
        return {k: math.nan for k in
                ("mean", "std", "median", "min", "max", "q5", "q25", "q75",
                 "q95", "frac_neg", "count")}
    return {
        "mean": float(np.mean(v)), "std": float(np.std(v)),
        "median": float(np.median(v)), "min": float(np.min(v)),
        "max": float(np.max(v)),
        "q5": float(np.percentile(v, 5)), "q25": float(np.percentile(v, 25)),
        "q75": float(np.percentile(v, 75)), "q95": float(np.percentile(v, 95)),
        "frac_neg": float(np.mean(v < 0)), "count": int(v.size),
    }


def cell_key(row):
    param = f"xi={row['xi']}" if row["deformation_mode"] != "baseline" else ""
    # distinguish mode A (fixed xi grid) vs mode B (fixed delta grid) by which
    # of xi/delta is a round frozen value; store both
    return (row["shape_n"], row["scale_a0"], row["deformation_mode"],
            row["delta"], row["xi"])


def group_rows(rows):
    groups: dict = {}
    for r in rows:
        if r.get("solve_status") != "OK":
            continue
        groups.setdefault(cell_key(r), []).append(r)
    return groups


def ok_values(rows, metric):
    vals = [fnum(r, metric) for r in rows if r.get("branch_status") == "OK"]
    return np.array(vals, dtype=float)


def all_values(rows, metric):
    return np.array([fnum(r, metric) for r in rows], dtype=float)


def main() -> None:
    main_rows = load(OUTPUT_DIR / "pilot_main_rows.csv")
    conv_rows = load(OUTPUT_DIR / "pilot_conv_rows.csv")

    groups = group_rows(main_rows)
    agg_records = []
    for key, rows in sorted(groups.items()):
        n, a0, mode, delta, xi = key
        n_all = len(rows)
        n_amb = sum(1 for r in rows if r.get("branch_status") == "AMBIGUOUS")
        for metric in METRICS:
            s = stats(ok_values(rows, metric))
            agg_records.append({
                "shape_n": n, "scale_a0": a0, "deformation_mode": mode,
                "delta": delta, "xi": xi, "metric": metric,
                "frac_ambiguous": n_amb / n_all if n_all else math.nan,
                "n_placements": n_all, **s,
            })

    with open(OUTPUT_DIR / "pilot_aggregates.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(agg_records[0].keys()))
        writer.writeheader()
        writer.writerows(agg_records)

    # convergence: match conv points against 16x16 main rows
    conv_groups = group_rows(conv_rows)
    conv_records = []
    for key, rows32 in sorted(conv_groups.items()):
        n, a0, mode, delta, xi = key
        rows16 = groups.get(key, [])
        for metric in PRIMARY:
            v16 = ok_values(rows16, metric)
            v32 = ok_values(rows32, metric)
            s16, s32 = stats(v16), stats(v32)
            def rel(a, b):
                return abs(a - b) / abs(b) if b not in (0, math.nan) and abs(b) > 1e-12 else abs(a - b)
            mean_ch = rel(s32["mean"], s16["mean"])
            med_ch = rel(s32["median"], s16["median"])
            q_ch = max(rel(s32[q], s16[q]) for q in ("q5", "q25", "q75", "q95"))
            negfrac_ch = abs(s32["frac_neg"] - s16["frac_neg"])
            resolved = (mean_ch <= 0.02 and med_ch <= 0.02 and q_ch <= 0.05
                        and negfrac_ch <= 0.03)
            conv_records.append({
                "shape_n": n, "scale_a0": a0, "deformation_mode": mode,
                "delta": delta, "xi": xi, "metric": metric,
                "mean16": s16["mean"], "mean32": s32["mean"], "mean_relchange": mean_ch,
                "median16": s16["median"], "median32": s32["median"], "median_relchange": med_ch,
                "max_quantile_relchange": q_ch, "negfrac16": s16["frac_neg"],
                "negfrac32": s32["frac_neg"], "negfrac_change": negfrac_ch,
                "status": "RESOLVED" if resolved else "GRID_UNRESOLVED",
            })
    with open(OUTPUT_DIR / "pilot_convergence.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(conv_records[0].keys()))
        writer.writeheader()
        writer.writerows(conv_records)

    # distribution arrays for chi_split at the convergence-anchor cells
    dist_lines = []
    for n in ("2.0", "4.0"):
        for a0 in ("24.3", "33.7", "48.2"):
            key = (n, a0, "area_preserving", str(0.40 / float(a0)), "0.4")
            # xi=0.4 rows: find by matching xi value
            rows = [r for r in main_rows
                    if r["shape_n"] == n and r["scale_a0"] == a0
                    and r["deformation_mode"] == "area_preserving"
                    and abs(fnum(r, "xi") - 0.4) < 1e-9 and r.get("solve_status") == "OK"]
            if rows:
                v = ok_values(rows, "chi_split")
                v = v[np.isfinite(v)]
                if v.size:
                    dist_lines.append(f"{n},{a0},xi=0.4,chi_split,"
                                      + ",".join(f"{x:.5f}" for x in np.sort(v)))
    (OUTPUT_DIR / "pilot_chi_split_distributions_xi0.4.csv").write_text(
        "shape_n,scale_a0,param,metric,sorted_values\n" + "\n".join(dist_lines),
        encoding="utf-8")

    # --- summary ---
    lines = ["# Article-G pilot analysis (protocol sections 8-10)", ""]

    def cell_line(n, a0, mode, param_name, param_val, metric):
        rows = [r for r in main_rows
                if r["shape_n"] == str(n) and r["scale_a0"] == str(a0)
                and r["deformation_mode"] == mode
                and abs(fnum(r, param_name) - param_val) < 1e-9
                and r.get("solve_status") == "OK"]
        s = stats(ok_values(rows, metric))
        namb = sum(1 for r in rows if r.get("branch_status") == "AMBIGUOUS")
        return s, (namb / len(rows) if rows else math.nan)

    lines.append("## Primary signed observable chi_split (area_preserving, mode A)")
    lines.append("| n | a0 | xi | mean | median | std | q5 | q95 | frac_neg | frac_amb |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for n in (2.0, 4.0):
        for a0 in (24.3, 33.7, 48.2):
            for xi in (0.05, 0.10, 0.20, 0.40, 0.80):
                s, amb = cell_line(n, a0, "area_preserving", "xi", xi, "chi_split")
                lines.append(f"| {n} | {a0} | {xi} | {s['mean']:.4f} | {s['median']:.4f} "
                             f"| {s['std']:.4f} | {s['q5']:.4f} | {s['q95']:.4f} "
                             f"| {s['frac_neg']:.2f} | {amb:.2f} |")
    lines.append("")

    lines.append("## chi_center (area_preserving, mode A)")
    lines.append("| n | a0 | xi | mean | median | std | frac_neg |")
    lines.append("|---|---|---|---|---|---|---|")
    for n in (2.0, 4.0):
        for a0 in (24.3, 33.7, 48.2):
            for xi in (0.05, 0.10, 0.20, 0.40, 0.80):
                s, _ = cell_line(n, a0, "area_preserving", "xi", xi, "chi_center")
                lines.append(f"| {n} | {a0} | {xi} | {s['mean']:.4f} | {s['median']:.4f} "
                             f"| {s['std']:.4f} | {s['frac_neg']:.2f} |")
    lines.append("")

    lines.append("## Mode B (fixed delta) chi_split, delta->0")
    lines.append("| n | a0 | delta | mean | median | std | frac_neg |")
    lines.append("|---|---|---|---|---|---|---|")
    for n in (2.0, 4.0):
        for a0 in (24.3, 33.7, 48.2):
            for d in (0.001, 0.002, 0.004, 0.008):
                s, _ = cell_line(n, a0, "area_preserving", "delta", d, "chi_split")
                lines.append(f"| {n} | {a0} | {d} | {s['mean']:.4f} | {s['median']:.4f} "
                             f"| {s['std']:.4f} | {s['frac_neg']:.2f} |")
    lines.append("")

    lines.append("## Legacy vs sorted-baseline-corrected vs signed (n=4, a0=33.7, mode A xi)")
    lines.append("| xi | legacy_raw mean | sorted_bc mean | chi_split mean | chi_split median |")
    lines.append("|---|---|---|---|---|")
    for xi in (0.05, 0.10, 0.20, 0.40, 0.80):
        sl, _ = cell_line(4.0, 33.7, "area_preserving", "xi", xi, "legacy_raw_ratio")
        sb, _ = cell_line(4.0, 33.7, "area_preserving", "xi", xi, "sorted_baseline_corrected_ratio")
        sc, _ = cell_line(4.0, 33.7, "area_preserving", "xi", xi, "chi_split")
        lines.append(f"| {xi} | {sl['mean']:.4f} | {sb['mean']:.4f} | {sc['mean']:.4f} | {sc['median']:.4f} |")
    lines.append("")

    lines.append("## Convergence 16x16 -> 32x32 (primary metrics)")
    lines.append("| n | a0 | param | metric | mean16 | mean32 | mean_relΔ | qmax_relΔ | negfracΔ | status |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for c in conv_records:
        p = f"xi={c['xi']}" if abs(fnum(c, 'xi')) > 1e-9 and c['xi'] not in ('', 'nan') else f"delta={c['delta']}"
        lines.append(f"| {c['shape_n']} | {c['scale_a0']} | {p} | {c['metric']} "
                     f"| {c['mean16']:.4f} | {c['mean32']:.4f} | {c['mean_relchange']:.3f} "
                     f"| {c['max_quantile_relchange']:.3f} | {c['negfrac_change']:.3f} | {c['status']} |")
    lines.append("")

    (OUTPUT_DIR / "analysis_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("analysis done")


if __name__ == "__main__":
    main()
