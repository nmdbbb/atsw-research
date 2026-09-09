"""Cận dưới, bản đã sửa bốn lỗi do phản biện chỉ ra.

LỖI 1 — chọn lặp: vòng chọn không loại cặp đã giải trên CÙNG ma trận ML, nên "R lời gọi LP" không
        bằng "R miền đã phủ". SỬA: dedup theo (t, phiên bản ML); đếm riêng lời gọi, cặp KHÁC NHAU,
        và lời gọi KHÔNG cải thiện cận.
LỖI 2 — min(Lt, J) không phải "giữ cận dưới tốt nhất": nó chỉ ép L <= J và có thể làm L tụt.
        SỬA: giữ SÀN từ lần chạy trước (mọi cận dưới hợp lệ đều dùng được: L = max(L_moi, L_san)).
LỖI 3 — bỏ cận MIỄN PHÍ: c >= 0 nên V* >= 0; thêm cả cận nửa-nới-lỏng (bỏ một ràng buộc biên) và
        c-transform từ alpha=0. Tất cả O(nm), không LP. Cận dưới 0 đã cho độ rộng ~100%, tốt hơn
        276%/311% của bản trước.
LỖI 4 — thời gian: cộng đủ thời gian cận trên (đánh giá chính sách) + thời gian tính mu + cận dưới.
Và: mọi benchmark nằm dưới __main__ để import không tự chạy.
"""
import os, sys, time, csv
sys.path.append(os.getcwd())
import numpy as np, ot
import kmarkov_driver as KD

def nw_plan(wa, wb):
    ca = np.concatenate(([0.], np.cumsum(wa))); cb = np.concatenate(([0.], np.cumsum(wb)))
    lo = np.maximum(ca[:-1, None], cb[None, :-1]); hi = np.minimum(ca[1:, None], cb[None, 1:])
    return np.clip(hi - lo, 0, None)

def ctransform(M, al):
    be = (M - al[:, None]).min(0); al = (M - be[None, :]).min(1); return al, be

def svd_ord(M):
    R = M - M.mean(1, keepdims=True) - M.mean(0, keepdims=True) + M.mean()
    U, s, Vt = np.linalg.svd(R, full_matrices=False)
    return np.argsort(U[:, 0]), np.argsort(Vt[0]), np.argsort(-Vt[0])

def policy_eval(ra, Ka, rb, Kb, T=50):
    J = np.zeros((len(ra[T]), len(rb[T]))); Js = [None]*(T+1); Js[T] = J
    for t in range(T-1, -1, -1):
        M = np.ascontiguousarray((ra[t+1][:, None]-rb[t+1][None, :])**2 + J)
        WA, WB = Ka[t]/Ka[t].sum(1, keepdims=True), Kb[t]/Kb[t].sum(1, keepdims=True)
        oa, obp, obm = svd_ord(M); Mp, Mm = M[np.ix_(oa, obp)], M[np.ix_(oa, obm)]
        Jn = np.empty((WA.shape[0], WB.shape[0]))
        for i in range(WA.shape[0]):
            wa = WA[i][oa]
            for j in range(WB.shape[0]):
                Jn[i, j] = min(float((nw_plan(wa, WB[j][obp])*Mp).sum()),
                               float((nw_plan(wa, WB[j][obm])*Mm).sum()))
        J = Jn; Js[t] = J
    return Js

def occupancy(ra, Ka, rb, Kb, Js, T=50):
    mus = []; mu = np.zeros((Ka[0].shape[0], Kb[0].shape[0])); mu[0, 0] = 1.0
    for t in range(T):
        mus.append(mu)
        M = np.ascontiguousarray((ra[t+1][:, None]-rb[t+1][None, :])**2 + Js[t+1])
        WA = Ka[t]/Ka[t].sum(1, keepdims=True); WB = Kb[t]/Kb[t].sum(1, keepdims=True)
        oa, obp, obm = svd_ord(M); Mp, Mm = M[np.ix_(oa, obp)], M[np.ix_(oa, obm)]
        nxt = np.zeros(M.shape)
        for (i, j) in np.argwhere(mu > 1e-14):
            wa = WA[i][oa]
            P1 = nw_plan(wa, WB[j][obp]); P2 = nw_plan(wa, WB[j][obm])
            P, ob = (P1, obp) if (P1*Mp).sum() <= (P2*Mm).sum() else (P2, obm)
            full = np.zeros(M.shape); full[np.ix_(oa, ob)] = P
            nxt += mu[i, j]*full
        mu = nxt
    return mus

def free_lb(ML, WA, WB):
    """Cận dưới MIỄN PHÍ (không LP): 0, nửa-nới-lỏng hai chiều, c-transform từ alpha=0."""
    al, be = ctransform(ML, np.zeros(ML.shape[0]))
    lb = (WA @ al)[:, None] + (WB @ be)[None, :]
    lb = np.maximum(lb, (WA @ ML.min(1))[:, None])
    lb = np.maximum(lb, (WB @ ML.min(0))[None, :])
    return np.maximum(lb, 0.0)

