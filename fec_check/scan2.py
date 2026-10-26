import numpy as np
from pcode import n, decode
rng = np.random.default_rng(1)
for p in [1.6e-2, 1.4e-2, 1.3e-2, 1.2e-2, 1.1e-2, 1.0e-2]:
    B=64; E=(rng.random((B,n,n))<p).astype(np.uint8); out={}
    for k in ("actual","ref"):
        F=E.copy(); decode(F,k,10); res=F.reshape(B,-1).sum(1)
        out[k]=(int((res>0).sum()), float(res.sum()/(B*n*n)))
    print(f"p={p:.2e}  actual FER {out['actual'][0]}/{B} BER {out['actual'][1]:.2e} | ref FER {out['ref'][0]}/{B} BER {out['ref'][1]:.2e}", flush=True)
