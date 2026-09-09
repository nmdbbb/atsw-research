"""Kiểm bốn phản biện, mỗi cái bằng một số đo.

A. "99% năng lượng" != hạng 1: báo ||E||_F/||R||_F (chuẩn), không phải năng lượng.
B. "thẳng hàng": đo cos(R(V), R(c)) và sai số của xấp xỉ R(V) ~ alpha*R(c). Nếu thẳng hàng
   với hệ số dương thì thứ tự SVD PHẢI trùng thứ tự trạng thái -> mâu thuẫn với cải thiện đã đo.
C. hạng 1 có phải do cost cơ sở: chạy lại với c=|x-y| (căn giữa KHÔNG cho hạng 1) và
   c=(x-y)^2 để so. Nếu chỉ (x-y)^2 mới hạng 1 thì cấu trúc là của benchmark, không phải cơ chế.
D. quy tắc thứ tự phải xác định: thay heuristic dấu bằng "thử cả hai chiều, lấy min" (vẫn O(nm),
   không gọi LP) và đo xem heuristic cũ có chọn sai chiều ở đâu không.
"""
import os, sys, json
sys.path.append(os.getcwd())
import numpy as np, ot
import kmarkov_driver as KD

def center2(M):
    return M - M.mean(1, keepdims=True) - M.mean(0, keepdims=True) + M.mean()

def harvest(cost, delta=0.5, shift=0.25, npaths=4000, T=50, seed=32_000_777):
    rg = np.random.default_rng(seed)
    Xa = KD.gen_paths(T, npaths, rg, a=0.7); Xb = KD.gen_paths(T, npaths, rg, a=0.55, sigma=1.15)
    _a, ra, Ka = KD.build(Xa, delta, shift); _b, rb, Kb = KD.build(Xb, delta, shift)
    V = np.zeros((len(ra[T]), len(rb[T]))); lays = []
    for t in range(T-1, -1, -1):
        C = cost(ra[t+1][:, None] - rb[t+1][None, :]); M = np.ascontiguousarray(C + V)
        lays.append(dict(WA=np.ascontiguousarray(Ka[t]), WB=np.ascontiguousarray(Kb[t]),
                         M=M, C=np.ascontiguousarray(C), V=V.copy()))
        Vn = np.empty((Ka[t].shape[0], Kb[t].shape[0]))
        for i in range(Ka[t].shape[0]):
            wa = np.ascontiguousarray(Ka[t][i])
            for j in range(Kb[t].shape[0]):
                Vn[i, j] = ot.emd2(wa, np.ascontiguousarray(Kb[t][j]), M)
        V = Vn
    return lays

def nw(wa, wb, Mo):
    ca = np.concatenate(([0.], np.cumsum(wa))); cb = np.concatenate(([0.], np.cumsum(wb)))
    lo = np.maximum(ca[:-1, None], cb[None, :-1]); hi = np.minimum(ca[1:, None], cb[None, 1:])
    return float((np.clip(hi - lo, 0, None) * Mo).sum())

