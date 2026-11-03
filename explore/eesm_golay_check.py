import numpy as np, itertools, math
from math import erfc
rng=np.random.default_rng(0)
# extended Golay [24,12,8]
B=np.array([[1,1,0,1,1,1,0,0,0,1,0,1],[1,0,1,1,1,0,0,0,1,0,1,1],[0,1,1,1,0,0,0,1,0,1,1,1],[1,1,1,0,0,0,1,0,1,1,0,1],
[1,1,0,0,0,1,0,1,1,0,1,1],[1,0,0,0,1,0,1,1,0,1,1,1],[0,0,0,1,0,1,1,0,1,1,1,1],[0,0,1,0,1,1,0,1,1,1,0,1],
[0,1,0,1,1,0,1,1,1,0,0,1],[1,0,1,1,0,1,1,1,0,0,0,1],[0,1,1,0,1,1,1,0,0,0,1,1],[1,1,1,1,1,1,1,1,1,1,1,0]])
G=np.hstack([np.eye(12,dtype=int),B])
msgs=np.array(list(itertools.product([0,1],repeat=12)))
C=(msgs@G)%2; w=C.sum(1); print('weights',np.unique(w,return_counts=True))
X=1-2*C.astype(float)   # BPSK codebook
nz=C[w>0].astype(bool)
Qf=np.vectorize(lambda x: 0.5*erfc(x/np.sqrt(2)))
def ub(snr):  # union bound BPSK ML given per-position SNR (Es/N0) ; PEP=Q(sqrt(2*sum snr))
    s=nz@snr; return min(1.0,Qf(np.sqrt(2*s)).sum())
def mc(snr,n):
    sig=np.sqrt(1/(2*snr))
    y=X[0][None,:]+rng.standard_normal((n,24))*sig[None,:]
    # ML with per-position weights snr (LLR scale)
    met=(y*snr[None,:])@X.T
    return (met.argmax(1)!=0).mean()
# channel: TDL with L taps, 24 subcarriers spaced
def chan(Ltap=6,spread=0.4):
    taps=(rng.standard_normal(Ltap)+1j*rng.standard_normal(Ltap))/np.sqrt(2)*np.exp(-np.arange(Ltap)*spread)
    taps/=np.sqrt((np.abs(taps)**2).sum()) if False else np.sqrt((np.exp(-2*np.arange(Ltap)*spread)).sum())
    k=np.arange(24); H=np.exp(-2j*np.pi*np.outer(k,np.arange(Ltap))*8/256)@taps   # delay spread over band
    perm=rng.permutation(24); return (np.abs(H)**2)[perm]
# AWGN reference curve: union bound at low BLER, MC at high
def awgn(snr_db):
    s=10**(snr_db/10)*np.ones(24); return ub(s)
grid=np.arange(-6,12,0.05); awgn_ub=np.array([awgn(x) for x in grid])
def inv_awgn(p):  # SNR dB giving BLER p on AWGN union bound curve
    i=np.argmin(np.abs(np.log(awgn_ub)-np.log(p))); return grid[i]
def eesm(g,snr,beta): return -beta*np.log(np.mean(np.exp(-g*snr/beta)))
R=150; chans=[chan() for _ in range(R)]
# per realization find mean SNR giving true BLER = target (union bound truth valid at low BLER)
def snr_for(g,target):
    lo,hi=-10,40
    for _ in range(40):
        m=(lo+hi)/2; p=ub(g*10**(m/10))
        if p>target: lo=m
        else: hi=m
    return (lo+hi)/2
for target in (1e-2,1e-3,1e-5,1e-7):
    req=np.array([snr_for(g,target) for g in chans])  # dB mean SNR needed
    awgn_req=inv_awgn(target)
    best=None
    for beta in np.arange(0.3,3.01,0.05):
        # EESM predicted effective SNR at the true required mean SNR should equal awgn_req
        eff=np.array([10*np.log10(eesm(g,10**(r/10),beta)) for g,r in zip(chans,req)])
        err=eff-awgn_req; rms=np.sqrt(np.mean(err**2))
        if best is None or rms<best[0]: best=(rms,beta,np.percentile(np.abs(err),95))
    print('target %.0e: best beta %.2f  rms err %.2f dB  95%% |err| %.2f dB'%(target,best[1],best[0],best[2]))
