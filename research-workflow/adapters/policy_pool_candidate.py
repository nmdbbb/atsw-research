"""Generalized SVD-policy plus shared-dual-pool candidate on the common model.

This ports the mathematical mechanism of the archived ``certify5.py`` without
importing its top-level benchmark or inheriting its deterministic-root, k=1,
quadratic-cost assumptions.  It supports the corrected common finite model,
arbitrary initial laws, k>=1 and both registered costs.

The returned interval is a *float64 numerical enclosure candidate*.  Every
lower witness is made dual feasible for the represented float matrix and every
upper value comes from a feasible NW coupling, but sums are not outward rounded
with interval arithmetic.  Therefore this module may be used in development
and target-equivalence tests; it is not yet a publication-grade certificate.
"""
from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import eye, kron, vstack

from common_model import build_window_model, stage_cost

FROZEN_SHIFTS = {
    0.5: (0.0, 0.1667, 0.3333),
    0.3: (0.0, 0.1, 0.2),
    0.18: (0.0, 0.06, 0.12),
}


@dataclass
class Counters:
    policy_pair_evaluations: int = 0
    policy_svd_calls: int = 0
    occupation_pair_evaluations: int = 0
    selected_pair_solves: int = 0
    linprog_calls: int = 0
    distinct_selected_pair_versions: int = 0
    nonimproving_selected_solves: int = 0
    root_dual_solves: int = 0

    def as_dict(self):
        return dict(vars(self))


def _normalized(weights):
    weights = np.asarray(weights, dtype=float)
    if weights.ndim != 1 or (weights < 0).any() or not np.isfinite(weights).all():
        raise ValueError("weights must be a finite nonnegative vector")
    total = float(weights.sum())
    if total <= 0:
        raise ValueError("weights must have positive mass")
    return weights / total


def nw_plan(a, b):
    """Increasing-order coupling from intersections of cumulative intervals."""
    a, b = _normalized(a), _normalized(b)
    ca = np.concatenate(([0.0], np.cumsum(a)))
    cb = np.concatenate(([0.0], np.cumsum(b)))
    plan = np.clip(np.minimum(ca[1:, None], cb[None, 1:])
                   - np.maximum(ca[:-1, None], cb[None, :-1]), 0.0, None)
    if (np.max(np.abs(plan.sum(1) - a)) > 2e-12
            or np.max(np.abs(plan.sum(0) - b)) > 2e-12):
        raise RuntimeError("NW plan failed its marginal gate")
    return plan


def _orders(matrix):
    residual = (matrix - matrix.mean(1, keepdims=True)
                - matrix.mean(0, keepdims=True) + matrix.mean())
    u, _, vt = np.linalg.svd(residual, full_matrices=False)
    left = np.argsort(u[:, 0], kind="stable")
    right = np.argsort(vt[0], kind="stable")
    return left, right, right[::-1]


def _ordered_policy(a, b, matrix, orders=None):
    """Try both rank-one orientations and return the cheaper feasible plan."""
    if orders is None:
        orders = _orders(matrix)
    left, right_a, right_b = orders
    best = None
    for right in (right_a, right_b):
        ordered = nw_plan(np.asarray(a)[left], np.asarray(b)[right])
        plan = np.zeros_like(matrix, dtype=float)
        plan[np.ix_(left, right)] = ordered
        value = float(np.sum(plan * matrix))
        if best is None or value < best[0]:
            best = value, plan
    return best


def _make_feasible(alpha, beta, matrix):
    """Shift beta down until alpha_i+beta_j<=M_ij in float arithmetic."""
    alpha = np.asarray(alpha, dtype=float).copy()
    beta = np.asarray(beta, dtype=float).copy()
    scale = max(1.0, float(np.max(np.abs(matrix))),
                float(np.max(np.abs(alpha))), float(np.max(np.abs(beta))))
    guard = 16.0 * np.finfo(float).eps * scale
    violation = float(np.max(alpha[:, None] + beta[None, :] - matrix))
    beta -= max(0.0, violation) + guard
    violation = float(np.max(alpha[:, None] + beta[None, :] - matrix))
    if violation > 0:
        beta -= violation + guard
    if float(np.max(alpha[:, None] + beta[None, :] - matrix)) > 0:
        raise RuntimeError("failed to construct a float-feasible dual")
    return alpha, beta


