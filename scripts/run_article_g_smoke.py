"""Article-G smoke tests (protocol.md section 6). All must PASS before the pilot.

Writes reports/article_g_signed_response/smoke_report.md.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np  # noqa: E402

from src import article_g_signed_response as g  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_g_signed_response"


def solve(a_x, a_y, n, x0, y0, k=4):
    return g.solve_sites(g.placed_sites(a_x, a_y, n, x0, y0, 0.0), k=k)


def check_1_generic_split():
    s0 = solve(12.0, 10.0, 2.0, 0.31, 0.17)
    s = s0.energies[2] - s0.energies[1]
    return s > 1e-4, f"generic placement baseline S(0)={s:.3e} (expect >0)"


def check_2_site_c4v():
    s0 = solve(9.0, 9.0, 2.0, 0.0, 0.0)
    split = abs(s0.energies[2] - s0.energies[1])
    cls = g.symmetry_class(0.0, 0.0, 0.0)
    return split < 1e-9 and cls == "C4v", (
        f"site-centered: class={cls}, doublet split={split:.2e} (expect ~0)"
    )


def check_3_plaquette_c4v():
    s0 = solve(9.0, 9.0, 2.0, 0.5, 0.5)
    split = abs(s0.energies[2] - s0.energies[1])
    cls = g.symmetry_class(0.5, 0.5, 0.0)
    return split < 1e-9 and cls == "C4v", (
        f"plaquette-centered: class={cls}, doublet split={split:.2e} (expect ~0)"
    )


def check_4_no_pure_c4():
    grid = [i / g.FROZEN_PLACEMENT_GRID for i in range(g.FROZEN_PLACEMENT_GRID)]
    classes = {g.symmetry_class(dx, dy, 0.0) for dx in grid for dy in grid}
    ok = "C4" not in classes and "C4v" in classes
    return ok, f"pilot placement classes = {sorted(classes)}"


def check_5_order_swap_tracking():
    s0 = solve(12.0, 10.0, 2.0, 0.31, 0.17)  # generic, split
    # artificial deformed spectrum: swap the doublet eigenvectors so the
    # lower-energy deformed state carries the baseline HIGHER character.
    sd = g.Spectrum(s0.sites, s0.index, s0.energies.copy(), s0.vectors.copy())
    sd.vectors[:, [1, 2]] = s0.vectors[:, [2, 1]]
    res = g.track_and_observe(s0, sd, "C1", 0.31, 0.02)
    # baseline minus should track to the deformed state with matching character,
    # i.e. the swap assignment; legacy raw uses sorted gap regardless.
    swapped = res["overlap_12"] + res["overlap_21"] > res["overlap_11"] + res["overlap_22"]
    return swapped, (
        f"overlap identity={res['overlap_11']+res['overlap_22']:.3f} "
        f"swap={res['overlap_12']+res['overlap_21']:.3f} -> tracking follows overlap"
    )


def check_6_union_embedding():
    s0 = solve(10.0, 10.0, 4.0, 0.0, 0.0)
    ax, ay = g.semi_axes(10.0, 0.02, "area_preserving")
    sd = solve(ax, ay, 4.0, 0.0, 0.0)
    Va, Vb = g.embed_pair(s0, (1, 2), sd, (1, 2))
    norms = [np.linalg.norm(Va[:, 0]), np.linalg.norm(Va[:, 1]),
             np.linalg.norm(Vb[:, 0]), np.linalg.norm(Vb[:, 1])]
    self_a = Va.T @ Va
    ok = all(abs(nn - 1) < 1e-9 for nn in norms) and np.allclose(self_a, np.eye(2), atol=1e-9)
    return ok, f"union size differs, embedded column norms={[round(x,6) for x in norms]}"


def check_7_basis_invariance():
    s0 = solve(8.0, 8.0, 2.0, 0.0, 0.0)  # C4v exact doublet
    ax, ay = g.semi_axes(8.0, 0.02, "area_preserving")
    sd = solve(ax, ay, 2.0, 0.0, 0.0)
    base = g.track_and_observe(s0, sd, "C4v", 0.0, 0.02)
    rng = np.random.default_rng(0)
    ang = rng.uniform(0, 2 * math.pi)
    rot = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    s0r = g.Spectrum(s0.sites, s0.index, s0.energies.copy(), s0.vectors.copy())
    s0r.vectors[:, 1:3] = s0.vectors[:, 1:3] @ rot
    rotd = g.track_and_observe(s0r, sd, "C4v", 0.0, 0.02)
    dc = abs(base["chi_center"] - rotd["chi_center"])
    ds = abs(base["chi_split"] - rotd["chi_split"])
    return dc < 1e-9 and ds < 1e-9, f"d(chi_center)={dc:.2e}, d(chi_split)={ds:.2e}"


def check_8_legacy_confound():
    s0 = solve(12.0, 10.0, 2.0, 0.29, 0.13)
    ax, ay = g.semi_axes(11.0, 0.02, "area_preserving")
    sd = solve(ax, ay, 2.0, 0.29, 0.13)
    res = g.track_and_observe(s0, sd, "C1", 0.29, 0.02)
    lhs = res["legacy_raw_ratio"]
    rhs = res["S0_sorted"] / 0.02 + res["sorted_baseline_corrected_ratio"]
    return abs(lhs - rhs) < 1e-9, (
        f"legacy_raw={lhs:.6f} vs S0/delta+sorted_bc={rhs:.6f}, "
        f"S0={res['S0_sorted']:.3e}"
    )


CHECKS = [
    ("1 generic nonzero S(0,p)", check_1_generic_split),
    ("2 site-centered C4v degeneracy", check_2_site_c4v),
    ("3 plaquette-centered C4v degeneracy", check_3_plaquette_c4v),
    ("4 no pure-C4-without-mirror in pilot grid", check_4_no_pure_c4),
    ("5 order-swap: tracking follows overlap", check_5_order_swap_tracking),
    ("6 union-space embedding", check_6_union_embedding),
    ("7 basis invariance in degenerate subspace", check_7_basis_invariance),
    ("8 legacy confound decomposition identity", check_8_legacy_confound),
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = ["# Article-G smoke report (protocol.md section 6)", ""]
    all_pass = True
    for name, fn in CHECKS:
        ok, detail = fn()
        all_pass &= ok
        lines.append(f"- [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    lines.append("")
    lines.append(f"## Overall: {'ALL PASS' if all_pass else 'FAILURE'}")
    (OUTPUT_DIR / "smoke_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("ALL PASS" if all_pass else "FAILURE")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
