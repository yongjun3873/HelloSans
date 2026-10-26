"""GPU (CuPy) / CPU (numpy) simulator for hard-decision iterative BDD with t=2 extended-BCH components.

Two code families:
  * product   : square product code of an extended BCH [2^m, 2^m-1-2m, 6] (m=8 -> [256,239,6]^2), row/column iBDD.
  * staircase : staircase code (Smith et al. 2012) with a shortened extended BCH [2*M, 2*M-19, 6] component
                (M=255 -> [510,491], the code of Holzbaur-Bartz-Wachter-Zeh 2019, Sec. 4.2), sliding-window decoder.

Error-domain simulation (all-zero codeword). Two decoders on identical errors:
  actual : true t=2 BDD (syndrome -> unique coset leader of weight <= 2; miscorrections happen)
  ref    : miscorrection-free genie (a component is corrected only if its true error weight is <= 2)

Syndromes are computed as an integer matmul (errors @ H) mod 2, which runs on GPU tensor cores and on CPU alike.
"""
import json, os, time
import numpy as np

try:
    import cupy as cp
    xp = cp
    GPU = True
except Exception:  # pragma: no cover
    xp = np
    GPU = False


def to_np(a):
    return cp.asnumpy(a) if GPU else a


# ---------------------------------------------------------------- component code
class BCH2:
    """t=2 extended BCH over GF(2^m), shortened to length L (positions 0..L-2 are BCH positions, L-1 is overall parity)."""
    PRIM = {8: 0x11D, 9: 0x211}

    def __init__(self, m, L):
        q = (1 << m) - 1
        assert L - 1 <= q
        alpha = np.zeros(q, dtype=np.int64)
        v = 1
        for i in range(q):
            alpha[i] = v
            v <<= 1
            if v >> m:
                v ^= self.PRIM[m]
        self.m, self.L, self.nb = m, L, 2 * m + 1
        code = np.zeros(L, dtype=np.int64)
        for j in range(L - 1):
            code[j] = alpha[j] | (alpha[(3 * j) % q] << m) | (1 << (2 * m))
        code[L - 1] = 1 << (2 * m)
        self.code = code
        # bit matrix H (L x nb) for matmul syndromes
        H = ((code[:, None] >> np.arange(self.nb)[None, :]) & 1).astype(np.float32)
        size = 1 << self.nb
        T1 = -np.ones(size, dtype=np.int32); T2 = -np.ones(size, dtype=np.int32)
        found = np.zeros(size, dtype=bool); found[0] = True
        for a in range(L):
            k = code[a]; assert not found[k]; found[k] = True; T1[k] = a
        ka = code[:, None] ^ code[None, :]
        ia, ib = np.triu_indices(L, 1)
        kk = ka[ia, ib]
        assert not found[kk].any() and len(np.unique(kk)) == len(kk), "syndrome collision"
        found[kk] = True; T1[kk] = ia; T2[kk] = ib
        # fp16 on GPU (tensor cores): row sums <= 512 and keys < 2^19 handled below are exact
        self.ft = xp.float16 if GPU else xp.float32
        self.H = xp.asarray(H).astype(self.ft)
        self.pow2 = xp.asarray((1 << np.arange(self.nb)).astype(np.float32))
        self.T1, self.T2, self.FOUND = xp.asarray(T1), xp.asarray(T2), xp.asarray(found)

    def keys(self, W):
        """W: (..., L) uint8 words -> integer syndrome keys (...)."""
        s = xp.matmul(W.astype(self.ft), self.H)
        s = xp.remainder(s.astype(xp.float32), 2.0)
        return xp.matmul(s, self.pow2).astype(xp.int64)


# ---------------------------------------------------------------- product code
def product_half_iter(E, comp, kind):
    """Decode all rows of E (B,n,n) in place; returns number of components changed."""
    if kind == "ref":
        w = E.sum(axis=2, dtype=xp.int32)
        fix = (w >= 1) & (w <= 2)
        b, r = xp.nonzero(fix)
        if b.size:
            E[b, r, :] = 0
        return int(b.size)
    key = comp.keys(E)
    fix = (key != 0) & comp.FOUND[key]
    b, r = xp.nonzero(fix)
    if b.size == 0:
        return 0
    k = key[b, r]
    p1 = comp.T1[k]; p2 = comp.T2[k]
    E[b, r, p1] ^= 1
    m = p2 >= 0
    E[b[m], r[m], p2[m]] ^= 1
    return int(b.size)


