import numpy as np, time
from pcode import code, FOUND, T1, T2, n, decode
rng = np.random.default_rng(0)
# find a weight-6 codeword W
while True:
    q = rng.choice(n, 4, replace=False)
    k = np.bitwise_xor.reduce(code[q])
    if FOUND[k] and T2[k] >= 0 and T1[k] not in q and T2[k] not in q:
        W = sorted(list(q) + [int(T1[k]), int(T2[k])]); break
print("weight-6 codeword support W =", W)
c0,c1,c2,c3,c4,c5 = W
def run(rows):
    E = np.zeros((1,n,n), np.uint8)
    for r, cols in rows.items():
        E[0, r, cols] = 1
    res = {}
    for kind in ("actual","ref"):
        F = E.copy(); decode(F, kind, max_sweeps=20); res[kind] = int(F.sum())
    return int(E.sum()), res
core = [c0,c1,c2]
print("3x3 square          :", run({10:core, 50:core, 90:core}))
print("generation motif    :", run({10:[c1,c2,c4,c5], 50:core, 90:core}))   # row 10: 2 core + 2 non-core of W
print("generation (1 core) :", run({10:[c0,c3,c4,c5], 50:core, 90:core}))   # row 10: 1 core + 3 non-core
print("transposed motif    :", (lambda: None)() or "skip")
E = np.zeros((1,n,n),np.uint8); E[0,[c1,c2,c4,c5],10]=1; E[0,core,50]=1; E[0,core,90]=1
r={k:int(decode(E.copy(),k,20).sum()) for k in("actual","ref")}; print("  transposed       :", int(E.sum()), r)
alt = [c0,c1,c3]   # rescue: square on columns {c0,c1,c3}; row 10 = W plus... per doc: {0,1,3,5,11,12}
other = [x for x in range(n) if x not in W][:1]
print("rescue motif        :", run({10:[c0,c1,c3]+[c2-0 if False else c3][:0]+[c5, c4, other[0]] if False else [c0,c1,c3,c5,c4,W[2]] , 50:[c0,c1,c3], 90:[c0,c1,c3]}))
# timing
p=5e-3; B=32
E = (rng.random((B,n,n))<p).astype(np.uint8)
for kind in ("actual","ref"):
    F=E.copy(); t=time.time(); decode(F,kind,10); print(kind,"B=32 decode time %.2fs"%(time.time()-t), "frames failed", int((F.reshape(B,-1).sum(1)>0).sum()))
