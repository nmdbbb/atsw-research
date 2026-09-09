"""Cận dưới: chọn cặp đại diện theo ĐỘ RỘNG vs theo ĐỘ RỘNG x KHỐI LƯỢNG CHIẾM CHỖ.

Lý do có cơ sở (sửa lập luận sup-norm của lượt trước): toán tử Bellman không khuếch đại theo chuẩn
sup, và độ lệch tại GỐC lan truyền qua KỲ VỌNG, không qua sup. Nên độ lệch tại gốc xấp xỉ
  sum_t  E_{mu_t}[ slack_t ],
với mu_t là khối lượng chiếm chỗ tại tầng t. Cặp có khoảng rộng nhưng mu ~ 0 không ảnh hưởng gốc.
=> chọn cặp đại diện theo (J - L) * mu thay vì (J - L).

Kiểm luôn giới hạn biểu diễn: pool là max các hàm TUYẾN TÍNH theo (p,q), mà V(p,q) là hàm lồi
tuyến-tính-từng-khúc với số miền ~ số cơ sở tối ưu phân biệt. Đã đo trước: 99% cặp có cơ sở riêng
(~462 miền/tầng). Nếu đúng thì pool phải lớn cỡ số cặp mới chặt — tức không rẻ hơn giải hết.
"""
import os, sys, time, csv
sys.path.append(os.getcwd())
import numpy as np, ot
import kmarkov_driver as KD
from certify3 import nw_plan, ctransform, svd_ord, policy_eval

def occupancy(ra, Ka, rb, Kb, T=50, J=None, Js=None):
    """Khối lượng chiếm chỗ mu_t dưới chính sách SVD (tiến từ gốc)."""
    mus = []
    mu = np.zeros((Ka[0].shape[0], Kb[0].shape[0])); mu[0, 0] = 1.0
    for t in range(T):
        mus.append(mu)
        M = np.ascontiguousarray((ra[t+1][:, None]-rb[t+1][None, :])**2 + (Js[t+1] if Js else 0.0))
        WA = Ka[t]/Ka[t].sum(1, keepdims=True); WB = Kb[t]/Kb[t].sum(1, keepdims=True)
        oa, obp, obm = svd_ord(M); Mp, Mm = M[np.ix_(oa, obp)], M[np.ix_(oa, obm)]
        nxt = np.zeros((M.shape[0], M.shape[1]))
        nz = np.argwhere(mu > 1e-14)
        for (i, j) in nz:
            wa = WA[i][oa]
            P1 = nw_plan(wa, WB[j][obp]); P2 = nw_plan(wa, WB[j][obm])
            P, ob = (P1, obp) if (P1*Mp).sum() <= (P2*Mm).sum() else (P2, obm)
            full = np.zeros_like(nxt); full[np.ix_(oa, ob)] = P
            nxt += mu[i, j]*full
        mu = nxt
    return mus

def lower_bound(ra, Ka, rb, Kb, Js, R, mus=None, T=50):
    L = np.zeros((len(ra[T]), len(rb[T]))); n_lp = 0
    for t in range(T-1, -1, -1):
        ML = np.ascontiguousarray((ra[t+1][:, None]-rb[t+1][None, :])**2 + L)
        WA = Ka[t]/Ka[t].sum(1, keepdims=True); WB = Kb[t]/Kb[t].sum(1, keepdims=True)
        Lt = np.full((WA.shape[0], WB.shape[0]), -np.inf)
        w8 = (mus[t] if mus is not None else None)
        for k in range(R):
            if k == 0: i0, j0 = 0, 0
            else:
                sc = Js[t] - Lt
                if w8 is not None: sc = sc * w8
                i0, j0 = np.unravel_index(int(np.argmax(sc)), sc.shape)
            _, lg = ot.emd(np.ascontiguousarray(WA[i0]), np.ascontiguousarray(WB[j0]), ML, log=True)
            n_lp += 1
            al, be = ctransform(ML, np.asarray(lg["u"], float))
            Lt = np.maximum(Lt, (WA @ al)[:, None] + (WB @ be)[None, :])
        L = np.minimum(Lt, Js[t])
    return L, n_lp

rows = []
for sd in range(2):
    rg = np.random.default_rng(50_000_000 + sd)
    Xa = KD.gen_paths(50, 4000, rg, a=0.7); Xb = KD.gen_paths(50, 4000, rg, a=0.55, sigma=1.15)
    _a, ra, Ka = KD.build(Xa, 0.5, 0.25); _b, rb, Kb = KD.build(Xb, 0.5, 0.25)
    t0 = time.perf_counter(); ve = KD.dp(ra, Ka, rb, Kb, KD.solve_lp)[0]; t_ex = time.perf_counter()-t0
    J0, Js = policy_eval(ra, Ka, rb, Kb); U0 = float(J0[0, 0])
    t0 = time.perf_counter(); mus = occupancy(ra, Ka, rb, Kb, Js=Js); t_mu = time.perf_counter()-t0
    supp = [int((m > 1e-14).sum()) for m in mus]
    print(f"[seed{sd}] V={ve:.6f} U0={U0:.6f} (+{100*(U0-ve)/ve:.3f}%) | giá của mu: "
          f"trung vị {int(np.median(supp))} cặp/tầng trên {mus[-1].size} ({t_mu:.1f}s)", flush=True)
    for R in (16, 64, 128, 256):
        for tag, mm in (("rộng", None), ("rộng×mu", mus)):
            t0 = time.perf_counter(); L, nlp = lower_bound(ra, Ka, rb, Kb, Js, R, mus=mm)
            dt = time.perf_counter()-t0; L0 = float(L[0, 0])
            rows.append(dict(seed=sd, R=R, sel=tag, v_exact=ve, U0=U0, L0=L0, width_abs=U0-L0,
                             width_rel=100*(U0-L0)/ve, valid=bool(L0 <= ve+1e-9 and ve <= U0+1e-9),
                             ratio=dt/t_ex, n_lp=nlp))
            print(f"   R={R:3d} [{tag:8s}] L0={L0:9.5f}  rộng {100*(U0-L0)/ve:8.2f}%  "
                  f"{'OK' if rows[-1]['valid'] else 'VI PHẠM'}  {dt/t_ex:.2f}x  LP={nlp}", flush=True)
with open("handoff/certify4.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
