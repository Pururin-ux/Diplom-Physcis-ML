"""Falsification study of the superellipse zero-mode claims.

Runs the nine checks requested in the review and writes one CSV per check to
``reports/``. Nothing here is written to argue for the claims; each block is
designed so that a specific claim can fail.

Claims under test
-----------------
C1  nullity exceeds the sublattice-imbalance bound for most superellipses
C2  at aspect ratio 1 and centre (0,0), nullity = 2*floor(a) + 1
C3  C2 is independent of the shape exponent n
C4  the effect is a property of the *shape* rather than of the shape's
    registration against the lattice
C5  the excess over the imbalance bound is explained by maximum-matching
    deficiency
C6  the degeneracies are exact rather than an artefact of the eigenvalue
    threshold

Usage
-----
    python notebooks/zero_mode_falsification.py            # all checks
    python notebooks/zero_mode_falsification.py registration rotation
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.zero_modes import (  # noqa: E402
    analyse,
    bipartite_blocks,
    chiral_breaking_splitting,
    dense_hamiltonian,
    exact_nullity,
    localisation_metrics,
    null_space_density,
    superellipse_sites,
)

REPORTS = Path(__file__).resolve().parents[1] / "reports"
N_VALUES = (1.2, 2.0, 3.0, 4.0)


def write_csv(name: str, rows: list[dict]) -> Path:
    path = REPORTS / name
    if not rows:
        raise ValueError(f"no rows produced for {name}")
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {path.relative_to(REPORTS.parent)}  ({len(rows)} rows)")
    return path


def banner(text: str) -> None:
    print(f"\n=== {text} ===", flush=True)


# ---------------------------------------------------------------- check 1
def check_aspect_ratio_scan() -> list[dict]:
    """The AR scan that the earlier report quoted but never saved."""
    banner("1. aspect-ratio scan (a = 18, all n, AR 0.60..1.00 step 0.02)")
    rows = []
    for n in N_VALUES:
        for ar in np.round(np.arange(0.60, 1.0001, 0.02), 2):
            rows.append(analyse(18, float(ar), n))
    write_csv("zero_modes_aspect_ratio_scan.csv", rows)

    for n in N_VALUES:
        seq = [r for r in rows if r["n"] == n]
        counts = [r["exact_nullity"] for r in seq]
        print(f"  n={n}: nullity ranges {min(counts)}..{max(counts)}")
    exceed = sum(r["exact_nullity"] > r["imbalance_bound"] for r in rows)
    print(f"  C1: nullity > imbalance bound in {exceed}/{len(rows)} geometries")
    return rows


# ---------------------------------------------------------------- check 2
def check_exact_vs_numerical() -> list[dict]:
    """Modular rank against thresholded eigenvalues and against the SVD."""
    banner("2. exact modular rank vs threshold counting vs SVD")
    rows = []
    for n in N_VALUES:
        for a in (8, 12, 16, 20):
            for ar in (0.67, 0.83, 1.0):
                sites = superellipse_sites(a, ar, n)
                blocks = bipartite_blocks(sites)
                exact = exact_nullity(blocks)
                H = dense_hamiltonian(sites)
                w = np.sort(np.abs(np.linalg.eigvalsh(H)))
                singular = np.linalg.svd(blocks.T.astype(float), compute_uv=False)
                svd_rank = int(np.sum(singular > singular[0] * 1e-10))
                rows.append(
                    {
                        "a": a,
                        "aspect_ratio": ar,
                        "n": n,
                        "N_sites": blocks.n_sites,
                        "imbalance_bound": blocks.imbalance,
                        "exact_nullity": exact["exact_nullity"],
                        "primes_agree": exact["rank_agrees_across_primes"],
                        "svd_nullity": blocks.n_sites - 2 * svd_rank,
                        "nullity_tol_1e8": int(np.sum(w < 1e-8)),
                        "nullity_tol_1e12": int(np.sum(w < 1e-12)),
                        "largest_zero_abs_E": float(
                            w[exact["exact_nullity"] - 1]
                        )
                        if exact["exact_nullity"]
                        else 0.0,
                        "next_level_abs_E": float(w[exact["exact_nullity"]]),
                    }
                )
    write_csv("zero_modes_exact_vs_numerical.csv", rows)

    mismatch_svd = [r for r in rows if r["svd_nullity"] != r["exact_nullity"]]
    mismatch_tol = [r for r in rows if r["nullity_tol_1e8"] != r["exact_nullity"]]
    disagree = [r for r in rows if not r["primes_agree"]]
    print(f"  exact vs SVD mismatches:        {len(mismatch_svd)}/{len(rows)}")
    print(f"  exact vs tol=1e-8 mismatches:   {len(mismatch_tol)}/{len(rows)}")
    print(f"  geometries where primes differ: {len(disagree)}/{len(rows)}")
    worst = min(r["next_level_abs_E"] for r in rows)
    print(f"  C6: smallest separation to the first non-zero level: {worst:.3e}")
    return rows


# ---------------------------------------------------------------- check 3
def check_registration() -> list[dict]:
    """The decisive test: shape held fixed, position on the lattice varied."""
    banner("3. lattice registration (centre offsets)")
    offsets = [
        (0.0, 0.0),
        (0.1, 0.0),
        (0.25, 0.0),
        (0.5, 0.0),
        (0.75, 0.0),
        (0.25, 0.25),
        (0.5, 0.5),
        (0.5, 0.25),
        (0.33, 0.17),
    ]
    rows = []
    for n in N_VALUES:
        for a in (8, 12, 16):
            for ar in (0.67, 1.0):
                for dx, dy in offsets:
                    rows.append(analyse(a, ar, n, center=(dx, dy)))
    write_csv("zero_modes_registration_scan.csv", rows)

    print("  nullity by centre offset (AR = 1.0):")
    print(f"    {'offset':>12} " + " ".join(f"a={a},n={n}" for a in (8, 12, 16) for n in (1.2, 2.0)))
    for dx, dy in offsets:
        cells = []
        for a in (8, 12, 16):
            for n in (1.2, 2.0):
                match = [
                    r
                    for r in rows
                    if r["a"] == a
                    and r["n"] == n
                    and r["aspect_ratio"] == 1.0
                    and r["center_x"] == dx
                    and r["center_y"] == dy
                ]
                cells.append(f"{match[0]['exact_nullity']:>7}")
        print(f"    ({dx:.2f},{dy:.2f}) " + " ".join(cells))

    centred = [r for r in rows if r["center_x"] == 0.0 and r["center_y"] == 0.0]
    shifted = [r for r in rows if not (r["center_x"] == 0.0 and r["center_y"] == 0.0)]
    print(
        f"  C4: mean nullity centred {np.mean([r['exact_nullity'] for r in centred]):.1f}"
        f" vs shifted {np.mean([r['exact_nullity'] for r in shifted]):.1f}"
    )

    # The three high-symmetry registrations of a square lattice: a site, the
    # midpoint of a bond, and the centre of a plaquette.
    print("\n  high-symmetry registrations at AR = 1 (nullity vs a):")
    classes = {"site (0,0)": (0.0, 0.0), "bond (1/2,0)": (0.5, 0.0), "plaquette (1/2,1/2)": (0.5, 0.5)}
    a_values = (6, 8, 10, 12, 14, 16, 18, 20)
    print(f"    {'registration':>20} " + " ".join(f"a={a:<3}" for a in a_values))
    for label, center in classes.items():
        for n in (1.2, 2.0, 4.0):
            counts = [
                analyse(a, 1.0, n, center=center, numeric=False)["exact_nullity"]
                for a in a_values
            ]
            print(f"    {label + f', n={n}':>20} " + " ".join(f"{c:<5}" for c in counts))
            rows.extend(
                analyse(a, 1.0, n, center=center) for a in a_values
            )
    return rows


# ---------------------------------------------------------------- check 4
def check_rotation() -> list[dict]:
    """Shape and centre fixed, orientation relative to the lattice varied."""
    banner("4. rotation of the shape against the lattice axes")
    angles = np.round(np.arange(0.0, 46.0, 5.0), 1)
    rows = []
    for n in N_VALUES:
        for a in (12, 16):
            for ar in (0.67, 1.0):
                for deg in angles:
                    rows.append(
                        analyse(a, ar, n, theta=float(np.deg2rad(deg)))
                        | {"theta_deg": float(deg)}
                    )
    write_csv("zero_modes_rotation_scan.csv", rows)

    for n in N_VALUES:
        seq = [
            r["exact_nullity"]
            for r in rows
            if r["n"] == n and r["a"] == 16 and r["aspect_ratio"] == 1.0
        ]
        print(f"  n={n}, a=16, AR=1: nullity vs angle {seq}")
    return rows


# ---------------------------------------------------------------- check 5
def check_scaling_law() -> list[dict]:
    """Does nullity = 2*floor(a) + 1 survive non-integer a and other n?"""
    banner("5. the 2*floor(a)+1 law at AR = 1, integer and non-integer a")
    a_values = [6, 8, 10, 12, 14, 16, 18, 20, 8.5, 10.3, 12.5, 12.7, 16.5, 18.25]
    extra_n = (1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 8.0)
    rows = []
    for n in extra_n:
        for a in a_values:
            record = analyse(float(a), 1.0, n)
            record["predicted_2floor_a_plus_1"] = 2 * int(np.floor(a)) + 1
            record["law_holds"] = (
                record["exact_nullity"] == record["predicted_2floor_a_plus_1"]
            )
            record["n_columns_spanned"] = int(
                np.ptp(superellipse_sites(float(a), 1.0, n)[:, 0]) + 1
            )
            rows.append(record)
    write_csv("zero_modes_scaling_law.csv", rows)

    holds = sum(r["law_holds"] for r in rows)
    print(f"  C2/C3: law holds in {holds}/{len(rows)} geometries")
    cols = sum(r["exact_nullity"] == r["n_columns_spanned"] for r in rows)
    print(f"  alternative reading (nullity = number of columns spanned): {cols}/{len(rows)}")
    for n in extra_n:
        bad = [
            (r["a"], r["exact_nullity"], r["predicted_2floor_a_plus_1"])
            for r in rows
            if r["n"] == n and not r["law_holds"]
        ]
        if bad:
            print(f"    n={n} violations (a, got, predicted): {bad}")
    return rows


# ---------------------------------------------------------------- check 6
def check_matching(all_rows: list[dict]) -> None:
    """Is the excess over the imbalance bound structural or algebraic?"""
    banner("6. maximum-matching deficiency vs exact algebraic nullity")
    rows = [r for r in all_rows if "structural_nullity" in r and "exact_nullity" in r]
    if not rows:
        print("  no pooled geometries carried both counts; nothing to compare")
        return
    structural_equals_imbalance = sum(
        r["structural_nullity"] == r["imbalance_bound"] for r in rows
    )
    algebraic_exceeds_structural = sum(
        r["exact_nullity"] > r["structural_nullity"] for r in rows
    )
    gaps = [r["exact_nullity"] - r["structural_nullity"] for r in rows]
    print(f"  geometries examined: {len(rows)}")
    print(
        f"  structural nullity == imbalance bound: "
        f"{structural_equals_imbalance}/{len(rows)}"
    )
    print(
        f"  C5: algebraic nullity > structural nullity: "
        f"{algebraic_exceeds_structural}/{len(rows)}, "
        f"max gap {max(gaps)}, mean gap {np.mean(gaps):.1f}"
    )


# ---------------------------------------------------------------- check 7
def check_localisation() -> list[dict]:
    """Where the zero-mode weight actually sits."""
    banner("7. zero-mode localisation (projector density)")
    rows = []
    for n in N_VALUES:
        for a in (12, 16, 20):
            for ar in (0.67, 1.0):
                for center in ((0.0, 0.0), (0.5, 0.5)):
                    sites = superellipse_sites(a, ar, n, center=center)
                    blocks = bipartite_blocks(sites)
                    exact = exact_nullity(blocks)
                    H = dense_hamiltonian(sites)
                    density = null_space_density(H)
                    record = {
                        "a": a,
                        "aspect_ratio": ar,
                        "n": n,
                        "center_x": center[0],
                        "center_y": center[1],
                        "N_sites": blocks.n_sites,
                        "imbalance_bound": blocks.imbalance,
                        "exact_nullity": exact["exact_nullity"],
                    }
                    record.update(localisation_metrics(sites, density))
                    rows.append(record)
    write_csv("zero_modes_localisation.csv", rows)

    centred = [r for r in rows if r["center_x"] == 0.0 and r["exact_nullity"] > 0]
    if centred:
        print(
            f"  centred: boundary weight "
            f"{np.mean([r['boundary_weight_fraction'] for r in centred]):.3f}, "
            f"sublattice polarisation "
            f"{np.mean([r['sublattice_polarisation'] for r in centred]):.3f}, "
            f"IPR {np.mean([r['ipr'] for r in centred]):.4f}"
        )
    return rows


# ---------------------------------------------------------------- check 8
def check_chiral_breaking() -> list[dict]:
    """How the degenerate manifold responds to physical symmetry breaking."""
    banner("8. chiral-symmetry-breaking perturbations")
    rows = []
    for n in (1.2, 2.0, 4.0):
        for a in (12, 16):
            sites = superellipse_sites(a, 1.0, n)
            blocks = bipartite_blocks(sites)
            n_modes = exact_nullity(blocks)["exact_nullity"]
            for kind in ("onsite", "nnn"):
                for strength in (0.001, 0.01, 0.1):
                    result = chiral_breaking_splitting(
                        sites, kind, strength, n_modes, seed=0
                    )
                    rows.append(
                        {
                            "a": a,
                            "n": n,
                            "N_sites": blocks.n_sites,
                            "n_zero_modes": n_modes,
                            **result,
                        }
                    )
    write_csv("zero_modes_chiral_breaking.csv", rows)

    for kind in ("onsite", "nnn"):
        for strength in (0.001, 0.01, 0.1):
            sel = [
                r for r in rows if r["perturbation"] == kind and r["strength"] == strength
            ]
            ratio = np.mean([r["rms_shift"] / r["strength"] for r in sel])
            print(f"  {kind:>7} w={strength:<6}: mean rms_shift/strength = {ratio:.3f}")
    return rows


# ---------------------------------------------------------------- driver
CHECKS = {
    "aspect": check_aspect_ratio_scan,
    "exact": check_exact_vs_numerical,
    "registration": check_registration,
    "rotation": check_rotation,
    "law": check_scaling_law,
    "localisation": check_localisation,
    "chiral": check_chiral_breaking,
}


def main(argv: list[str]) -> None:
    selected = argv[1:] or list(CHECKS)
    started = time.time()
    pooled: list[dict] = []
    for name in selected:
        if name not in CHECKS:
            raise SystemExit(f"unknown check {name!r}; choose from {list(CHECKS)}")
        result = CHECKS[name]()
        if result:
            pooled.extend(result)
    if pooled:
        check_matching(pooled)
    print(f"\ntotal runtime {time.time() - started:.1f} s")


if __name__ == "__main__":
    main(sys.argv)