def ctransform(matrix, alpha=None):
    """Two exact coordinate maximizations followed by a feasibility shift."""
    if alpha is None:
        alpha = np.zeros(matrix.shape[0])
    beta = np.min(matrix - np.asarray(alpha)[:, None], axis=0)
    alpha = np.min(matrix - beta[None, :], axis=1)
    return _make_feasible(alpha, beta, matrix)


def transport_plan_and_dual(a, b, matrix, counters=None):
    """Solve one OT and extend its dual to every row/column of ``matrix``."""
    a, b = _normalized(a), _normalized(b)
    posa, posb = a > 0, b > 0
    aa, bb = a[posa], b[posb]
    reduced = np.asarray(matrix)[np.ix_(posa, posb)]
    n, m = reduced.shape
    if n == 1 or m == 1:
        plan_reduced = np.outer(aa, bb)
        alpha_reduced, beta_reduced = ctransform(reduced)
    else:
        constraints = vstack((kron(eye(n), np.ones((1, m))),
                              kron(np.ones((1, n)), eye(m))), format="csr")
        marginals = np.concatenate((aa, bb))
        result = linprog(reduced.ravel(), A_eq=constraints, b_eq=marginals,
                         bounds=(0, None), method="highs")
        if counters is not None:
            counters.linprog_calls += 1
        if not result.success:
            raise RuntimeError(f"transport LP failed: {result.message}")
        plan_reduced = result.x.reshape(n, m)
        alpha_reduced = np.asarray(result.eqlin.marginals[:n], dtype=float)
        beta_reduced = np.asarray(result.eqlin.marginals[n:n + m], dtype=float)
        alpha_reduced, beta_reduced = _make_feasible(
            alpha_reduced, beta_reduced, reduced)
    if (np.max(np.abs(plan_reduced.sum(1) - aa)) > 1e-8
            or np.max(np.abs(plan_reduced.sum(0) - bb)) > 1e-8
            or plan_reduced.min(initial=0.0) < -1e-9):
        raise RuntimeError("transport primal failed residual gate")

    # Preserve the selected-support dual, then assign maximal feasible values
    # to coordinates that have zero mass in this particular solve.  This makes
    # the witness reusable for all other parent marginals on the same matrix.
    alpha = np.empty(len(a))
    beta = np.empty(len(b))
    alpha[posa] = alpha_reduced
    beta[posb] = beta_reduced
    if (~posb).any():
        beta[~posb] = np.min(
            np.asarray(matrix)[np.ix_(posa, ~posb)] - alpha_reduced[:, None], axis=0)
    if (~posa).any():
        alpha[~posa] = np.min(
            np.asarray(matrix)[np.ix_(~posa, np.ones(len(b), dtype=bool))]
            - beta[None, :], axis=1)
    alpha, beta = _make_feasible(alpha, beta, np.asarray(matrix))
    plan = np.zeros_like(matrix, dtype=float)
    plan[np.ix_(posa, posb)] = plan_reduced
    primal = float(np.sum(plan * matrix))
    dual = float(a @ alpha + b @ beta)
    if dual > primal + 1e-8 * max(1.0, abs(primal)):
        raise RuntimeError("dual exceeds primal")
    return primal, plan, alpha, beta, dual


def evaluate_policy(left, right, cost, counters):
    """Evaluate one globally defined SVD-order policy backward."""
    T = left.horizon
    values = [None] * (T + 1)
    values[T] = np.zeros((len(left.states[T]), len(right.states[T])))
    for t in range(T - 1, -1, -1):
        matrix = stage_cost(left.representatives[t + 1],
                            right.representatives[t + 1], cost) + values[t + 1]
        orders = _orders(matrix)
        counters.policy_svd_calls += 1
        current = np.empty((len(left.states[t]), len(right.states[t])))
        for i, a in enumerate(left.kernels[t]):
            for j, b in enumerate(right.kernels[t]):
                current[i, j] = _ordered_policy(a, b, matrix, orders)[0]
                counters.policy_pair_evaluations += 1
        values[t] = current
    root_orders = _orders(values[0])
    counters.policy_svd_calls += 1
    root_value, root_plan = _ordered_policy(
        left.initial, right.initial, values[0], root_orders)
    return root_value, root_plan, values


