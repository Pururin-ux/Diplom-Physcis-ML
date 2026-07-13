"""Article-Ic: canonical event-resolved spectral shifts for digital billiards.

Exact analytic enumeration of boundary events for the area-preserving
superellipse deformation, plus finite-rank spectral marks. Transport-free,
gauge-free: everything is computed from the physical spectra of two digital
domains. No smooth derivative is defined.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.sparse import lil_matrix, csc_matrix, identity
from scipy.sparse.linalg import eigsh

NEIGH = ((1, 0), (-1, 0), (0, 1), (0, -1))


def semi_axes(a0, delta):
    r = 1.0 - delta
    return a0 / math.sqrt(r), a0 * math.sqrt(r)


def in_domain(x, y, a0, n, delta):
    ax, ay = semi_axes(a0, delta)
    return abs(x / ax) ** n + abs(y / ay) ** n <= 1.0 + 1e-12


def site_thresholds(x, y, a0, n, dmax):
    """Exact delta values in (0, dmax] where site (x,y) crosses the boundary.

    F = (|x|^n t + |y|^n / t)/a0^n with t=(1-delta)^{n/2}; F=1 gives
    |x|^n t^2 - a0^n t + |y|^n = 0. Solve for t, then delta = 1 - t^{2/n}.
    """
    ax_n = abs(x) ** n
    ay_n = abs(y) ** n
    a0n = a0 ** n
    out = []
    if ax_n < 1e-15:
        # |y|^n/t = a0^n -> t = |y|^n/a0^n
        if ay_n > 0:
            t = ay_n / a0n
            roots = [t]
        else:
            roots = []
    else:
        disc = a0n ** 2 - 4 * ax_n * ay_n
        if disc < 0:
            roots = []
        else:
            sq = math.sqrt(disc)
            roots = [(a0n + sq) / (2 * ax_n), (a0n - sq) / (2 * ax_n)]
    for t in roots:
        if t <= 0:
            continue
        delta = 1.0 - t ** (2.0 / n)
        if 1e-9 < delta <= dmax:
            out.append(delta)
    return out


def domain_sites(a0, n, delta):
    ax, ay = semi_axes(a0, delta)
    R = int(math.ceil(max(ax, ay))) + 2
    return frozenset(
        (x, y) for x in range(-R, R + 1) for y in range(-R, R + 1)
        if abs(x / ax) ** n + abs(y / ay) ** n <= 1.0
    )


def enumerate_events(a0, n, dmax):
    """Return the ordered list of distinct (delta_mid, S) domains and events."""
    ax, ay = semi_axes(a0, dmax)
    R = int(math.ceil(max(ax, ay))) + 3
    thresholds = set()
    for x in range(-R, R + 1):
        for y in range(-R, R + 1):
            for d in site_thresholds(x, y, a0, n, dmax):
                thresholds.add(round(d, 12))
    ths = sorted(thresholds)
    # bundle near-coincident thresholds
    bundled = []
    for d in ths:
        if bundled and abs(d - bundled[-1]) < 1e-7:
            continue
        bundled.append(d)
    # build the sequence of distinct domains at midpoints
    mids = [0.0]
    for i, d in enumerate(bundled):
        nxt = bundled[i + 1] if i + 1 < len(bundled) else dmax + 1e-6
        mids.append(0.5 * (d + min(nxt, dmax + 1e-6)))
    seq = []
    prev = None
    for m in mids:
        S = domain_sites(a0, n, min(m, dmax))
        if prev is None or S != prev:
            seq.append((m, S))
            prev = S
    return seq, bundled


def build_H(sites):
    idx = {s: i for i, s in enumerate(sorted(sites))}
    n = len(idx)
    H = lil_matrix((n, n))
    for (x, y), i in idx.items():
        for dx, dy in ((1, 0), (0, 1)):
            j = idx.get((x + dx, y + dy))
            if j is not None:
                H[i, j] = -1.0
                H[j, i] = -1.0
    return csc_matrix(H), idx


def low_spectrum(sites, k=6):
    H, idx = build_H(sites)
    kk = min(k, H.shape[0] - 2)
    vals, vecs = eigsh(H, k=kk, sigma=-4.2, which="LM")
    o = np.argsort(vals)
    return vals[o], vecs[:, o], H, idx


def bonds(sites):
    sset = set(sites)
    B = set()
    for (x, y) in sites:
        for dx, dy in ((1, 0), (0, 1)):
            if (x + dx, y + dy) in sset:
                B.add(((x, y), (x + dx, y + dy)))
    return B


def normal_angle(x, y, a0, n, delta):
    ax, ay = semi_axes(a0, delta)
    gx = n * abs(x) ** (n - 1) * (1 if x >= 0 else -1) / ax ** n
    gy = n * abs(y) ** (n - 1) * (1 if y >= 0 else -1) / ay ** n
    return math.degrees(math.atan2(gy, gx))


def projector_distance(vecs_a, idx_a, cols_a, vecs_b, idx_b, cols_b):
    """||P_a - P_b||_F between two 2D subspaces embedded in the union space."""
    union = sorted(set(idx_a) | set(idx_b))
    ui = {s: i for i, s in enumerate(union)}
    m = len(union)

    def emb(vecs, idx, cols):
        V = np.zeros((m, 2))
        for s, li in idx.items():
            for c, col in enumerate(cols):
                V[ui[s], c] = vecs[li, col]
        # orthonormalize (guard against tiny nonorthogonality from restriction)
        q, _ = np.linalg.qr(V)
        return q

    Va = emb(vecs_a, idx_a, cols_a)
    Vb = emb(vecs_b, idx_b, cols_b)
    Pa = Va @ Va.T
    Pb = Vb @ Vb.T
    dist = float(np.linalg.norm(Pa - Pb))
    sv = np.linalg.svd(Va.T @ Vb, compute_uv=False)
    sv = np.clip(sv, -1, 1)
    angles = np.degrees(np.arccos(sv))
    return dist, float(angles[0]), float(angles[-1])
