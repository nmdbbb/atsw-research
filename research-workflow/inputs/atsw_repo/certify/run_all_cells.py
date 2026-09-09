"""Chạy toàn bộ lưới ô: k=1 và k=2, nhiều δ, kế toán thời gian ĐÚNG, điều kiện dừng solver tự tính.

SỬA KẾ TOÁN (lỗi lượt trước: tính đôi đánh giá chính sách ở f=0, bỏ t_pe ở f>0):
  một đồng hồ duy nhất chạy từ lúc có paths tới lúc trả kết quả; mọi bước nằm trong đó.

k=2: trạng thái là CỬA SỔ (c_{t-1}, c_t). Phải kiểm lại trên biểu diễn này chứ không mặc định
  mọi phép tái sử dụng của k=1 còn đúng: chi phí chỉ phụ thuộc ô HIỆN TẠI của cửa sổ, nên M có
  hàng/cột trùng nhau; nhân chuyển cửa sổ thưa (chỉ nối được khi ô hiện tại khớp).
  Số trạng thái ~ (số ô)^2 nên chi phí đánh giá chính sách ~ (nm)^2: ô k=2 buộc phải dùng lưới thô
  hơn và T ngắn hơn. Khai rõ, không so trực tiếp thời gian giữa ô k=1 và k=2.

ĐIỀU KIỆN DỪNG: (U0-L0)/L0 <= 0.005, không dùng V*. Leo thang đồng thời f (cải thiện chính sách)
  và B (pool đối ngẫu); sàn cận dưới GIỮ NGUYÊN qua mọi bước leo thang (mọi cận dưới hợp lệ đều
  dùng lại được — sàn không phụ thuộc J, J chỉ dùng để CHỌN).
"""
import os, sys, time, csv, json
sys.path.append(os.getcwd())
import numpy as np, ot
import kmarkov_driver as KD
from certify5 import nw_plan, ctransform, svd_ord, free_lb

TOL = 0.005

def build_k2(X, delta, shift):
    """Trạng thái = cửa sổ (c_{t-1}, c_t), t=1..T. Trả (reps_cur, kernels, root_idx)."""
    C = np.floor((X - shift)/delta).astype(np.int64); T = C.shape[1]-1
    W = [None]*(T+1); codes = [None]*(T+1); reps = [None]*(T+1)
    for t in range(1, T+1):
        pair = np.stack([C[:, t-1], C[:, t]], 1)
        uniq, inv = np.unique(pair, axis=0, return_inverse=True)
        W[t] = inv; codes[t] = uniq
        reps[t] = (uniq[:, 1] + 0.5)*delta + shift          # chi phí chỉ dùng ô HIỆN TẠI
    K = []
    for t in range(1, T):
        Kt = np.zeros((len(codes[t]), len(codes[t+1])))
        np.add.at(Kt, (W[t], W[t+1]), 1.0)
        row = Kt.sum(1, keepdims=True)
        K.append(np.ascontiguousarray(np.where(row > 0, Kt/np.maximum(row, 1e-300), 1.0/Kt.shape[1])))
    root = int(np.bincount(W[1]).argmax())
    return reps[1:], K, root                                # reps[0] ứng với tầng đầu của DP

def exact_dp(reps, K, root):
    T = len(K); V = np.zeros((K[T-1].shape[1], 0)) if False else None
    nA = [k.shape[0] for k in K] + [K[-1].shape[1]]
    return None

def dp_generic(repsA, KA, repsB, KB, inner, rootA=0, rootB=0):
    T = len(KA); V = np.zeros((KA[T-1].shape[1], KB[T-1].shape[1])); npairs = 0
    for t in range(T-1, -1, -1):
        M = np.ascontiguousarray((repsA[t+1][:, None]-repsB[t+1][None, :])**2 + V)
        WA = KA[t]/KA[t].sum(1, keepdims=True); WB = KB[t]/KB[t].sum(1, keepdims=True)
        Vn = np.empty((WA.shape[0], WB.shape[0]))
        for i in range(WA.shape[0]):
            wa = np.ascontiguousarray(WA[i])
            for j in range(WB.shape[0]):
                Vn[i, j] = inner(wa, np.ascontiguousarray(WB[j]), M); npairs += 1
        V = Vn
    return float(V[rootA, rootB]), npairs

