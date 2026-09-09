"""A common finite k-window model and a small-instance LP reference.

Paths have shape (sample_count, T+1), including time zero. Quantization uses
floor((x-shift)/delta), and a state's output is its CURRENT cell center.
The objective sums costs at times 1 through T, with no time-zero cost.
Initial distributions are coupled by a root OT problem; no modal root is
selected. Exact DP means unregularized LP formulation solved numerically,
not exact arithmetic or an outward-rounded mathematical certificate.

This adapter preserves the archive. Dense transition tables and general LP
solves are intended for target-equivalence checks, not a SOTA implementation.
"""

from dataclasses import dataclass
import hashlib
import json

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import eye, kron, vstack


@dataclass(frozen=True)
class FiniteWindowModel:
    states: tuple[np.ndarray, ...]
    representatives: tuple[np.ndarray, ...]
    kernels: tuple[np.ndarray, ...]
    initial: np.ndarray
    k: int
    delta: float
    shift: float
    sample_count: int

    @property
    def horizon(self):
        return len(self.kernels)

    @property
    def model_hash(self):
        digest = hashlib.sha256()
        digest.update(json.dumps({
            'schema': 'finite-window-v1', 'k': self.k,
            'delta': self.delta, 'shift': self.shift,
            'horizon': self.horizon, 'sample_count': self.sample_count,
            'cost_times': '1..T', 'root': 'couple_initial_marginals'
        }, sort_keys=True).encode())
        for array in (*self.states, *self.representatives,
                      *self.kernels, self.initial):
            digest.update(str(array.shape).encode())
            digest.update(str(array.dtype).encode())
            digest.update(np.ascontiguousarray(array).tobytes())
        return digest.hexdigest()


def build_window_model(paths, k=1, delta=0.5, shift=0.0):
    """Estimate all T transitions and the time-zero empirical distribution.

    Each history key is the last min(k,t+1) cell indices. The returned model
    is the specified finite-memory approximation; no claim of equality to
    the original full-history or population process is made.
    """
    paths = np.asarray(paths, dtype=np.float64)
    if paths.ndim != 2 or not paths.shape[0] or not paths.shape[1]:
        raise ValueError('paths must be a nonempty (samples, T+1) scalar array')
    if not np.isfinite(paths).all():
        raise ValueError('paths must be finite')
    if isinstance(k, (bool, np.bool_)) or not isinstance(k, (int, np.integer)) or k < 1:
        raise ValueError('k must be a positive integer')
    if not np.isfinite(delta) or delta <= 0 or not np.isfinite(shift):
        raise ValueError('delta must be positive finite and shift must be finite')
    scaled = np.floor((paths - shift) / delta)
    # Float64 cannot represent int64's largest integer exactly; use a strict
    # upper threshold so a rounded 2**63 never casts to a negative cell code.
    if (not np.isfinite(scaled).all() or (scaled < -(2.0 ** 63)).any()
            or (scaled >= 2.0 ** 63).any()):
        raise ValueError('quantized cell indices exceed int64 range')
    cells = scaled.astype(np.int64)
    sample_count, time_count = paths.shape
    states, representatives, inverse = [], [], []
    for t in range(time_count):
        histories = cells[:, max(0, t - k + 1):t + 1]
        unique, codes = np.unique(histories, axis=0, return_inverse=True)
        states.append(np.ascontiguousarray(unique))
        representatives.append(np.ascontiguousarray(
            (unique[:, -1].astype(float) + 0.5) * delta + shift))
        inverse.append(codes)
    initial = np.bincount(inverse[0], minlength=len(states[0])).astype(float)
    initial /= sample_count
    kernels = []
    for t in range(time_count - 1):
        counts = np.zeros((len(states[t]), len(states[t + 1])))
        np.add.at(counts, (inverse[t], inverse[t + 1]), 1.0)
        totals = counts.sum(axis=1, keepdims=True)
        # Every listed current state is observed in at least one full path.
        # No arbitrary fallback transition distribution is necessary.
        if (totals <= 0).any():
            raise ValueError('an observed state unexpectedly has no outgoing sample')
        kernels.append(np.ascontiguousarray(counts / totals))
    return FiniteWindowModel(tuple(states), tuple(representatives),
                             tuple(kernels), np.ascontiguousarray(initial),
                             int(k), float(delta), float(shift), sample_count)


def stage_cost(left, right, kind='squared'):
    """Return a current-scalar cost matrix, never a history-vector distance."""
    difference = np.asarray(left)[:, None] - np.asarray(right)[None, :]
    if kind == 'squared':
        return difference ** 2
    if kind == 'absolute':
        return np.abs(difference)
    raise ValueError("cost must be 'squared' or 'absolute'")


def _transport_value(a, b, matrix):
    """Solve a finite unregularized transport LP with basic residual checks."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if (not np.isfinite(a).all() or not np.isfinite(b).all()
            or (a < 0).any() or (b < 0).any()
            or abs(a.sum() - 1) > 1e-10 or abs(b.sum() - 1) > 1e-10):
        raise ValueError('transport marginals must be normalized probabilities')
    if matrix.shape != (len(a), len(b)) or not np.isfinite(matrix).all():
        raise ValueError('invalid transport cost matrix')
    positive_a, positive_b = a > 0, b > 0
    cost = matrix[np.ix_(positive_a, positive_b)]
    pa, pb = a[positive_a].copy(), b[positive_b].copy()
    # Normalization corrects summation roundoff, not missing probability mass.
    pa /= pa.sum()
    pb /= pb.sum()
    n, m = cost.shape
    if n == 1 or m == 1:
        return float(pa @ cost @ pb)
    constraints = vstack((kron(eye(n), np.ones((1, m))),
                          kron(np.ones((1, n)), eye(m))), format='csr')
    marginals = np.concatenate((pa, pb))
    result = linprog(cost.ravel(), A_eq=constraints, b_eq=marginals,
                     bounds=(0, None), method='highs')
    if not result.success:
        raise RuntimeError(f'transport LP failed: {result.message}')
    if (np.max(np.abs(constraints @ result.x - marginals)) > 1e-8
            or result.x.min() < -1e-8):
        raise RuntimeError('transport LP returned excessive primal residual')
    return float(result.fun)


def exact_dp(left, right, cost='squared'):
    """Numerical reference for the finite models, including the root OT.

    V_T=0; each step solves OT(K_A[t][i],K_B[t][j],c_{t+1}+V_{t+1}).
    Finally solve OT(initial_A,initial_B,V_0), since time zero is uncharged.
    Both input laws use their own histories and may have different k values.
    """
    if left.horizon != right.horizon:
        raise ValueError('models must have the same horizon')
    if cost not in ('squared', 'absolute'):
        raise ValueError("cost must be 'squared' or 'absolute'")
    value = np.zeros((len(left.states[-1]), len(right.states[-1])))
    for t in range(left.horizon - 1, -1, -1):
        matrix = stage_cost(left.representatives[t + 1],
                            right.representatives[t + 1], cost) + value
        value = np.empty((len(left.states[t]), len(right.states[t])))
        for i, a in enumerate(left.kernels[t]):
            for j, b in enumerate(right.kernels[t]):
                value[i, j] = _transport_value(a, b, matrix)
    return _transport_value(left.initial, right.initial, value)
