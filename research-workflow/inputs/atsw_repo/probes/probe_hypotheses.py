"""Ba probe tầng giả thuyết — xác định PHÉP TÍNH NÀO KHÔNG CẦN THỰC HIỆN, và vì sao.

Khung: tại mỗi nút, M = c + V_tiep. Mọi M tách duy nhất thành phần TÁCH ĐƯỢC f(a)+g(b) và
phần dư R (căn giữa hai chiều). Phần tách được KHÔNG ảnh hưởng lựa chọn coupling (với biên cố
định nó cộng hằng số vào mọi coupling). Nên toàn bộ "phần quyết định" là R.
Với c=(x-y)^2 thì R(c) = -2xy chính xác: hạng 1, submodular, cố định mọi tầng.

TIÊU CHÍ KHAI TRƯỚC — không sửa sau khi thấy số
  H1 (phần dư hạng thấp): hạng hiệu dụng của R (số trị kỳ dị giữ 99% năng lượng Frobenius)
     <= 3 ở đa số tầng, VÀ giải bằng R chặt cụt hạng 1 cho gap < 0,23% (mức comonotone ở δ=0,5).
     GIẾT: hạng hiệu dụng > 10 ở đa số tầng => R không nén được, hướng này chết.
  H2 (ít đỉnh phân biệt): số đỉnh tối ưu PHÂN BIỆT trong 462 cặp của một tầng <= 10% số cặp.
     GIẾT: > 50% => mỗi cặp một đỉnh riêng, không phân loại được, hướng này chết.
  H3 (bỏ qua được phần lớn): với MỘT nghiệm đối ngẫu chung cho cả tầng, tỉ lệ cặp có
     (UB-LB)/|V| <= 1e-3 phải >= 50% trên TRUNG BÌNH 50 tầng (số 67,2% của lane đọc chỉ đo 1 tầng).
     GIẾT: < 20% => chặn quá rộng, hướng này chết.
Thống kê CHÍNH của mỗi probe in ra cuối. Chạy trên CÙNG bộ tầng harvest ở hai δ.
"""
import os, sys, time, json
sys.path.append(os.getcwd())
import numpy as np, ot
import kmarkov_driver as KD

def harvest(delta, shift, npaths, T=50, seed=32_000_777):
    rg = np.random.default_rng(seed)
    Xa = KD.gen_paths(T, npaths, rg, a=0.7); Xb = KD.gen_paths(T, npaths, rg, a=0.55, sigma=1.15)
    _a, ra, Ka = KD.build(Xa, delta, shift); _b, rb, Kb = KD.build(Xb, delta, shift)
    V = np.zeros((len(ra[T]), len(rb[T]))); lays = []
    for t in range(T-1, -1, -1):
        C = (ra[t+1][:,None] - rb[t+1][None,:])**2
        M = np.ascontiguousarray(C + V)
        lays.append(dict(t=t, WA=np.ascontiguousarray(Ka[t]), WB=np.ascontiguousarray(Kb[t]),
                         M=M, C=np.ascontiguousarray(C), V=V.copy()))
        Vn = np.empty((Ka[t].shape[0], Kb[t].shape[0]))
        for i in range(Ka[t].shape[0]):
            wa = np.ascontiguousarray(Ka[t][i])
            for j in range(Kb[t].shape[0]):
                Vn[i,j] = ot.emd2(wa, np.ascontiguousarray(Kb[t][j]), M)
        V = Vn
    return lays, float(V[0,0])

def center2(M):
    """Tách M = f(a)+g(b) + R (R căn giữa cả hàng lẫn cột)."""
    r = M.mean(axis=1, keepdims=True); c = M.mean(axis=0, keepdims=True); g = M.mean()
    return M - r - c + g

def eff_rank(R, frac=0.99):
    s = np.linalg.svd(R, compute_uv=False); e = np.cumsum(s**2)/max((s**2).sum(), 1e-300)
    return int(np.searchsorted(e, frac) + 1), s

def truncate(R, r):
    U, s, Vt = np.linalg.svd(R, full_matrices=False)
    return (U[:, :r] * s[:r]) @ Vt[:r]