def lower_sweep(ra, Ka, rb, Kb, Js, B, sel, mus=None, floors=None, T=50):
    """Một lượt lùi với ngân sách B cặp KHÁC NHAU mỗi tầng. Trả (L0, tables, thống kê)."""
    L = np.zeros((len(ra[T]), len(rb[T]))); tables = [None]*(T+1); tables[T] = L
    n_lp = distinct = wasted = 0
    for t in range(T-1, -1, -1):
        ML = np.ascontiguousarray((ra[t+1][:, None]-rb[t+1][None, :])**2 + L)
        WA = Ka[t]/Ka[t].sum(1, keepdims=True); WB = Kb[t]/Kb[t].sum(1, keepdims=True)
        Lt = free_lb(ML, WA, WB)
        if floors is not None: Lt = np.maximum(Lt, floors[t])       # LỖI 2: giữ sàn hợp lệ đã có
        seen = set()
        for _ in range(B):
            w = Js[t] - Lt
            if sel == "mu":    sc = w * mus[t]
            elif sel == "lai": sc = w * np.maximum(mus[t], 1e-6)     # lai: khối lượng + phủ rộng
            else:              sc = w
            sc = sc.copy()
            for (i, j) in seen: sc[i, j] = -np.inf                   # LỖI 1: chống lặp
            i0, j0 = np.unravel_index(int(np.argmax(sc)), sc.shape)
            if not np.isfinite(sc[i0, j0]): break
            seen.add((i0, j0)); distinct += 1
            _, lg = ot.emd(np.ascontiguousarray(WA[i0]), np.ascontiguousarray(WB[j0]), ML, log=True)
            n_lp += 1
            al, be = ctransform(ML, np.asarray(lg["u"], float))
            cand = (WA @ al)[:, None] + (WB @ be)[None, :]
            before = Lt.sum(); Lt = np.maximum(Lt, cand)
            if Lt.sum() <= before + 1e-12: wasted += 1
        L = Lt; tables[t] = L
    return float(L[0, 0]), tables, dict(n_lp=n_lp, distinct=distinct, wasted=wasted)

if __name__ == "__main__":
    rows = []
    for sd in range(2):
        rg = np.random.default_rng(50_000_000 + sd)
        Xa = KD.gen_paths(50, 4000, rg, a=0.7); Xb = KD.gen_paths(50, 4000, rg, a=0.55, sigma=1.15)
        _a, ra, Ka = KD.build(Xa, 0.5, 0.25); _b, rb, Kb = KD.build(Xb, 0.5, 0.25)
        t0 = time.perf_counter(); ve = KD.dp(ra, Ka, rb, Kb, KD.solve_lp)[0]; t_ex = time.perf_counter()-t0
        t0 = time.perf_counter(); Js = policy_eval(ra, Ka, rb, Kb); t_pe = time.perf_counter()-t0
        U0 = float(Js[0][0, 0])
        t0 = time.perf_counter(); mus = occupancy(ra, Ka, rb, Kb, Js); t_mu = time.perf_counter()-t0
        # cận dưới MIỄN PHÍ, 0 LP
        t0 = time.perf_counter(); L0f, _, _ = lower_sweep(ra, Ka, rb, Kb, Js, 0, "rong"); t_free = time.perf_counter()-t0
        print(f"[seed{sd}] V*={ve:.6f}  U0={U0:.6f} (+{100*(U0-ve)/ve:.3f}%, {t_pe/t_ex:.2f}x)  "
              f"| cận dưới MIỄN PHÍ L0={L0f:.6f} -> rộng {100*(U0-L0f)/ve:.2f}% ở {(t_pe+t_free)/t_ex:.2f}x", flush=True)
        for sel in ("rong", "mu", "lai"):
            floors = None
            for B in (4, 16, 64):
                t0 = time.perf_counter()
                L0, tabs, st = lower_sweep(ra, Ka, rb, Kb, Js, B, sel, mus=mus, floors=floors)
                dt = time.perf_counter()-t0; floors = tabs
                tot = (t_pe + dt + (t_mu if sel != "rong" else 0.0))/t_ex
                rows.append(dict(seed=sd, sel=sel, B=B, v_exact=ve, U0=U0, L0=L0,
                                 width_rel=100*(U0-L0)/ve, valid=bool(L0 <= ve+1e-9 and ve <= U0+1e-9),
                                 ratio_total=tot, **st))
                print(f"   [{sel:4s}] B={B:3d}: L0={L0:9.5f} rộng {100*(U0-L0)/ve:7.2f}%  "
                      f"{'OK' if rows[-1]['valid'] else 'VI PHẠM'}  {tot:.2f}x tổng | LP={st['n_lp']} "
                      f"cặp khác nhau={st['distinct']} lời gọi vô ích={st['wasted']}", flush=True)
    with open("handoff/certify5.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