def product_decode(E, comp, kind, max_sweeps=10):
    for _ in range(max_sweeps):
        c1 = product_half_iter(E, comp, kind)
        Et = xp.ascontiguousarray(E.transpose(0, 2, 1))
        c2 = product_half_iter(Et, comp, kind)
        E[...] = Et.transpose(0, 2, 1)
        if c1 + c2 == 0:
            break
    return E


class _HostRNG:
    """numpy RNG whose samples are moved to the device: identical error patterns on CPU and GPU (used by selftest)."""
    def __init__(self, seed):
        self.rs = np.random.RandomState(seed)

    def random_sample(self, shape):
        return xp.asarray(self.rs.random_sample(shape))


def run_product(p, frames, batch=256, seed=0, max_sweeps=10, out_path=None, capture=True, flush_frames=65536,
                host_rng=False):
    """Direct MC for the [256,239,6]^2 product code. Appends one JSON line per ~flush_frames frames to out_path
    (checkpointing). Failed frames (up to 20 per line) are stored with their initial and final error positions."""
    comp = BCH2(8, 256)
    n = 256
    rs = _HostRNG(seed) if host_rng else xp.random.RandomState(seed)
    t0 = time.time()
    kinds = ("actual", "ref")

    def fresh():
        return {k: {"frame_errors": 0, "residual_bits": 0, "residual_weights": [], "captures": []} for k in kinds}

    stats = fresh(); done = 0; pending = 0
    while done < frames:
        B = min(batch, frames - done)
        E0 = (rs.random_sample((B, n, n)) < p).astype(xp.uint8)
        for k in kinds:
            E = E0.copy()
            product_decode(E, comp, k, max_sweeps)
            res = to_np(E.reshape(B, -1).sum(axis=1, dtype=xp.int64))
            st = stats[k]
            st["frame_errors"] += int((res > 0).sum()); st["residual_bits"] += int(res.sum())
            st["residual_weights"] += [int(x) for x in res[res > 0]]
            if capture:
                for i in np.flatnonzero(res > 0)[: max(0, 20 - len(st["captures"]))]:
                    st["captures"].append({"init": to_np(xp.argwhere(E0[i])).tolist(),
                                           "final": to_np(xp.argwhere(E[i])).tolist()})
        done += B; pending += B
        if out_path and (pending >= flush_frames or done >= frames):
            rec = {"code": "product256", "p": p, "seed": seed, "frames": pending, "max_sweeps": max_sweeps,
                   "elapsed_s": round(time.time() - t0, 1), **stats}
            with open(out_path, "a") as f:
                f.write(json.dumps(rec) + "\n")
            stats = fresh(); pending = 0
    return time.time() - t0


# ---------------------------------------------------------------- staircase code
def _bdd_flips(Wd, comp, kind):
    """Rows of Wd (S,M,2M) to correct and the positions to flip. Returns (s, r, p1, p2) with p2 = -1 for single errors;
    for kind == 'ref' p1 is None (the whole row is cleared)."""
    if kind == "ref":
        w = Wd.sum(axis=2, dtype=xp.int32)
        s, r = xp.nonzero((w >= 1) & (w <= 2))
        return s, r, None, None
    key = comp.keys(Wd)
    s, r = xp.nonzero((key != 0) & comp.FOUND[key])
    k = key[s, r]
    return s, r, comp.T1[k], comp.T2[k]


