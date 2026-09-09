"""V1 — chứng chỉ đối ngẫu: cần và đủ, thay cho điều kiện Monge (chỉ đủ).

Ghép comonotone = quy tắc góc tây-bắc trên giá đã sắp; support là một bậc thang.
Dựng thế (u,v) bằng bù trừ trên bậc thang (u_i+v_j = M_ij tại ô có khối lượng), rồi kiểm
khả thi đối ngẫu u_i+v_j <= M_ij ở MỌI ô. Đạt => ghép comonotone tối ưu chính xác (dừng, O(nm));
không đạt => gọi LP. Monge => chứng chỉ này luôn đạt, nên frac_lp chỉ có thể giảm.
"""
import numpy as np, ot

def _nw_staircase(a, b, tol=1e-14):
    """Trả danh sách ô cơ sở (i,j) theo bậc thang, giữ liên thông cả khi suy biến."""
    a = a.copy(); b = b.copy(); n, m = len(a), len(b)
    i = j = 0; cells = [(0, 0)]
    while True:
        s = min(a[i], b[j]); a[i] -= s; b[j] -= s
        ai0, bj0 = a[i] <= tol, b[j] <= tol
        if ai0 and bj0:
            if i + 1 < n:  i += 1                  # suy biến: đi hàng trước, ô khối lượng 0 giữ liên thông
            elif j + 1 < m: j += 1
            else: break
        elif ai0:
            if i + 1 < n: i += 1
            else: break
        else:
            if j + 1 < m: j += 1
            else: break
        cells.append((i, j))
    return cells

def dual_potentials(a, b, M):
    n, m = M.shape
    u = np.full(n, np.nan); v = np.full(m, np.nan)
    u[0] = 0.0
    for (i, j) in _nw_staircase(a, b):
        if not np.isnan(u[i]) and np.isnan(v[j]):   v[j] = M[i, j] - u[i]
        elif np.isnan(u[i]) and not np.isnan(v[j]): u[i] = M[i, j] - v[j]
        elif np.isnan(u[i]) and np.isnan(v[j]):     return None, None
    if np.isnan(u).any() or np.isnan(v).any():
        return None, None
    return u, v

def solve_dual_cert(wA, wB, M, tol=1e-9):
    u, v = dual_potentials(wA, wB, M)
    if u is not None and (u[:, None] + v[None, :] - M).max() <= tol:
        # bù trừ đúng theo dựng => giá trị ghép comonotone = <u,a>+<v,b> = tối ưu LP
        return float(u @ wA + v @ wB), False
    return float(ot.emd2(wA, wB, M)), True