def policy_occupation(left, right, cost, policy_values, root_plan, counters):
    """Forward occupation induced by exactly the policy evaluated above."""
    occupation = [root_plan]
    left_mass, right_mass = left.initial.copy(), right.initial.copy()
    for t in range(left.horizon):
        matrix = stage_cost(left.representatives[t + 1],
                            right.representatives[t + 1], cost) + policy_values[t + 1]
        orders = _orders(matrix)
        nxt = np.zeros((len(left.states[t + 1]), len(right.states[t + 1])))
        for i, j in np.argwhere(occupation[t] > 0):
            _, plan = _ordered_policy(left.kernels[t][i], right.kernels[t][j],
                                      matrix, orders)
            nxt += occupation[t][i, j] * plan
            counters.occupation_pair_evaluations += 1
        left_mass = left_mass @ left.kernels[t]
        right_mass = right_mass @ right.kernels[t]
        if (nxt.min(initial=0.0) < -1e-12
                or np.max(np.abs(nxt.sum(1) - left_mass)) > 1e-8
                or np.max(np.abs(nxt.sum(0) - right_mass)) > 1e-8):
            raise RuntimeError("policy occupation failed marginal gate")
        occupation.append(nxt)
    return occupation


def free_lower(matrix, left_kernel, right_kernel):
    """Zero, two one-marginal relaxations and one reusable feasible dual."""
    alpha, beta = ctransform(matrix)
    lower = ((left_kernel @ alpha)[:, None]
             + (right_kernel @ beta)[None, :])
    lower = np.maximum(lower, (left_kernel @ matrix.min(1))[:, None])
    lower = np.maximum(lower, (right_kernel @ matrix.min(0))[None, :])
    return np.maximum(lower, 0.0)


def lower_sweep(left, right, cost, upper_tables, occupation, budget,
                counters, floors=None):
    """One backward sweep with at most ``budget`` selected pairs per layer."""
    T = left.horizon
    lower = [None] * (T + 1)
    lower[T] = np.zeros((len(left.states[T]), len(right.states[T])))
    for t in range(T - 1, -1, -1):
        matrix = stage_cost(left.representatives[t + 1],
                            right.representatives[t + 1], cost) + lower[t + 1]
        lt = free_lower(matrix, left.kernels[t], right.kernels[t])
        if floors is not None:
            lt = np.maximum(lt, floors[t])
        seen = set()
        for _ in range(int(budget)):
            score = np.maximum(upper_tables[t] - lt, 0.0) * occupation[t]
            for pair in seen:
                score[pair] = -np.inf
            i, j = np.unravel_index(int(np.argmax(score)), score.shape)
            if not np.isfinite(score[i, j]):
                break
            seen.add((i, j))
            counters.selected_pair_solves += 1
            counters.distinct_selected_pair_versions += 1
            _, _, alpha, beta, _ = transport_plan_and_dual(
                left.kernels[t][i], right.kernels[t][j], matrix, counters)
            candidate = ((left.kernels[t] @ alpha)[:, None]
                         + (right.kernels[t] @ beta)[None, :])
            before = float(lt.sum())
            lt = np.maximum(lt, candidate)
            if float(lt.sum()) <= before + 1e-12:
                counters.nonimproving_selected_solves += 1
        # A feasible policy table is a valid upper pointwise.  This clamp only
        # suppresses floating disagreement; it cannot invalidate a lower bound.
        lower[t] = np.minimum(lt, upper_tables[t])
    counters.root_dual_solves += 1
    _, _, alpha, beta, root_lower = transport_plan_and_dual(
        left.initial, right.initial, lower[0], counters)
    return root_lower, lower, {"root_alpha": alpha, "root_beta": beta}