# ---------- H1 ----------
def h1(lays, tag, rmax=3):
    ranks, share_sep = [], []
    for L in lays:
        R = center2(L["M"]); k, s = eff_rank(R)
        ranks.append(k)
        share_sep.append(1.0 - (R**2).sum()/max((L["M"] - L["M"].mean())**2, 1e-300).sum()
                         if False else 1.0 - (R**2).sum()/max(((L["M"]-L["M"].mean())**2).sum(), 1e-300))
    # gap khi CHỌN coupling bằng R chặt cụt hạng r, nhưng ĐÁNH GIÁ bằng M thật
    gaps = {}
    sub = lays[::10]
    for r in range(1, rmax+1):
        tot_e = tot_a = 0.0
        for L in sub:
            R = center2(L["M"]); Ma = truncate(R, r)
            WA, WB, M = L["WA"], L["WB"], L["M"]
            for i in range(0, WA.shape[0], 3):
                wa = np.ascontiguousarray(WA[i])
                for j in range(0, WB.shape[0], 3):
                    wb = np.ascontiguousarray(WB[j])
                    P = ot.emd(wa, wb, np.ascontiguousarray(Ma))
                    tot_a += float((P*M).sum()); tot_e += float(ot.emd2(wa, wb, M))
        gaps[r] = 100.0*(tot_a - tot_e)/tot_e
    return dict(tag=tag, rank_median=float(np.median(ranks)), rank_max=int(max(ranks)),
                rank_frac_le3=float(np.mean(np.array(ranks) <= 3)),
                sep_share_median=float(np.median(share_sep)), gaps=gaps)

# ---------- H2 ----------
def h2(lays, tag, nlay=6):
    out = []
    for L in lays[-nlay:]:                       # tầng gần gốc: V giàu cấu trúc nhất
        WA, WB, M = L["WA"], L["WB"], L["M"]
        pats = set(); npair = 0
        for i in range(WA.shape[0]):
            wa = np.ascontiguousarray(WA[i])
            for j in range(WB.shape[0]):
                P = ot.emd(wa, np.ascontiguousarray(WB[j]), M)
                pats.add((P > 1e-12).tobytes()); npair += 1
        out.append((L["t"], npair, len(pats), len(pats)/npair))
    return dict(tag=tag, per_layer=out,
                frac_distinct_mean=float(np.mean([o[3] for o in out])))

# ---------- H3 ----------
def h3(lays, tag, tol=1e-3):
    fr, widths = [], []
    for L in lays:
        WA, WB, M = L["WA"], L["WB"], L["M"]
        wa0 = np.ascontiguousarray(WA[0]/WA[0].sum()); wb0 = np.ascontiguousarray(WB[0]/WB[0].sum())
        _, log = ot.emd(wa0, wb0, M, log=True)
        u, v = log["u"], log["v"]
        LB = (WA @ u)[:, None] + (WB @ v)[None, :]
        UB = np.empty_like(LB)
        for i in range(WA.shape[0]):
            wa = np.ascontiguousarray(WA[i])
            for j in range(WB.shape[0]):
                wb = np.ascontiguousarray(WB[j])
                # ghép góc tây-bắc: chi phí đóng, không gọi LP
                ca = np.concatenate(([0.0], np.cumsum(wa))); cb = np.concatenate(([0.0], np.cumsum(wb)))
                lo = np.maximum(ca[:-1, None], cb[None, :-1]); hi = np.minimum(ca[1:, None], cb[None, 1:])
                UB[i, j] = float((np.clip(hi-lo, 0, None) * M).sum())
        scale = max(abs(float(np.median(UB))), 1e-12)
        gapm = (UB - LB)/scale
        fr.append(float((gapm <= tol).mean())); widths.append(float(np.median(gapm)))
    return dict(tag=tag, frac_skippable_mean=float(np.mean(fr)),
                frac_skippable_min=float(np.min(fr)), width_median=float(np.median(widths)))

if __name__ == "__main__":
    res = {}
    for tag, (d, sh, npth) in {"delta0.5": (0.5, 0.25, 4000), "delta0.18": (0.18, 0.07, 8000)}.items():
        t0 = time.perf_counter(); lays, root = harvest(d, sh, npth)
        print(f"[{tag}] harvest {time.perf_counter()-t0:.1f}s | {len(lays)} tầng | "
              f"M {lays[0]['M'].shape} | gốc={root:.5f}", flush=True)
        res[tag] = dict(H1=h1(lays, tag), H2=h2(lays, tag), H3=h3(lays, tag))
        print(f"[{tag}] H1 {res[tag]['H1']['rank_median']=} {res[tag]['H1']['gaps']}", flush=True)
        print(f"[{tag}] H2 frac_distinct={res[tag]['H2']['frac_distinct_mean']:.4f}", flush=True)
        print(f"[{tag}] H3 skippable={res[tag]['H3']['frac_skippable_mean']:.4f}", flush=True)
    json.dump(res, open("handoff/probes.json", "w"), indent=1)
    print("DONE")
