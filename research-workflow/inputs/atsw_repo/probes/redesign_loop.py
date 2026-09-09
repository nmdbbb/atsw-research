"""Vòng lặp thiết kế lại inner solver: sinh biến thể (LLM) -> oracle chấm -> giữ champion -> lặp.

MỤC TIÊU VẬN HÀNH (khai một lần, không nới trong lúc chạy)
  G1  tính đúng là CỔNG CỨNG: |gap| <= 1e-6 % so với DP chính xác trên mọi instance.
      Biến thể không đạt G1 bị loại, trừ khi tự khai là xấp xỉ KÈM chặn -> nhánh riêng.
  G2  tỉ lệ cặp nút phải gọi LP: worst case THEO INSTANCE <= 5%.
      (champion hiện tại: 9,78% worst / 3,10% mean -> CHƯA đạt)
  G3  frac_lp KHÔNG tăng theo độ sâu T trên dải đo được.
      (champion hiện tại: nb=3 đi 2,73% ở T=2 lên 7,17% ở T=3 -> CHƯA đạt, đây là rủi ro chính)
  G4  thời gian < 0,5x DP chính xác.  (champion: 0,29x -> ĐẠT)

BẤT BIẾN
  I1  không bao giờ chấm biến thể trên instance đã sinh ra nó: seed offset = f(cycle), tăng mỗi chu kỳ.
  I2  G1 là cổng cứng, kiểm trước khi xét bất kỳ chỉ số nào khác.
  I3  mỗi chu kỳ phải có research_notes khác rỗng (bước "cần gì + tra nhanh") mới chạy được.
  I4  mọi phán quyết vào claim_ledger.csv.

DỪNG khi đạt G1-G4, hoặc 3 chu kỳ liên tiếp không biến thể nào vượt champion -> báo người
(đó là tín hiệu mục tiêu sai hoặc thiếu ý tưởng từ ngoài, không phải thiếu compute).

ĐƠN VỊ ĐỘT BIẾN: hàm inner_solve(wA, wB, M) -> (value, used_lp: bool)
  wA, wB: khối lượng con đã sắp theo giá trị (chuẩn hoá). M: chi phí hiệu dụng, đã sắp cùng thứ tự.
  Hợp đồng: trả về đúng min_{pi} <M,pi> nếu muốn qua G1. used_lp=True khi có gọi LP.
"""
import os, sys, time, json, csv
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
import numpy as np, ot
from monge_gap_experiment import rand_markov_tree, comono_cost, monge_viol, SCALE

# ---------- oracle ----------

def dp_with_solver(xl_m, ml_m, xl_n, nl_n, inner_solve):
    T = len(xl_m) - 1
    V = (xl_m[T][:, None] - xl_n[T][None, :]) ** 2 / SCALE
    npairs = nlp = 0
    def kids(xl, ml, t, i):
        idx, w = ml[t + 1][i]
        w = np.asarray(w, float); w = w / w.sum()
        o = np.argsort(xl[t + 1][list(idx)])
        return [idx[a] for a in o], np.ascontiguousarray(w[o])
    for t in range(T - 1, -1, -1):
        base = (xl_m[t][:, None] - xl_n[t][None, :]) ** 2 / SCALE
        Vn = np.empty_like(base)
        for i in range(base.shape[0]):
            iA, wA = kids(xl_m, ml_m, t, i)
            for j in range(base.shape[1]):
                iB, wB = kids(xl_n, nl_n, t, j)
                M = np.ascontiguousarray(V[np.ix_(iA, iB)])
                val, used = inner_solve(wA, wB, M)
                Vn[i, j] = base[i, j] + val
                npairs += 1; nlp += bool(used)
        V = Vn
    i0, w0 = ml_m[0]; j0, v0 = nl_n[0]
    w0 = np.ascontiguousarray(np.asarray(w0, float) / np.sum(w0))
    v0 = np.ascontiguousarray(np.asarray(v0, float) / np.sum(v0))
    M = np.ascontiguousarray(V[np.ix_(list(i0), list(j0))])
    val, used = inner_solve(w0, v0, M)
    return float(val), npairs + 1, nlp + bool(used)


