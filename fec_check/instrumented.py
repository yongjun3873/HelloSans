# Direct MC that stores initial and final error positions of every failed frame (both decoders), for trajectory classification.
import numpy as np, json, sys, time
from pcode import n, decode
p = float(sys.argv[1]); nf = int(sys.argv[2]); seed = int(sys.argv[3])
rng = np.random.default_rng(seed); B = 64; out = []; t = time.time(); frames = 0
for _ in range(nf // B):
    E = (rng.random((B, n, n)) < p).astype(np.uint8); frames += B
    finals = {}
    for kind in ("actual", "ref"):
        F = E.copy(); decode(F, kind, 10); finals[kind] = F
    for i in range(B):
        fa, fr = int(finals["actual"][i].sum()), int(finals["ref"][i].sum())
        if fa or fr:
            out.append({"init": np.argwhere(E[i]).tolist(), "final_actual": np.argwhere(finals["actual"][i]).tolist(),
                        "final_ref": np.argwhere(finals["ref"][i]).tolist()})
json.dump({"p": p, "frames": frames, "fails": out}, open(f"inst_{sys.argv[1]}_{seed}.json", "w"))
print(p, seed, "frames", frames, "failed frames", len(out), "%.0fs" % (time.time() - t), flush=True)
