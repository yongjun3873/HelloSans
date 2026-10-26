"""Exact t=2 BDD for the extended BCH [256,239,6] code and iterative BDD (iBDD) of its square product code.

Error-domain simulation (all-zero codeword): valid because the code is linear and BDD acts on syndromes only.
Two decoders run on identical error matrices:
  actual : real BDD (syndrome -> unique weight<=2 coset leader; may miscorrect)
  ref    : miscorrection-free genie reference (corrects a component only if its true error weight <= 2)
"""
import numpy as np

n = 256
# GF(256), primitive polynomial x^8+x^4+x^3+x^2+1
alpha = np.zeros(255, dtype=np.int64)
v = 1
for i in range(255):
    alpha[i] = v
    v <<= 1
    if v & 0x100:
        v ^= 0x11D
# per-position 17-bit syndrome code: S1 | S3<<8 | parity<<16 ; position 255 = overall parity bit
code = np.zeros(n, dtype=np.int64)
for j in range(255):
    code[j] = alpha[j] | (alpha[(3 * j) % 255] << 8) | (1 << 16)
code[255] = 1 << 16

# syndrome -> coset leader of weight <= 2
T1 = -np.ones(1 << 17, dtype=np.int64)
T2 = -np.ones(1 << 17, dtype=np.int64)
FOUND = np.zeros(1 << 17, dtype=bool)
FOUND[0] = True
for a in range(n):
    k = code[a]
    assert not FOUND[k]
    FOUND[k] = True; T1[k] = a
for a in range(n):
    ka = code[a]
    for b in range(a + 1, n):
        k = ka ^ code[b]
        assert not FOUND[k], "syndrome collision -> code construction wrong"
        FOUND[k] = True; T1[k] = a; T2[k] = b


def half_iter_actual(E):
    """Row BDD on all rows of E (B,n,n uint8), in place. Returns number of rows changed."""
    key = np.bitwise_xor.reduce(E.astype(np.int64) * code, axis=2)
    nz = key != 0
    fix = nz & FOUND[key]
    b, r = np.nonzero(fix)
    k = key[b, r]
    p1 = T1[k]; p2 = T2[k]
    E[b, r, p1] ^= 1
    m = p2 >= 0
    E[b[m], r[m], p2[m]] ^= 1
    return len(b)


def half_iter_ref(E):
    w = E.sum(axis=2)
    fix = (w >= 1) & (w <= 2)
    b, r = np.nonzero(fix)
    E[b, r, :] = 0
    return len(b)


def decode(E, kind, max_sweeps=10):
    """Row-then-column iBDD, up to max_sweeps sweeps, early stop when nothing changes. In place."""
    h = half_iter_actual if kind == "actual" else half_iter_ref
    for _ in range(max_sweeps):
        c1 = h(E)
        c2 = h(E.transpose(0, 2, 1))
        if c1 + c2 == 0:
            break
    return E
