"""MỐC 2 — đệ quy mang khoảng dưới–trên, chứng nhận TẠI GỐC.

Cơ sở: toán tử OT đơn điệu theo ma trận chi phí. Nếu L_{t+1} <= V*_{t+1} <= U_{t+1} theo từng ô thì
   OT(p,q; c+L_{t+1})  <=  V*_t(i,j)  <=  OT(p,q; c+U_{t+1}).
Không cần giải hai LP mỗi nút:
  - CẬN DƯỚI rẻ: một thế đối ngẫu KHẢ THI (alpha,beta) cho c+L dùng chung cả tầng (khả thi đối ngẫu
    không phụ thuộc biên) => LB(i,j) = <p_i,alpha> + <q_j,beta> <= OT(c+L) <= V*.
  - CẬN TRÊN rẻ: bất kỳ coupling KHẢ THI nào đánh giá trên c+U => UB(i,j) >= OT(c+U) >= V*.
    Dùng ghép góc tây-bắc theo thứ tự SVD (phát hiện trước đó) làm coupling đề xuất.
Chi phí: 1 LP mỗi TẦNG (lấy đối ngẫu) + O(nm) mỗi cặp. Không LP ở mức cặp.

TIÊU CHÍ KHAI TRƯỚC — không sửa sau khi thấy số
  B1 (tính hợp lệ, cổng cứng): L_0 <= V_exact <= U_0 trên MỌI seed. Vi phạm => cận sai, dừng.
  B2 (đáng dùng): độ rộng tương đối tại gốc (U_0-L_0)/V_exact < 100% ở vòng 0.
      >= 100% => cận quá lỏng để làm nền, thiết kế này chết.
  B3 (sửa thích nghi có tác dụng): mỗi vòng tinh chỉnh (giải chính xác các cặp có khoảng rộng nhất)
      phải làm hẹp độ rộng tại gốc; sau <= 3 vòng phải đạt < 10% với tổng thời gian < thời gian DP chính xác.
Phụ (sửa lỗi phép đo cũ): khoảng cách Kendall-tau CHUẨN HOÁ giữa thứ tự SVD và thứ tự trạng thái
  (số CẶP đảo, không phải số chỗ giảm kề nhau như audit trước).
"""
import os, sys, time, json, csv
sys.path.append(os.getcwd())
import numpy as np, ot
import kmarkov_driver as KD

def center2(M): return M - M.mean(1, keepdims=True) - M.mean(0, keepdims=True) + M.mean()

def nw_plan(wa, wb):
    ca = np.concatenate(([0.], np.cumsum(wa))); cb = np.concatenate(([0.], np.cumsum(wb)))
    lo = np.maximum(ca[:-1, None], cb[None, :-1]); hi = np.minimum(ca[1:, None], cb[None, 1:])
    return np.clip(hi - lo, 0, None)

def kendall_norm(o):
    n = len(o); r = np.empty(n); r[o] = np.arange(n)
    inv = sum(int((r[i+1:] < r[i]).sum()) for i in range(n))
    return inv / (n*(n-1)/2)

def svd_order(M):
    U, s, Vt = np.linalg.svd(center2(M), full_matrices=False)
    u, v = U[:, 0], Vt[0]
    return np.argsort(u), np.argsort(v), np.argsort(-v)

