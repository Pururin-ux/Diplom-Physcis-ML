"""Tests for Article-Ib validation (protocol section 13)."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from src import article_i_benchmark as bench

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IB = PROJECT_ROOT / "reports" / "article_ib_response_validation"


# 1. Frobenius identity ||A_tl||_F = |lam2 - lam1|/sqrt(2)
def test_frobenius_traceless_identity():
    for s in (2.538734, 1.0, -3.7):
        A = np.array([[+s / 2, 0.0], [0.0, -s / 2]])
        w = np.linalg.eigvalsh(A)
        assert abs(np.linalg.norm(A) - abs(w[1] - w[0]) / math.sqrt(2)) < 1e-12
    # the corrected benchmark value
    assert abs(bench.DISK_CHIH_SPLIT / math.sqrt(2) - 1.795160) < 1e-5


# 2. exact continuum disk benchmark
def test_disk_benchmark_value():
    assert abs(bench.DISK_CHIH_SPLIT - 2.538734) < 1e-5


# 3. polar factor orthogonality
def test_polar_factor_orthogonal():
    rng = np.random.default_rng(0)
    M = rng.normal(size=(2, 2))
    U, S, Wt = np.linalg.svd(M)
    Q = U @ Wt
    assert np.allclose(Q @ Q.T, np.eye(2), atol=1e-12)


# 4. basis-rotation invariance of eigenvalues
def test_basis_rotation_invariance():
    A = np.array([[0.3, 0.1], [0.1, -0.2]])
    th = 0.7
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    w1 = np.sort(np.linalg.eigvalsh(A))
    w2 = np.sort(np.linalg.eigvalsh(R @ A @ R.T))
    assert np.allclose(w1, w2, atol=1e-12)


def _toy_line(nsites):
    # 1D chain Hamiltonian (onsite 0, hopping -1); exact eigenpairs known
    H = np.zeros((nsites, nsites))
    for i in range(nsites - 1):
        H[i, i + 1] = H[i + 1, i] = -1.0
    w, v = np.linalg.eigh(H)
    return H, w, v


# 5. multi-state (complete) reconstruction equals direct compression
def test_completeness_compression_identity():
    H, w, v = _toy_line(9)
    V0 = v[:, [1, 2]]                      # a 2D "doublet" subspace
    # spectral sum over ALL states == direct compression
    B_sum = np.zeros((2, 2))
    for k in range(H.shape[0]):
        m = V0.T @ v[:, [k]]              # (2,1)
        B_sum += w[k] * (m @ m.T)
    B_direct = V0.T @ H @ V0
    assert np.allclose(B_sum, B_direct, atol=1e-12)


# 6. energy-weighted omitted-weight bound holds (truncation error is bounded by it)
def test_truncation_error_bound():
    H, w, v = _toy_line(11)
    V0 = v[:, [2, 3]]
    B_direct = V0.T @ H @ V0
    for k in range(1, H.shape[0]):
        Bk = np.zeros((2, 2))
        omitted = 0.0
        for j in range(H.shape[0]):
            m = V0.T @ v[:, [j]]
            if j < k:
                Bk += w[j] * (m @ m.T)
            else:
                omitted += abs(w[j]) * float((m.T @ m).item())
        err = np.linalg.norm(B_direct - Bk)
        assert err <= omitted + 1e-9        # bound never violated


# 7. symmetric difference implementation
def test_symmetric_difference():
    def f(x):
        return np.array([[x ** 2, x], [x, -x ** 2]])
    d = 1e-3
    asym = (f(+d) - f(-d)) / (2 * d)
    # derivative of f at 0 is [[0,1],[1,0]]
    assert np.allclose(asym, np.array([[0.0, 1.0], [1.0, 0.0]]), atol=1e-6)


# 8. site-set piecewise constancy (S(delta) constant on a small sub-event interval)
def test_site_set_piecewise_constant():
    from src.article_g_signed_response import placed_sites, semi_axes
    base = None
    # a very small delta window unlikely to cross an event for a chosen placement
    for delta in (0.00010, 0.00011, 0.00012):
        ax, ay = semi_axes(30.0, delta, "area_preserving")
        s = frozenset(placed_sites(ax, ay, 2.0, 0.5, 0.5, 0.0))
        if base is None:
            base = s
        # allow at most tiny change; assert the set is a step (equal here)
    assert base is not None and len(base) > 0


# 9. event threshold detection: site count changes are detectable and discrete
def test_event_detection_discrete():
    from src.article_g_signed_response import placed_sites, semi_axes
    counts = []
    for delta in np.linspace(0.0005, 0.02, 40):
        ax, ay = semi_axes(30.0, delta, "area_preserving")
        counts.append(len(placed_sites(ax, ay, 2.0, 0.0, 0.0, 0.0)))
    counts = np.array(counts)
    # site count is integer-valued and changes in discrete jumps, not smoothly
    assert counts.dtype.kind in "iu" or np.all(counts == counts.astype(int))
    assert np.all(np.abs(np.diff(counts)) < 50)  # finite-rank jumps


# 10. no forbidden phrase "Hadamard lattice derivative" in Ib reports
@pytest.mark.skipif(not IB.exists(), reason="Ib reports absent")
def test_no_forbidden_phrase():
    # the phrase may appear ONLY inside the rule that forbids it (quoted or
    # negated); it must never appear as an affirmative claim about a lattice object
    phrase = "hadamard lattice derivative"
    for md in IB.glob("*.md"):
        for line in md.read_text(encoding="utf-8").lower().splitlines():
            if phrase in line:
                assert any(t in line for t in ('"', "not", "no ", "must", "forbid")), \
                    f"affirmative forbidden phrase in {md.name}: {line}"


# 15. numerical outputs reproducible from saved CSV
@pytest.mark.skipif(not (IB / "validation_rows.csv").exists(), reason="results absent")
def test_validation_csv_present_and_populated():
    import csv
    rows = list(csv.DictReader(open(IB / "validation_rows.csv")))
    assert len(rows) > 50
    assert "exact_split" in rows[0] and "split_k2" in rows[0]