def instances(grid, seeds, cycle):
    for T, nb in grid:
        for sd in seeds:
            rng = np.random.default_rng(10_000_000 * (cycle + 1) + 1000 * T + 10 * nb + sd)
            yield T, nb, sd, rand_markov_tree(T, nb, rng), rand_markov_tree(T, nb, rng)


def score(name, inner_solve, grid, seeds, cycle):
    rows = []
    for T, nb, sd, (xl_m, ml_m), (xl_n, nl_n) in instances(grid, seeds, cycle):
        ex, npairs, _ = dp_with_solver(xl_m, ml_m, xl_n, nl_n, solve_lp)
        t0 = time.perf_counter()
        va, np2, nlp = dp_with_solver(xl_m, ml_m, xl_n, nl_n, inner_solve)
        dt = time.perf_counter() - t0
        t0 = time.perf_counter(); dp_with_solver(xl_m, ml_m, xl_n, nl_n, solve_lp)
        dt_ex = time.perf_counter() - t0
        rows.append(dict(variant=name, cycle=cycle, T=T, nb=nb, seed=sd, exact=ex, value=va,
                         gap_pct=100.0 * (va - ex) / ex, n_nodepairs=np2, n_lp=nlp,
                         frac_lp=nlp / np2, t=dt, t_exact=dt_ex, time_ratio=dt / dt_ex))
    return rows


def verdict(rows):
    g = np.abs([r["gap_pct"] for r in rows]); fl = np.array([r["frac_lp"] for r in rows])
    tr = np.array([r["time_ratio"] for r in rows])
    byT = {}
    for r in rows:
        byT.setdefault((r["nb"], r["T"]), []).append(r["frac_lp"])
    depth = {k: float(np.mean(v)) for k, v in sorted(byT.items())}
    nbs = sorted({k[0] for k in depth})
    grows = any(len(s) > 1 and s[-1][1] > s[0][1] + 1e-9 for s in
                [[(t, depth[(nb, t)]) for (nb2, t) in sorted(depth) if nb2 == nb] for nb in nbs])
    return dict(G1_exact=bool(g.max() <= 1e-6), max_abs_gap=float(g.max()),
                G2_frac_lp=bool(fl.max() <= 0.05), frac_lp_worst=float(fl.max()),
                frac_lp_mean=float(fl.mean()),
                G3_no_depth_growth=bool(not grows), depth_profile=depth,
                G4_time=bool(tr.mean() < 0.5), time_ratio_mean=float(tr.mean()))

# ---------- biến thể xuất phát ----------

def solve_lp(wA, wB, M):
    return float(ot.emd2(wA, wB, M)), True

def solve_comono(wA, wB, M):
    return comono_cost(wA, wB, M), False

def solve_monge_hybrid(wA, wB, M, tol=1e-12):           # champion vào chu kỳ 1
    v, _ = monge_viol(M)
    if v <= tol:
        return comono_cost(wA, wB, M), False
    return float(ot.emd2(wA, wB, M)), True

REGISTRY = {"all_lp": solve_lp, "comono": solve_comono, "monge_hybrid": solve_monge_hybrid}


def run_cycle(cycle, variants, grid, seeds, research_notes, out="handoff"):
    assert research_notes and research_notes.strip(), "I3: chu kỳ phải có bước 'cần gì + tra nhanh'"
    allrows, report = [], {}
    for name, fn in variants.items():
        rows = score(name, fn, grid, seeds, cycle)
        allrows += rows; report[name] = verdict(rows)
    os.makedirs(out, exist_ok=True)
    with open(f"{out}/cycle{cycle}_rows.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(allrows[0].keys())); w.writeheader(); w.writerows(allrows)
    json.dump(dict(cycle=cycle, research_notes=research_notes, grid=grid,
                   seeds=list(seeds), report=report),
              open(f"{out}/cycle{cycle}_report.json", "w"), indent=1, ensure_ascii=False)
    return report
