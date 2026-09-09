"""Registered C1 audit for H-B temporal reachability-envelope headroom.

This program is a non-deployable falsification probe: it deliberately uses the
exact value tables and exact optimal occupation.  It does not implement H-B,
does not produce a candidate certificate, and must not be timed against SOTA.

Run from the workspace root after registering the companion hypothesis:
    python research-workflow/probes/envelope_headroom_c1.py
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import eye, kron, vstack

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "adapters"))

import generators  # noqa: E402
from common_model import build_window_model, stage_cost  # noqa: E402

EPSILON = 0.005
SEEDS = (1000, 1001)
DELTAS = (0.5, 0.3, 0.18)
COSTS = ("squared", "absolute")
PROCESSES = ("ar1", "second_order_nonmonotone")
PATHS = {0.5: 4000, 0.3: 6000, 0.18: 8000}
T = 4
K = 1


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transport_plan(a, b, matrix):
    """Numerical OT value and a full coupling, with explicit residual gates."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    matrix = np.asarray(matrix, dtype=float)
    posa, posb = a > 0, b > 0
    aa, bb = a[posa].copy(), b[posb].copy()
    aa /= aa.sum()
    bb /= bb.sum()
    cost = matrix[np.ix_(posa, posb)]
    n, m = cost.shape
    if n == 1 or m == 1:
        reduced = np.outer(aa, bb)
    else:
        constraints = vstack((kron(eye(n), np.ones((1, m))),
                              kron(np.ones((1, n)), eye(m))), format="csr")
        marginals = np.concatenate((aa, bb))
        result = linprog(cost.ravel(), A_eq=constraints, b_eq=marginals,
                         bounds=(0, None), method="highs")
        if not result.success:
            raise RuntimeError(f"transport LP failed: {result.message}")
        reduced = result.x.reshape(n, m)
        if (np.max(np.abs(reduced.sum(1) - aa)) > 1e-8
                or np.max(np.abs(reduced.sum(0) - bb)) > 1e-8
                or reduced.min() < -1e-9):
            raise RuntimeError("transport plan failed residual gate")
    plan = np.zeros_like(matrix, dtype=float)
    plan[np.ix_(posa, posb)] = reduced
    return float(np.sum(plan * matrix)), plan


def exact_tables_and_occupation(left, right, cost):
    """Backward exact numerical DP followed by its optimal pair-state flow."""
    values = [None] * (T + 1)
    plans = [None] * T
    values[T] = np.zeros((len(left.states[T]), len(right.states[T])))
    local_lps = 0
    for t in range(T - 1, -1, -1):
        matrix = stage_cost(left.representatives[t + 1],
                            right.representatives[t + 1], cost) + values[t + 1]
        vt = np.empty((len(left.states[t]), len(right.states[t])))
        pt = [[None for _ in range(len(right.states[t]))]
              for _ in range(len(left.states[t]))]
        for i, a in enumerate(left.kernels[t]):
            for j, b in enumerate(right.kernels[t]):
                vt[i, j], pt[i][j] = transport_plan(a, b, matrix)
                local_lps += 1
        values[t], plans[t] = vt, pt
    root, root_plan = transport_plan(left.initial, right.initial, values[0])
    occupation = [root_plan]
    left_mass = left.initial.copy()
    right_mass = right.initial.copy()
    if (np.max(np.abs(root_plan.sum(1) - left_mass)) > 1e-8
            or np.max(np.abs(root_plan.sum(0) - right_mass)) > 1e-8):
        raise RuntimeError("root occupation has incorrect marginals")
    for t in range(T):
        nxt = np.zeros_like(values[t + 1])
        for i, j in np.argwhere(occupation[t] > 0):
            nxt += occupation[t][i, j] * plans[t][i][j]
        left_mass = left_mass @ left.kernels[t]
        right_mass = right_mass @ right.kernels[t]
        if (nxt.min(initial=0.0) < -1e-12
                or abs(float(nxt.sum()) - 1.0) > 1e-8
                or np.max(np.abs(nxt.sum(1) - left_mass)) > 1e-8
                or np.max(np.abs(nxt.sum(0) - right_mass)) > 1e-8):
            raise RuntimeError("occupation flow failed mass or marginal gate")
        occupation.append(nxt)
    return root, values, occupation, local_lps


def reachability_ranges(model):
    """lo[t][s], hi[t][s]: output extrema at s reachable from state t."""
    lo = [[None] * (T + 1) for _ in range(T + 1)]
    hi = [[None] * (T + 1) for _ in range(T + 1)]
    edge_visits = 0
    for s in range(T + 1):
        lo[s][s] = np.asarray(model.representatives[s], dtype=float).copy()
        hi[s][s] = lo[s][s].copy()
        for t in range(s - 1, -1, -1):
            lt = np.empty(len(model.states[t]))
            ht = np.empty(len(model.states[t]))
            for i, row in enumerate(model.kernels[t]):
                successors = np.flatnonzero(row > 0)
                edge_visits += len(successors)
                lt[i] = np.min(lo[t + 1][s][successors])
                ht[i] = np.max(hi[t + 1][s][successors])
            lo[t][s], hi[t][s] = lt, ht
    return lo, hi, edge_visits


