"""Hai họ quá trình đã ĐÓNG BĂNG cho lưới thí nghiệm. Luật sinh khai TRƯỚC khi đo.

objective.json đòi họ thứ hai phải có (i) chuyển tiếp có điều kiện KHÔNG đơn điệu và (ii) phụ thuộc
thật vượt quá trạng thái hiện tại; và ghi rõ "một phép gán nhãn phi tuyến yếu của AR(1) là không đủ".

HỌ 1 — ar1 (đối chứng, đã dùng trong archive):
    X_0 = 0,  X_{t+1} = a*X_t + sigma*eps_t,   a = 0.7,  sigma = 1.0,  eps ~ N(0,1) iid.

HỌ 2 — second_order_nonmonotone (khai trước, KHÔNG phải AR(1) gán nhãn lại):
    X_0 = 0,  X_1 = sigma*eps_0,
    X_{t+1} = b*X_t + c*sin(w*X_t) + d*(X_t - X_{t-1}) + sigma*eps_t,
    b = 0.55,  c = 0.95,  w = 1.7,  d = -0.45,  sigma = 0.7.
  Hai tính chất được nhắm tới, và PHẢI kiểm bằng số chứ không mặc định:
   (i) không đơn điệu: d/dx [b*x + c*sin(w*x)] = b + c*w*cos(w*x) = 0.55 + 1.615*cos(1.7x), âm khi
       cos(1.7x) < -0.3406 -> tồn tại khoảng x mà kỳ vọng có điều kiện GIẢM theo x.
   (ii) phụ thuộc bậc hai thật: hệ số d != 0 nên E[X_{t+1} | X_t, X_{t-1}] đổi theo X_{t-1} ngay khi
       X_t giữ nguyên. Kiểm bằng cách so trung bình trong cùng một bin hẹp của X_t, tách theo
       tam phân vị của X_{t-1}.
  Không tuyên bố dừng theo lý thuyết; tính dừng thực nghiệm được đo (độ lệch chuẩn theo t ở nửa sau).
"""
from __future__ import annotations
import numpy as np

AR1 = dict(a=0.7, sigma=1.0)
SON = dict(b=0.55, c=0.95, w=1.7, d=-0.45, sigma=0.7)


def ar1(T, n, rng, a=AR1["a"], sigma=AR1["sigma"]):
    X = np.zeros((n, T + 1))
    for t in range(1, T + 1):
        X[:, t] = a * X[:, t - 1] + sigma * rng.standard_normal(n)
    return X


def second_order_nonmonotone(T, n, rng, **kw):
    p = {**SON, **kw}
    X = np.zeros((n, T + 1))
    X[:, 1] = p["sigma"] * rng.standard_normal(n)
    for t in range(1, T):
        X[:, t + 1] = (p["b"] * X[:, t] + p["c"] * np.sin(p["w"] * X[:, t])
                       + p["d"] * (X[:, t] - X[:, t - 1]) + p["sigma"] * rng.standard_normal(n))
    return X


FAMILIES = {"ar1": ar1, "second_order_nonmonotone": second_order_nonmonotone}


# ---------- kiểm chứng hai tính chất (chạy trên chuỗi, không trên mô hình lượng tử hoá) ----------

def conditional_mean_curve(X, bins=14, lo=0.05, hi=0.95, burn=10):
    """E[X_{t+1} | X_t] theo bin của X_t, gộp mọi t >= burn. Trả (tâm bin, trung bình, số điểm)."""
    cur = X[:, burn:-1].ravel(); nxt = X[:, burn + 1:].ravel()
    edges = np.quantile(cur, np.linspace(lo, hi, bins + 1))
    idx = np.clip(np.searchsorted(edges, cur, side="right") - 1, 0, bins - 1)
    keep = (cur >= edges[0]) & (cur <= edges[-1])
    centres = 0.5 * (edges[:-1] + edges[1:])
    means = np.array([nxt[keep & (idx == b)].mean() for b in range(bins)])
    counts = np.array([int((keep & (idx == b)).sum()) for b in range(bins)])
    return centres, means, counts


def monotonicity_violations(centres, means):
    """Số lần kỳ vọng có điều kiện GIẢM khi x tăng, và độ giảm lớn nhất."""
    dif = np.diff(means)
    return int((dif < 0).sum()), float(dif.min()), float(np.abs(dif).max())


def lag2_effect(X, x_bins=6, burn=10):
    """Trong cùng bin hẹp của X_t, so E[X_{t+1}] giữa tam phân vị THẤP và CAO của X_{t-1}."""
    prev = X[:, burn - 1:-2].ravel(); cur = X[:, burn:-1].ravel(); nxt = X[:, burn + 1:].ravel()
    edges = np.quantile(cur, np.linspace(0.1, 0.9, x_bins + 1))
    out = []
    for b in range(x_bins):
        m = (cur >= edges[b]) & (cur < edges[b + 1])
        if m.sum() < 400:
            continue
        p = prev[m]; y = nxt[m]
        q1, q2 = np.quantile(p, [1 / 3, 2 / 3])
        lowm, highm = y[p <= q1], y[p >= q2]
        if len(lowm) < 100 or len(highm) < 100:
            continue
        d = float(highm.mean() - lowm.mean())
        se = float(np.sqrt(highm.var(ddof=1) / len(highm) + lowm.var(ddof=1) / len(lowm)))
        out.append(dict(x_centre=float(0.5 * (edges[b] + edges[b + 1])), diff=d, se=se,
                        z=(d / se if se > 0 else float("nan")),
                        n_low=int(len(lowm)), n_high=int(len(highm))))
    return out


def stationarity(X, burn=10):
    sd = X[:, burn:].std(axis=0)
    return dict(sd_first=float(sd[0]), sd_last=float(sd[-1]),
                sd_ratio=float(sd[-1] / sd[0]), sd_max=float(sd.max()))
