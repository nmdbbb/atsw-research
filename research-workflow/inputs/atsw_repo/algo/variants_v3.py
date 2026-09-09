"""Biến thể chu kỳ 3 — hợp đồng mức TẦNG: solve_layer(WA, WB, M) -> V (n,m).
Khai thác: 462 cặp biên trong một tầng dùng CHUNG một ma trận chi phí M.
Sinh bằng claude-fable-5. v3_4 = "chuẩn bị một lần theo M" (champion chu kỳ 3):
đúng tuyệt đối (|gap| <= 2,5e-13%), 0,618x thời gian DP chính xác end-to-end trên seed mới.
v3_2 = dùng lại đồ thị đẳng thức (0,712x). Chưa đạt mục tiêu G4 (<0,5x)."""
import numpy as np
import ot


# ================= v3_4 =================
def solve_layer(WA, WB, M):
    """V[i,j] = OT(WA[i], WB[j]; M), chinh xac (<=1e-9 so voi ot.emd2).

    Y tuong: ke hoach comonotone (goc tay-bac) tinh duoc HOAN TOAN vector hoa cho ca 462 cap.
    Voi moi cap, dung the vi doi ngau lan truyen doc bac thang cua chinh no (cung vector hoa);
    neu the vi do kha thi doi ngau toan cuc (chi phu thuoc M) thi ke hoach NW la TOI UU
    (bo doi ngau bo sung nhau). Cac cap chua chung nhan duoc thu chung nhan bang kho doi ngau
    dung chung (kha thi doi ngau chi phu thuoc M nen tai su dung duoc cho moi cap), cuoi cung
    moi roi vao ot.emd tung cap — thuong chi con rat it cap."""
    WA = np.ascontiguousarray(WA, dtype=np.float64)
    WB = np.ascontiguousarray(WB, dtype=np.float64)
    M = np.ascontiguousarray(M, dtype=np.float64)
    n, S = WA.shape
    m, S2 = WB.shape
    P = n * m
    TOL = 2e-10  # sai so chung nhan <= 2*TOL = 4e-10 < 1e-9

    CA = np.cumsum(WA, axis=1); CA[:, -1] = 1.0
    CB = np.cumsum(WB, axis=1); CB[:, -1] = 1.0

    # ---- chi phi ke hoach NW cho MOI cap, khong vong lap Python ----
    TT = np.sort(np.concatenate([
        np.broadcast_to(CA[:, None, :], (n, m, S)),
        np.broadcast_to(CB[None, :, :], (n, m, S2))], axis=2), axis=2)
    D = np.diff(TT, axis=2, prepend=0.0)
    R = np.minimum((CA[:, None, :, None] < TT[:, :, None, :]).sum(axis=2), S - 1)
    C = np.minimum((CB[None, :, :, None] < TT[:, :, None, :]).sum(axis=2), S2 - 1)
    NW = np.einsum('abk,abk->ab', D, M[R, C]).reshape(-1)

    # ---- the vi (u,v) doc bac thang NW cua tung cap: vong lap S+S2-2 buoc,
    # ---- moi buoc vector hoa tren toan bo P cap ----
    ii = np.repeat(np.arange(n), m)
    jj = np.tile(np.arange(m), n)
    ca = CA[ii]; cb = CB[jj]
    u = np.zeros((P, S)); v = np.zeros((P, S2)); v[:, 0] = M[0, 0]
    r = np.zeros(P, dtype=np.intp); c = np.zeros(P, dtype=np.intp)
    ar = np.arange(P)
    for _ in range(S + S2 - 2):
        down = ca[ar, r] <= cb[ar, c]
        down |= (c == S2 - 1)
        down &= (r < S - 1)
        rn = (r + down).astype(np.intp)
        cn = (c + ~down).astype(np.intp)
        mv = M[rn, cn]
        g = ~down
        u[ar[down], rn[down]] = mv[down] - v[ar[down], cn[down]]
        v[ar[g], cn[g]] = mv[g] - u[ar[g], rn[g]]
        r, c = rn, cn

    # ---- kiem tra kha thi doi ngau toan cuc (chi phu thuoc M) ----
    viol = (u[:, :, None] + v[:, None, :] - M[None, :, :]).max(axis=(1, 2))
    feas = viol <= TOL
    V = NW.copy()  # NW la toi uu tai moi cap co the vi kha thi

    rem = np.where(~feas)[0]
    if rem.size and feas.any():
        # kho doi ngau dung chung: chan duoi <u,a>+<v,b> dung cho MOI cap
        Uc = u[feas]; Vc = v[feas]
        lb = (WA[ii[rem]] @ Uc.T + WB[jj[rem]] @ Vc.T).max(axis=1)
        rem = rem[lb < NW[rem] - TOL]

    # ---- du phong chinh xac: giai emd cho cap chua chung nhan, tai dung doi ngau moi ----
    rem = list(rem)
    pos = 0
    while pos < len(rem):
        q = rem[pos]; pos += 1
        _, log = ot.emd(WA[ii[q]], WB[jj[q]], M, log=True)
        V[q] = log['cost']
        if pos < len(rem):
            tail = np.asarray(rem[pos:])
            lb = WA[ii[tail]] @ log['u'] + WB[jj[tail]] @ log['v']
            rem = rem[:pos] + list(tail[lb < NW[tail] - TOL])

    return V.reshape(n, m)
