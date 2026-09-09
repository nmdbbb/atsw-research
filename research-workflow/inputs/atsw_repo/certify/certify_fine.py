"""Ô khó (δ=0,18): cải thiện chính sách + điều kiện dừng solver tự tính được.

ĐIỀU KIỆN DỪNG (không dùng V*): (U0 - L0)/L0 <= 0.005. Hợp lệ vì 0 < L0 <= V* <= U0 nên
   (U0 - V*)/V* <= (U0 - L0)/L0. Mọi thời gian (chính sách, cải thiện, mu, pool) đều tính vào tổng.

CẢI THIỆN CHÍNH SÁCH: định lý cải thiện chính sách — lấy bước greedy theo J tại MỘT SỐ cặp, giữ
   coupling cũ ở phần còn lại => J' <= J theo từng ô, nên J' vẫn là cận trên hợp lệ và chặt hơn.
   Chọn cặp theo khối lượng chiếm chỗ mu (chỗ ảnh hưởng gốc), phần f nhỏ nhất trước.
TIÊU CHÍ: ở δ=0,18, U0 hiện lệch 1,465% > 0,5% nên chứng nhận KHÔNG THỂ đạt 0,5% mà không cải
   thiện chính sách. Cần đo: f bằng bao nhiêu thì U0 xuống dưới 0,5%, và tổng thời gian bao nhiêu.
"""
import os, sys, time, csv
sys.path.append(os.getcwd())
import numpy as np, ot
import kmarkov_driver as KD
from certify5 import nw_plan, ctransform, svd_ord, free_lb, occupancy

def policy_eval_improved(ra, Ka, rb, Kb, f, mus=None, T=50):
    """Đánh giá chính sách: greedy theo J tại phần f cặp có mu lớn nhất, NW-SVD ở phần còn lại."""
    J = np.zeros((len(ra[T]), len(rb[T]))); Js = [None]*(T+1); Js[T] = J; n_lp = 0
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
        if f > 0 and mus is not None:
            k = int(f*Jn.size)
            if k > 0:
                sel = np.argpartition(mus[t].ravel(), -k)[-k:]
                for fl in sel:
                    i, j = divmod(int(fl), Jn.shape[1])
                    v = float(ot.emd2(np.ascontiguousarray(WA[i]), np.ascontiguousarray(WB[j]), M))
                    n_lp += 1
                    if v < Jn[i, j]: Jn[i, j] = v          # greedy: chỉ nhận nếu tốt hơn
        J = Jn; Js[t] = J
    return Js, n_lp

def lower_to_threshold(ra, Ka, rb, Kb, Js, mus, tol=0.005, Bs=(16, 64, 128, 256), T=50):
    """Tăng ngân sách theo đợt, giữ sàn, dừng khi (U-L)/L <= tol. Trả (L0, tổng LP, lịch sử)."""
    floors = None; hist = []; n_lp = 0; U0 = float(Js[0][0, 0])
    for B in Bs:
        L = np.zeros((len(ra[T]), len(rb[T]))); tabs = [None]*(T+1); tabs[T] = L
        for t in range(T-1, -1, -1):
            ML = np.ascontiguousarray((ra[t+1][:, None]-rb[t+1][None, :])**2 + L)
            WA = Ka[t]/Ka[t].sum(1, keepdims=True); WB = Kb[t]/Kb[t].sum(1, keepdims=True)
            Lt = free_lb(ML, WA, WB)
            if floors is not None: Lt = np.maximum(Lt, floors[t])
            seen = set()
            for _ in range(B):
                sc = ((Js[t] - Lt) * mus[t]).copy()
                for (i, j) in seen: sc[i, j] = -np.inf
                i0, j0 = np.unravel_index(int(np.argmax(sc)), sc.shape)
                if not np.isfinite(sc[i0, j0]): break
                seen.add((i0, j0))
                _, lg = ot.emd(np.ascontiguousarray(WA[i0]), np.ascontiguousarray(WB[j0]), ML, log=True)
                n_lp += 1
                al, be = ctransform(ML, np.asarray(lg["u"], float))
                Lt = np.maximum(Lt, (WA @ al)[:, None] + (WB @ be)[None, :])
            L = Lt; tabs[t] = L
        floors = tabs; L0 = float(L[0, 0])
        cert = (U0 - L0)/L0 if L0 > 0 else np.inf
        hist.append((B, L0, cert, n_lp))
        if cert <= tol: break
    return L0, n_lp, hist

if __name__ == "__main__":
    rows = []
    for delta, shift, npth in ((0.18, 0.07, 8000),):
        rg = np.random.default_rng(60_000_000)
        Xa = KD.gen_paths(50, npth, rg, a=0.7); Xb = KD.gen_paths(50, npth, rg, a=0.55, sigma=1.15)
        _a, ra, Ka = KD.build(Xa, delta, shift); _b, rb, Kb = KD.build(Xb, delta, shift)
        t0 = time.perf_counter(); ve = KD.dp(ra, Ka, rb, Kb, KD.solve_lp)[0]; t_ex = time.perf_counter()-t0
        print(f"[δ={delta}] V*={ve:.6f}  DP chính xác {t_ex:.1f}s  ({Ka[0].shape[1]} trạng thái)", flush=True)
        t0 = time.perf_counter(); Js0, _ = policy_eval_improved(ra, Ka, rb, Kb, 0.0); t_pe = time.perf_counter()-t0
        t0 = time.perf_counter(); mus = occupancy(ra, Ka, rb, Kb, Js0); t_mu = time.perf_counter()-t0
        print(f"   chính sách SVD: U0={float(Js0[0][0,0]):.6f} (+{100*(float(Js0[0][0,0])-ve)/ve:.3f}%) "
              f"{t_pe/t_ex:.2f}x | mu {t_mu/t_ex:.2f}x", flush=True)
        for f in (0.0, 0.02, 0.10, 0.30):
            t0 = time.perf_counter(); Js, nlp_pi = policy_eval_improved(ra, Ka, rb, Kb, f, mus=mus)
            t_pi = time.perf_counter()-t0; U0 = float(Js[0][0, 0])
            gapU = 100*(U0-ve)/ve
            t0 = time.perf_counter(); L0, nlp_lb, hist = lower_to_threshold(ra, Ka, rb, Kb, Js, mus)
            t_lb = time.perf_counter()-t0
            cert = 100*(U0-L0)/L0 if L0 > 0 else float("inf")
            tot = (t_pe if f == 0 else 0) + t_mu + t_pi + t_lb
            rows.append(dict(delta=delta, f=f, v_exact=ve, U0=U0, L0=L0, gapU_pct=gapU,
                             cert_pct=cert, valid=bool(L0 <= ve+1e-9 and ve <= U0+1e-9),
                             t_total=tot, ratio=tot/t_ex, nlp_pi=nlp_pi, nlp_lb=nlp_lb,
                             hist=";".join(f"B{b}:{100*c:.3f}%" for b, _l, c, _n in hist)))
            print(f"   f={f:.2f}: U0 lệch {gapU:6.3f}%  chứng nhận (U-L)/L = {cert:6.3f}%  "
                  f"{'OK' if rows[-1]['valid'] else 'VI PHẠM'}  tổng {tot/t_ex:.2f}x  "
                  f"LP(cải thiện)={nlp_pi} LP(cận dưới)={nlp_lb} | {rows[-1]['hist']}", flush=True)
    with open("handoff/certify_fine.csv", "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
