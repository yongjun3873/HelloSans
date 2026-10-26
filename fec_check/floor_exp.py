"""Stage-1 experiment: does miscorrection change the error floor of the [256,239,6]^2 product code under iBDD by >=10x?

(A) Planted-family estimator (importance sampling with exact family weights, background Bern(p) included):
    contribution_F(p) = sum_{e in F} P(E ⊇ e) * E[h(E) | E ⊇ e],  h = residual errors / N.
    F_0 : 3x3 squares (classical minimal stall).
    F_k (k=1,2,3): 3 rows sharing a 3-column core; k of the rows instead carry a 4-error subset S of a weight-6
          codeword W ⊇ core with S ⊉ core (BDD miscorrects S -> W, which creates the 3x3 stall).
    Sum over families approximates BER when instance overlaps are rare (low p). Both decoders run on identical frames.
(B) Direct paired Monte Carlo at the largest p where floor events are observable (cross-check of (A)).
"""
import numpy as np, json, time, sys
from math import comb
from pcode import code, FOUND, T1, T2, n, decode
N = n * n
rng = np.random.default_rng(2026)
C3 = comb(n, 3)

def codewords_containing(core):
    a, b, c = core
    s = code[a] ^ code[b] ^ code[c]
    out = set()
    for d in range(n):
        if d in core: continue
        k = s ^ code[d]
        if FOUND[k] and T2[k] >= 0:
            e, f = int(T1[k]), int(T2[k])
            if e in core or f in core or e == d or f == d: continue
            out.add(tuple(sorted((a, b, c, d, e, f))))
    return list(out)

def sample_family(k, B, p):
    """Returns error batch E (B,n,n) and per-sample weight factor (12*m(core))^k."""
    E = (rng.random((B, n, n)) < p).astype(np.uint8)
    wts = np.ones(B)
    for i in range(B):
        rows = rng.choice(n, 3, replace=False)
        core = tuple(sorted(rng.choice(n, 3, replace=False)))
        if k == 0:
            for r in rows: E[i, r, list(core)] = 1
            continue
        Ws = codewords_containing(core)
        m = len(Ws)
        if m == 0:
            wts[i] = 0.0; continue
        wts[i] = (12.0 * m) ** k
        mis = rng.choice(3, k, replace=False)
        for j, r in enumerate(rows):
            if j in mis:
                W = Ws[rng.integers(m)]
                non = [x for x in W if x not in core]
                # 4-subsets of W not containing the full core: 1 core + 3 noncore (3) or 2 core + 2 noncore (9)
                opts = [[c] + non for c in core] + [[c1, c2, x1, x2] for ci, c1 in enumerate(core) for c2 in core[ci+1:]
                                                     for xi, x1 in enumerate(non) for x2 in non[xi+1:]]
                assert len(opts) == 12
                E[i, r, opts[rng.integers(12)]] = 1
            else:
                E[i, r, list(core)] = 1
    return E, wts

def family_contrib(k, p, nsamp, B=32):
    acc = {"actual": [], "ref": []}
    fails = {"actual": 0, "ref": 0}
    for _ in range(nsamp // B):
        E, wts = sample_family(k, B, p)
        for kind in ("actual", "ref"):
            F = E.copy(); decode(F, kind, 10)
            res = F.reshape(B, -1).sum(1)
            fails[kind] += int((res > 0).sum())
            acc[kind].append(wts * res / N)
    mult = C3 * comb(3, k) * C3 * p ** (9 + k)
    out = {}
    for kind in acc:
        x = np.concatenate(acc[kind])
        out[kind] = {"est": float(mult * x.mean()), "se": float(mult * x.std(ddof=1) / np.sqrt(len(x))),
                     "frac_fail": fails[kind] / len(x)}
    return out

def direct(p, nframes, B=64):
    st = {"actual": [0, 0], "ref": [0, 0]}
    for _ in range(nframes // B):
        E = (rng.random((B, n, n)) < p).astype(np.uint8)
        for kind in st:
            F = E.copy(); decode(F, kind, 10); res = F.reshape(B, -1).sum(1)
            st[kind][0] += int((res > 0).sum()); st[kind][1] += int(res.sum())
    nf = (nframes // B) * B
    return {kind: {"frames": nf, "frame_errors": v[0], "FER": v[0] / nf, "BER": v[1] / (nf * N)} for kind, v in st.items()}

if __name__ == "__main__":
    mode = sys.argv[1]
    t = time.time(); results = {}
    if mode == "family":
        nsamp = int(sys.argv[2])
        for p in [5e-3, 6e-3, 7e-3, 8e-3, 9e-3]:
            results[str(p)] = {}
            for k in range(4):
                results[str(p)][f"F{k}"] = family_contrib(k, p, nsamp)
                print(p, k, results[str(p)][f"F{k}"], "%.0fs" % (time.time() - t), flush=True)
    else:
        p = float(sys.argv[2]); nf = int(sys.argv[3])
        results = direct(p, nf)
        print(p, results, "%.0fs" % (time.time() - t), flush=True)
    json.dump(results, open(f"res_{mode}_{sys.argv[2]}.json", "w"), indent=1)
