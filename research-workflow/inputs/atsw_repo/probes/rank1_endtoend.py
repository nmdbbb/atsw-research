"""Thuật toán 'nghiệm đóng hạng 1': ghép góc tây-bắc theo THỨ TỰ VECTOR KỲ DỊ của phần dư
quyết định R = M - f(a) - g(b). Không gọi LP ở bất kỳ nút nào. O(nm log n) mỗi TẦNG (SVD hạng 1
qua power iteration hoặc svd đầy đủ) + O(nm) mỗi cặp.

TIÊU CHÍ KHAI TRƯỚC — không sửa sau khi thấy số
  R1: sai số end-to-end của thứ tự SVD phải NHỎ HƠN ÍT NHẤT 2 LẦN sai số của thứ tự trạng thái
      (đã đo: 0,23% ở δ=0,5; 2,32% ở δ=0,18). Không đạt => cấu trúc hạng 1 không chuyển end-to-end.
  R2: thời gian phải <= 1,5x thời gian comonotone thuần (SVD một lần mỗi tầng, chia cho n*m cặp).
  Đo trên 2 seed MỚI (base 40M), T=50, hai δ.
"""
import os, sys, time, csv
sys.path.append(os.getcwd())
import numpy as np, ot
import kmarkov_driver as KD

def nw_cost_ord(wa, wb, Mo):
    ca = np.concatenate(([0.0], np.cumsum(wa))); cb = np.concatenate(([0.0], np.cumsum(wb)))
    lo = np.maximum(ca[:-1, None], cb[None, :-1]); hi = np.minimum(ca[1:, None], cb[None, 1:])
    return float((np.clip(hi - lo, 0, None) * Mo).sum())

def dp_run(ra, Ka, rb, Kb, mode, T=50):
    V = np.zeros((len(ra[T]), len(rb[T])))
    for t in range(T-1, -1, -1):
        M = np.ascontiguousarray((ra[t+1][:,None] - rb[t+1][None,:])**2 + V)
        WA, WB = Ka[t], Kb[t]
        if mode == "svd":
            R = M - M.mean(axis=1, keepdims=True) - M.mean(axis=0, keepdims=True) + M.mean()
            U, s, Vt = np.linalg.svd(R, full_matrices=False)
            u, v = U[:,0], Vt[0]
            oa = np.argsort(u)
            ob = np.argsort(v) if (u[oa][-1]*v[np.argsort(v)][-1] < 0) else np.argsort(-v)
            Mo = M[np.ix_(oa, ob)]
        Vn = np.empty((WA.shape[0], WB.shape[0]))
        for i in range(WA.shape[0]):
            wa = np.ascontiguousarray(WA[i])
            for j in range(WB.shape[0]):
                wb = np.ascontiguousarray(WB[j])
                if mode == "lp":     Vn[i,j] = ot.emd2(wa, wb, M)
                elif mode == "state":Vn[i,j] = nw_cost_ord(wa, wb, M)
                else:                Vn[i,j] = nw_cost_ord(wa[oa], wb[ob], Mo)
        V = Vn
    return float(V[0,0])

rows = []
for tag, (d, sh, npth) in {"delta0.5": (0.5,0.25,4000), "delta0.18": (0.18,0.07,8000)}.items():
    for sd in range(2):
        rg = np.random.default_rng(40_000_000 + 1000*int(d*100) + sd)
        Xa = KD.gen_paths(50, npth, rg, a=0.7); Xb = KD.gen_paths(50, npth, rg, a=0.55, sigma=1.15)
        _a, ra, Ka = KD.build(Xa, d, sh); _b, rb, Kb = KD.build(Xb, d, sh)
        r = dict(tag=tag, delta=d, seed=sd, states=Ka[0].shape[1])
        for mode in ("lp", "state", "svd"):
            t0 = time.perf_counter(); val = dp_run(ra, Ka, rb, Kb, mode)
            r[f"t_{mode}"] = time.perf_counter()-t0; r[f"v_{mode}"] = val
        r["gap_state"] = 100*(r["v_state"]-r["v_lp"])/r["v_lp"]
        r["gap_svd"]   = 100*(r["v_svd"]-r["v_lp"])/r["v_lp"]
        r["r_state"] = r["t_state"]/r["t_lp"]; r["r_svd"] = r["t_svd"]/r["t_lp"]
        rows.append(r)
        print(f"[{tag} seed{sd}] gap thứ-tự-trạng-thái {r['gap_state']:.4f}%  thứ-tự-SVD {r['gap_svd']:.4f}%  "
              f"| thời gian {r['r_state']:.3f}x / {r['r_svd']:.3f}x LP", flush=True)
with open("handoff/rank1_endtoend.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
import statistics as st
for tag in ("delta0.5","delta0.18"):
    g = [x for x in rows if x["tag"]==tag]
    print(f"{tag}: state {st.mean(x['gap_state'] for x in g):.4f}%  svd {st.mean(x['gap_svd'] for x in g):.4f}%  "
          f"cải thiện {st.mean(x['gap_state'] for x in g)/max(st.mean(x['gap_svd'] for x in g),1e-12):.1f}x  "
          f"| svd {st.mean(x['r_svd'] for x in g):.3f}x LP, {st.mean(x['r_svd'] for x in g)/st.mean(x['r_state'] for x in g):.2f}x comonotone")
