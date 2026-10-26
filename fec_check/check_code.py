# Validate the code: count weight-4 supports that BDD would miscorrect -> 15*A6 (each weight-6 codeword has 15 4-subsets).
import numpy as np, time
from pcode import code, FOUND, T2, n
t=time.time()
pair_keys = {}
cnt = 0
idx = np.arange(n)
for a in range(n):
    for b in range(a+1, n):
        kab = code[a]^code[b]
        c = idx[b+1:]
        # all (c,d) with b<c<d
        for ci in range(b+1, n):
            d = idx[ci+1:]
            if len(d)==0: continue
            k = kab ^ code[ci] ^ code[d]
            hit = FOUND[k] & (T2[k] >= 0)
            cnt += int(hit.sum())
A6 = cnt // 15
from math import comb
print("weight-4 miscorrectable supports:", cnt, " A6 =", A6, " (doc: 5757696)", " alpha4 =", cnt/comb(n,4), "(doc 15876/32131 =", 15876/32131, ")  time %.0fs"%(time.time()-t))
