"""Article-G pilot run (protocol.md sections 5, 7). Frozen grids only.

Produces:
- pilot_main_rows.csv : 16x16 placements, modes A (fixed xi) and B (fixed
  delta), area_preserving deformation, all shapes/scales; plus a labelled
  legacy_fixed_major_axis control slice (n=4, a0=33.7, mode A).
- pilot_conv_rows.csv  : 32x32 placements at the 5 pre-registered points.

Baselines are solved once per (n, a0, placement) and reused across all
deformations. Any per-solve failure is recorded, not fatal.
"""

from __future__ import annotations

import csv
from pathlib import Path
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import article_g_signed_response as g  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_g_signed_response"

FIELDS = [
    "shape_n", "scale_a0", "deformation_mode", "placement_grid", "delta", "xi",
    "dx", "dy", "theta", "n_sites_0", "n_sites_delta", "added_sites",
    "removed_sites", "symmetric_difference", "cut_bonds", "E0_0", "Eminus_0",
    "Eplus_0", "E0_delta", "Eminus_delta", "Eplus_delta", "S0_sorted",
    "Sdelta_sorted", "legacy_raw_ratio", "sorted_baseline_corrected_ratio",
    "chi_minus", "chi_plus", "chi_center", "chi_split", "overlap_11",
    "overlap_12", "overlap_21", "overlap_22", "assignment_score_best",
    "assignment_score_second", "assignment_margin", "subspace_sv_min",
    "subspace_sv_max", "branch_status", "symmetry_class_0",
    "symmetry_class_delta", "solve_status",
]


def grid_offsets(m: int):
    return [i / m for i in range(m)]


def cut_bonds_count(sites0: set, sites_d: set) -> int:
    removed = sites0 - sites_d
    bonds = 0
    for s in removed:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (s[0] + dx, s[1] + dy) in sites0:
                bonds += 1
    return bonds  # counts each cut half-bond from the removed side


def one_row(n, a0, mode, grid, dx, dy, delta, xi, spec0, sites0_set):
    try:
        ax, ay = g.semi_axes(a0, delta, mode)
        sd_sites = g.placed_sites(ax, ay, n, dx, dy, 0.0)
        specd = g.solve_sites(sd_sites, k=4)
        sdset = set(sd_sites)
        obs = g.track_and_observe(spec0, specd, g.symmetry_class(dx, dy, 0.0), dx, delta)
        row = {
            "shape_n": n, "scale_a0": a0, "deformation_mode": mode,
            "placement_grid": grid, "delta": delta, "xi": xi, "dx": dx, "dy": dy,
            "theta": 0.0, "n_sites_0": len(sites0_set),
            "n_sites_delta": len(sdset),
            "added_sites": len(sdset - sites0_set),
            "removed_sites": len(sites0_set - sdset),
            "symmetric_difference": len(sites0_set ^ sdset),
            "cut_bonds": cut_bonds_count(sites0_set, sdset),
            "symmetry_class_0": g.symmetry_class(dx, dy, 0.0),
            "symmetry_class_delta": g.symmetry_class(dx, dy, 0.0),
            "solve_status": "OK",
        }
        row.update({k: obs[k] for k in obs if k != "baseline_pair_kind"})
        return row
    except Exception as exc:  # noqa: BLE001 - record, do not abort the sweep
        return {
            "shape_n": n, "scale_a0": a0, "deformation_mode": mode,
            "placement_grid": grid, "delta": delta, "xi": xi, "dx": dx, "dy": dy,
            "theta": 0.0, "solve_status": f"FAIL:{type(exc).__name__}",
            "branch_status": "SOLVE_FAIL",
        }


def run_block(writer, n, a0, grid, mode_a_xi, mode_b_delta, legacy=False):
    offs = grid_offsets(grid)
    count = 0
    for dx in offs:
        for dy in offs:
            base_sites = g.placed_sites(a0, a0, n, dx, dy, 0.0)
            try:
                spec0 = g.solve_sites(base_sites, k=4)
            except Exception as exc:  # noqa: BLE001
                writer.writerow({
                    "shape_n": n, "scale_a0": a0, "deformation_mode": "baseline",
                    "placement_grid": grid, "dx": dx, "dy": dy, "theta": 0.0,
                    "solve_status": f"BASELINE_FAIL:{type(exc).__name__}",
                    "branch_status": "SOLVE_FAIL",
                })
                continue
            s0set = set(base_sites)
            mode = "legacy_fixed_major_axis" if legacy else "area_preserving"
            for xi in mode_a_xi:
                writer.writerow(one_row(n, a0, mode, grid, dx, dy, xi / a0, xi, spec0, s0set))
                count += 1
            for delta in mode_b_delta:
                writer.writerow(one_row(n, a0, mode, grid, dx, dy, delta, delta * a0, spec0, s0set))
                count += 1
    return count


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # main grid
    with open(OUTPUT_DIR / "pilot_main_rows.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for n in g.FROZEN_SHAPES:
            for a0 in g.FROZEN_SCALES:
                t0 = time.time()
                c = run_block(writer, n, a0, g.FROZEN_PLACEMENT_GRID,
                              g.FROZEN_MODE_A_XI, g.FROZEN_MODE_B_DELTA)
                fh.flush()
                print(f"main n={n} a0={a0}: {c} rows, {time.time()-t0:.0f}s", flush=True)
        # legacy control slice: n=4, a0=33.7, mode A only
        t0 = time.time()
        c = run_block(writer, 4.0, 33.7, g.FROZEN_PLACEMENT_GRID,
                      g.FROZEN_MODE_A_XI, (), legacy=True)
        fh.flush()
        print(f"legacy control n=4 a0=33.7: {c} rows, {time.time()-t0:.0f}s", flush=True)

    # convergence grid: 32x32 at 5 pre-registered points
    with open(OUTPUT_DIR / "pilot_conv_rows.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        # group conv points by (n, a0) to reuse baselines
        offs = grid_offsets(g.FROZEN_CONV_GRID)
        for n, a0, mode, kind, value in g.FROZEN_CONV_POINTS:
            t0 = time.time()
            xi_list = (value,) if kind == "xi" else ()
            delta_list = (value,) if kind == "delta" else ()
            c = 0
            for dx in offs:
                for dy in offs:
                    base_sites = g.placed_sites(a0, a0, n, dx, dy, 0.0)
                    try:
                        spec0 = g.solve_sites(base_sites, k=4)
                    except Exception:  # noqa: BLE001
                        continue
                    s0set = set(base_sites)
                    for xi in xi_list:
                        writer.writerow(one_row(n, a0, mode, g.FROZEN_CONV_GRID,
                                                dx, dy, xi / a0, xi, spec0, s0set))
                        c += 1
                    for delta in delta_list:
                        writer.writerow(one_row(n, a0, mode, g.FROZEN_CONV_GRID,
                                                dx, dy, delta, delta * a0, spec0, s0set))
                        c += 1
            fh.flush()
            print(f"conv n={n} a0={a0} {kind}={value}: {c} rows, {time.time()-t0:.0f}s", flush=True)

    print(f"PILOT DONE total {time.time()-t_start:.0f}s", flush=True)


if __name__ == "__main__":
    main()
