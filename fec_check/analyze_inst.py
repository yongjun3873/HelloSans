import json, sys, numpy as np
from itertools import combinations
d = json.load(open(sys.argv[1]))
print("p", d["p"], "frames", d["frames"], "failed frames", len(d["fails"]))
for i, f in enumerate(d["fails"]):
    init = set(map(tuple, f["init"]))
    for kind in ("actual", "ref"):
        fin = set(map(tuple, f[f"final_{kind}"]))
        if not fin: continue
        rows = sorted({r for r, c in fin}); cols = sorted({c for r, c in fin})
        in_init = len(fin & init)
        # did the initial pattern contain ANY full 3x3 core?
        R = {}
        for r, c in init: R.setdefault(r, set()).add(c)
        heavy = [r for r in R if len(R[r]) >= 3]
        has_core = any(len(R[a] & R[b] & R[c]) >= 3 for a, b, c in combinations(heavy, 3))
        init_w_rows = [len(R.get(r, ())) for r in rows]
        print(f"#{i} {kind:6s} residual {len(fin):3d} rows {rows} cols {cols}  final∩init {in_init}/{len(fin)}  "
              f"init row weights of stall rows {init_w_rows}  initial contains a 3x3 core: {has_core}  init weight {len(init)}")