def audit(tag, cost):
    lays = harvest(cost)
    fr_E, cos_, alpha_err, rkC, rkV, inv = [], [], [], [], [], []
    for L in lays:
        R, Rc, Rv = center2(L["M"]), center2(L["C"]), center2(L["V"])
        U, s, Vt = np.linalg.svd(R, full_matrices=False)
        fr_E.append(float(np.sqrt((s[1:]**2).sum()) / max(np.linalg.norm(R), 1e-300)))
        nc, nv = np.linalg.norm(Rc), np.linalg.norm(Rv)
        cos_.append(float((Rc*Rv).sum()/max(nc*nv, 1e-300)) if nv > 1e-12 else np.nan)
        al = (Rc*Rv).sum()/max((Rc*Rc).sum(), 1e-300)
        alpha_err.append(float(np.linalg.norm(Rv - al*Rc)/max(nv, 1e-300)) if nv > 1e-12 else np.nan)
        sc = np.linalg.svd(Rc, compute_uv=False); sv = np.linalg.svd(Rv, compute_uv=False)
        f = lambda ss: int(np.searchsorted(np.cumsum(ss**2)/max((ss**2).sum(), 1e-300), .99)+1)
        rkC.append(f(sc)); rkV.append(f(sv) if nv > 1e-12 else 0)
        o = np.argsort(U[:, 0]); inv.append(int((np.diff(o) < 0).sum()))
    # D: thứ tự SVD với quy tắc "thử cả hai chiều lấy min", so với heuristic cũ
    tot = dict(exact=0., state=0., svd_min=0., svd_heur=0.); flip = 0; npair = 0
    for L in lays[::5]:
        M, WA, WB = L["M"], L["WA"], L["WB"]
        U, s, Vt = np.linalg.svd(center2(M), full_matrices=False)
        u, v = U[:, 0], Vt[0]; oa = np.argsort(u)
        obp, obm = np.argsort(v), np.argsort(-v)
        heur = obp if (u[oa][-1]*v[obp][-1] < 0) else obm
        Mp, Mm = M[np.ix_(oa, obp)], M[np.ix_(oa, obm)]
        Mh = M[np.ix_(oa, heur)]
        ids, jds = np.arange(M.shape[0]), np.arange(M.shape[1])
        for i in range(0, WA.shape[0], 2):
            wa = WA[i]/WA[i].sum()
            for j in range(0, WB.shape[0], 2):
                wb = WB[j]/WB[j].sum()
                e = float(ot.emd2(np.ascontiguousarray(wa), np.ascontiguousarray(wb), M))
                cp, cm = nw(wa[oa], wb[obp], Mp), nw(wa[oa], wb[obm], Mm)
                tot["exact"] += e; tot["state"] += nw(wa, wb, M[np.ix_(ids, jds)])
                tot["svd_min"] += min(cp, cm); tot["svd_heur"] += nw(wa[oa], wb[heur], Mh)
                flip += int(nw(wa[oa], wb[heur], Mh) > min(cp, cm) + 1e-12); npair += 1
    g = {k: 100*(tot[k]-tot["exact"])/tot["exact"] for k in ("state", "svd_min", "svd_heur")}
    return dict(tag=tag, fracE_median=float(np.median(fr_E)), fracE_max=float(np.max(fr_E)),
                cos_median=float(np.nanmedian(cos_)), alpha_err_median=float(np.nanmedian(alpha_err)),
                rank_Rc=int(np.median(rkC)), rank_Rv=int(np.median(rkV)),
                inversions_median=float(np.median(inv)), npair=npair,
                flip_frac=flip/max(npair, 1), gaps=g)

out = []
for tag, cost in (("c=(x-y)^2", lambda d: d**2), ("c=|x-y|", lambda d: np.abs(d))):
    r = audit(tag, cost); out.append(r)
    print(f"[{tag}] ||E||/||R|| trung vị {r['fracE_median']:.3f} (max {r['fracE_max']:.3f}) "
          f"| hạng R(c)={r['rank_Rc']} hạng R(V)={r['rank_Rv']}", flush=True)
    print(f"[{tag}] cos(R(V),R(c)) trung vị {r['cos_median']:.3f} | sai số xấp xỉ R(V)≈αR(c): "
          f"{r['alpha_err_median']:.3f} | đảo thứ tự SVD vs trạng thái: {r['inversions_median']:.0f}", flush=True)
    print(f"[{tag}] gap: trạng thái {r['gaps']['state']:.4f}%  SVD-min {r['gaps']['svd_min']:.4f}%  "
          f"SVD-heuristic {r['gaps']['svd_heur']:.4f}%  | heuristic chọn sai chiều {100*r['flip_frac']:.1f}% cặp", flush=True)
json.dump(out, open("handoff/audit_rank1.json", "w"), indent=1)
