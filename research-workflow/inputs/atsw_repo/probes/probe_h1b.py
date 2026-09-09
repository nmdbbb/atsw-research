"""H1b — hệ quả của 'phần dư quyết định hạng 1'.

M = f(a)+g(b) + R. Phần tách được không ảnh hưởng coupling. R = R(c) + R(V), và R(c) = -2xy
CHÍNH XÁC hạng 1 với c=(x-y)^2. Nếu R tổng vẫn ~hạng 1 thì bài toán tại nút có NGHIỆM ĐÓNG:
với chi phí hạng 1 (sigma * u v^T), Hardy-Littlewood cho biết coupling tối ưu là ghép đơn điệu
theo THỨ TỰ CỦA u và v (comonotone nếu sigma<0, antitone nếu sigma>0). Không cần LP.

Đây là điểm khác biệt thật so với comonotone hiện tại: comonotone hiện ghép theo THỨ TỰ TRẠNG
THÁI; nghiệm đóng đúng phải ghép theo thứ tự VECTOR KỲ DỊ TRÁI/PHẢI của R.

TIÊU CHÍ KHAI TRƯỚC
  A. ||R(V)||_F / ||R(c)||_F theo tầng: nếu << 1 thì R(c) chi phối và thứ tự u ~ thứ tự trạng thái.
  B. gap của 'ghép theo thứ tự u,v' phải NHỎ HƠN gap comonotone theo thứ tự trạng thái
     (0,23% ở δ=0,5; 2,32% ở δ=0,18) trên cùng bộ tầng. Nếu KHÔNG nhỏ hơn => hướng hạng-1 chết.
  C. mọi biên phải chuẩn hoá về tổng 1 trước khi gọi POT (lỗi của lần chạy trước).
"""
import os, sys, time, json
sys.path.append(os.getcwd())
import numpy as np, ot
from probe_hypotheses import harvest, center2, eff_rank

def nw_cost(wa, wb, M, oa, ob):
    """chi phí ghép góc tây-bắc khi hàng sắp theo oa, cột sắp theo ob (không gọi LP)."""
    a = wa[oa]; b = wb[ob]
    ca = np.concatenate(([0.0], np.cumsum(a))); cb = np.concatenate(([0.0], np.cumsum(b)))
    lo = np.maximum(ca[:-1, None], cb[None, :-1]); hi = np.minimum(ca[1:, None], cb[None, 1:])
    return float((np.clip(hi - lo, 0, None) * M[np.ix_(oa, ob)]).sum())

def run(tag, delta, shift, npaths):
    lays, root = harvest(delta, shift, npaths)
    rel, rk = [], []
    for L in lays:
        Rc = center2(L["C"]); Rv = center2(L["V"]); R = center2(L["M"])
        rel.append(float(np.linalg.norm(Rv)/max(np.linalg.norm(Rc), 1e-300)))
        rk.append(eff_rank(R)[0])
    idord = None
    tot = {"exact":0.0, "state":0.0, "svd":0.0}; npair = 0
    for L in lays[::5]:
        WA, WB, M = L["WA"], L["WB"], L["M"]
        R = center2(M)
        U, s, Vt = np.linalg.svd(R, full_matrices=False)
        u = U[:,0]*s[0]; v = Vt[0]
        # chi phí hạng 1 = u_i v_j: tối ưu là ghép đơn điệu ngược dấu tích
        oa = np.argsort(u); ob = np.argsort(v) if u[np.argsort(u)][-1]*v[np.argsort(v)][-1] < 0 else np.argsort(-v)
        ids = np.arange(M.shape[0]); jds = np.arange(M.shape[1])
        for i in range(0, WA.shape[0], 2):
            wa = WA[i]/WA[i].sum()
            for j in range(0, WB.shape[0], 2):
                wb = WB[j]/WB[j].sum()
                tot["exact"] += float(ot.emd2(np.ascontiguousarray(wa), np.ascontiguousarray(wb), M))
                tot["state"] += nw_cost(wa, wb, M, ids, jds)
                tot["svd"]   += nw_cost(wa, wb, M, oa, ob)
                npair += 1
    g = {k: 100.0*(tot[k]-tot["exact"])/tot["exact"] for k in ("state","svd")}
    return dict(tag=tag, npair=npair, rank_median=float(np.median(rk)),
                relRv_median=float(np.median(rel)), relRv_max=float(np.max(rel)),
                gap_state_order=g["state"], gap_svd_order=g["svd"])

if __name__ == "__main__":
    out = []
    for tag, (d, sh, n) in {"delta0.5": (0.5,0.25,4000), "delta0.18": (0.18,0.07,8000)}.items():
        r = run(tag, d, sh, n); out.append(r)
        print(f"[{tag}] hạng R = {r['rank_median']:.0f} | ||R(V)||/||R(c)|| trung vị {r['relRv_median']:.3f} "
              f"max {r['relRv_max']:.3f}", flush=True)
        print(f"[{tag}] gap ghép theo THỨ TỰ TRẠNG THÁI = {r['gap_state_order']:.3f}%  |  "
              f"theo THỨ TỰ SVD = {r['gap_svd_order']:.3f}%   ({r['npair']} cặp)", flush=True)
    json.dump(out, open("handoff/probe_h1b.json","w"), indent=1)
