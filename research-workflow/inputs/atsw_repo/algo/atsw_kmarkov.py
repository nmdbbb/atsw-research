"""ATSW dạng k-Markov: điều kiện hóa theo CỬA SỔ k bước cuối thay vì toàn bộ lịch sử.

Động cơ (từ thí nghiệm 09/2026): với lịch sử đầy đủ, số nút ở tầng sâu tăng theo hàm mũ của T
nên mỗi nút chỉ còn 1-2 đường -> phân phối có điều kiện thành khối lượng điểm -> chệch lên rất
mạnh. Cửa sổ k bước chặn số nút bởi (số ô)^k, độc lập với T, mà KHÔNG làm thô giá trị ô
(nên chi phí không bị sai như khi tăng delta).

Cấu trúc vẫn là nested DP vị nhân quả hai chiều; điểm khác với Eckstein-Pammer là ở mỗi cặp nút
ta dùng GHÉP QUANTILE O(b log b) thay cho LP O(b^3) / Sinkhorn.
"""
import numpy as np


def quantile_codes(P1, P2, m):
    """Ô thích nghi theo phân vị của mẫu gộp, mỗi tầng m ô; đại diện = trung bình ô.
    Trả (C1, C2, reps) với C[:, t] là mã ô tại thời điểm t (t = 0..T, t=0 là gốc)."""
    T = P1.shape[1] - 1
    C1 = np.zeros((len(P1), T + 1), np.int64)
    C2 = np.zeros((len(P2), T + 1), np.int64)
    reps = [np.array([0.5 * (P1[0, 0] + P2[0, 0])])]  # tầng 0: một ô (gốc)
    reps[0] = np.array([P1[0, 0]])                     # giá trị gốc của A (dùng cho chi phí t=0, không tính)
    reps0_b = np.array([P2[0, 0]])
    repsB = [reps0_b]
    for t in range(1, T + 1):
        pool = np.concatenate([P1[:, t], P2[:, t]])
        edges = np.quantile(pool, np.linspace(0, 1, m + 1)[1:-1]) if m > 1 else np.array([])
        c1 = np.searchsorted(edges, P1[:, t], side="right")
        c2 = np.searchsorted(edges, P2[:, t], side="right")
        cp = np.searchsorted(edges, pool, side="right")
        rep = np.array([pool[cp == k].mean() if (cp == k).any() else np.nan for k in range(m)])
        # ô rỗng: lấy trung điểm biên gần nhất để không sinh NaN
        if np.isnan(rep).any():
            good = ~np.isnan(rep)
            rep[~good] = np.interp(np.flatnonzero(~good), np.flatnonzero(good), rep[good])
        C1[:, t] = c1; C2[:, t] = c2
        reps.append(rep); repsB.append(rep)
    return C1, C2, reps


def window_states(C, t, k):
    """Mã trạng thái cửa sổ: tuple mã ô của k bước cuối tính đến t (rút gọn về id liên tục)."""
    lo = max(0, t - k + 1)
    W = C[:, lo:t + 1]
    _, inv = np.unique(W, axis=0, return_inverse=True)
    return inv


def _quantile_cost(pa, pb, M, tol=1e-14):
    """Chi phí của ghép comonotone (quantile) giữa hai phân phối rời rạc đã sắp theo giá trị.
    pa, pb: khối lượng (đã chuẩn hóa); M[i, j]: chi phí. O(len(pa)+len(pb))."""
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


def atsw_kmarkov(P1, w1, P2, w2, m, k=1, gcost=lambda dx: dx ** 2):
    """Trả (giá trị, số cặp trạng thái đã thăm). Chi phí = sum_{t=1..T} gcost(x_t - y_t)."""
    T = P1.shape[1] - 1
    C1, C2, reps = quantile_codes(P1, P2, m)
    w1 = np.asarray(w1, float) / np.sum(w1); w2 = np.asarray(w2, float) / np.sum(w2)

    # trạng thái cửa sổ tại mỗi thời điểm + giá trị "vị trí hiện tại" của trạng thái đó
    SA = [window_states(C1, t, k) for t in range(T + 1)]
    SB = [window_states(C2, t, k) for t in range(T + 1)]
    nA = [int(s.max()) + 1 for s in SA]; nB = [int(s.max()) + 1 for s in SB]
    # mã ô hiện tại của từng trạng thái (để lấy giá trị đại diện và để sắp thứ tự)
    curA = [np.zeros(nA[t], np.int64) for t in range(T + 1)]
    curB = [np.zeros(nB[t], np.int64) for t in range(T + 1)]
    for t in range(T + 1):
        curA[t][SA[t]] = C1[:, t]; curB[t][SB[t]] = C2[:, t]

    # kernel chuyển: từ trạng thái tại t sang trạng thái tại t+1, ước lượng bằng khối lượng mẫu
    def kernel(S, w, t, nfrom, nto):
        M = np.zeros((nfrom, nto))
        np.add.at(M, (S[t], S[t + 1]), w)
        row = M.sum(1, keepdims=True)
        return M / np.maximum(row, 1e-300), row.ravel()

    KA = [kernel(SA, w1, t, nA[t], nA[t + 1]) for t in range(T)]
    KB = [kernel(SB, w2, t, nB[t], nB[t + 1]) for t in range(T)]

    V = np.zeros((nA[T], nB[T]))
    pairs = 0
    for t in range(T - 1, -1, -1):
        Vn = np.zeros((nA[t], nB[t]))
        ka, _ = KA[t]; kb, _ = KB[t]
        # chi phí tại t+1 giữa các trạng thái đích, theo giá trị đại diện của ô hiện tại
        va = reps[t + 1][curA[t + 1]]; vb = reps[t + 1][curB[t + 1]]
        Cm = gcost(va[:, None] - vb[None, :]) + V
        oa = np.argsort(va); ob = np.argsort(vb)          # sắp theo giá trị -> ghép comonotone
        Cs = Cm[np.ix_(oa, ob)]
        for i in range(nA[t]):
            pa_full = ka[i][oa]
            nzA = pa_full > 1e-14
            if not nzA.any():
                continue
            pa = pa_full[nzA] / pa_full[nzA].sum()
            Csub = Cs[nzA, :]
            for j in range(nB[t]):
                pb_full = kb[j][ob]
                nzB = pb_full > 1e-14
                if not nzB.any():
                    continue
                pb = pb_full[nzB] / pb_full[nzB].sum()
                Vn[i, j] = _quantile_cost(pa, pb, Csub[:, nzB])
                pairs += 1
        V = Vn
    return float(V[0, 0]), pairs
