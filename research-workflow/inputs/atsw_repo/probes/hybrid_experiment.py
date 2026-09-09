"""ATSW-hybrid: comonotone ở nút có chứng chỉ Monge, LP ở nút vi phạm.

Sinh ra từ C27–C31 (monge_gap_experiment.py). Giả thuyết đến từ 55 instance CŨ, nên bộ này
dùng SEED MỚI HOÀN TOÀN (offset 100..109; bộ cũ dùng 0..4).

DỰ ĐOÁN + TIÊU CHÍ GIẾT — viết trước khi chạy, không sửa sau khi thấy số
  H1 (tính đúng, dự đoán mạnh): hybrid phải TRÙNG DP chính xác, |gap| <= 1e-6 % trên MỌI
     instance. Lý do: quy nạp — nếu mọi nút trong cây con hoặc thoả Monge (comonotone tối ưu
     đúng cho chi phí hiệu dụng đó) hoặc được giải LP, thì V_hybrid = V_exact.
     GIẾT: tồn tại instance |gap| > 1e-6 % => lập luận quy nạp sai ở đâu đó.
  H2 (đáng giá): tỉ lệ cặp nút phải gọi LP <= 20% trung bình.
     GIẾT: > 50% => hybrid chỉ là LP kèm phí kiểm, không đáng.
  H3 (có lợi thật về chi phí): thời gian hybrid < 50% thời gian DP chính xác ở nb >= 10.
     GIẾT: >= 90% => không có lợi thế chi phí.
  Báo cáo kèm, KHÔNG quyết định: thời gian là phụ thuộc cách cài (overhead Python của emd2 ở
  bài toán nhỏ), nên đại lượng thuật toán là tỉ lệ LP tránh được, không phải wall time.

Quy ước chi phí: y nguyên monge_gap_experiment.py.
"""
import numpy as np, ot, time, csv
from monge_gap_experiment import rand_markov_tree, comono_cost, monge_viol, SCALE


def _sorted_children(xl, ml, t, i):
    idx, w = ml[t + 1][i]
    w = np.asarray(w, float); w = w / w.sum()
    o = np.argsort(xl[t + 1][list(idx)])
    return [idx[a] for a in o], np.ascontiguousarray(w[o])


def dp_run(xl_m, ml_m, xl_n, nl_n, mode, tol=1e-12):
    """mode: 'exact' | 'comono' | 'hybrid'. Trả (giá trị, số cặp nút, số lần gọi LP)."""
    T = len(xl_m) - 1
    V = (xl_m[T][:, None] - xl_n[T][None, :]) ** 2 / SCALE
    npairs = nlp = 0
    for t in range(T - 1, -1, -1):
        base = (xl_m[t][:, None] - xl_n[t][None, :]) ** 2 / SCALE
        Vn = np.empty_like(base)
        for i in range(base.shape[0]):
            iA, wA = _sorted_children(xl_m, ml_m, t, i)
            for j in range(base.shape[1]):
                iB, wB = _sorted_children(xl_n, nl_n, t, j)
                M = np.ascontiguousarray(V[np.ix_(iA, iB)])
                npairs += 1
                if mode == "exact":
                    inner = ot.emd2(wA, wB, M); nlp += 1
                elif mode == "comono":
                    inner = comono_cost(wA, wB, M)
                else:
                    v, _ = monge_viol(M)
                    if v <= tol:
                        inner = comono_cost(wA, wB, M)
                    else:
                        inner = ot.emd2(wA, wB, M); nlp += 1
                Vn[i, j] = base[i, j] + inner
        V = Vn
    i0, w0 = ml_m[0]; j0, v0 = nl_n[0]
    w0 = np.ascontiguousarray(np.asarray(w0, float) / np.sum(w0))
    v0 = np.ascontiguousarray(np.asarray(v0, float) / np.sum(v0))
    M = np.ascontiguousarray(V[np.ix_(list(i0), list(j0))])
    npairs += 1
    if mode == "exact":
        val = ot.emd2(w0, v0, M); nlp += 1
    elif mode == "comono":
        val = comono_cost(w0, v0, M)
    else:
        v, _ = monge_viol(M)
        if v <= tol:
            val = comono_cost(w0, v0, M)
        else:
            val = ot.emd2(w0, v0, M); nlp += 1
    return float(val), npairs, nlp


def run(grid, seeds=range(100, 110), out_csv="handoff/hybrid.csv"):
    rows = []
    for T, nb in grid:
        for sd in seeds:
            rng = np.random.default_rng(7_000_000 + 1000 * T + 10 * nb + sd)
            xl_m, ml_m = rand_markov_tree(T, nb, rng)
            xl_n, nl_n = rand_markov_tree(T, nb, rng)
            r = dict(T=T, nb=nb, seed=sd)
            for mode in ("exact", "comono", "hybrid"):
                t0 = time.perf_counter()
                val, npairs, nlp = dp_run(xl_m, ml_m, xl_n, nl_n, mode)
                r[f"{mode}_val"] = val
                r[f"t_{mode}"] = time.perf_counter() - t0
                r["n_nodepairs"] = npairs
                if mode == "hybrid":
                    r["n_lp_hybrid"] = nlp
                    r["frac_lp"] = nlp / npairs
            r["gap_comono_pct"] = 100.0 * (r["comono_val"] - r["exact_val"]) / r["exact_val"]
            r["gap_hybrid_pct"] = 100.0 * (r["hybrid_val"] - r["exact_val"]) / r["exact_val"]
            r["time_ratio"] = r["t_hybrid"] / r["t_exact"]
            rows.append(r)
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return rows


if __name__ == "__main__":
    grid = [(2, nb) for nb in (3, 5, 10, 20, 30)] + [(3, nb) for nb in (3, 4, 5)]
    print(f"instances={len(run(grid))}")