def interval_cost_bounds(xlo, xhi, ylo, yhi, power):
    lower = np.maximum.reduce((np.zeros((len(xlo), len(ylo))),
                               xlo[:, None] - yhi[None, :],
                               ylo[None, :] - xhi[:, None]))
    upper = np.maximum(np.abs(xlo[:, None] - yhi[None, :]),
                       np.abs(xhi[:, None] - ylo[None, :]))
    return lower ** power, upper ** power


def envelope_tables(left, right, cost):
    lx, hx, ex = reachability_ranges(left)
    ly, hy, ey = reachability_ranges(right)
    power = 2 if cost == "squared" else 1
    lower, upper = [], []
    queries = 0
    for t in range(T + 1):
        elo = np.zeros((len(left.states[t]), len(right.states[t])))
        ehi = np.zeros_like(elo)
        for s in range(t + 1, T + 1):
            a, b = interval_cost_bounds(lx[t][s], hx[t][s],
                                        ly[t][s], hy[t][s], power)
            elo += a
            ehi += b
            queries += elo.size
        lower.append(elo)
        upper.append(ehi)
    return lower, upper, ex + ey, queries


def max_servable_mass(mu, slack, budget, mask=None):
    """Fractional-knapsack optimistic mass bound, ordered by slack per mass."""
    if mask is None:
        mask = np.ones_like(mu, dtype=bool)
    weights = mu[mask]
    gaps = slack[mask]
    # This is an optimistic upper bound, so even tiny positive mass must be
    # retained.  Dropping it would make the reported maximum nonconservative.
    positive = weights > 0
    weights, gaps = weights[positive], gaps[positive]
    order = np.argsort(gaps, kind="stable")
    remaining = float(budget)
    mass = 0.0
    for idx in order:
        w, g = float(weights[idx]), max(0.0, float(gaps[idx]))
        cost = w * g
        if cost <= remaining + 1e-15:
            mass += w
            remaining -= cost
        elif g > 0 and remaining > 0:
            mass += remaining / g
            break
    return min(1.0, mass)


def optimistic_entry_fraction(mu, slack, budget):
    """Necessary-bound relaxation; ignores alternative-policy and frontier constraints."""
    damage = np.maximum(mu * slack, 0.0).ravel()
    cumulative = np.cumsum(np.sort(damage, kind="stable"))
    return float(np.searchsorted(cumulative, budget + 1e-15, side="right") / len(damage))


def side_parameters(process):
    if process == "ar1":
        return ({"a": 0.7, "sigma": 1.0}, {"a": 0.55, "sigma": 1.15})
    return ({"b": 0.55, "c": 0.95, "w": 1.7, "d": -0.45, "sigma": 0.7},
            {"b": 0.4, "c": 0.95, "w": 1.7, "d": -0.2, "sigma": 0.85})


def generate_pair(process, seed, n):
    children = np.random.SeedSequence(seed).spawn(2)
    rng_a, rng_b = (np.random.default_rng(child) for child in children)
    pa, pb = side_parameters(process)
    generator = generators.FAMILIES[process]
    return generator(T, n, rng_a, **pa), generator(T, n, rng_b, **pb)


