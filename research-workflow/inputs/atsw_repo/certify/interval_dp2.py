"""Chẩn đoán + sửa cận dưới của đệ quy khoảng.

CHẨN ĐOÁN: r0 cho độ rộng 1e15% => cận dưới bùng nổ. Cận trên (coupling khả thi đánh giá trên c+U)
lành vì luôn là giá trị thật của một coupling hợp lệ. Cận dưới dùng MỘT thế đối ngẫu của MỘT cặp
đại diện: khả thi nên hợp lệ, nhưng lỏng ở các cặp xa, và độ lỏng cộng dồn qua 50 tầng.

SỬA (vẫn không LP ở mức cặp):
  1. c-transform: từ alpha bất kỳ, beta_j = min_i (M_ij - alpha_i), rồi alpha_i = min_j (M_ij - beta_j)
     -> thế đối ngẫu khả thi cực đại theo toạ độ, cận dưới chặt nhất trong lớp đó. O(nm).
  2. R thế đối ngẫu từ R cặp đại diện, LB = max theo từng ô. O(R*nm).
TIÊU CHÍ: B1 (hợp lệ tại gốc) giữ nguyên; B2' độ rộng tại gốc vòng 0 phải < 100%.
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
    be = (M - al[:, None]).min(axis=0)
    al = (M - be[None, :]).min(axis=1)
    return al, be

def svd_ord(M):
    R = M - M.mean(1, keepdims=True) - M.mean(0, keepdims=True) + M.mean()
    U, s, Vt = np.linalg.svd(R, full_matrices=False)
    return np.argsort(U[:, 0]), np.argsort(Vt[0]), np.argsort(-Vt[0])

def run(ra, Ka, rb, Kb, T=50, R=4, refine_frac=0.0, diag=False):
    L = np.zeros((len(ra[T]), len(rb[T]))); U = L.copy(); n_lp = 0; slack = []
    for t in range(T-1, -1, -1):
        C = (ra[t+1][:, None] - rb[t+1][None, :])**2
        ML = np.ascontiguousarray(C + L); MU = np.ascontiguousarray(C + U)
        WA, WB = Ka[t], Kb[t]
        WAn = WA/WA.sum(1, keepdims=True); WBn = WB/WB.sum(1, keepdims=True)
        LBt = np.full((WA.shape[0], WB.shape[0]), -np.inf)
        for ri in np.linspace(0, WA.shape[0]-1, R).astype(int):
            _, lg = ot.emd(np.ascontiguousarray(WAn[ri]), np.ascontiguousarray(WBn[0]), ML, log=True)
            n_lp += 1
            al, be = ctransform(ML, np.asarray(lg["u"], float))
            LBt = np.maximum(LBt, (WAn @ al)[:, None] + (WBn @ be)[None, :])
        oa, obp, obm = svd_ord(MU); MUp = MU[np.ix_(oa, obp)]; MUm = MU[np.ix_(oa, obm)]
        UBt = np.empty_like(LBt)
        for i in range(WA.shape[0]):
            wa = WAn[i][oa]
            for j in range(WB.shape[0]):
                UBt[i, j] = min(float((nw_plan(wa, WBn[j][obp])*MUp).sum()),
                                float((nw_plan(wa, WBn[j][obm])*MUm).sum()))
        if diag and t >= T-3:
            ex = np.array([[float(ot.emd2(np.ascontiguousarray(WAn[i]), np.ascontiguousarray(WBn[j]), ML))
                            for j in range(WB.shape[0])] for i in range(WA.shape[0])])
            sc = max(abs(float(np.median(ex))), 1e-12)
            slack.append((t, float(np.median((ex-LBt)/sc)), float(np.median((UBt-ex)/sc))))
        if refine_frac > 0:
            w = UBt - LBt; k = max(1, int(refine_frac*w.size))
            for f in np.argpartition(w.ravel(), -k)[-k:]:
                i, j = divmod(int(f), w.shape[1])
                a_ = np.ascontiguousarray(WAn[i]); b_ = np.ascontiguousarray(WBn[j])
                LBt[i, j] = max(LBt[i, j], float(ot.emd2(a_, b_, ML)))
                UBt[i, j] = min(UBt[i, j], float(ot.emd2(a_, b_, MU))); n_lp += 2
        L, U = LBt, np.maximum(UBt, LBt)
    return float(L[0, 0]), float(U[0, 0]), n_lp, slack

rows = []
for sd in range(3):
    rg = np.random.default_rng(50_000_000 + sd)
    Xa = KD.gen_paths(50, 4000, rg, a=0.7); Xb = KD.gen_paths(50, 4000, rg, a=0.55, sigma=1.15)
    _a, ra, Ka = KD.build(Xa, 0.5, 0.25); _b, rb, Kb = KD.build(Xb, 0.5, 0.25)
    t0 = time.perf_counter(); ve = KD.dp(ra, Ka, rb, Kb, KD.solve_lp)[0]; t_ex = time.perf_counter()-t0
    r = dict(seed=sd, v_exact=ve, t_exact=t_ex)
    if sd == 0:
        _, _, _, sl = run(ra, Ka, rb, Kb, diag=True)
        print("độ lỏng tương đối 3 tầng đầu (t, LB thiếu, UB thừa):",
              [(t, round(a, 4), round(b, 4)) for t, a, b in sl], flush=True)
    for tag, fr in (("r0", 0.0), ("r1", 0.05), ("r2", 0.20)):
        t0 = time.perf_counter(); L0, U0, nlp, _ = run(ra, Ka, rb, Kb, refine_frac=fr)
        dt = time.perf_counter()-t0
        r.update({f"{tag}_L": L0, f"{tag}_U": U0, f"{tag}_width": 100*(U0-L0)/ve,
                  f"{tag}_valid": bool(L0 <= ve+1e-9 and ve <= U0+1e-9),
                  f"{tag}_ratio": dt/t_ex, f"{tag}_nlp": nlp})
    rows.append(r)
    print(f"[seed{sd}] exact={ve:.5f} | " + "  ".join(
        f"{tg}: rộng {r[f'{tg}_width']:.3f}% {'OK' if r[f'{tg}_valid'] else 'VI PHẠM'} {r[f'{tg}_ratio']:.2f}x"
        for tg in ("r0", "r1", "r2")), flush=True)
with open("handoff/interval_dp2.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
import statistics as st
print("\nB1 hợp lệ:", all(r[f"{t}_valid"] for r in rows for t in ("r0", "r1", "r2")))
for tg in ("r0", "r1", "r2"):
    print(f"  {tg}: rộng {st.mean(r[f'{tg}_width'] for r in rows):.3f}%  "
          f"{st.mean(r[f'{tg}_ratio'] for r in rows):.2f}x  LP {st.mean(r[f'{tg}_nlp'] for r in rows):.0f}")
