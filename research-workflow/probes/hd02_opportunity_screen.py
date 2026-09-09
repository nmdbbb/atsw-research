"""Exploratory H_D02 opportunity ceiling on cumulative clamped-DP traces.

Uses fresh numerical OT as a diagnostic oracle, never the candidate acceptance
routine. This is neither H_C02's policy nor a performance/certificate benchmark.
Freeze the companion manifest before running; results are append-only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import eye, kron, vstack

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "adapters")]
import generators
from common_model import build_window_model, stage_cost
from global_subsolution import solve_clamped_subsolution

OUT = ROOT / "runs/cycle_2/hd02_opportunity"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def solve(a, b, matrix, allowed=None):
    start = time.perf_counter()
    n, m = matrix.shape
    constraints = vstack((kron(eye(n), np.ones((1, m))),
                          kron(np.ones((1, n)), eye(m))), format="csr")
    bounds = (0, None) if allowed is None else [
        (0, None) if edge else (0, 0) for edge in allowed.ravel()]
    result = linprog(matrix.ravel(), A_eq=constraints,
                     b_eq=np.r_[a, b], bounds=bounds, method="highs",
                     options={"primal_feasibility_tolerance": 1e-10,
                              "dual_feasibility_tolerance": 1e-10,
                              "time_limit": 2.0})
    seconds = time.perf_counter() - start
    if not result.success:
        if allowed is not None and result.status == 2:
            return None, seconds
        raise RuntimeError(result.message)
    plan = result.x.reshape(n, m)
    residual = max(np.max(abs(plan.sum(1) - a)),
                   np.max(abs(plan.sum(0) - b)), max(0, -plan.min()))
    if residual > 1e-10:
        raise RuntimeError(f"oracle feasibility residual {residual}")
    dual = result.eqlin.marginals
    return {"value": float(result.fun), "plan": plan,
            "reduced": matrix - dual[:n, None] - dual[None, n:],
            "residual": float(residual)}, seconds


def main():
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for path, expected in manifest["source_sha256"].items():
        if digest(ROOT / path) != expected:
            raise RuntimeError(f"source changed since manifest freeze: {path}")
    for name in ("results.json", "trace.jsonl"):
        if (OUT / name).exists():
            raise RuntimeError(f"preserve existing {name}; do not rerun in place")
    started = time.perf_counter()
    rows, current_events = [], []
    partial = False
    trace = (OUT / "trace.jsonl").open("x", encoding="utf-8")
    try:
        for family in manifest["families"]:
            seeds = np.random.SeedSequence(manifest["seed"]).spawn(2)
            params = manifest["pair_parameters"][family]
            paths = [generators.FAMILIES[family](manifest["T"], manifest["paths"],
                     np.random.default_rng(seed), **p) for seed, p in zip(seeds, params)]
            for k in manifest["k"]:
                left, right = [build_window_model(x, k, manifest["delta"], manifest["shift"])
                               for x in paths]
                for cost in manifest["costs"]:
                    cache, current_events, roots = {}, [], []
                    cell_started = time.perf_counter()
                    solves, total_seconds, audit_seconds, replay_seconds = 0, 0.0, 0.0, 0.0
                    tag = {"family": family, "k": k, "cost": cost}
                    for phase in manifest["activation_phases"]:
                        values = [np.zeros((len(a), len(b)))
                                  for a, b in zip(left.states, right.states)]
                        masks = []
                        for t, value in enumerate(values[:-1]):
                            i, j = np.indices(value.shape)
                            masks.append((17 * i + 31 * j + 13 * t) % 4 < phase)
                        for t in range(left.horizon - 1, -2, -1):
                            if t == -1:
                                matrix = values[0]
                                blocks = [(-1, -1, left.initial, right.initial)]
                            else:
                                matrix = stage_cost(left.representatives[t + 1],
                                                    right.representatives[t + 1], cost) + values[t + 1]
                                blocks = [(int(i), int(j), left.kernels[t][i], right.kernels[t][j])
                                          for i, j in np.argwhere(masks[t])]
                            for i, j, full_a, full_b in blocks:
                                if time.perf_counter() - started > manifest["wall_budget_seconds"]:
                                    raise TimeoutError("declared wall budget reached")
                                ia, ib = full_a > 0, full_b > 0
                                a, b = full_a[ia], full_b[ib]
                                local = matrix[np.ix_(ia, ib)]
                                new, seconds = solve(a, b, local)
                                total_seconds += seconds
                                solves += 1
                                key = (t, i, j)
                                if key in cache:
                                    old_matrix, old = cache[key]
                                    delta = local - old_matrix
                                    event = {**tag, "phase": phase, "node": key,
                                             "entries": int(local.size), "weighted_ot_seconds": seconds,
                                             "cost_changed": bool(np.any(delta != 0)),
                                             "nontrivial_ot": bool(min(local.shape) > 1)}
                                    increment = float(np.sum(old["plan"] * delta))
                                    gain = new["value"] - old["value"]
                                    scale_tol = 1e-9 * max(1.0, abs(old["value"]), abs(new["value"]))
                                    hit = bool(np.any((old["plan"] > 0) & (delta > 0)))
                                    monotone = bool(np.all(delta >= 0))
                                    event.update(support_hit=hit, monotone_float=monotone,
                                                 min_delta=float(delta.min()), incumbent_increment=increment,
                                                 optimum_increment=gain, oracle_tolerance=scale_tol,
                                                 old_face_density=float(np.mean(abs(old["reduced"]) <= 1e-10)),
                                                 unavoidable_by_row_column=bool(
                                                     np.any(np.all(delta > 0, axis=1)) or
                                                     np.any(np.all(delta > 0, axis=0))))
                                    if not event["cost_changed"]:
                                        decision = "no_update"
                                    elif not monotone or (hit and increment <= scale_tol):
                                        decision = "numerically_ambiguous"
                                    elif not hit:
                                        decision = "support_miss"
                                    elif gain > scale_tol:
                                        decision = "value_increased_numerically"
                                    elif abs(gain) <= scale_tol:
                                        allowed = (abs(old["reduced"]) <= 1e-10) & (delta == 0)
                                        face, face_seconds = solve(a, b, np.zeros_like(local), allowed)
                                        audit_seconds += face_seconds
                                        event["face_lp_seconds"] = face_seconds
                                        event["face_allowed_edges"] = int(allowed.sum())
                                        valid = face is not None
                                        if valid:
                                            old_gap = abs(float(np.sum(face["plan"] * old_matrix)) - old["value"])
                                            event["face_old_objective_residual"] = old_gap
                                            event["face_marginal_residual"] = face["residual"]
                                            valid = old_gap <= scale_tol and float(np.sum(face["plan"] * delta)) == 0
                                        decision = "numerical_face_rescue_unresolved_exact" if valid else "numerically_ambiguous"
                                    else:
                                        decision = "numerically_ambiguous"
                                    event["decision"] = decision
                                    current_events.append(event)
                                    trace.write(json.dumps({**event, "a": a.tolist(), "b": b.tolist(),
                                                "old_matrix": old_matrix.tolist(), "new_matrix": local.tolist(),
                                                "old_plan": old["plan"].tolist(), "old_reduced": old["reduced"].tolist()}) + "\n")
                                cache[key] = (local.copy(), new)
                                if t >= 0:
                                    values[t][i, j] = new["value"]
                                else:
                                    roots.append(new["value"])
                        # Independently replay the existing implementation for each phase.
                        replay_started = time.perf_counter()
                        reference = solve_clamped_subsolution(left, right, cost, active=masks)
                        replay_seconds += time.perf_counter() - replay_started
                        if abs(reference.lower - roots[-1]) > 1e-8 or any(
                                np.max(abs(a - b)) > 1e-8 for a, b in zip(values, reference.tables)):
                            raise RuntimeError("instrumented recurrence disagrees with existing clamped DP")
                    hits = [e for e in current_events if e["support_hit"] and e["cost_changed"]]
                    opportunities = [e for e in hits if e["decision"] == "numerical_face_rescue_unresolved_exact"]
                    ambiguous = [e for e in current_events if e["decision"] == "numerically_ambiguous"]
                    row = {**tag, "all_revisited_events": len(current_events),
                           "changed_events": sum(e["cost_changed"] for e in current_events),
                           "support_hits": len(hits), "numerical_face_rescues": len(opportunities),
                           "nontrivial_revisited_events": sum(e["nontrivial_ot"] for e in current_events),
                           "nontrivial_hits": sum(e["nontrivial_ot"] for e in hits),
                           "ambiguous_events": len(ambiguous),
                           "unavoidable_by_row_column": sum(e["unavoidable_by_row_column"] for e in hits),
                           "mean_old_face_density_on_hits": float(np.mean([e["old_face_density"] for e in hits])) if hits else None,
                           "all_reference_solves": solves, "all_reference_solve_seconds": total_seconds,
                           "initial_solves": solves - len(current_events),
                           "initial_solve_seconds": total_seconds - sum(e["weighted_ot_seconds"] for e in current_events),
                           "controller_materialization_trace_seconds": time.perf_counter() - cell_started - total_seconds - audit_seconds - replay_seconds,
                           "independent_clamped_replay_seconds": replay_seconds,
                           "hit_reference_solve_seconds": sum(e["weighted_ot_seconds"] for e in hits),
                           "rescue_reference_solve_seconds": sum(e["weighted_ot_seconds"] for e in opportunities),
                           "face_audit_seconds": audit_seconds, "root_values_by_phase": roots,
                           "model_hashes": [left.model_hash, right.model_hash],
                           "decisions": {d: sum(e["decision"] == d for e in current_events)
                                         for d in sorted({e["decision"] for e in current_events})}}
                    rows.append(row)
                    current_events = []
                    print(json.dumps(row), flush=True)
    except TimeoutError:
        partial = True
    finally:
        trace.close()
        result = {"manifest_sha256": digest(manifest_path), "partial": partial,
                  "wall_seconds": time.perf_counter() - started, "completed_cells": rows,
                  "partial_cell_events": current_events,
                  "exact_certificate_claim": False, "runtime_savings_claim": False,
                  "interpretation": "Numerical optimistic opportunity screen; unresolved exactness and controller-policy representativeness."}
        (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