def policy_eval(repsA, KA, repsB, KB, f=0.0, mus=None):
    T = len(KA); J = np.zeros((KA[T-1].shape[1], KB[T-1].shape[1])); Js = [None]*(T+1); Js[T] = J
    n_lp = 0
    for t in range(T-1, -1, -1):
        M = np.ascontiguousarray((repsA[t+1][:, None]-repsB[t+1][None, :])**2 + J)
        WA = KA[t]/KA[t].sum(1, keepdims=True); WB = KB[t]/KB[t].sum(1, keepdims=True)
        oa, obp, obm = svd_ord(M); Mp, Mm = M[np.ix_(oa, obp)], M[np.ix_(oa, obm)]
        Jn = np.empty((WA.shape[0], WB.shape[0]))
        for i in range(WA.shape[0]):
            wa = WA[i][oa]
            for j in range(WB.shape[0]):
                Jn[i, j] = min(float((nw_plan(wa, WB[j][obp])*Mp).sum()),
                               float((nw_plan(wa, WB[j][obm])*Mm).sum()))
        if f > 0 and mus is not None:
            k = int(f*Jn.size)
            if k > 0:
                for fl in np.argpartition(mus[t].ravel(), -k)[-k:]:
                    i, j = divmod(int(fl), Jn.shape[1])
                    v = float(ot.emd2(np.ascontiguousarray(WA[i]), np.ascontiguousarray(WB[j]), M))
                    n_lp += 1
                    if v < Jn[i, j]: Jn[i, j] = v
        J = Jn; Js[t] = J
    return Js, n_lp

def occupancy(repsA, KA, repsB, KB, Js, rootA=0, rootB=0):
    T = len(KA); mus = []
    mu = np.zeros((KA[0].shape[0], KB[0].shape[0])); mu[rootA, rootB] = 1.0
    for t in range(T):
        mus.append(mu)
        M = np.ascontiguousarray((repsA[t+1][:, None]-repsB[t+1][None, :])**2 + Js[t+1])
        WA = KA[t]/KA[t].sum(1, keepdims=True); WB = KB[t]/KB[t].sum(1, keepdims=True)
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

def lower_sweep(repsA, KA, repsB, KB, Js, B, mus, floors=None):
    T = len(KA); L = np.zeros((KA[T-1].shape[1], KB[T-1].shape[1]))
    tabs = [None]*(T+1); tabs[T] = L; n_lp = 0
    for t in range(T-1, -1, -1):
        ML = np.ascontiguousarray((repsA[t+1][:, None]-repsB[t+1][None, :])**2 + L)
        WA = KA[t]/KA[t].sum(1, keepdims=True); WB = KB[t]/KB[t].sum(1, keepdims=True)
        Lt = free_lb(ML, WA, WB)
        if floors is not None: Lt = np.maximum(Lt, floors[t])
        seen = set()
        for _ in range(B):
            sc = ((Js[t]-Lt)*mus[t]).copy()
            for (i, j) in seen: sc[i, j] = -np.inf
            i0, j0 = np.unravel_index(int(np.argmax(sc)), sc.shape)
            if not np.isfinite(sc[i0, j0]): break
            seen.add((i0, j0))
            _, lg = ot.emd(np.ascontiguousarray(WA[i0]), np.ascontiguousarray(WB[j0]), ML, log=True)
            n_lp += 1
            al, be = ctransform(ML, np.asarray(lg["u"], float))
            Lt = np.maximum(Lt, (WA @ al)[:, None] + (WB @ be)[None, :])
        L = Lt; tabs[t] = L
    return L, tabs, n_lp

