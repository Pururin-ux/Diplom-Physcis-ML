"""Run article-F checks R7 (8x8 placement ensemble, several sizes) and R8
(exact Feshbach/T-matrix closure of the boundary-event problem).

Frozen definitions: reports/article_f_boundary_realization/protocol_addendum_3.md
(committed before execution, commit d777647).
"""

from __future__ import annotations

import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np  # noqa: E402

from src.geometry import (  # noqa: E402
    build_superellipse_dot_placed,
    placed_superellipse_sites,
)
from src.kwant_solver import lowest_energies_of_system  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_f_boundary_realization"

N_VAL = 4.0
R7_SIZES = (24.0, 33.0, 48.0)
R7_XI = (0.25, 0.5, 0.75, 1.5, 3.0)
GRID_8 = tuple(i / 8 for i in range(8))
R8_STEPS = ((0.75, 1.00), (1.00, 1.25))
R8_A = 33.0
TRUNCATIONS = (4, 20, 100, 500)


def r7_ensemble(lines: list[str]) -> None:
    lines.append("## R7. 8x8 placement ensemble, sizes 24/33/48")
    rows = []
    for a in R7_SIZES:
        for xi in R7_XI:
            r = 1.0 - xi / a
            ys = []
            for dx in GRID_8:
                for dy in GRID_8:
                    fsys = build_superellipse_dot_placed(
                        a, a * r, N_VAL, x0=dx, y0=dy
                    )
                    vals = lowest_energies_of_system(fsys, k=4)
                    ys.append(
                        ((vals[2] - vals[1]) / (vals[0] + 4.0)) / (1.0 - r)
                    )
            ys = np.array(ys)
            rows.append(
                {
                    "a": a,
                    "xi": xi,
                    "mean_y": ys.mean(),
                    "std_y": ys.std(),
                    "frac_suppressed": float(np.mean(ys < 1.0)),
                }
            )
            print(f"R7 done a={a} xi={xi}: mean={ys.mean():.3f}")
    with open(OUTPUT_DIR / "r7_ensemble_8x8.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    lines.append("| a | xi | mean y (8x8) | std | frac y<1 |")
    lines.append("|---|---|---|---|---|")
    for row in rows:
        lines.append(
            f"| {row['a']:.0f} | {row['xi']:.2f} | {row['mean_y']:.3f} "
            f"| {row['std_y']:.3f} | {row['frac_suppressed']:.2f} |"
        )
    lines.append("")
    r6 = list(csv.DictReader(open(OUTPUT_DIR / "r6_ensemble_rows.csv")))
    lines.append("4x4 (R6) vs 8x8 means at a = 33 (shared xi):")
    for xi in R7_XI:
        m4 = np.mean([float(r["y"]) for r in r6 if float(r["xi"]) == xi])
        m8 = next(
            r["mean_y"] for r in rows if r["a"] == 33.0 and r["xi"] == xi
        )
        lines.append(f"- xi={xi}: 4x4 mean={m4:.3f}, 8x8 mean={m8:.3f}")
    lines.append("")


def dense_eig(a: float, b: float, n: float):
    fsys = build_superellipse_dot_placed(a, b, n)
    h = fsys.hamiltonian_submatrix(sparse=True).toarray().real
    vals, vecs = np.linalg.eigh(h)
    tag_index = {tuple(s.tag): i for i, s in enumerate(fsys.sites)}
    return vals, vecs, tag_index


def r8_exact_closure(lines: list[str]) -> None:
    lines.append("## R8. Exact Feshbach/T-matrix closure")
    out_rows = []
    for xi_old, xi_new in R8_STEPS:
        b_old = R8_A - xi_old
        b_new = R8_A - xi_new
        vals, vecs, tag_index = dense_eig(R8_A, b_old, N_VAL)
        old_sites = set(placed_superellipse_sites(R8_A, b_old, N_VAL))
        new_sites = set(placed_superellipse_sites(R8_A, b_new, N_VAL))
        removed = sorted(old_sites - new_sites)
        ridx = [tag_index[s] for s in removed]
        vr = vecs[ridx, :]  # (|R|, N) rows of eigenvectors on removed sites

        fsys_new = build_superellipse_dot_placed(R8_A, b_new, N_VAL)
        direct = lowest_energies_of_system(fsys_new, k=4)

        def det_sign(e: float, m: int | None) -> float:
            if m is None:
                weights = 1.0 / (e - vals)
                g = (vr * weights) @ vr.T
            else:
                weights = 1.0 / (e - vals[:m])
                g = (vr[:, :m] * weights) @ vr[:, :m].T
            sign, _ = np.linalg.slogdet(g)
            return sign

        def find_zero(e_lo: float, e_hi: float, m: int | None) -> float:
            lo, hi = e_lo + 1e-13, e_hi - 1e-13
            s_lo = det_sign(lo, m)
            if s_lo == det_sign(hi, m):
                return float("nan")
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                if det_sign(mid, m) == s_lo:
                    lo = mid
                else:
                    hi = mid
                if hi - lo < 1e-13:
                    break
            return 0.5 * (lo + hi)

        # low-lying old levels are vals[0..3]; doublet is vals[1], vals[2]
        intervals = [(vals[1], vals[2]), (vals[2], vals[3])]
        for label, (lo, hi), direct_val in zip(
            ("E1", "E2"), intervals, (direct[1], direct[2])
        ):
            pred_full = find_zero(lo, hi, None)
            row = {
                "step": f"xi {xi_old}->{xi_new}",
                "removed": len(removed),
                "level": label,
                "direct": direct_val,
                "pred_full": pred_full,
                "abs_err_full": abs(pred_full - direct_val),
            }
            for m in TRUNCATIONS:
                pred_m = find_zero(lo, hi, m)
                row[f"pred_m{m}"] = pred_m
                row[f"err_kin_m{m}"] = (
                    abs(pred_m - direct_val) / (direct_val + 4.0)
                )
            out_rows.append(row)
            lines.append(
                f"- {row['step']} {label}: direct={direct_val:.12f}, "
                f"exact-closure={pred_full:.12f}, |err|={row['abs_err_full']:.2e}"
            )
        print(f"R8 done step {xi_old}->{xi_new}")
    with open(OUTPUT_DIR / "r8_exact_closure.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    ok = all(r["abs_err_full"] < 1e-9 for r in out_rows)
    lines.append(
        f"- frozen PASS criterion (|err| < 1e-9 for all levels): "
        f"{'PASS' if ok else 'FAIL'}"
    )
    lines.append("")
    lines.append("Truncation study (relative error on the E+4 scale):")
    lines.append("| step | level | m=4 | m=20 | m=100 | m=500 |")
    lines.append("|---|---|---|---|---|---|")
    for r in out_rows:
        lines.append(
            f"| {r['step']} | {r['level']} | "
            + " | ".join(f"{r[f'err_kin_m{m}']:.2e}" for m in TRUNCATIONS)
            + " |"
        )
    lines.append("")


def main() -> None:
    lines = [
        "# Article-F checks R7-R8",
        "",
        "Frozen definitions: protocol_addendum_3.md (commit d777647).",
        "",
    ]
    r8_exact_closure(lines)
    print("R8 complete")
    r7_ensemble(lines)
    print("R7 complete")
    (OUTPUT_DIR / "r7_r8_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("R7-R8 complete")


if __name__ == "__main__":
    main()
