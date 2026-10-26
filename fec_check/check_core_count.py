# Validate the 3x3-core combinatorics: E[#full 3x3 sub-squares of a Bern(p) n x n matrix] = C(n,3)^2 p^9.
import numpy as np
from math import comb
from itertools import combinations
n = 256
rng = np.random.default_rng(7)
for p in [0.03, 0.035]:
    tot = 0; F = 200
    for _ in range(F):
        E = rng.random((n, n)) < p
        rows = [np.flatnonzero(E[r]) for r in range(n)]
        cnt = 0
        heavy = [r for r in range(n) if len(rows[r]) >= 3]
        S = [set(rows[r]) for r in range(n)]
        for a, b in combinations(heavy, 2):
            ab = S[a] & S[b]
            if len(ab) < 3: continue
            for c in heavy:
                if c <= b: continue
                k = len(ab & S[c])
                if k >= 3: cnt += comb(k, 3)
        tot += cnt
    print(f"p={p}: measured mean #cores {tot/F:.4f}  theory {comb(n,3)**2 * p**9:.4f}", flush=True)
