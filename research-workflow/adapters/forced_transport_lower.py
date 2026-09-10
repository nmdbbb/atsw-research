"""Numerical baseline for singleton-sided local transports, not novel OT."""
from __future__ import annotations
import numpy as np


def forced_values(matrix, left_kernel, right_kernel):
    """Return mask/values for uniquely determined couplings and narrow work counts.

    Exact-arithmetic identity: if either marginal is Dirac, OT(M)=a.T M b.
    Positive masses are never classified using a tolerance. The returned float64
    values include a conservative heuristic guard, NOT outward certification.
    """
    M, A, B = (np.asarray(x, dtype=float) for x in (matrix, left_kernel, right_kernel))
    if M.ndim != 2 or A.ndim != 2 or B.ndim != 2 or A.shape[1] != M.shape[0] or B.shape[1] != M.shape[1]:
        raise ValueError("matrix/kernel shape mismatch")
    if any(not x.size or not np.isfinite(x).all() or (x < 0).any() for x in (M,A,B)):
        raise ValueError("require finite nonempty nonnegative inputs")
    if (A.sum(1) <= 0).any() or (B.sum(1) <= 0).any():
        raise ValueError("empty marginal")
    A = A / A.sum(1, keepdims=True)
    B = B / B.sum(1, keepdims=True)
    sa = [np.flatnonzero(a > 0) for a in A]
    sb = [np.flatnonzero(b > 0) for b in B]
    da = np.array([len(x) == 1 for x in sa])
    db = np.array([len(x) == 1 for x in sb])
    mask = da[:,None] | db[None,:]
    values = np.zeros(mask.shape)
    entries = 0
    for i,j in np.argwhere(mask):
        if da[i]:
            cols = sb[j]
            value = float(M[sa[i][0],cols] @ B[j,cols])
            width = len(cols)
        else:
            rows = sa[i]
            value = float(A[i,rows] @ M[rows,sb[j][0]])
            width = len(rows)
        guard = 32*np.finfo(float).eps*(width+1)*max(1.,abs(value))
        values[i,j] = max(0.,value-guard)
        entries += width
    return mask, values, dict(forced_pairs=int(mask.sum()), parent_pairs=int(mask.size),
        cost_entries_read=entries, marginal_entries_scanned=int(A.size+B.size),
        mask_entries=int(mask.size), values_allocated=int(values.size))
