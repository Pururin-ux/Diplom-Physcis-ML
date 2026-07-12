"""Article-G distributional analysis (protocol section 8): n=2 vs n=4 KS
distance, branch-crossing fraction, tail asymmetry, and scale narrowing of the
signed observable. Post-processing of the frozen pilot CSVs only.
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
from scipy import stats  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_g_signed_response"


def load(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def fnum(r, k):
    try:
        return float(r[k])
    except (ValueError, KeyError, TypeError):
        return math.nan


def ok_area_mode_a(rows, n, a0, xi):
    return [r for r in rows
            if r["shape_n"] == str(n) and r["scale_a0"] == str(a0)
            and r["deformation_mode"] == "area_preserving"
            and abs(fnum(r, "xi") - xi) < 1e-9
            and r.get("branch_status") == "OK" and r.get("solve_status") == "OK"]


def main():
    rows = load(OUTPUT_DIR / "pilot_main_rows.csv")
    lines = ["# Article-G distributional statistics (protocol section 8)", ""]

    lines.append("## n=2 vs n=4 chi_split distribution (area_preserving, mode A)")
    lines.append("| a0 | xi | KS dist | KS p | n2 std | n4 std | n2 q5 | n4 q5 | n2 fracneg | n4 fracneg |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for a0 in (24.3, 33.7, 48.2):
        for xi in (0.05, 0.10, 0.20, 0.40, 0.80):
            v2 = np.array([fnum(r, "chi_split") for r in ok_area_mode_a(rows, 2.0, a0, xi)])
            v4 = np.array([fnum(r, "chi_split") for r in ok_area_mode_a(rows, 4.0, a0, xi)])
            v2 = v2[np.isfinite(v2)]; v4 = v4[np.isfinite(v4)]
            ks, p = stats.ks_2samp(v2, v4)
            lines.append(
                f"| {a0} | {xi} | {ks:.3f} | {p:.2e} | {v2.std():.4f} | {v4.std():.4f} "
                f"| {np.percentile(v2,5):.4f} | {np.percentile(v4,5):.4f} "
                f"| {np.mean(v2<0):.2f} | {np.mean(v4<0):.2f} |")
    lines.append("")

    # branch-crossing fraction: tracked upper branch falls below tracked lower
    lines.append("## Branch-crossing fraction (Eplus_delta < Eminus_delta), area_preserving mode A")
    lines.append("| n | a0 | xi | cross_frac | n_ok |")
    lines.append("|---|---|---|---|---|")
    for n in (2.0, 4.0):
        for a0 in (24.3, 33.7, 48.2):
            for xi in (0.05, 0.40, 0.80):
                rr = ok_area_mode_a(rows, n, a0, xi)
                cross = [1 for r in rr if fnum(r, "Eplus_delta") < fnum(r, "Eminus_delta")]
                lines.append(f"| {n} | {a0} | {xi} | {len(cross)/len(rr):.3f} | {len(rr)} |")
    lines.append("")

    # scale narrowing: does std(chi_split) shrink ~ 1/a0 at fixed xi?
    lines.append("## Scale narrowing of std(chi_split) at xi=0.4 (mode A)")
    lines.append("| n | std@24.3 | std@33.7 | std@48.2 | ratio 24.3/48.2 | (a ratio=1.984) |")
    lines.append("|---|---|---|---|---|---|")
    for n in (2.0, 4.0):
        s = []
        for a0 in (24.3, 33.7, 48.2):
            v = np.array([fnum(r, "chi_split") for r in ok_area_mode_a(rows, n, a0, 0.40)])
            v = v[np.isfinite(v)]
            s.append(v.std())
        lines.append(f"| {n} | {s[0]:.4f} | {s[1]:.4f} | {s[2]:.4f} | {s[0]/s[2]:.2f} | |")
    lines.append("")

    # global central-tendency vs zero across all mode-A area cells
    lines.append("## Central tendency vs zero (all area_preserving mode-A OK cells)")
    all_means = []
    all_medians = []
    all_fracneg = []
    for n in (2.0, 4.0):
        for a0 in (24.3, 33.7, 48.2):
            for xi in (0.05, 0.10, 0.20, 0.40, 0.80):
                v = np.array([fnum(r, "chi_split") for r in ok_area_mode_a(rows, n, a0, xi)])
                v = v[np.isfinite(v)]
                all_means.append(v.mean()); all_medians.append(np.median(v))
                all_fracneg.append(np.mean(v < 0))
    am = np.array(all_means)
    lines.append(f"- chi_split cell means: range [{am.min():.4f}, {am.max():.4f}], "
                 f"|mean| median = {np.median(np.abs(am)):.4f}")
    lines.append(f"- chi_split cell frac_neg: range "
                 f"[{min(all_fracneg):.2f}, {max(all_fracneg):.2f}], median "
                 f"{np.median(all_fracneg):.2f} (0.5 = symmetric about zero)")
    lines.append("")

    (OUTPUT_DIR / "distribution_stats.md").write_text("\n".join(lines), encoding="utf-8")
    print("distribution stats done")


if __name__ == "__main__":
    main()
