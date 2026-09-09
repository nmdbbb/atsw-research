"""Vi phạm Monge của chi phí hiệu dụng có giải thích gap ghép comonotone không?

TIÊU CHÍ GIẾT — viết trước khi chạy, không sửa sau khi thấy số
  K1 (phản chứng logic, quyết định): tồn tại instance có gap >= 5% mà Phi_max <= 1e-9
      => chương trình chặn-có-điều-kiện (3b: gap <= C*Phi) CHẾT.
  K2 (tương quan): Spearman rho(Phi_max, gap%) < 0.5 => CHẾT.
  K3 (dự đoán từ note.md "cây nhị phân gần như không vi phạm"): nb=2 phải có
      Phi_max ~ 0 VÀ gap < 1%. Nếu Phi_max ~ 0 mà gap >= 5% thì trùng K1 => CHẾT.
  Thống kê CHÍNH: Phi_max (dạng sup, khớp dạng mệnh đề 3b). Phụ, không quyết định: Phi_mean, frac_viol.

QUY ƯỚC CHI PHÍ  (note.md khai "chưa ghi dùng quy ước chi phí nào" — chốt tại đây)
  c(x,y) = (x-y)^2 / (4*udrange^2);  bài toán MINIMISATION.
  Điều kiện Monge (submodular) trên giá đã sắp tăng theo giá trị:
      W[i,j] + W[i+1,j+1] <= W[i,j+1] + W[i+1,j]
  Vi phạm D = W[i,j] + W[i+1,j+1] - W[i,j+1] - W[i+1,j], lấy phần dương, chuẩn hoá bởi
  (max W - min W). Chỉ cần khối 2x2 kề nhau: submodular trên lưới tương đương điều kiện kề.

CHI PHÍ HIỆU DỤNG lấy từ quy nạp lùi CHÍNH XÁC (V thật), vì 3a phát biểu "chi phí hiệu dụng
M_t + V_{t+1} thoả Monge => comonotone tối ưu tại nút đó".

INSTANCE: cây Markov ngẫu nhiên TỰ SINH. Repo rand_tree_pichler của đối thủ không có trong
workspace, nên các số ở đây KHÔNG so trực tiếp với Bảng 1 của bản thảo; đây là thí nghiệm cơ chế
nội bộ, không phải tuyên bố tỉ lệ với đối thủ.
"""
import numpy as np, ot, json, csv

UDRANGE = 100
SCALE = 4.0 * UDRANGE ** 2


def rand_markov_tree(T, nb, rng, udrange=UDRANGE):
    xl = [np.array([0.0])]
    ml = [([0], np.array([1.0]))]
    for t in range(1, T + 1):
        vals, entries = [], []
        for _ in range(len(xl[t - 1])):
            v = rng.integers(-udrange, udrange + 1, size=nb).astype(float)
            w = rng.random(nb); w = w / w.sum()
            entries.append((list(range(len(vals), len(vals) + nb)), w))
            vals.extend(v.tolist())
        xl.append(np.array(vals)); ml.append(entries)
    return xl, ml


def comono_cost(pa, pb, M, tol=1e-14):
    """Ghép comonotone; pa/pb đã sắp theo giá trị (dùng lại _quantile_cost của atsw_kmarkov.py)."""
    i = j = 0; tot = 0.0
    a = pa.copy(); b = pb.copy()
    while i < len(a) and j < len(b):
        s = min(a[i], b[j])
        if s > tol:
            tot += s * M[i, j]
        a[i] -= s; b[j] -= s
        if a[i] <= tol: i += 1
        if b[j] <= tol: j += 1
    return tot


def monge_viol(W):
    if W.shape[0] < 2 or W.shape[1] < 2:
        return 0.0, 0.0
    D = W[:-1, :-1] + W[1:, 1:] - W[:-1, 1:] - W[1:, :-1]
    return float(np.maximum(D, 0.0).max()), float(W.max() - W.min())


def dp_both(xl_m, ml_m, xl_n, nl_n):
    """Trả (giá trị chính xác, giá trị comonotone, danh sách Phi_rel theo từng cặp nút)."""
    T = len(xl_m) - 1
    Vex = (xl_m[T][:, None] - xl_n[T][None, :]) ** 2 / SCALE
    Vco = Vex.copy()
    phis = []
    for t in range(T - 1, -1, -1):
        base = (xl_m[t][:, None] - xl_n[t][None, :]) ** 2 / SCALE
        Vex_n = np.empty_like(base); Vco_n = np.empty_like(base)
        for i in range(base.shape[0]):
            iA, wA = ml_m[t + 1][i]
            wA = np.asarray(wA, float); wA = wA / wA.sum()
            oa = np.argsort(xl_m[t + 1][list(iA)])
            iA_s = [iA[a] for a in oa]; wA_s = np.ascontiguousarray(wA[oa])
            for j in range(base.shape[1]):
                iB, wB = nl_n[t + 1][j]
                wB = np.asarray(wB, float); wB = wB / wB.sum()
                ob = np.argsort(xl_n[t + 1][list(iB)])
                iB_s = [iB[b] for b in ob]; wB_s = np.ascontiguousarray(wB[ob])
                Mex = np.ascontiguousarray(Vex[np.ix_(iA_s, iB_s)])
                Vex_n[i, j] = base[i, j] + ot.emd2(wA_s, wB_s, Mex)
                v, sc = monge_viol(Mex)
                phis.append(v / sc if sc > 0 else 0.0)
                Mco = np.ascontiguousarray(Vco[np.ix_(iA_s, iB_s)])
                Vco_n[i, j] = base[i, j] + comono_cost(wA_s, wB_s, Mco)
        Vex, Vco = Vex_n, Vco_n
    i0, w0 = ml_m[0]; j0, v0 = nl_n[0]
    w0 = np.ascontiguousarray(np.asarray(w0, float) / np.sum(w0))
    v0 = np.ascontiguousarray(np.asarray(v0, float) / np.sum(v0))
    Mex = np.ascontiguousarray(Vex[np.ix_(list(i0), list(j0))])
    exact = float(ot.emd2(w0, v0, Mex))
    if Mex.shape[0] > 1 or Mex.shape[1] > 1:
        v, sc = monge_viol(Mex); phis.append(v / sc if sc > 0 else 0.0)
    Mco = np.ascontiguousarray(Vco[np.ix_(list(i0), list(j0))])
    como = float(comono_cost(w0, v0, Mco))
    return exact, como, phis


def run(grid, n_seeds=5, out_csv="handoff/monge_gap.csv"):
    rows = []
    for T, nb in grid:
        for seed in range(n_seeds):
            rng = np.random.default_rng(1000 * T + 10 * nb + seed)
            xl_m, ml_m = rand_markov_tree(T, nb, rng)
            xl_n, nl_n = rand_markov_tree(T, nb, rng)
            exact, como, phis = dp_both(xl_m, ml_m, xl_n, nl_n)
            phis = np.asarray(phis)
            rows.append(dict(
                T=T, nb=nb, seed=seed, exact=exact, comono=como,
                gap_pct=100.0 * (como - exact) / exact,
                phi_max=float(phis.max()), phi_mean=float(phis.mean()),
                frac_viol=float((phis > 1e-12).mean()), n_nodepairs=int(phis.size)))
    with open(out_csv, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    return rows


if __name__ == "__main__":
    grid = [(2, nb) for nb in (2, 3, 4, 5, 10, 15, 20)] + [(3, nb) for nb in (2, 3, 4, 5)]
    rows = run(grid)
    print(f"instances={len(rows)}")
