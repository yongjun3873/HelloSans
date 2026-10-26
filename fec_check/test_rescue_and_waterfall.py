import numpy as np, time
from pcode import code, FOUND, T1, T2, n, decode
rng = np.random.default_rng(0)
W=[0,67,100,170,206,219]; c0,c1,c2,c3,c4,c5=W
X = 5  # not in W
E=np.zeros((1,n,n),np.uint8)
E[0,10,[c0,c1,X,c3,c4,c5]]=1   # (W \ {c2}) U {X}: distance 2 from W
E[0,50,[c0,c1,X]]=1; E[0,90,[c0,c1,X]]=1
print("rescue motif:", int(E.sum()), {k:int(decode(E.copy(),k,20).sum()) for k in ("actual","ref")})
# quick waterfall scan
for p in [9e-3, 8e-3, 7e-3, 6.5e-3, 6e-3, 5.5e-3]:
    B=64; E=(rng.random((B,n,n))<p).astype(np.uint8)
    out={}
    for k in ("actual","ref"):
        F=E.copy(); decode(F,k,10); res=F.reshape(B,-1).sum(1)
        out[k]=(int((res>0).sum()), float(res.sum()/(B*n*n)))
    print(f"p={p:.1e}  actual FER {out['actual'][0]}/{B} BER {out['actual'][1]:.2e} | ref FER {out['ref'][0]}/{B} BER {out['ref'][1]:.2e}")