def staircase_group_decode(Lb, Rb, comp, kind, lock_left=False):
    """One decoding pass over the M component words of the group [Lb^T  Rb] (Lb, Rb: (S,M,M)), in place.
    Word r = concat(Lb[:, r], Rb[r, :]). With lock_left the block Lb was already delivered and is not modified
    (only the Rb part of a decision is applied). Returns the number of words whose bits actually changed."""
    S, M, _ = Rb.shape
    Wd = xp.concatenate([Lb.transpose(0, 2, 1), Rb], axis=2)  # (S, M, 2M)
    s, r, p1, p2 = _bdd_flips(Wd, comp, kind)
    if s.size == 0:
        return 0
    if kind == "ref":
        if lock_left:
            changed = Wd[s, r, M:].sum(axis=1) > 0
            Wd[s, r, M:] = 0
        else:
            changed = xp.ones(s.size, dtype=bool)
            Wd[s, r, :] = 0
    else:
        m2 = p2 >= 0
        if lock_left:
            a1 = p1 >= M
            a2 = m2 & (p2 >= M)
        else:
            a1 = xp.ones(s.size, dtype=bool)
            a2 = m2
        Wd[s[a1], r[a1], p1[a1]] ^= 1
        Wd[s[a2], r[a2], p2[a2]] ^= 1
        changed = a1 | a2
    if not lock_left:
        Lb[...] = Wd[:, :, :M].transpose(0, 2, 1)
    Rb[...] = Wd[:, :, M:]
    return int(changed.sum())


def run_staircase(p, out_blocks, streams=256, W=7, v_max=10, seed=0, out_path=None, chunk_steps=50, warmup=None,
                  lock_first=False, host_rng=False):
    """Direct MC for the staircase code with M=255 and the [510,491] shortened extended BCH component
    (Holzbaur et al., Sec. 4.2 parameters), sliding-window decoder.

    Decoder of Smith et al. as described in Holzbaur et al. Sec. 2.2: the window holds B_i..B_{i+W-1}; the groups
    [B_i^T B_{i+1}], ..., [B_{i+W-2}^T B_{i+W-1}] are decoded from the oldest to the newest, and this pass is repeated
    up to v_max times (early stop when a pass changes nothing). Then B_i is delivered and the window slides.
    With lock_first=True the group [B_{i-1}^T B_i] (B_{i-1} already delivered, not modified) is also decoded
    (a variant; not the paper's decoder).
    'streams' independent staircase streams run in parallel; both decoders see the same channel errors.
    One JSON line is appended to out_path every chunk_steps window positions (checkpointing)."""
    M = 255
    comp = BCH2(9, 2 * M)
    rs = _HostRNG(seed) if host_rng else xp.random.RandomState(seed)
    warmup = W if warmup is None else warmup
    t0 = time.time()
    kinds = ("actual", "ref")
    win = {k: [xp.zeros((streams, M, M), dtype=xp.uint8)] for k in kinds}
    for _ in range(W):
        Eb = (rs.random_sample((streams, M, M)) < p).astype(xp.uint8)
        for k in kinds:
            win[k].append(Eb.copy())

    def fresh():
        return {k: {"block_errors": 0, "residual_bits": 0, "residual_weights": []} for k in kinds}

    # Group j = [B^T_j B_{j+1}] of the window list. A group decoded with no later change to its two blocks is a fixed
    # point (all its words are codewords, or weight >= 3 for ref), so it is skipped until a neighbour changes one of
    # its blocks. This gives exactly the same result as re-decoding every group in every pass.
    j0 = 0 if lock_first else 1
    dirty = {k: [True] * W for k in kinds}
    stats = fresh(); produced = 0; step = 0; chunk_units = 0
    while produced < out_blocks:
        for k in kinds:
            blocks, d = win[k], dirty[k]
            for _ in range(v_max):
                if not any(d[j0:]):
                    break
                for j in range(j0, W):
                    if not d[j]:
                        continue
                    d[j] = False
                    if staircase_group_decode(blocks[j], blocks[j + 1], comp, k, lock_left=(j == 0)):
                        if j > j0:
                            d[j - 1] = True
                        if j + 1 < W:
                            d[j + 1] = True
            dirty[k] = d[1:] + [True]
        step += 1
        if step > warmup:
            for k in kinds:
                res = to_np(win[k][1].reshape(streams, -1).sum(axis=1, dtype=xp.int64))
                stats[k]["block_errors"] += int((res > 0).sum())
                stats[k]["residual_bits"] += int(res.sum())
                stats[k]["residual_weights"] += [int(x) for x in res[res > 0]]
            produced += streams; chunk_units += streams
        Eb = (rs.random_sample((streams, M, M)) < p).astype(xp.uint8)
        for k in kinds:
            win[k].pop(0)
            win[k].append(Eb.copy())
        if out_path and chunk_units and (chunk_units >= chunk_steps * streams or produced >= out_blocks):
            rec = {"code": "staircase255_510", "p": p, "seed": seed, "W": W, "v_max": v_max, "lock_first": lock_first,
                   "blocks": chunk_units,
                   "bits_per_block": M * M, "elapsed_s": round(time.time() - t0, 1), **stats}
            with open(out_path, "a") as f:
                f.write(json.dumps(rec) + "\n")
            stats = fresh(); chunk_units = 0
    return time.time() - t0


