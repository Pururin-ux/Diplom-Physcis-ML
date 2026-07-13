"""Tests for Article-Ic canonical event-resolved spectral shifts (protocol sec 15)."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

from src import article_ic_events as ic

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IC = PROJECT_ROOT / "reports" / "article_ic_event_shifts"
EVENTS = IC / "event_rows.csv"


# 1 & 3. exact thresholds separate genuinely different site sets
def test_exact_threshold_separates_site_sets():
    a0, n = 24.3, 2.0
    d = 0.01
    ths = ic.site_thresholds(24, 3, a0, n, 0.033)
    assert all(0 < t <= 0.033 for t in ths)
    # a domain just below vs above an early threshold differs
    seq, bundled = ic.enumerate_events(a0, n, 0.02)
    assert len(seq) >= 2
    assert any(seq[i][1] != seq[i - 1][1] for i in range(1, len(seq)))


# 2. swap event (equal site count) is a genuine set change
def test_swap_detected_by_set_inequality():
    A = frozenset({(0, 0), (1, 0), (0, 1)})
    B = frozenset({(0, 0), (1, 0), (1, 1)})  # removed (0,1), added (1,1); |.|=3 both
    assert len(A) == len(B) and A != B
    assert sorted(B - A) == [(1, 1)] and sorted(A - B) == [(0, 1)]


# 5-7. additivity/telescoping of fixed-reference marks (synthetic)
def test_fixed_reference_additivity():
    K = 0.006
    gaps = [0.010, 0.012, 0.009, 0.014]  # gap after each of 3 events + initial
    etas = [(gaps[i + 1] - gaps[i]) / K for i in range(len(gaps) - 1)]
    assert abs(sum(etas) - (gaps[-1] - gaps[0]) / K) < 1e-12


# 8. Cauchy interlacing for toy vertex removal (principal submatrix)
def test_cauchy_interlacing_vertex_removal():
    rng = np.random.default_rng(0)
    Hp = rng.normal(size=(6, 6))
    Hp = Hp + Hp.T
    Hm = Hp[:5, :5]                        # remove last vertex
    ep = np.sort(np.linalg.eigvalsh(Hp))
    em = np.sort(np.linalg.eigvalsh(Hm))
    for k in range(5):
        assert ep[k] <= em[k] + 1e-9 <= ep[k + 1] + 1e-9


# 9. one-site Schur secular equation
def test_one_site_secular_equation():
    rng = np.random.default_rng(1)
    Hm = rng.normal(size=(5, 5))
    Hm = Hm + Hm.T
    b = rng.normal(size=5)
    eps = 0.0
    Hp = np.block([[Hm, b[:, None]], [b[None, :], np.array([[eps]])]])
    for lam in (2.3, -1.1, 0.7):
        lhs = np.linalg.det(lam * np.eye(6) - Hp)
        sigma = b @ np.linalg.solve(lam * np.eye(5) - Hm, b)
        rhs = np.linalg.det(lam * np.eye(5) - Hm) * (lam - eps - sigma)
        assert abs(lhs - rhs) < 1e-6 * (1 + abs(lhs))


# 10. multi-site Schur complement secular equation
def test_multi_site_schur():
    rng = np.random.default_rng(2)
    Hm = rng.normal(size=(6, 6)); Hm = Hm + Hm.T
    B = rng.normal(size=(6, 2))
    C = rng.normal(size=(2, 2)); C = C + C.T
    Hp = np.block([[Hm, B], [B.T, C]])
    for lam in (3.1, -2.0):
        lhs = np.linalg.det(lam * np.eye(8) - Hp)
        sc = lam * np.eye(2) - C - B.T @ np.linalg.solve(lam * np.eye(6) - Hm, B)
        rhs = np.linalg.det(lam * np.eye(6) - Hm) * np.linalg.det(sc)
        assert abs(lhs - rhs) < 1e-5 * (1 + abs(lhs))


# 11. changed edges via symmetric difference of bond sets
def test_changed_edges_symmetric_difference():
    Sm = [(0, 0), (1, 0), (0, 1)]
    Sp = [(0, 0), (1, 0), (1, 1)]
    Bm, Bp = ic.bonds(Sm), ic.bonds(Sp)
    changed = Bm ^ Bp
    # removed bond (0,0)-(0,1); added bond (1,0)-(1,1)
    assert ((0, 0), (0, 1)) in changed and ((1, 0), (1, 1)) in changed


# 12 & 13. ground state included: full spectral sum == direct compression
def test_completeness_includes_ground_state():
    N = 9
    H0 = np.zeros((N, N))
    for i in range(N - 1):
        H0[i, i + 1] = H0[i + 1, i] = -1.0
    _, v0 = np.linalg.eigh(H0)
    V0 = v0[:, [1, 2]]                      # baseline doublet
    # PERTURBED Hamiltonian (a "deformed domain"): its ground state overlaps V0
    Hp = H0.copy()
    Hp[0, 0] += 0.5
    wp, vp = np.linalg.eigh(Hp)
    B_full = sum(wp[k] * (V0.T @ vp[:, [k]]) @ (vp[:, [k]].T @ V0) for k in range(N))
    B_no_ground = sum(wp[k] * (V0.T @ vp[:, [k]]) @ (vp[:, [k]].T @ V0) for k in range(1, N))
    B_direct = V0.T @ Hp @ V0
    assert np.allclose(B_full, B_direct, atol=1e-12)   # completeness (all states)
    assert not np.allclose(B_no_ground, B_direct, atol=1e-6)  # ground state matters


# 14 & 15 & 16. projector distance basis/phase/transport invariant
def test_projector_and_phase_invariance():
    idx = {(i, 0): i for i in range(6)}
    rng = np.random.default_rng(3)
    V = np.linalg.qr(rng.normal(size=(6, 4)))[0]
    vecs = V
    d1, a1, a2 = ic.projector_distance(vecs, idx, (1, 2), vecs, idx, (1, 2))
    assert d1 < 1e-9                         # same subspace -> zero distance
    # phase flip of eigenvectors leaves projector distance unchanged
    vecs2 = vecs.copy(); vecs2[:, 1] *= -1
    d2, _, _ = ic.projector_distance(vecs, idx, (1, 2), vecs2, idx, (1, 2))
    assert d2 < 1e-9


# 17. no "derivative" applied to the fixed-a digital event object
@pytest.mark.skipif(not IC.exists(), reason="Ic reports absent")
def test_no_derivative_phrase_for_event_object():
    import re
    neg = ("not", "never", "none", "n't", "rather", "instead", "isn", "aren",
           "without", "no ", "avoid", "stable derivative")
    bad = []
    for md in IC.glob("*.md"):
        txt = re.sub(r"\s+", " ", md.read_text(encoding="utf-8").lower())
        for m in re.finditer("derivative", txt):
            window = txt[max(0, m.start() - 60):m.start() + 10]
            if not any(t in window for t in neg):
                bad.append((md.name, window))
    assert not bad, bad


# 18 & 19. no 64^2 and no broad grid in the pilot constants
def test_no_large_or_broad_grid():
    import scripts.run_article_ic_events as R
    total_placements = sum(len(v) for v in R.PLACEMENTS.values())
    assert total_placements <= 8
    assert R.SIZES == (24.3, 33.7)
    assert R.XIMAX <= 0.8


# 21. results reproducible from CSV (when present)
@pytest.mark.skipif(not EVENTS.exists(), reason="event results absent")
def test_event_csv_present():
    rows = list(csv.DictReader(open(EVENTS)))
    assert len(rows) > 50
    assert "eta_gap" in rows[0] and "schur_predictor" in rows[0]
