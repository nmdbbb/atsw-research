"""k-Markov ATSW với LƯỚI CỐ ĐỊNH (không ước lượng ô từ dữ liệu).

Động cơ: chứng minh nhất quán giả thiết phân hoạch cố định, trong khi `quantile_codes`
của atsw_kmarkov.py dựng ô từ phân vị mẫu gộp — biên ô ngẫu nhiên. Bản này đóng khoảng
cách đó: ô = ⌊(x−s)/δ⌋, đại diện = tâm ô, cả hai đều tất định khi (δ, s) cho trước.
Trung bình trên s ~ U[0,δ) giữ nguyên phần "sliced".
"""
import numpy as np
from atsw_kmarkov import window_states, _quantile_cost


def fixed_codes(P1, P2, delta, s):
    """Lưới đều: ô = floor((x-s)/delta), đại diện = tâm ô. Trả (C1, C2, reps).

    Không gian ô mỗi tầng là hợp các ô quan sát được ở CẢ HAI chuỗi, đánh số liên tục;
    ánh xạ id -> tâm ô là tất định (không phụ thuộc dữ liệu ngoài việc chọn ô nào xuất hiện).
    """
    T = P1.shape[1] - 1
    C1 = np.zeros((len(P1), T + 1), np.int64)
    C2 = np.zeros((len(P2), T + 1), np.int64)
    reps = [np.array([P1[0, 0]])]
    for t in range(1, T + 1):
        k1 = np.floor((P1[:, t] - s) / delta).astype(np.int64)
        k2 = np.floor((P2[:, t] - s) / delta).astype(np.int64)
        keys = np.unique(np.concatenate([k1, k2]))
        idx = {int(k): i for i, k in enumerate(keys)}
        C1[:, t] = [idx[int(v)] for v in k1]
        C2[:, t] = [idx[int(v)] for v in k2]
        reps.append((keys + 0.5) * delta + s)
    return C1, C2, reps


def atsw_km_codes(C1, C2, reps, w1, w2, k=1, gcost=lambda dx: dx ** 2):
    """DP k-Markov trên mã ô cho trước. Trả (giá trị, số cặp trạng thái đã thăm)."""
    T = C1.shape[1] - 1
    w1 = np.asarray(w1, float) / np.sum(w1)
    w2 = np.asarray(w2, float) / np.sum(w2)
    SA = [window_states(C1, t, k) for t in range(T + 1)]
    SB = [window_states(C2, t, k) for t in range(T + 1)]
    nA = [int(x.max()) + 1 for x in SA]
    nB = [int(x.max()) + 1 for x in SB]
    curA = [np.zeros(nA[t], np.int64) for t in range(T + 1)]
    curB = [np.zeros(nB[t], np.int64) for t in range(T + 1)]
    for t in range(T + 1):
        curA[t][SA[t]] = C1[:, t]
        curB[t][SB[t]] = C2[:, t]

    def kern(S, w, t, nfrom, nto):
        M = np.zeros((nfrom, nto))
        np.add.at(M, (S[t], S[t + 1]), w)
        row = M.sum(1, keepdims=True)
        return M / np.maximum(row, 1e-300)

    KA = [kern(SA, w1, t, nA[t], nA[t + 1]) for t in range(T)]
    KB = [kern(SB, w2, t, nB[t], nB[t + 1]) for t in range(T)]
    V = np.zeros((nA[T], nB[T]))
    pairs = 0
    for t in range(T - 1, -1, -1):
        Vn = np.zeros((nA[t], nB[t]))
        va = reps[t + 1][curA[t + 1]]
        vb = reps[t + 1][curB[t + 1]]
        Cm = gcost(va[:, None] - vb[None, :]) + V
        oa = np.argsort(va)
        ob = np.argsort(vb)
        Cs = Cm[np.ix_(oa, ob)]
        for i in range(nA[t]):
            pa_full = KA[t][i][oa]
            nzA = pa_full > 1e-14
            if not nzA.any():
                continue
            pa = pa_full[nzA] / pa_full[nzA].sum()
            Csub = Cs[nzA, :]
            for j in range(nB[t]):
                pb_full = KB[t][j][ob]
                nzB = pb_full > 1e-14
                if not nzB.any():
                    continue
                pb = pb_full[nzB] / pb_full[nzB].sum()
                Vn[i, j] = _quantile_cost(pa, pb, Csub[:, nzB])
                pairs += 1
        V = Vn
    return float(V[0, 0]), pairs


def atsw_fixed(P1, w1, P2, w2, delta, shifts, k=1, gcost=lambda dx: dx ** 2):
    """Trung bình trên các dịch lưới s. shifts: iterable giá trị s trong [0, delta)."""
    vals, tot = [], 0
    for s in shifts:
        C1, C2, reps = fixed_codes(P1, P2, delta, float(s))
        v, pr = atsw_km_codes(C1, C2, reps, w1, w2, k=k, gcost=gcost)
        vals.append(v)
        tot += pr
    return float(np.mean(vals)), tot