def solve_model(left, right, cost="squared", budgets=(16, 64, 128)):
    """Run the policy once and an escalating lower-pool schedule."""
    if left.horizon != right.horizon:
        raise ValueError("models must have equal horizons")
    if cost not in ("squared", "absolute"):
        raise ValueError("cost must be squared or absolute")
    budgets = tuple(int(b) for b in budgets)
    if not budgets or any(b < 0 for b in budgets):
        raise ValueError("budgets must be nonnegative integers")
    counters = Counters()
    started = time.perf_counter()
    upper, root_plan, upper_tables = evaluate_policy(left, right, cost, counters)
    policy_seconds = time.perf_counter() - started
    occ_started = time.perf_counter()
    occupation = policy_occupation(left, right, cost, upper_tables, root_plan, counters)
    occupation_seconds = time.perf_counter() - occ_started
    floors = None
    levels = []
    for budget in budgets:
        sweep_started = time.perf_counter()
        lower, floors, witness = lower_sweep(
            left, right, cost, upper_tables, occupation, budget, counters, floors)
        sweep_seconds = time.perf_counter() - sweep_started
        gap = ((upper - lower) / lower if lower > 0
               else (0.0 if upper == 0 else float("inf")))
        levels.append({
            "budget_per_layer": budget,
            "lower": lower,
            "upper": upper,
            "relative_root_width": gap,
            "policy_seconds": policy_seconds,
            "occupation_seconds": occupation_seconds,
            "sweep_seconds": sweep_seconds,
            "elapsed_seconds": time.perf_counter() - started,
            "root_dual_feasibility_violation": float(np.max(
                witness["root_alpha"][:, None] + witness["root_beta"][None, :]
                - floors[0])),
            "counters_cumulative": counters.as_dict()
        })
    return {
        "status": "FLOAT64_NUMERICAL_INTERVAL_NOT_OUTWARD_ROUNDED",
        "cost": cost,
        "k_left": left.k,
        "k_right": right.k,
        "model_hash_left": left.model_hash,
        "model_hash_right": right.model_hash,
        "levels": levels
    }


def solve_from_paths(paths_left, paths_right, k, delta, cost="squared",
                     budgets=(16, 64, 128), shifts=None):
    """Charge construction and every frozen grid shift to a standalone call."""
    if shifts is None:
        try:
            shifts = FROZEN_SHIFTS[float(delta)]
        except KeyError as exc:
            raise ValueError("explicit shifts required outside the frozen deltas") from exc
    outer_started = time.perf_counter()
    results = []
    for shift in shifts:
        shift_started = time.perf_counter()
        left = build_window_model(paths_left, k=k, delta=delta, shift=shift)
        right = build_window_model(paths_right, k=k, delta=delta, shift=shift)
        construction_seconds = time.perf_counter() - shift_started
        solved = solve_model(left, right, cost=cost, budgets=budgets)
        solved["shift"] = float(shift)
        solved["representation_construction_seconds"] = construction_seconds
        solved["standalone_shift_seconds"] = time.perf_counter() - shift_started
        results.append(solved)
    aggregate = []
    for index, budget in enumerate(tuple(int(b) for b in budgets)):
        aggregate.append({
            "budget_per_layer": budget,
            "all_shift_seconds_sum": float(sum(
                r["representation_construction_seconds"]
                + r["levels"][index]["elapsed_seconds"] for r in results)),
            "max_relative_root_width_across_shifts": float(max(
                r["levels"][index]["relative_root_width"] for r in results)),
            "every_shift_at_0_5_percent": bool(all(
                r["levels"][index]["relative_root_width"] <= 0.005
                for r in results))
        })
    return {
        "status": "DEVELOPMENT_ONLY_FLOAT64_NUMERICAL_INTERVAL",
        "timing_boundary": "from_paths_including_all_requested_shifts_and_warmup_levels",
        "delta": float(delta), "k": int(k), "cost": cost,
        "shifts": results, "aggregate_levels": aggregate,
        "outer_wall_seconds": time.perf_counter() - outer_started
    }
