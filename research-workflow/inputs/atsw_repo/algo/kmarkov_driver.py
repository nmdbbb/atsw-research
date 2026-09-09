"""Driver T CAO: DP trên không gian trạng thái k-Markov, không phải cây n_b^T.

Lý do đổi họ instance: cây ngẫu nhiên có n_b^T nút nên T>8 là bất khả thi. Estimator thật của
bài chặn số trạng thái mỗi tầng bởi (số ô)^k, độc lập T -> DP tuyến tính theo T, T=50 chạy được.
Quá trình: AR(1) dừng (a=0.7) để giá đỡ ổn định theo t; lưới cố định (khớp atsw_fixedgrid);
k=1. Mã ô tăng theo giá trị nên hàng/cột đã ở thứ tự giá trị, comonotone dùng trực tiếp.
"""
import os, sys
if os.getcwd() not in sys.path: sys.path.append(os.getcwd())
import numpy as np, ot, time
from monge_gap_experiment import comono_cost, monge_viol
from variants_v1 import solve_dual_cert

def gen_paths(T, n, rng, a=0.7, sigma=1.0):
    X = np.zeros((n, T + 1))
    for t in range(1, T + 1):
        X[:, t] = a * X[:, t - 1] + sigma * rng.standard_normal(n)
    return X

def build(X, delta, shift, unif_tol=0):
    """Trả (states, reps, kernels): states[t] mã ô duy nhất đã sắp; kernels[t][i,j]=P(j|i)."""
    C = np.floor((X - shift) / delta).astype(np.int64)
    T = C.shape[1] - 1
    states, inv = [], []
    for t in range(T + 1):
        s, iv = np.unique(C[:, t], return_inverse=True)
        states.append(s); inv.append(iv)
    reps = [(s + 0.5) * delta + shift for s in states]
    K = []
    for t in range(T):
        Kt = np.zeros((len(states[t]), len(states[t + 1])))
        np.add.at(Kt, (inv[t], inv[t + 1]), 1.0)
        row = Kt.sum(1, keepdims=True)
        Kt = np.where(row > 0, Kt / np.maximum(row, 1e-300), 1.0 / Kt.shape[1])
        K.append(np.ascontiguousarray(Kt))
    return states, reps, K

def dp(repsA, KA, repsB, KB, inner_solve, gcost=lambda d: d ** 2):
    T = len(KA)
    V = np.zeros((len(repsA[T]), len(repsB[T])))
    npairs = nlp = 0
    for t in range(T - 1, -1, -1):
        M = gcost(repsA[t + 1][:, None] - repsB[t + 1][None, :]) + V
        M = np.ascontiguousarray(M)
        Vn = np.empty((KA[t].shape[0], KB[t].shape[0]))
        for i in range(KA[t].shape[0]):
            wa = np.ascontiguousarray(KA[t][i])
            for j in range(KB[t].shape[0]):
                val, used = inner_solve(wa, np.ascontiguousarray(KB[t][j]), M)
                Vn[i, j] = val; npairs += 1; nlp += bool(used)
        V = Vn
    return float(V[0, 0]), npairs, nlp

def solve_lp(wA, wB, M):      return float(ot.emd2(wA, wB, M)), True
def solve_comono(wA, wB, M):  return comono_cost(wA, wB, M), False
def solve_monge(wA, wB, M, tol=1e-12):
    v, _ = monge_viol(M)
    return (comono_cost(wA, wB, M), False) if v <= tol else (float(ot.emd2(wA, wB, M)), True)

VARIANTS = {"all_lp": solve_lp, "comono": solve_comono,
            "monge_hybrid": solve_monge, "dual_cert": solve_dual_cert}

def sweep(Ts, seeds, n_paths=4000, delta=0.5, cycle=1, out="handoff/kmarkov_sweep.csv"):
    import csv
    rows = []
    for T in Ts:
        for sd in seeds:
            rng = np.random.default_rng(10_000_000 * cycle + 100 * T + sd)
            XA = gen_paths(T, n_paths, rng, a=0.7)
            XB = gen_paths(T, n_paths, rng, a=0.55, sigma=1.15)
            sA, rA, KA = build(XA, delta, 0.25)
            sB, rB, KB = build(XB, delta, 0.25)
            ref = None; rec = dict(T=T, seed=sd, n_states_A=len(sA[T]), n_states_B=len(sB[T]))
            for name, fn in VARIANTS.items():
                t0 = time.perf_counter()
                val, npairs, nlp = dp(rA, KA, rB, KB, fn)
                dt = time.perf_counter() - t0
                if name == "all_lp": ref = val; rec["n_nodepairs"] = npairs
                rec[f"{name}_val"] = val; rec[f"t_{name}"] = dt
                rec[f"gap_{name}"] = 100.0 * (val - ref) / ref
                rec[f"fraclp_{name}"] = nlp / npairs
            rows.append(rec)
    os.makedirs("handoff", exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    return rows
