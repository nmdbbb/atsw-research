"""Biến thể chu kỳ 2 — sinh bằng model claude-fable-5 trong redesign_loop, gợi ý chiến lược #5 và #7.
Cả hai: đơn hình vận tải khởi động ấm từ đỉnh góc tây-bắc. Đúng tuyệt đối (sai lệch ≤3,4e-13% end-to-end),
0,66-0,67x thời gian ot.emd2 ở mọi nút khi δ=0,5; 0,378-0,445x trên ma trận 58x59.
KHÔNG phải "tránh LP" — chúng tự giải LP, nên used_lp=False chỉ nghĩa là không gọi POT."""
import numpy as np
import ot


# ================= v2_5 =================
def _nw_vertex(wA, wB, n, m):
    # North-West corner rule; always returns exactly n+m-1 basic cells
    # (zero-flow cells included on ties), so the basis graph is a spanning tree.
    nb = n + m - 1
    rows = [0] * nb
    cols = [0] * nb
    flow = [0.0] * nb
    a = wA.tolist()
    b = wB.tolist()
    i = 0
    j = 0
    for k in range(nb):
        rows[k] = i
        cols[k] = j
        ra = a[i]
        rb = b[j]
        if i == n - 1:
            flow[k] = rb
            a[i] = ra - rb
            j += 1
        elif j == m - 1:
            flow[k] = ra
            b[j] = rb - ra
            i += 1
        elif ra <= rb:
            flow[k] = ra
            b[j] = rb - ra
            i += 1
        else:
            flow[k] = rb
            a[i] = ra - rb
            j += 1
    return rows, cols, flow


def _simplex_from_nw(wA, wB, M, max_pivots):
    """Primal transportation simplex warm-started at the NW vertex.

    Iteration 0 is exactly the NW-staircase dual certificate (upper bound =
    vertex cost, lower bound = <u,wA>+<v,wB>); each pivot is one cheapest step
    that closes the primal-dual gap. Returns the exact optimum, or None if the
    pivot budget is exhausted (caller falls back to a full LP).
    """
    n, m = M.shape
    rows, cols, flow = _nw_vertex(wA, wB, n, m)
    nb = n + m - 1
    opt_tol = 1e-10  # gap bound: value - LB <= opt_tol * total mass (=1) << 1e-9
    u = np.empty(n)
    v = np.empty(m)
    nodes = n + m

    for _ in range(max_pivots):
        # adjacency of the basis tree (row nodes 0..n-1, col nodes n..n+m-1)
        adj = [[] for _ in range(nodes)]
        for k in range(nb):
            r = rows[k]
            c = n + cols[k]
            adj[r].append((c, k))
            adj[c].append((r, k))

        # dual potentials: u_i + v_j = M_ij on basic cells (complementary slackness)
        u[0] = 0.0
        seen = [False] * nodes
        seen[0] = True
        nseen = 1
        stack = [0]
        while stack:
            x = stack.pop()
            for y, k in adj[x]:
                if not seen[y]:
                    seen[y] = True
                    nseen += 1
                    if y >= n:
                        v[y - n] = M[rows[k], cols[k]] - u[rows[k]]
                    else:
                        u[y] = M[rows[k], cols[k]] - v[cols[k]]
                    stack.append(y)
        if nseen != nodes:
            return None  # numerically broken tree -> let LP handle it

        # reduced costs; nonnegative everywhere <=> UB and LB coincide -> optimal
        R = M - u[:, None]
        R -= v[None, :]
        kmin = int(np.argmin(R))
        if R.flat[kmin] >= -opt_tol:
            return float(np.dot(np.asarray(flow), M[rows, cols]))

        # entering cell = most negative reduced cost
        ei, ej = divmod(kmin, m)
        target = n + ej

        # unique tree path row ei -> col ej gives the pivot cycle
        par = {ei: None}
        stack = [ei]
        done = False
        while stack and not done:
            x = stack.pop()
            for y, k in adj[x]:
                if y not in par:
                    par[y] = (x, k)
                    if y == target:
                        done = True
                        break
                    stack.append(y)
        path = []
        x = target
        while x != ei:
            px, k = par[x]
            path.append(k)
            x = px
        path.reverse()

        # entering arc is '+'; along the path signs alternate -,+,-,...
        minus = path[0::2]
        plus = path[1::2]
        lk = minus[0]
        theta = flow[lk]
        for k in minus:
            if flow[k] < theta:
                theta = flow[k]
                lk = k
        if theta < 0.0:
            theta = 0.0
        for k in minus:
            flow[k] -= theta
        for k in plus:
            flow[k] += theta
        # leaving arc replaced by entering arc: basis stays a spanning tree
        rows[lk] = ei
        cols[lk] = ej
        flow[lk] = theta

    return None


def inner_solve(wA, wB, M):
    wA = np.ascontiguousarray(wA, dtype=np.float64)
    wB = np.ascontiguousarray(wB, dtype=np.float64)
    M = np.ascontiguousarray(M, dtype=np.float64)
    n, m = M.shape

    # trivial marginals: the plan is unique
    if n == 1:
        return float(np.dot(wB, M[0])), False
    if m == 1:
        return float(np.dot(wA, M[:, 0])), False

    # near-Monge => NW vertex is optimal or a handful of pivots away;
    # budget ~2(n+m) pivots, beyond that a cold LP is the cheaper exact route
    val = _simplex_from_nw(wA, wB, M, 2 * (n + m))
    if val is not None:
        return val, False

    return float(ot.emd2(wA, wB, M)), True
