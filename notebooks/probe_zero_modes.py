"""Quick probe: zero-mode count vs Lieb bound for superellipse tight-binding billiards.

Pure numpy/scipy reimplementation of the repo's square-lattice TB billiard
(onsite 0, nearest-neighbour hopping -1, hard-wall open boundaries).
"""

import numpy as np


def superellipse_sites(a: float, ar: float, n: float):
    b = a * ar
    R = int(np.ceil(max(a, b))) + 1
    xs = np.arange(-R, R + 1)
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    mask = (np.abs(X / a) ** n + np.abs(Y / b) ** n) <= 1.0
    return np.array([(int(x), int(y)) for x, y in zip(X[mask], Y[mask])])


def hamiltonian(sites):
    index = {(x, y): i for i, (x, y) in enumerate(sites)}
    N = len(sites)
    H = np.zeros((N, N))
    for (x, y), i in index.items():
        for dx, dy in ((1, 0), (0, 1)):
            j = index.get((x + dx, y + dy))
            if j is not None:
                H[i, j] = H[j, i] = -1.0
    return H


def analyse(a, ar, n, tol=1e-9):
    sites = superellipse_sites(a, ar, n)
    N = len(sites)
    parity = (sites[:, 0] + sites[:, 1]) % 2
    NA, NB = int(np.sum(parity == 0)), int(np.sum(parity == 1))
    lieb = abs(NA - NB)
    H = hamiltonian(sites)
    w = np.linalg.eigvalsh(H)
    nullity = int(np.sum(np.abs(w) < tol * max(1.0, N)))
    return dict(n=n, a=a, ar=ar, N=N, NA=NA, NB=NB, lieb=lieb,
                nullity=nullity, extra=nullity - lieb)


print(f"{'n':>5} {'a':>4} {'AR':>5} {'N':>6} {'|NA-NB|':>8} {'nullity':>8} {'extra':>6}")
print("-" * 48)
rows = []
for n in (1.2, 2.0, 3.0, 4.0):
    for a in (12, 18, 24, 30):
        for ar in (0.67, 1.0):
            r = analyse(a, ar, n)
            rows.append(r)
            print(f"{r['n']:>5} {r['a']:>4} {r['ar']:>5} {r['N']:>6} "
                  f"{r['lieb']:>8} {r['nullity']:>8} {r['extra']:>6}")

extra_any = [r for r in rows if r["extra"] > 0]
print(f"\ngeometries with zero modes BEYOND the Lieb/imbalance bound: "
      f"{len(extra_any)} / {len(rows)}")
if extra_any:
    print("max extra:", max(r["extra"] for r in extra_any))