def interval_dp(ra, Ka, rb, Kb, T=50, refine_frac=0.0, rounds=0):
    """Trả (L0, U0, n_lp, kt) — n_lp = tổng số lần gọi LP thật."""
    nA, nB = len(ra[T]), len(rb[T])
    L = np.zeros((nA, nB)); U = np.zeros((nA, nB)); n_lp = 0; kts = []
    for t in range(T-1, -1, -1):
        C = (ra[t+1][:, None] - rb[t+1][None, :])**2
        ML = np.ascontiguousarray(C + L); MU = np.ascontiguousarray(C + U)
        WA, WB = Ka[t], Kb[t]
        # --- cận dưới: một thế đối ngẫu khả thi cho ML, dùng chung cả tầng
        p0 = np.ascontiguousarray(WA[0]/WA[0].sum()); q0 = np.ascontiguousarray(WB[0]/WB[0].sum())
        _, lg = ot.emd(p0, q0, ML, log=True); n_lp += 1
        al, be = lg["u"], lg["v"]
        LBt = (WA @ al)[:, None] + (WB @ be)[None, :]
        # --- cận trên: coupling đề xuất theo thứ tự SVD, đánh giá trên MU
        oa, obp, obm = svd_order(MU); kts.append(kendall_norm(oa))
        MUp = MU[np.ix_(oa, obp)]; MUm = MU[np.ix_(oa, obm)]
        UBt = np.empty((WA.shape[0], WB.shape[0]))
        for i in range(WA.shape[0]):
            wa = WA[i]/WA[i].sum()
            for j in range(WB.shape[0]):
                wb = WB[j]/WB[j].sum()
                P = nw_plan(wa[oa], wb[obp]); c1 = float((P*MUp).sum())
                P2 = nw_plan(wa[oa], wb[obm]); c2 = float((P2*MUm).sum())
                UBt[i, j] = min(c1, c2)
        # --- tinh chỉnh: giải chính xác các cặp có khoảng rộng nhất
        if refine_frac > 0:
            w = UBt - LBt; k = int(refine_frac*w.size)
            if k > 0:
                idx = np.argpartition(w.ravel(), -k)[-k:]
                for f in idx:
                    i, j = divmod(int(f), w.shape[1])
                    wa = np.ascontiguousarray(WA[i]/WA[i].sum()); wb = np.ascontiguousarray(WB[j]/WB[j].sum())
                    lo_ = float(ot.emd2(wa, wb, ML)); hi_ = float(ot.emd2(wa, wb, MU)); n_lp += 2
                    LBt[i, j] = max(LBt[i, j], lo_); UBt[i, j] = min(UBt[i, j], hi_)
        L, U = LBt, np.maximum(UBt, LBt)
    return float(L[0, 0]), float(U[0, 0]), n_lp, float(np.median(kts))

rows = []
for sd in range(3):
    rg = np.random.default_rng(50_000_000 + sd)
    Xa = KD.gen_paths(50, 4000, rg, a=0.7); Xb = KD.gen_paths(50, 4000, rg, a=0.55, sigma=1.15)
    _a, ra, Ka = KD.build(Xa, 0.5, 0.25); _b, rb, Kb = KD.build(Xb, 0.5, 0.25)
    t0 = time.perf_counter(); ve = KD.dp(ra, Ka, rb, Kb, KD.solve_lp)[0]; t_ex = time.perf_counter()-t0
    r = dict(seed=sd, v_exact=ve, t_exact=t_ex)
    for tag, fr in (("r0", 0.0), ("r1", 0.02), ("r2", 0.10), ("r3", 0.30)):
        t0 = time.perf_counter(); L0, U0, nlp, kt = interval_dp(ra, Ka, rb, Kb, refine_frac=fr)
        dt = time.perf_counter()-t0
        r[f"{tag}_L"], r[f"{tag}_U"] = L0, U0
        r[f"{tag}_width"] = 100*(U0-L0)/ve
        r[f"{tag}_valid"] = bool(L0 <= ve + 1e-9 and ve <= U0 + 1e-9)
        r[f"{tag}_t"] = dt; r[f"{tag}_ratio"] = dt/t_ex; r[f"{tag}_nlp"] = nlp
        r["kendall"] = kt
    rows.append(r)
    print(f"[seed{sd}] exact={ve:.5f} ({t_ex:.1f}s) | " + "  ".join(
        f"{tg}: rộng {r[f'{tg}_width']:.2f}% {'OK' if r[f'{tg}_valid'] else 'VI PHẠM'} {r[f'{tg}_ratio']:.2f}x"
        for tg in ("r0","r1","r2","r3")), flush=True)
with open("handoff/interval_dp.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
import statistics as st
print("\nB1 hợp lệ mọi seed/mọi vòng:", all(r[f"{tg}_valid"] for r in rows for tg in ("r0","r1","r2","r3")))
for tg in ("r0","r1","r2","r3"):
    print(f"  {tg}: rộng {st.mean(r[f'{tg}_width'] for r in rows):.2f}%  "
          f"thời gian {st.mean(r[f'{tg}_ratio'] for r in rows):.2f}x  LP {st.mean(r[f'{tg}_nlp'] for r in rows):.0f}")
print(f"Kendall-tau chuẩn hoá (thứ tự SVD vs trạng thái): {st.mean(r['kendall'] for r in rows):.4f}")