# ---------------------------------------------------------------- summary
def summarize(path):
    agg = {}
    for line in open(path):
        r = json.loads(line)
        key = (r["code"], r["p"])
        unit = r.get("frames", r.get("blocks"))
        bits = 65536 if r["code"] == "product256" else r["bits_per_block"]
        a = agg.setdefault(key, {"units": 0, "bits": bits, "actual": [0, 0], "ref": [0, 0]})
        a["units"] += unit
        for k in ("actual", "ref"):
            fe = r[k].get("frame_errors", r[k].get("block_errors"))
            a[k][0] += fe; a[k][1] += r[k]["residual_bits"]
    out = []
    for (code, p), a in sorted(agg.items()):
        row = {"code": code, "p": p, "units": a["units"]}
        for k in ("actual", "ref"):
            row[k] = {"events": a[k][0], "BER": a[k][1] / (a["units"] * a["bits"])}
        out.append(row)
    return out


# ---------------------------------------------------------------- self-test
# Reference numbers produced with the numpy path (same host-generated errors); a GPU run must reproduce them exactly.
SELFTEST_EXPECTED = {'product256/actual': [64, 35844], 'product256/ref': [29, 5774],
                     'staircase255_510/actual': [64, 23171], 'staircase255_510/ref': [64, 12888]}


def selftest():
    import tempfile
    got = {}
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "t.jsonl")
        run_product(0.0125, 64, batch=32, seed=1, out_path=f, capture=False, host_rng=True)
        run_staircase(0.0068, 64, streams=16, W=7, v_max=10, seed=1, out_path=f, chunk_steps=2, host_rng=True)
        for line in open(f):
            r = json.loads(line)
            for k in ("actual", "ref"):
                key = f'{r["code"]}/{k}'
                e = r[k].get("frame_errors", r[k].get("block_errors"))
                a = got.setdefault(key, [0, 0]); a[0] += e; a[1] += r[k]["residual_bits"]
    print("selftest", got)
    if SELFTEST_EXPECTED is not None:
        ok = got == SELFTEST_EXPECTED
        print("SELFTEST", "PASSED" if ok else f"FAILED (expected {SELFTEST_EXPECTED})")
        if not ok:
            raise SystemExit(1)


# ---------------------------------------------------------------- command line
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("code", choices=["product", "staircase", "summary", "selftest"])
    ap.add_argument("--p", type=float, nargs="+", default=[])
    ap.add_argument("--units", type=int, default=1_000_000, help="frames (product) or delivered blocks (staircase)")
    ap.add_argument("--batch", type=int, default=256, help="frames per batch (product) or parallel streams (staircase)")
    ap.add_argument("--seed", type=int, default=None, help="default: derived from p and time")
    ap.add_argument("--W", type=int, default=7)
    ap.add_argument("--vmax", type=int, default=10)
    ap.add_argument("--lock_first", action="store_true")
    ap.add_argument("--out", default="results.jsonl")
    a = ap.parse_args()
    print("GPU" if GPU else "CPU (numpy)", flush=True)
    if a.code == "selftest":
        selftest()
    elif a.code == "summary":
        for row in summarize(a.out):
            print(row)
    for p in a.p:
        seed = a.seed if a.seed is not None else (int(time.time()) ^ int(p * 1e7)) & 0x7FFFFFFF
        print(f"{a.code} p={p} units={a.units} seed={seed}", flush=True)
        if a.code == "product":
            t = run_product(p, a.units, batch=a.batch, seed=seed, out_path=a.out)
        else:
            t = run_staircase(p, a.units, streams=a.batch, W=a.W, v_max=a.vmax, seed=seed, out_path=a.out,
                              lock_first=a.lock_first)
        print(f"done in {t:.0f}s", [r for r in summarize(a.out) if r["p"] == p], flush=True)
