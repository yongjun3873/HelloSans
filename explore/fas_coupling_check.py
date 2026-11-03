"""Quick physics check: does mutual coupling (all ports terminated) change selection-FAS outage vs. the standard
Jakes/J0 model?  Side-by-side thin half-wave dipoles, 2D-isotropic incidence (open-circuit voltage corr = J0(kd)),
antenna noise with Twiss covariance 4kT_A B Re(Z), receiver noise kT_R B per port (delivered-power units)."""
import numpy as np, sys
eta=376.73; k=2*np.pi  # wavelength = 1
def Si(x):
    t=np.linspace(0,1,4001); return np.trapezoid(np.sin(np.outer(x,t))/1.0*1.0,t,axis=1)*x if False else _si(x)
def _si(x):
    x=np.atleast_1d(x).astype(float); out=np.zeros_like(x)
    for i,v in enumerate(x):
        t=np.linspace(1e-12,v,20001); out[i]=np.trapezoid(np.sin(t)/t,t)
    return out
def _ci(x):
    x=np.atleast_1d(x).astype(float); out=np.zeros_like(x); g=0.5772156649
    for i,v in enumerate(x):
        t=np.linspace(1e-12,v,20001); out[i]=g+np.log(v)+np.trapezoid((np.cos(t)-1)/t,t)
    return out
def Zmut(d,l=0.5):
    if d<1e-9: return 73.08+42.5j
    u0=k*d; u1=k*(np.sqrt(d*d+l*l)+l); u2=k*(np.sqrt(d*d+l*l)-l)
    R=eta/(4*np.pi)*(2*_ci(u0)-_ci(u1)-_ci(u2))[0]
    X=-eta/(4*np.pi)*(2*_si(u0)-_si(u1)-_si(u2))[0]
    return R+1j*X
def J0(z):
    t=np.linspace(0,np.pi,4001); return np.trapezoid(np.cos(np.multiply.outer(z,np.sin(t))),t,axis=-1)/np.pi
def run(N,W,snr0_db,thr_db,S=400000,seed=1,TA=1.0,TR=1.0):
    rng=np.random.default_rng(seed)
    x=np.linspace(0,W,N); D=np.abs(x[:,None]-x[None,:])
    Rc=J0(k*D)                                  # open-circuit signal correlation
    Z=np.array([[Zmut(D[i,j]) for j in range(N)] for i in range(N)])
    Z11=Z[0,0]; ZL=np.conj(Z11); RL=ZL.real
    Lc=np.linalg.cholesky(Rc+1e-9*np.eye(N))
    h=(rng.standard_normal((S,N))+1j*rng.standard_normal((S,N)))/np.sqrt(2)@Lc.T   # v_oc / sqrt(4 R11 P0)
    # standard model: delivered SNR = |h|^2 * snr0 ; snr0 = isolated matched dipole SNR with noise k(TA+TR)B
    snr0=10**(snr0_db/10); thr=10**(thr_db/10)
    g_std=(np.abs(h)**2).max(1)*snr0
    # coupled, all ports terminated in ZL
    T=ZL*np.linalg.inv(Z+ZL*np.eye(N))          # v_L = T v_oc
    voc_scale=np.sqrt(4*Z11.real)                # v_oc = sqrt(4R11 P0) h  (P0 = available power unit)
    vL=(h*voc_scale)@T.T
    Psig=np.abs(vL)**2/(4*RL)*4                  # delivered power |vL|^2/RL  (|vL|^2/(4RL) *4 = |vL|^2/RL)
    Psig=np.abs(vL)**2/RL
    # noise: antenna thermal (Twiss, open-circuit cov 4 k TA Re Z) -> delivered; receiver kTR per port
    Cn_oc=4*TA*Z.real
    Cn_L=T@Cn_oc@T.conj().T
    Pn_ant=np.real(np.diag(Cn_L))/RL
    Pn=Pn_ant+TR
    # normalise so that a single isolated matched dipole gives snr0: isolated delivered signal = P0, noise=TA+TR
    snr_c=Psig/Pn[None,:]*(TA+TR)*snr0/1.0
    g_cpl=snr_c.max(1)
    return (g_std<thr).mean(),(g_cpl<thr).mean(),np.mean(Pn_ant/TA),np.mean(np.abs(T)**2)
if __name__=="__main__":
    for W in (0.5,1.0,2.0):
        for N in (2,4,8,16,32):
            # find outage at snr0 so that standard model gives ~1e-3, compare coupled
            for snr0 in (10,15,20):
                ps,pc,na,_=run(N,W,snr0,0.0)
                print(f"W={W} N={N:2d} snr0={snr0}dB  outage std={ps:.2e}  coupled={pc:.2e}  ratio={pc/max(ps,1e-9):.2f}  antnoise factor={na:.2f}",flush=True)