def run_case(process, delta, cost, seed):
    started = time.perf_counter()
    paths_a, paths_b = generate_pair(process, seed, PATHS[delta])
    build_started = time.perf_counter()
    left = build_window_model(paths_a, k=K, delta=delta, shift=0.0)
    right = build_window_model(paths_b, k=K, delta=delta, shift=0.0)
    build_seconds = time.perf_counter() - build_started
    exact_started = time.perf_counter()
    root, values, occupation, local_lps = exact_tables_and_occupation(left, right, cost)
    exact_seconds = time.perf_counter() - exact_started
    if not math.isfinite(root) or root <= 0:
        raise RuntimeError("relative-gap probe requires a positive finite root")
    env_started = time.perf_counter()
    elo, ehi, edge_visits, envelope_queries = envelope_tables(left, right, cost)
    envelope_seconds = time.perf_counter() - env_started
    max_lower_violation = max(float(np.max(elo[t] - values[t])) for t in range(T + 1))
    max_upper_violation = max(float(np.max(values[t] - ehi[t])) for t in range(T + 1))
    if max_lower_violation > 1e-9 or max_upper_violation > 1e-9:
        raise RuntimeError("reachability envelope failed containment gate")
    budget = EPSILON * root
    layers = []
    for t in range(T - 1):
        slack = np.maximum(values[t] - elo[t], 0.0)
        out_a = (left.kernels[t] > 0).sum(1)
        out_b = (right.kernels[t] > 0).sum(1)
        nondegenerate = (out_a[:, None] > 1) & (out_b[None, :] > 1)
        layers.append({
            "t": t,
            "state_pairs": int(slack.size),
            "occupation_support_pairs": int((occupation[t] > 1e-15).sum()),
            "mean_out_degree_left": float(out_a.mean()),
            "mean_out_degree_right": float(out_b.mean()),
            "out_degree_one_state_fraction_left": float((out_a == 1).mean()),
            "out_degree_one_state_fraction_right": float((out_b == 1).mean()),
            "zero_slack_entry_fraction": float((slack <= 1e-12).mean()),
            "occupation_weighted_gap_over_budget": float(np.sum(occupation[t] * slack) / budget),
            "servable_occupation_fraction": max_servable_mass(occupation[t], slack, budget),
            "servable_nondegenerate_occupation_fraction": max_servable_mass(
                occupation[t], slack, budget, nondegenerate),
            "optimistic_omittable_entry_fraction_relaxation": optimistic_entry_fraction(
                occupation[t], slack, budget)
        })
    return {
        "process": process, "delta": delta, "cost": cost, "seed": seed,
        "T": T, "k": K, "paths_per_side": PATHS[delta], "shift": 0.0,
        "root_value": root, "root_budget": budget,
        "model_hash_left": left.model_hash, "model_hash_right": right.model_hash,
        "max_lower_containment_violation": max_lower_violation,
        "max_upper_containment_violation": max_upper_violation,
        "local_transport_solves": local_lps,
        "reachability_edge_visits": edge_visits,
        "envelope_scalar_entry_queries": envelope_queries,
        "build_seconds": build_seconds,
        "exact_reference_seconds": exact_seconds,
        "envelope_seconds": envelope_seconds,
        "total_seconds": time.perf_counter() - started,
        "layers": layers
    }


def aggregate(cases):
    groups = []
    for process in PROCESSES:
        for cost in COSTS:
            for delta in DELTAS:
                rows = [r for r in cases if (r["process"], r["cost"], r["delta"])
                        == (process, cost, delta)]
                layer_ids = range(T - 1)
                med_all = [float(np.median([r["layers"][t]["servable_occupation_fraction"]
                                            for r in rows])) for t in layer_ids]
                med_nd = [float(np.median([
                    r["layers"][t]["servable_nondegenerate_occupation_fraction"]
                    for r in rows])) for t in layer_ids]
                eligible = [t for t in layer_ids if med_all[t] >= 0.10 and med_nd[t] >= 0.10]
                groups.append({
                    "process": process, "cost": cost, "delta": delta,
                    "median_servable_by_layer": med_all,
                    "median_servable_nondegenerate_by_layer": med_nd,
                    "qualifying_layers": eligible,
                    "occupation_prediction_pass": bool(eligible),
                    "max_median_optimistic_entry_fraction_relaxation": max(
                        float(np.median([r["layers"][t]["optimistic_omittable_entry_fraction_relaxation"]
                                         for r in rows])) for t in layer_ids)
                })
    passed = all(g["occupation_prediction_pass"] for g in groups)
    return {
        "occupation_prediction_pass": passed,
        "classification": ("mechanism_headroom_survives" if passed
                           else "mechanism_headroom_falsified_H_B01_remains_revise"),
        "original_entry_prediction_classification": "inconclusive_metric_mismatch",
        "groups": groups
    }


def main():
    prereg = ROOT / "ledger" / "preregistered" / "H_B01C1_envelope_headroom.json"
    if not prereg.is_file():
        raise RuntimeError("register H_B01C1_envelope_headroom before running")
    cases = []
    for process in PROCESSES:
        for delta in DELTAS:
            for cost in COSTS:
                for seed in SEEDS:
                    # Deterministic regeneration makes both costs consume identical paths.
                    cases.append(run_case(process, delta, cost, seed))
                    print(process, delta, cost, seed,
                          f"R={cases[-1]['root_value']:.6g}", flush=True)
    result = {
        "schema": "H-B01-C1-envelope-headroom-v1",
        "hypothesis": "H_B01C1_envelope_headroom",
        "registered_record_sha256": sha256(prereg),
        "probe_code_sha256": sha256(Path(__file__)),
        "design_sha256": sha256(ROOT / "frozen_design.json"),
        "design_amendment_sha256": sha256(ROOT / "frozen_design_amendment_1.json"),
        "generators_sha256": sha256(ROOT / "generators.py"),
        "prior_data_disclosed": True,
        "scientific_scope": "short_horizon_non_deployable_mechanism_replication_not_SOTA",
        "aggregate": aggregate(cases),
        "cases": cases
    }
    output = ROOT / "runs" / "cycle_2" / "H_B01C1_envelope_headroom.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                      encoding="utf-8")
    print(json.dumps({"output": str(output), "aggregate": result["aggregate"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
