"""Continuum Dirichlet eigenvalues of superellipses via the method of
particular solutions with a fundamental-solution basis (Betcke-Trefethen
interior-point QR regularization).

Frozen protocol: reports/article_f_boundary_realization/protocol.md, section 4.
Acceptance gate: circle must reproduce j01^2 and j11^2 to relative 1e-6 and
values must be stable under basis-size increase; failures are reported, not
silently replaced.
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
from scipy.linalg import qr, svdvals  # noqa: E402
from scipy.optimize import minimize_scalar  # noqa: E402
from scipy.special import y0 as bessel_y0  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "article_f_boundary_realization"

J01 = 2.404825557695773
J11 = 3.831705970207512
N_VALUES = (1.2, 2.0, 3.0, 4.0)
CHARGE_FACTOR = 1.2
K_MIN, K_MAX, K_STEP = 2.0, 4.7, 0.002
BASIS_SIZES = (100, 160)
INTERIOR_POINTS = 60
RNG_SEED = 42


def boundary_points(n: float, count: int, scale: float = 1.0) -> np.ndarray:
    t = np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)
    ct, st = np.cos(t), np.sin(t)
    x = np.sign(ct) * np.abs(ct) ** (2.0 / n)
    y = np.sign(st) * np.abs(st) ** (2.0 / n)
    return scale * np.column_stack([x, y])


def interior_points(n: float, count: int) -> np.ndarray:
    rng = np.random.default_rng(RNG_SEED)
    pts = []
    while len(pts) < count:
        cand = rng.uniform(-1.0, 1.0, size=(count * 4, 2))
        mask = np.abs(cand[:, 0]) ** n + np.abs(cand[:, 1]) ** n <= 0.9
        pts.extend(cand[mask].tolist())
    return np.array(pts[:count])


def make_sigma_function(n: float, n_charges: int):
    bpts = boundary_points(n, 3 * n_charges)
    ipts = interior_points(n, INTERIOR_POINTS)
    charges = boundary_points(n, n_charges, scale=CHARGE_FACTOR)
    all_pts = np.vstack([bpts, ipts])
    dists = np.linalg.norm(all_pts[:, None, :] - charges[None, :, :], axis=2)
    n_b = len(bpts)

    def sigma(k: float) -> float:
        a_mat = bessel_y0(k * dists)
        q_mat, _ = qr(a_mat, mode="economic")
        return float(svdvals(q_mat[:n_b, :])[-1])

    return sigma


def find_minima(sigma, k_lo: float, k_hi: float) -> list[tuple[float, float]]:
    ks = np.arange(k_lo, k_hi, K_STEP)
    vals = np.array([sigma(k) for k in ks])
    minima = []
    for i in range(1, len(ks) - 1):
        if vals[i] < vals[i - 1] and vals[i] < vals[i + 1] and vals[i] < 0.5:
            res = minimize_scalar(
                sigma,
                bounds=(ks[i - 1], ks[i + 1]),
                method="bounded",
                options={"xatol": 1e-10},
            )
            minima.append((float(res.x), float(res.fun)))
    return minima


def eigenvalues_for(n: float, n_charges: int) -> list[tuple[float, float]]:
    sigma = make_sigma_function(n, n_charges)
    return [(k * k, s) for k, s in find_minima(sigma, K_MIN, K_MAX)]


def area_factor(n: float) -> float:
    return 4.0 * math.gamma(1 + 1 / n) ** 2 / math.gamma(1 + 2 / n)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    lines = ["# Continuum MFS/MPS reference for superellipses (a = b = 1)", ""]

    for n in N_VALUES:
        results = {}
        for basis in BASIS_SIZES:
            eigs = eigenvalues_for(n, basis)
            results[basis] = eigs
        small = [lam for lam, _ in results[BASIS_SIZES[0]]]
        large = [lam for lam, _ in results[BASIS_SIZES[1]]]
        paired = []
        for lam in large:
            close = [ls for ls in small if abs(ls - lam) / lam < 1e-3]
            drift = min((abs(ls - lam) / lam for ls in close), default=float("nan"))
            paired.append((lam, drift))
        lam1 = paired[0][0]
        lam2 = paired[1][0] if len(paired) > 1 else float("nan")
        stable = all(
            not math.isnan(d) and d < 1e-6 for _, d in paired[:2]
        )
        gate = "PASS" if stable else "UNSTABLE"
        if n == 2.0:
            err1 = abs(lam1 - J01**2) / J01**2
            err2 = abs(lam2 - J11**2) / J11**2
            gate = "PASS" if (err1 < 1e-6 and err2 < 1e-6 and stable) else "FAIL"
            lines.append(
                f"- circle validation: lam1 err {err1:.2e}, lam2 err {err2:.2e}"
            )
        lam_a = lam1 * area_factor(n) / math.pi
        q0 = lam2 / lam1 - 1.0
        rows.append(
            {
                "n": n,
                "lambda1": lam1,
                "lambda2": lam2,
                "lam1_drift_rel": paired[0][1],
                "lam2_drift_rel": paired[1][1] if len(paired) > 1 else float("nan"),
                "lamA_an_over_pi": lam_a,
                "Q0_continuum": q0,
                "gate": gate,
            }
        )
        lines.append(
            f"## n = {n}: lambda1 = {lam1:.8f}, lambda2 = lambda3 = {lam2:.8f} "
            f"(drift {paired[0][1]:.1e}/{paired[1][1] if len(paired) > 1 else float('nan'):.1e}), "
            f"lam1*A/pi = {lam_a:.6f}, Q0 = {q0:.6f}, gate = {gate}"
        )
        print(f"n={n}: lam1={lam1:.8f} lam2={lam2:.8f} gate={gate}")

    with open(OUTPUT_DIR / "continuum_mfs_values.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    (OUTPUT_DIR / "continuum_mfs_summary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
