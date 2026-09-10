"""Support-sized implementation of the existing two-orientation NW policy.

This is an engineering baseline, not a new transport policy or a certified
enclosure. It retains the original global matrix SVD orders. Support extraction
and rank sorting occur once per marginal, outside the parent-pair loop. Float
normalization and residual subtraction can change epsilon-level flows or break
nearly tied orientation objectives differently from the dense cumulative code.
No positive mass is removed using a tolerance.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from policy_pool_candidate import _orders


@dataclass(frozen=True)
class SparsePolicyResult:
    value: float
    rows: np.ndarray
    cols: np.ndarray
    masses: np.ndarray
    counts: dict


def _ordered_supports(marginals, size, order):
    rank = np.empty(size, dtype=np.intp)
    rank[order] = np.arange(size)
    supports = []
    scanned = positive = 0
    for weights in marginals:
        weights = np.asarray(weights, dtype=float)
        if (weights.shape != (size,) or not np.isfinite(weights).all()
                or (weights < 0).any()):
            raise ValueError("marginals must be finite nonnegative vectors of matching size")
        indices = np.flatnonzero(weights > 0)
        if not len(indices):
            raise ValueError("marginals must have positive total mass")
        indices = indices[np.argsort(rank[indices], kind="stable")]
        # Scale first so finite inputs whose naive sum overflows remain valid.
        mass = weights[indices] / float(weights[indices].max())
        mass /= math.fsum(mass)
        if (mass == 0).any():
            raise ValueError("normalization underflowed a positive mass")
        supports.append((indices, mass))
        scanned += size
        positive += len(indices)
    return supports, scanned, positive


def _nw_sparse(left, right, reverse=False):
    rows, aa = left
    cols, bb = right
    if reverse:
        cols, bb = cols[::-1], bb[::-1]
    i = j = steps = 0
    a_remaining, b_remaining = float(aa[0]), float(bb[0])
    out_rows, out_cols, masses = [], [], []
    while i < len(rows) and j < len(cols):
        steps += 1
        mass = min(a_remaining, b_remaining)
        if mass > 0:
            out_rows.append(rows[i])
            out_cols.append(cols[j])
            masses.append(mass)
        # At least one support entry is exhausted on every step. No epsilon
        # pruning: an arbitrarily small positive remainder is still processed.
        advance_left = a_remaining <= b_remaining
        advance_right = b_remaining <= a_remaining
        if advance_left:
            i += 1
            if i < len(rows):
                a_remaining = float(aa[i])
        else:
            a_remaining -= mass
        if advance_right:
            j += 1
            if j < len(cols):
                b_remaining = float(bb[j])
        else:
            b_remaining -= mass
    rr = np.asarray(out_rows, dtype=np.intp)
    cc = np.asarray(out_cols, dtype=np.intp)
    mm = np.asarray(masses, dtype=float)
    # The only unprocessed residual may be floating mass-balance error after
    # the other side exhausts. Gate it explicitly rather than call this exact.
    remainder = 0.0
    if i < len(rows):
        remainder = a_remaining + math.fsum(aa[i + 1:])
    if j < len(cols):
        remainder = b_remaining + math.fsum(bb[j + 1:])
    if remainder > 2e-12:
        raise RuntimeError("sparse NW plan failed its marginal gate")
    return rr, cc, mm, steps, remainder


@dataclass(frozen=True)
class PreparedLayer:
    matrix: np.ndarray
    left_supports: list
    right_supports: list
    counts: dict

    def evaluate(self, i, j):
        """Evaluate one parent pair in support-sized work, including both trials."""
        left, right = self.left_supports[i], self.right_supports[j]
        counts = dict(orientations=2, support_entries_read=0, nw_steps=0,
                      emitted_edges=0, cost_entries_read=0,
                      dense_plan_entries_allocated=0,
                      max_unprocessed_roundoff_mass=0.0)
        best = None
        for reverse in (False, True):
            rows, cols, masses, steps, remainder = _nw_sparse(left, right, reverse)
            value = float(np.sum(masses * self.matrix[rows, cols]))
            if not np.isfinite(value):
                raise ValueError("policy objective overflowed")
            counts["support_entries_read"] += len(left[0]) + len(right[0])
            counts["nw_steps"] += steps
            counts["emitted_edges"] += len(masses)
            counts["cost_entries_read"] += len(masses)
            counts["max_unprocessed_roundoff_mass"] = max(
                counts["max_unprocessed_roundoff_mass"], remainder)
            if best is None or value < best[0]:
                best = value, rows, cols, masses
        return SparsePolicyResult(*best, counts)


def prepare_layer(matrix, left_marginals, right_marginals, orders=None):
    """Validate once and cache global-rank-restricted positive supports.

    Costs and marginals must be finite and nonnegative. The caller must not
    mutate the supplied matrix while using the returned layer. ``orders`` may
    cache the original policy's global SVD; its reverse orientation must be the
    exact reversal of the first right order. Preparation scans the whole matrix
    and every input marginal; these costs are reported separately from pairs.
    """
    matrix = np.asarray(matrix, dtype=float)
    if (matrix.ndim != 2 or 0 in matrix.shape or not np.isfinite(matrix).all()
            or (matrix < 0).any()):
        raise ValueError("matrix must be finite, nonnegative and nonempty")
    computed_orders = orders is None
    if computed_orders:
        orders = _orders(matrix)
    if len(orders) != 3:
        raise ValueError("expected left, right and reverse-right orders")
    left, right, reverse = [np.asarray(order) for order in orders]
    for order, size in ((left, matrix.shape[0]), (right, matrix.shape[1]),
                        (reverse, matrix.shape[1])):
        if (order.shape != (size,) or order.dtype.kind not in "iu"
                or not np.array_equal(np.sort(order), np.arange(size))):
            raise ValueError("orders must be permutations of matrix indices")
    if not np.array_equal(reverse, right[::-1]):
        raise ValueError("second right orientation must reverse the first")
    left_supports, left_scanned, left_positive = _ordered_supports(
        left_marginals, matrix.shape[0], left)
    right_supports, right_scanned, right_positive = _ordered_supports(
        right_marginals, matrix.shape[1], right)
    counts = dict(matrix_entries_validated=int(matrix.size),
                  marginal_entries_scanned=left_scanned + right_scanned,
                  positive_entries_sorted=left_positive + right_positive,
                  global_rank_entries=matrix.shape[0] + matrix.shape[1],
                  policy_svd_calls=int(computed_orders))
    return PreparedLayer(matrix, left_supports, right_supports, counts)
