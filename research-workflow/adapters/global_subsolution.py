"""Small-instance global Bellman-subsolution LP for H_C01.

This module is a correctness and work-count probe, not a benchmark solver.  It
keeps a certified baseline ``h`` at every inactive pair node and introduces
Bellman dual variables only at active nodes.  Activity may decide where work is
spent; it never removes a successor inequality required by an active node.

The numerical result is a float64 lower-bound witness.  Publication-grade
certification still requires independently audited outward rounding.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from common_model import _transport_value, stage_cost


@dataclass(frozen=True)
class WorkCounts:
    active_pair_nodes: int
    inactive_pair_nodes: int
    value_variables: int
    dual_variables: int
    bellman_value_constraints: int
    successor_constraints: int
    root_constraints: int
    inequality_nonzeros: int

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class SubsolutionResult:
    lower: float
    tables: tuple[np.ndarray, ...]
    work: WorkCounts
    max_inequality_residual: float


@dataclass(frozen=True)
class ClampedWorkCounts:
    active_pair_nodes: int
    inactive_pair_nodes: int
    local_transport_calls: int
    successor_cost_entries: int
    root_transport_calls: int
    root_cost_entries: int

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class ClampedResult:
    lower: float
    tables: tuple[np.ndarray, ...]
    work: ClampedWorkCounts


def future_marginal_subsolution(left, right, cost="squared", depth=2):
    """Construct the fixed-depth future-marginal cost subsolution ``h^H``.

    Each term is the one-time OT cost on propagated scalar-output marginals.
    For squared cost this is W_2 squared, in the same units as the target.
    The construction is deliberately dense and its OT calls must be charged.
    """
    if isinstance(depth, bool) or not isinstance(depth, (int, np.integer)) or depth < 0:
        raise ValueError("depth must be a nonnegative integer")
    h = list(zero_subsolution(left, right))
    calls = 0
    for t in range(left.horizon):
        px = np.eye(len(left.states[t]))
        py = np.eye(len(right.states[t]))
        for s in range(t + 1, min(left.horizon, t + int(depth)) + 1):
            px = px @ left.kernels[s - 1]
            py = py @ right.kernels[s - 1]
            matrix = stage_cost(left.representatives[s],
                                right.representatives[s], cost)
            for i in range(len(px)):
                for j in range(len(py)):
                    h[t][i, j] += _transport_value(px[i], py[j], matrix)
                    calls += 1
    return tuple(h), {"one_time_transport_calls": calls,
                      "dense_pair_entries": int(sum(x.size for x in h))}


def zero_subsolution(left, right):
    """Return the free subsolution for either registered nonnegative cost."""
    if left.horizon != right.horizon:
        raise ValueError("models must have the same horizon")
    return tuple(
        np.zeros((len(left.states[t]), len(right.states[t])), dtype=float)
        for t in range(left.horizon + 1)
    )


def _check_shapes(left, right, h, active=None):
    T = left.horizon
    if right.horizon != T or len(h) != T + 1:
        raise ValueError("model/subsolution horizons do not match")
    checked_h = []
    for t, table in enumerate(h):
        table = np.asarray(table, dtype=float)
        expected = (len(left.states[t]), len(right.states[t]))
        if table.shape != expected or not np.isfinite(table).all():
            raise ValueError(f"invalid h[{t}] shape or values")
        checked_h.append(table)
    if active is None:
        active = [np.ones_like(checked_h[t], dtype=bool) for t in range(T)]
    if len(active) != T:
        raise ValueError("active must contain one mask per nonterminal layer")
    checked_active = []
    for t, mask in enumerate(active):
        mask = np.asarray(mask, dtype=bool)
        if mask.shape != checked_h[t].shape:
            raise ValueError(f"invalid active[{t}] shape")
        checked_active.append(mask)
    return tuple(checked_h), tuple(checked_active)


def verify_subsolution(left, right, cost, h, tolerance=1e-9):
    """Numerically check ``h_t <= T_t h_(t+1)`` on every pair node.

    This deliberately solves every tiny local OT and is therefore a test oracle,
    not part of the claimed active-set cost.
    """
    h, _ = _check_shapes(left, right, h)
    if np.max(np.abs(h[-1])) > tolerance:
        return False, {"terminal_residual": float(np.max(np.abs(h[-1])))}
    worst = -np.inf
    location = None
    for t in range(left.horizon - 1, -1, -1):
        matrix = stage_cost(left.representatives[t + 1],
                            right.representatives[t + 1], cost) + h[t + 1]
        for i, a in enumerate(left.kernels[t]):
            for j, b in enumerate(right.kernels[t]):
                residual = float(h[t][i, j] - _transport_value(a, b, matrix))
                if residual > worst:
                    worst, location = residual, (t, i, j)
    return worst <= tolerance, {"max_residual": worst, "location": location}


def solve_active_subsolution(left, right, cost="squared", h=None, active=None):
    """Maximize the root lower bound for fixed active pair-node masks.

    The dummy root is always active.  For each active node, the LP instantiates
    all cross-products of positive successor supports.  Inactive values remain
    fixed at ``h``.  The caller must establish that ``h`` is a Bellman
    subsolution; use :func:`verify_subsolution` on small correctness fixtures.
    """
    if h is None:
        h = zero_subsolution(left, right)
    h, active = _check_shapes(left, right, h, active)
    if np.any(h[-1] != 0):
        raise ValueError("terminal baseline h_T must be exactly zero")
    T = left.horizon

    bounds = []
    value_index = {}

    def variable(bound=(None, None)):
        index = len(bounds)
        bounds.append(bound)
        return index

    root = variable()
    for t in range(T):
        for i, j in np.argwhere(active[t]):
            value_index[t, int(i), int(j)] = variable((float(h[t][i, j]), None))

    rows, cols, data, rhs = [], [], [], []

    def inequality(terms, upper):
        row = len(rhs)
        for col, coefficient in terms:
            if coefficient:
                rows.append(row)
                cols.append(col)
                data.append(float(coefficient))
        rhs.append(float(upper))

    dual_variables = 0
    bellman_constraints = 0
    successor_constraints = 0

    def add_dual_block(parent_index, a, b, continuation, next_t):
        nonlocal dual_variables, bellman_constraints, successor_constraints
        ia = np.flatnonzero(np.asarray(a) > 0)
        ib = np.flatnonzero(np.asarray(b) > 0)
        alpha = {int(x): variable() for x in ia}
        beta = {int(y): variable() for y in ib}
        dual_variables += len(alpha) + len(beta)
        terms = [(parent_index, 1.0)]
        terms += [(alpha[int(x)], -float(a[x])) for x in ia]
        terms += [(beta[int(y)], -float(b[y])) for y in ib]
        inequality(terms, 0.0)
        bellman_constraints += 1
        for x in ia:
            for y in ib:
                terms = [(alpha[int(x)], 1.0), (beta[int(y)], 1.0)]
                key = (next_t, int(x), int(y))
                if next_t < T and key in value_index:
                    terms.append((value_index[key], -1.0))
                    upper = float(continuation[x, y])
                else:
                    upper = float(continuation[x, y] + h[next_t][x, y])
                inequality(terms, upper)
                successor_constraints += 1

    # Root continuation has no stage cost: time zero is not charged.
    add_dual_block(root, left.initial, right.initial,
                   np.zeros_like(h[0]), 0)
    root_cross_count = int(np.count_nonzero(left.initial) *
                           np.count_nonzero(right.initial))
    root_constraint_count = 1 + root_cross_count

    for t in range(T):
        continuation = stage_cost(left.representatives[t + 1],
                                  right.representatives[t + 1], cost)
        for i, j in np.argwhere(active[t]):
            add_dual_block(value_index[t, int(i), int(j)],
                           left.kernels[t][i], right.kernels[t][j],
                           continuation, t + 1)

    objective = np.zeros(len(bounds))
    objective[root] = -1.0
    matrix = coo_matrix((data, (rows, cols)), shape=(len(rhs), len(bounds))).tocsr()
    result = linprog(objective, A_ub=matrix, b_ub=np.asarray(rhs),
                     bounds=bounds, method="highs")
    if not result.success:
        raise RuntimeError(f"global subsolution LP failed: {result.message}")
    residual = float(np.max(matrix @ result.x - np.asarray(rhs), initial=-np.inf))
    if residual > 1e-7:
        raise RuntimeError("global subsolution LP returned excessive residual")

    tables = [table.copy() for table in h]
    for (t, i, j), index in value_index.items():
        tables[t][i, j] = result.x[index]
    active_count = len(value_index)
    total_nonterminal = sum(table.size for table in h[:-1])
    work = WorkCounts(
        active_pair_nodes=active_count,
        inactive_pair_nodes=total_nonterminal - active_count,
        value_variables=active_count + 1,
        dual_variables=dual_variables,
        bellman_value_constraints=bellman_constraints - 1,
        successor_constraints=successor_constraints - root_cross_count,
        root_constraints=root_constraint_count,
        inequality_nonzeros=int(matrix.nnz),
    )
    return SubsolutionResult(float(result.x[root]), tuple(tables), work, residual)


def solve_clamped_subsolution(left, right, cost="squared", h=None, active=None):
    """Evaluate the same fixed ``(A,h)`` construction by backward local OT.

    This is the mandatory formulation ablation for H_C01.  Acyclic Bellman
    structure makes it mathematically equivalent at the root to the global LP,
    while exposing whether a claimed saving comes from inactive tree nodes or
    merely from choosing a different LP formulation.
    """
    if h is None:
        h = zero_subsolution(left, right)
    h, active = _check_shapes(left, right, h, active)
    if np.any(h[-1] != 0):
        raise ValueError("terminal baseline h_T must be exactly zero")
    values = [table.copy() for table in h]
    calls = 0
    entries = 0
    active_count = 0
    for t in range(left.horizon - 1, -1, -1):
        matrix = stage_cost(left.representatives[t + 1],
                            right.representatives[t + 1], cost) + values[t + 1]
        for i, j in np.argwhere(active[t]):
            a, b = left.kernels[t][i], right.kernels[t][j]
            values[t][i, j] = _transport_value(a, b, matrix)
            calls += 1
            active_count += 1
            entries += int(np.count_nonzero(a) * np.count_nonzero(b))
    lower = _transport_value(left.initial, right.initial, values[0])
    root_entries = int(np.count_nonzero(left.initial) *
                       np.count_nonzero(right.initial))
    total_nonterminal = sum(table.size for table in h[:-1])
    work = ClampedWorkCounts(
        active_pair_nodes=active_count,
        inactive_pair_nodes=total_nonterminal - active_count,
        local_transport_calls=calls,
        successor_cost_entries=entries,
        root_transport_calls=1,
        root_cost_entries=root_entries,
    )
    return ClampedResult(float(lower), tuple(values), work)