def certified_solve(repsA, KA, repsB, KB, rootA=0, rootB=0, schedule=None):
    """MỘT đồng hồ từ (reps,K) tới kết quả. Leo thang f và B tới khi (U-L)/L <= TOL."""
    if schedule is None:
        schedule = [(0.0, 32), (0.0, 128), (0.05, 256), (0.15, 512), (0.35, 1024)]
    t0 = time.perf_counter(); n_lp = 0; floors = None; hist = []
    Js, k1 = policy_eval(repsA, KA, repsB, KB); n_lp += k1
    mus = occupancy(repsA, KA, repsB, KB, Js, rootA, rootB)
    f_cur = 0.0
    for (f, B) in schedule:
        if f > f_cur:
            Js, k2 = policy_eval(repsA, KA, repsB, KB, f=f, mus=mus); n_lp += k2; f_cur = f
        L, floors, k3 = lower_sweep(repsA, KA, repsB, KB, Js, B, mus, floors); n_lp += k3
        U0 = float(Js[0][rootA, rootB]); L0 = float(L[rootA, rootB])
        cert = (U0-L0)/L0 if L0 > 0 else float("inf")
        hist.append(dict(f=f, B=B, U0=U0, L0=L0, cert=cert, n_lp=n_lp,
                         t=time.perf_counter()-t0))
        if cert <= TOL: break
    return dict(U0=U0, L0=L0, cert=cert, n_lp=n_lp, t_total=time.perf_counter()-t0,
                reached=bool(cert <= TOL), hist=hist)

if __name__ == "__main__":
    CELLS = [("k1", 0.5, 0.25, 50, 4000), ("k1", 0.3, 0.12, 50, 6000), ("k1", 0.18, 0.07, 50, 8000),
             ("k2", 1.0, 0.5, 15, 2000), ("k2", 0.7, 0.3, 15, 2000)]
    out = []
    for (kind, delta, shift, T, npth) in CELLS:
        rg = np.random.default_rng(70_000_000 + int(delta*100) + (1000 if kind == "k2" else 0))
        Xa = KD.gen_paths(T, npth, rg, a=0.7); Xb = KD.gen_paths(T, npth, rg, a=0.55, sigma=1.15)
        if kind == "k1":
            _s, raL, KA = KD.build(Xa, delta, shift); _s2, rbL, KB = KD.build(Xb, delta, shift)
            rA = rB = 0
        else:
            raL, KA, rA = build_k2(Xa, delta, shift); rbL, KB, rB = build_k2(Xb, delta, shift)
        nst = max(k.shape[0] for k in KA)
        npair_tot = sum(KA[t].shape[0]*KB[t].shape[0] for t in range(len(KA)))
        print(f"\n=== {kind} δ={delta} T={T}: {nst} trạng thái tối đa, {npair_tot} cặp nút", flush=True)
        if npair_tot > 700_000:
            print("   BỎ QUA: quá đắt cho tham chiếu chính xác", flush=True)
            out.append(dict(kind=kind, delta=delta, T=T, states=nst, npairs=npair_tot, skipped=True)); continue
        t0 = time.perf_counter()
        ve, _ = dp_generic(raL, KA, rbL, KB, lambda a, b, M: float(ot.emd2(a, b, M)), rA, rB)
        t_ex = time.perf_counter()-t0
        res = certified_solve(raL, KA, rbL, KB, rA, rB)
        rec = dict(kind=kind, delta=delta, T=T, states=nst, npairs=npair_tot, skipped=False,
                   v_exact=ve, t_exact=t_ex, U0=res["U0"], L0=res["L0"],
                   cert_pct=100*res["cert"], gapU_pct=100*(res["U0"]-ve)/ve,
                   valid=bool(res["L0"] <= ve+1e-9 and ve <= res["U0"]+1e-9),
                   reached=res["reached"], t_total=res["t_total"], ratio=res["t_total"]/t_ex,
                   n_lp=res["n_lp"], lp_frac=res["n_lp"]/npair_tot,
                   hist=";".join(f"f{h['f']}/B{h['B']}:{100*h['cert']:.2f}%@{h['t']:.0f}s" for h in res["hist"]))
        out.append(rec)
        print(f"   V*={ve:.6f} | U0 lệch {rec['gapU_pct']:.3f}% | chứng nhận {rec['cert_pct']:.3f}% "
              f"{'ĐẠT' if rec['reached'] else 'CHƯA ĐẠT'} | hợp lệ={rec['valid']} | "
              f"{rec['t_total']:.1f}s = {rec['ratio']:.2f}x | LP {res['n_lp']} = {100*rec['lp_frac']:.1f}%", flush=True)
        print(f"   lịch sử: {rec['hist']}", flush=True)
    keys = sorted({k for r in out for k in r})
    with open("handoff/all_cells.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(out)
    print("\nDONE", len(out), "ô")