v3_4_solve_layer = solve_layer

# ================= v3_2 =================
def _nw_costs(WA, WB, M):
    # Chi phí của phương án góc tây-bắc cho MỌI cặp, vector hóa hoàn toàn.
    # NW chỉ phụ thuộc các tổng tích lũy; hợp nhất hai dãy breakpoint đã sắp.
    n, S = WA.shape
    m, S2 = WB.shape
    CA = np.cumsum(WA, axis=1)
    CB = np.cumsum(WB, axis=1)
    CA[:, -1] = 1.0
    CB[:, -1] = 1.0
    K = S + S2
    T = np.empty((n, m, K), dtype=np.float64)
    T[:, :, :S] = CA[:, None, :]
    T[:, :, S:] = CB[None, :, :]
    order = np.argsort(T, axis=2, kind='stable')
    Ts = np.take_along_axis(T, order, axis=2)
    isB = order >= S
    cntA = np.cumsum(~isB, axis=2)
    cntB = np.cumsum(isB, axis=2)
    ri = np.empty((n, m, K), dtype=np.intp)
    ci = np.empty((n, m, K), dtype=np.intp)
    ri[:, :, 0] = 0
    ci[:, :, 0] = 0
    np.minimum(cntA[:, :, :-1], S - 1, out=ri[:, :, 1:], casting='unsafe')
    np.minimum(cntB[:, :, :-1], S2 - 1, out=ci[:, :, 1:], casting='unsafe')
    seg = np.empty((n, m, K), dtype=np.float64)
    seg[:, :, 0] = Ts[:, :, 0]
    seg[:, :, 1:] = Ts[:, :, 1:] - Ts[:, :, :-1]
    return np.einsum('abk,abk->ab', seg, M[ri, ci])


def solve_layer(WA, WB, M):
    """V[i,j] = min_{pi in U(WA[i],WB[j])} <M,pi>, chính xác (<=1e-9 so với ot.emd2).

    Nguyên lý: khả thi đối ngẫu chỉ phụ thuộc M. Mỗi nghiệm đối ngẫu (u,v) thu được
    từ MỘT lần giải cho chặn dưới hợp lệ <u,a>+<v,b> cho MỌI cặp (a,b).
    - Chặn trên: chi phí NW-corner (khả thi nguyên thủy), vector hóa cho cả 462 cặp.
    - Chặn dưới: max trên bể (pool) các nghiệm đối ngẫu đã gặp.
    - Nếu trên - dưới <= tol: NW là tối ưu (chứng chỉ đối ngẫu) -> nhận ngay.
    - Nếu không: giải chính xác cặp đó bằng ot.lp.emd, thêm đối ngẫu mới vào bể
      (cập nhật chặn dưới cho TẤT CẢ các cặp còn lại chỉ bằng một tích ngoài nhỏ).
    Vì các biên thay đổi trơn, vài nghiệm đối ngẫu chứng nhận gần hết tầng.
    """
    WA = np.ascontiguousarray(WA, dtype=np.float64)
    WB = np.ascontiguousarray(WB, dtype=np.float64)
    M = np.ascontiguousarray(M, dtype=np.float64)
    n = WA.shape[0]
    m = WB.shape[0]

    P = _nw_costs(WA, WB, M)          # chặn trên khả thi cho mọi cặp
    V = P.copy()
    low = np.full((n, m), -np.inf)    # chặn dưới đối ngẫu tốt nhất hiện có
    tol = 1e-10

    for i in range(n):
        a = WA[i]
        Pi = P[i]
        lowi = low[i]
        for j in range(m):
            if Pi[j] - lowi[j] <= tol:
                continue  # chứng chỉ đối ngẫu: NW tối ưu tại (i,j)
            G, log = ot.lp.emd(a, WB[j], M, log=True)
            V[i, j] = float(np.sum(G * M))
            u = np.asarray(log['u'], dtype=np.float64)
            v = np.asarray(log['v'], dtype=np.float64)
            # cập nhật chặn dưới cho toàn bộ tầng bằng đối ngẫu mới
            np.maximum(low, (WA @ u)[:, None] + (WB @ v)[None, :], out=low)

    return V
v3_2_solve_layer = solve_layer