v2_5_inner_solve = inner_solve

# ================= v2_7 =================
def _nw_vertex(wA, wB, n, m):
    # Đỉnh góc tây-bắc: đúng n+m-1 ô cơ sở (kể cả ô suy biến flow=0),
    # tạo thành một ĐƯỜNG (cây khung dạng path) trên đồ thị hàng/cột.
    K = n + m - 1
    bi = np.empty(K, dtype=np.int64)
    bj = np.empty(K, dtype=np.int64)
    f = np.empty(K, dtype=np.float64)
    i = 0
    j = 0
    a = float(wA[0])
    b = float(wB[0])
    for k in range(K):
        bi[k] = i
        bj[k] = j
        if i == n - 1 and j == m - 1:
            f[k] = 0.5 * (a + b)
            break
        if j == m - 1 or (i < n - 1 and a <= b):
            f[k] = a
            b -= a
            i += 1
            a = float(wA[i])
        else:
            f[k] = b
            a -= b
            j += 1
            b = float(wB[j])
    np.maximum(f, 0.0, out=f)
    return bi.tolist(), bj.tolist(), f.tolist()


def _duals(n, m, EI, EJ, M):
    # Thế đối ngẫu trên cây cơ sở: u_i + v_j = M_ij tại ô cơ sở, u_0 = 0.
    u = np.zeros(n)
    v = np.zeros(m)
    adj = [[] for _ in range(n + m)]
    for e in range(len(EI)):
        adj[EI[e]].append(e)
        adj[n + EJ[e]].append(e)
    known = [False] * (n + m)
    known[0] = True
    stack = [0]
    while stack:
        x = stack.pop()
        for e in adj[x]:
            r = EI[e]
            c = EJ[e]
            cn = n + c
            if x == r:
                if not known[cn]:
                    v[c] = M[r, c] - u[r]
                    known[cn] = True
                    stack.append(cn)
            elif not known[r]:
                u[r] = M[r, c] - v[c]
                known[r] = True
                stack.append(r)
    return u, v


def _path_in_tree(n, m, EI, EJ, ei, ej):
    # Đường duy nhất trong cây cơ sở từ nút-hàng ei tới nút-cột n+ej.
    N = n + m
    adj = [[] for _ in range(N)]
    for e in range(len(EI)):
        r = EI[e]
        c = n + EJ[e]
        adj[r].append((c, e))
        adj[c].append((r, e))
    parent = [-1] * N
    pedge = [-1] * N
    parent[ei] = ei
    target = n + ej
    stack = [ei]
    while stack:
        x = stack.pop()
        if x == target:
            break
        for (y, e) in adj[x]:
            if parent[y] == -1:
                parent[y] = x
                pedge[y] = e
                stack.append(y)
    path = []
    x = target
    while x != ei:
        path.append(pedge[x])
        x = parent[x]
    return path  # cạnh đầu tiên kề nút-cột ej => dấu '-', sau đó xen kẽ


def inner_solve(wA, wB, M):
    wA = np.asarray(wA, dtype=np.float64)
    wB = np.asarray(wB, dtype=np.float64)
    M = np.ascontiguousarray(M, dtype=np.float64)
    n, m = M.shape
    if n == 1:
        return float(np.dot(wB, M[0])), False
    if m == 1:
        return float(np.dot(wA, M[:, 0])), False

    # 1) Đỉnh NW trong O(n+m) — với M gần-Monge, đỉnh này gần/bằng tối ưu.
    EI, EJ, EF = _nw_vertex(wA, wB, n, m)

    tol = 1e-11 * (1.0 + float(np.abs(M).max()))
    maxit = 30 * (n + m)

    # 2) Đơn hình vận tải khởi động ấm từ cơ sở NW:
    #    - reduced cost >= -tol khắp nơi  => chứng chỉ tối ưu (bao trùm test Monge cũ)
    #    - ngược lại: pivot dọc chu trình duy nhất; gần-Monge => rất ít pivot.
    for _ in range(maxit):
        u, v = _duals(n, m, EI, EJ, M)
        R = M - u[:, None] - v[None, :]
        kmin = int(R.argmin())
        ei = kmin // m
        ej = kmin - ei * m
        if R[ei, ej] >= -tol:
            EIa = np.asarray(EI, dtype=np.int64)
            EJa = np.asarray(EJ, dtype=np.int64)
            val = float(np.dot(np.asarray(EF), M[EIa, EJa]))
            return val, False

        path = _path_in_tree(n, m, EI, EJ, ei, ej)
        theta = np.inf
        leave = -1
        for t in range(0, len(path), 2):  # các cạnh dấu '-'
            fe = EF[path[t]]
            if fe < theta:
                theta = fe
                leave = path[t]
        for t in range(len(path)):
            if t & 1:
                EF[path[t]] += theta
            else:
                EF[path[t]] -= theta
        # thay cạnh rời bằng cạnh vào (giữ đúng n+m-1 ô cơ sở, vẫn là cây)
        EI[leave] = ei
        EJ[leave] = ej
        EF[leave] = theta

    # 3) Lưới an toàn (chống suy biến/xoay vòng cực hiếm): LP đầy đủ.
    val = float(ot.emd2(wA, wB, M))
    return val, True
v2_7_inner_solve = inner_solve
