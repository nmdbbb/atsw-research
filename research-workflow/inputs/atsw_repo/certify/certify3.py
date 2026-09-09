"""Ba phép kiểm theo phản biện: (1) đơn điệu thật sự, (2) cận trên = đánh giá chính sách cố định,
(3) cận dưới bằng POOL thế đối ngẫu mở rộng thích nghi, mỗi thế dùng lại cho CẢ TẦNG.

Sửa hai suy luận sai của lượt trước:
 - Toán tử Bellman KHÔNG khuếch đại theo chuẩn sup: ||TV - TW||_inf <= ||V - W||_inf (kỳ vọng rồi min).
   Sai số cộng dồn CỘNG tính qua tầng, không nhân. Nên "mỗi tầng phải chặt 1e-3" là chưa suy ra được.
 - Khoảng rộng ra sau tinh chỉnh là DẤU HIỆU LỖI, không phải bằng chứng "sai số phân tán": phải giữ
   L_new = max(L_old, L_moi), U_new = min(U_old, U_moi) trên CÙNG instance.

CẬN TRÊN (không LP): chính sách pi = ghép NW theo thứ tự SVD. Đánh giá lùi J^pi = <pi, c + J^pi>.
   Mọi pi hợp lệ về biên => J^pi >= V* theo từng ô. Đây chính là nhánh 'svd' đã đo (+0,159%).
CẬN DƯỚI: L_t(i,j) = max_k [<p_i,alpha^k> + <q_j,beta^k>], pool duals khả thi cho c+L_{t+1},
   siết bằng c-transform. Pool chọn theo khoảng (J_t - L_t) hiện tại — mỗi dual mới cải thiện CẢ TẦNG.

BÁO CÁO: L_0, U_0, V_exact TUYỆT ĐỐI (không chỉ %), và độ rộng phải GIẢM đơn điệu theo R.
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
    """Cận TRÊN: đánh giá lùi chính sách NW-theo-thứ-tự-SVD. Không LP, không tối ưu thêm."""
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
    return J, Js

def lower_bound(ra, Ka, rb, Kb, Js, R, T=50):
    """Cận DƯỚI với pool R thế đối ngẫu mỗi tầng, chọn theo khoảng (J - L) hiện tại."""
    L = np.zeros((len(ra[T]), len(rb[T]))); n_lp = 0
    for t in range(T-1, -1, -1):
        ML = np.ascontiguousarray((ra[t+1][:, None]-rb[t+1][None, :])**2 + L)
        WA = Ka[t]/Ka[t].sum(1, keepdims=True); WB = Kb[t]/Kb[t].sum(1, keepdims=True)
        Lt = np.full((WA.shape[0], WB.shape[0]), -np.inf)
        for k in range(R):
            if k == 0:
                i0, j0 = 0, 0
            else:
                w = Js[t] - Lt; i0, j0 = np.unravel_index(int(np.argmax(w)), w.shape)
            _, lg = ot.emd(np.ascontiguousarray(WA[i0]), np.ascontiguousarray(WB[j0]), ML, log=True)
            n_lp += 1
            al, be = ctransform(ML, np.asarray(lg["u"], float))
            Lt = np.maximum(Lt, (WA @ al)[:, None] + (WB @ be)[None, :])
        L = np.minimum(Lt, Js[t])          # giữ cận tốt nhất đã biết, không bao giờ vượt cận trên
    return L, n_lp

rows = []
for sd in range(2):
    rg = np.random.default_rng(50_000_000 + sd)
    Xa = KD.gen_paths(50, 4000, rg, a=0.7); Xb = KD.gen_paths(50, 4000, rg, a=0.55, sigma=1.15)
    _a, ra, Ka = KD.build(Xa, 0.5, 0.25); _b, rb, Kb = KD.build(Xb, 0.5, 0.25)
    t0 = time.perf_counter(); ve = KD.dp(ra, Ka, rb, Kb, KD.solve_lp)[0]; t_ex = time.perf_counter()-t0
    t0 = time.perf_counter(); J0, Js = policy_eval(ra, Ka, rb, Kb); t_pe = time.perf_counter()-t0
    U0 = float(J0[0, 0])
    print(f"[seed{sd}] V_exact={ve:.6f} ({t_ex:.1f}s) | U0 (đánh giá chính sách)={U0:.6f} "
          f"(+{100*(U0-ve)/ve:.3f}%, {t_pe/t_ex:.2f}x) | U0>=V: {U0 >= ve-1e-9}", flush=True)
    for R in (1, 4, 16, 64):
        t0 = time.perf_counter(); L, nlp = lower_bound(ra, Ka, rb, Kb, Js, R); dt = time.perf_counter()-t0
        L0 = float(L[0, 0])
        rows.append(dict(seed=sd, R=R, v_exact=ve, U0=U0, L0=L0, width_abs=U0-L0,
                         width_rel=100*(U0-L0)/ve, valid=bool(L0 <= ve+1e-9 and ve <= U0+1e-9),
                         t_lb=dt, t_pe=t_pe, t_exact=t_ex, ratio=(dt+t_pe)/t_ex, n_lp=nlp))
        print(f"   R={R:3d}: L0={L0:.6f}  rộng tuyệt đối={U0-L0:.6f}  ({100*(U0-L0)/ve:.2f}%)  "
              f"{'OK' if rows[-1]['valid'] else 'VI PHẠM'}  {rows[-1]['ratio']:.2f}x  LP={nlp}", flush=True)
with open("handoff/certify3.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
mono = all(rows[i]["width_abs"] >= rows[i+1]["width_abs"] - 1e-12
           for i in range(len(rows)-1) if rows[i]["seed"] == rows[i+1]["seed"])
print("\nđơn điệu theo R (rộng không tăng):", mono)
