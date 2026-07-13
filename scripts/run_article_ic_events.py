"""Article-Ic event micro-pilot (frozen protocol). Exact event enumeration and
finite-rank spectral marks for a few placements. Event-mechanism pilot, NOT a
placement-distribution pilot. No 64^2, no broad grids.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np  # noqa: E402
from scipy.sparse import identity  # noqa: E402

from src.article_g_signed_response import symmetry_class  # noqa: E402
from src import article_ic_events as ic  # noqa: E402

OUT = PROJECT_ROOT / "reports" / "article_ic_event_shifts"
SHAPES = (2.0, 4.0)
SIZES = (24.3, 33.7)
XIMAX = 0.8
PLACEMENTS = {
    "C4v": [(0.0, 0.0), (0.5, 0.5)],
    "Cs_axis": [(0.5, 0.3), (0.0, 0.4)],
    "C1": [(0.31, 0.17), (0.23, 0.41), (0.6875, 0.75), (0.13, 0.62)],
}


def event_marks(n, a0, x0, y0):
    dmax = XIMAX / a0
    # sites are placed with center offset (x0,y0): shift the lattice by -center
    def sites_at(delta):
        ax, ay = ic.semi_axes(a0, delta)
        R = int(math.ceil(max(ax, ay))) + 3
        cx, cy = int(round(x0)), int(round(y0))
        return frozenset(
            (x, y) for x in range(cx - R, cx + R + 1) for y in range(cy - R, cy + R + 1)
            if abs((x - x0) / ax) ** n + abs((y - y0) / ay) ** n <= 1.0
        )

    # exact thresholds using shifted coordinates
    ax, ay = ic.semi_axes(a0, dmax)
    R = int(math.ceil(max(ax, ay))) + 3
    cx, cy = int(round(x0)), int(round(y0))
    ths = set()
    for x in range(cx - R, cx + R + 1):
        for y in range(cy - R, cy + R + 1):
            for d in ic.site_thresholds(x - x0, y - y0, a0, n, dmax):
                ths.add(round(d, 12))
    ths = sorted(ths)
    bundled = []
    for d in ths:
        if bundled and abs(d - bundled[-1]) < 1e-7:
            continue
        bundled.append(d)

    S0 = sites_at(0.0)
    # Build the ordered sequence of DISTINCT domains once (midpoints between
    # consecutive thresholds), and solve each spectrum a single time.
    mids = [0.0]
    for i, d in enumerate(bundled):
        nxt = bundled[i + 1] if i + 1 < len(bundled) else dmax + 1e-6
        mids.append(0.5 * (d + min(nxt, dmax + 1e-6)))
    seq = []
    prev = None
    for m in mids:
        S = sites_at(min(m, dmax))
        if prev is None or S != prev:
            seq.append((min(m, dmax), S))
            prev = S
    specs = [ic.low_spectrum(S, k=4) for (_, S) in seq]
    e0v = specs[0][0]
    K_ref = e0v[0] + 4.0

    rows = []
    site_sets = []
    ev_index = 0
    for i in range(1, len(seq)):
        d = seq[i][0]
        d_left, d_right = seq[i - 1][0], seq[i][0]
        Sm, Sp = seq[i - 1][1], seq[i][1]
        added = sorted(set(Sp) - set(Sm))
        removed = sorted(set(Sm) - set(Sp))
        if not added and not removed:
            continue
        em, vm, Hm, idxm = specs[i - 1]
        ep, vp, Hp, idxp = specs[i]
        # marks
        gap_b, gap_a = em[2] - em[1], ep[2] - ep[1]
        cen_b, cen_a = 0.5 * (em[1] + em[2]), 0.5 * (ep[1] + ep[2])
        dE = [ep[j] - em[j] for j in range(4)]
        dgap = gap_a - gap_b
        dcen = cen_a - cen_b
        # changed edges (symmetric difference of bond sets)
        Bm, Bp = ic.bonds(Sm), ic.bonds(Sp)
        changed_edges = len(Bm ^ Bp)
        # geometry marks
        chg = added + removed
        xs = [s[0] for s in chg]
        ys = [s[1] for s in chg]
        # coherent row/column: max run of changed sites sharing a row/column
        def max_run(coords, axis):
            from collections import defaultdict
            lines = defaultdict(list)
            for (x, y) in coords:
                lines[y if axis == 0 else x].append(x if axis == 0 else y)
            best = 0
            for _, vals in lines.items():
                vals = sorted(vals)
                run = cur = 1
                for a, b in zip(vals, vals[1:]):
                    cur = cur + 1 if b == a + 1 else 1
                    run = max(run, cur)
                best = max(best, run)
            return best
        max_row = max_run(chg, 0) if chg else 0
        max_col = max_run(chg, 1) if chg else 0
        na = ic.normal_angle((xs[0] if xs else 0) - x0, (ys[0] if ys else 0) - y0,
                             a0, n, d) if chg else 0.0
        na_mod = min(abs(na % 90.0), 90.0 - abs(na % 90.0))
        axis_aligned = 1 if (na_mod < 5.0) else 0
        etype = ("SWAP" if (added and removed) else
                 ("MULTI_ADD" if len(added) > 1 else "ADD_ONLY") if added else
                 ("MULTI_REMOVE" if len(removed) > 1 else "REMOVE_ONLY"))
        if max_row >= 3 or max_col >= 3:
            etype = "COHERENT_ROW" if max_row >= max_col else "COHERENT_COLUMN"
        # eigenfunction-weighted predictors (from the BEFORE state Sm)
        def mode_boundary_weight(col):
            w = 0.0
            for s in chg:
                for dx, dy in ic.NEIGH:
                    nb = (s[0] + dx, s[1] + dy)
                    if nb in idxm:
                        w += vm[idxm[nb], col] ** 2
            return w
        w1 = mode_boundary_weight(1)
        w2 = mode_boundary_weight(2)
        # changed-bond matrix element differential (doublet)
        def bond_me(ci, cj):
            acc = 0.0
            for (r, s) in (Bm ^ Bp):
                for (rr, ss) in ((r, s), (s, r)):
                    if rr in idxm and ss in idxm:
                        acc += vm[idxm[rr], ci] * vm[idxm[ss], cj]
            return acc
        me11, me22 = bond_me(1, 1), bond_me(2, 2)
        # subspace rotation (projector distance, principal angles)
        pd, pa1, pa2 = ic.projector_distance(vm, idxm, (1, 2), vp, idxp, (1, 2))
        # frozen-mode shift: Rayleigh quotient of old doublet modes in new domain
        def frozen_shift(col):
            # embed old mode col into Sp (large-barrier restrict), Rayleigh quotient
            V = np.zeros(Hp.shape[0])
            for s, li in idxp.items():
                i0 = idxm.get(s)
                if i0 is not None:
                    V[li] = vm[i0, col]
            nrm = V @ V
            if nrm < 1e-12:
                return float("nan")
            Hp4 = Hp + 4.0 * identity(Hp.shape[0], format="csc")
            return float(V @ (Hp4 @ V) / nrm) - (em[col] + 4.0)

        fz1 = frozen_shift(1)
        fz2 = frozen_shift(2)
        row = {
            "shape_n": n, "scale_a0": a0, "placement_x": x0, "placement_y": y0,
            "symmetry_class": symmetry_class(x0, y0, 0.0), "theta": 0.0,
            "event_index": ev_index, "delta_event": d, "xi_event": a0 * d,
            "delta_left": d_left, "delta_right": d_right,
            "event_type": etype, "added_count": len(added),
            "removed_count": len(removed), "net_site_change": len(added) - len(removed),
            "changed_edge_count": changed_edges, "event_rank": len(added) + len(removed),
            "max_row_length": max_row, "max_column_length": max_col,
            "local_normal_angle": na, "axis_aligned_normal": axis_aligned,
            "flatness_proxy": na_mod,
            "E0_before": em[0], "E1_before": em[1], "E2_before": em[2], "E3_before": em[3],
            "E0_after": ep[0], "E1_after": ep[1], "E2_after": ep[2], "E3_after": ep[3],
            "gap_before": gap_b, "gap_after": gap_a, "center_before": cen_b,
            "center_after": cen_a,
            "delta_E0": dE[0], "delta_E1": dE[1], "delta_E2": dE[2],
            "delta_gap": dgap, "delta_center": dcen,
            "eta_E0": dE[0] / K_ref, "eta_E1": dE[1] / K_ref, "eta_E2": dE[2] / K_ref,
            "eta_gap": dgap / K_ref, "eta_center": dcen / K_ref,
            "projector_distance": pd, "principal_angle_1": pa1, "principal_angle_2": pa2,
            "frozen_mode_shift_1": fz1, "frozen_mode_shift_2": fz2,
            "relaxation_residual_1": (dE[1]) - fz1, "relaxation_residual_2": (dE[2]) - fz2,
            "bare_event_size": len(added) + len(removed),
            "boundary_weight_mode1": w1, "boundary_weight_mode2": w2,
            "changed_bond_weight": me22 - me11, "schur_predictor": (w2 - w1),
            "K_ref": K_ref,
        }
        rows.append(row)
        site_sets.append({"shape_n": n, "scale_a0": a0, "placement_x": x0,
                          "placement_y": y0, "event_index": ev_index,
                          "added": added, "removed": removed})
        ev_index += 1
        prevS = Sp
    return rows, site_sets


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_rows, all_sets = [], []
    for n in SHAPES:
        for cls, plist in PLACEMENTS.items():
            for (x0, y0) in plist:
                for a0 in SIZES:
                    r, ss = event_marks(n, a0, x0, y0)
                    all_rows.extend(r)
                    all_sets.extend(ss)
        print(f"events n={n} done: {len(all_rows)} rows so far", flush=True)
    fields = list(all_rows[0].keys())
    with open(OUT / "event_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(all_rows)
    with open(OUT / "event_site_sets.jsonl", "w") as fh:
        for s in all_sets:
            fh.write(json.dumps(s) + "\n")

    # event-process summary + telescoping check per placement
    summ = []
    def key(r):
        return (r["shape_n"], r["scale_a0"], r["placement_x"], r["placement_y"])
    from collections import defaultdict
    groups = defaultdict(list)
    for r in all_rows:
        groups[key(r)].append(r)
    for k, rs in groups.items():
        rs = sorted(rs, key=lambda r: r["delta_event"])
        Jg = sum(r["eta_gap"] for r in rs)
        Vg = sum(r["eta_gap"] ** 2 for r in rs)
        absvar = sum(abs(r["eta_gap"]) for r in rs)
        # telescoping: sum of delta_gap == gap(final) - gap(initial)
        tele = sum(r["delta_gap"] for r in rs)
        gap_span = rs[-1]["gap_after"] - rs[0]["gap_before"]
        biggest = max(abs(r["eta_gap"]) for r in rs) if rs else 0.0
        summ.append({
            "shape_n": k[0], "scale_a0": k[1], "placement_x": k[2], "placement_y": k[3],
            "symmetry_class": rs[0]["symmetry_class"], "n_events": len(rs),
            "J_gap": Jg, "V_gap": Vg, "abs_variation_gap": absvar,
            "largest_event_frac": biggest / absvar if absvar > 0 else float("nan"),
            "telescope_sum_delta_gap": tele, "gap_span_direct": gap_span,
            "telescope_residual": tele - gap_span,
        })
    with open(OUT / "event_process_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summ[0].keys()))
        w.writeheader()
        w.writerows(summ)
    print("event pilot done:", len(all_rows), "events,", len(summ), "placements")


if __name__ == "__main__":
    main()
