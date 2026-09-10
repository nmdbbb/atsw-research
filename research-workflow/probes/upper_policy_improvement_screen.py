"""Posthoc bounded upper-policy diagnostic, never a root certificate."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "adapters"), str(ROOT / "probes")]
from common_model import build_window_model, stage_cost
from policy_pool_candidate import _orders, _ordered_policy, free_lower, transport_plan_and_dual, Counters
from policy_pool_common_smoke import paths

OUT = ROOT / "runs/cycle_2/upper_policy_screen"
CASES = [dict(process="ar1", k=1, delta=0.5, cost="squared"),
         dict(process="second_order_nonmonotone", k=2, delta=0.18, cost="absolute")]
FILES = ["probes/upper_policy_improvement_screen.py", "probes/policy_pool_common_smoke.py",
         "adapters/policy_pool_candidate.py", "adapters/common_model.py", "generators.py",
         "runs/cycle_2/policy_pool_smoke_manifest.json", "runs/cycle_2/policy_pool_common_smoke.json"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze():
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "manifest.json"
    if target.exists():
        raise RuntimeError("Never overwrite frozen manifest")
    manifest = dict(schema="upper-policy-improvement-screen-v1", frozen_before_execution=True,
        cases=CASES, T=5, paths_per_side=128, seed=1000, shift=0.0, budgets=[4, 16],
        selection="posthoc representative historical cases; exploratory not confirmation",
        deadline_seconds=60, deadline_rule="cooperative checks; finish current native operation then stop, never downsize",
        method="independent single backward pass from stored SVD policy; initial occupation times local policy-minus-free-lower score; positive scores only; one extra root solve per budget; full policy reevaluation",
        checks="marginals <=1e-8; pointwise and root upper nonincrease <=1e-8; forward objective equals backward root <=1e-8",
        reference="historical float64 DP reused only after manifest/probe/generator/model identity checks; reference never used in selection",
        decision="Measure whether few local solves repair upper barrier; no lower-cache work authorized by a mere upper decrease",
        nonclaims=["no root certificate", "no speed or SOTA claim", "no final-grid evidence", "local free_lower uses U_next and is not a continuation lower certificate"],
        hashes={name: digest(ROOT / name) for name in FILES})
    target.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def pack(plan):
    r, c = np.nonzero(plan)
    return r, c, plan[r, c].copy()


def value(plan, matrix):
    r, c, mass = plan
    return float(mass @ matrix[r, c])


def residual(plan, a, b):
    r, c, mass = plan
    return max(float(np.max(np.abs(np.bincount(r, weights=mass, minlength=len(a))-a))),
               float(np.max(np.abs(np.bincount(c, weights=mass, minlength=len(b))-b))),
               max(0.0, -float(mass.min(initial=0))))


def run():
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for name, expected in manifest["hashes"].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError("Frozen input changed: " + name)
    historical_manifest = ROOT / "runs/cycle_2/policy_pool_smoke_manifest.json"
    old = json.loads(historical_manifest.read_text())
    for key, name in [("probe_sha256", "probes/policy_pool_common_smoke.py"),
                      ("generators_sha256", "generators.py"),
                      ("common_model_sha256", "adapters/common_model.py"),
                      ("candidate_sha256", "adapters/policy_pool_candidate.py")]:
        if old[key] != digest(ROOT / name):
            raise RuntimeError("Historical identity unavailable: " + name)
    archive = json.loads((ROOT / "runs/cycle_2/policy_pool_common_smoke.json").read_text())
    if archive["manifest_sha256"] != digest(historical_manifest):
        raise RuntimeError("Historical manifest identity failed")
    started = time.perf_counter()
    result = dict(manifest_sha256=digest(manifest_path), status="running", cases=[],
                  reference_identity="historical manifest and complete generation/model/candidate source hashes matched")

    def check():
        if time.perf_counter()-started > 60:
            raise TimeoutError("60 second exploratory budget reached; no downsizing")

    try:
        for case in CASES:
            check()
            tick = time.perf_counter()
            x, y = paths(case["process"])
            left = build_window_model(x, k=case["k"], delta=case["delta"], shift=0.0)
            right = build_window_model(y, k=case["k"], delta=case["delta"], shift=0.0)
            T = left.horizon
            costs = [stage_cost(left.representatives[t+1], right.representatives[t+1], case["cost"]) for t in range(T)]
            row = dict(**case, model_hashes=[left.model_hash, right.model_hash],
                       construction_seconds=time.perf_counter()-tick, levels=[])
            result["cases"].append(row)
            refrow = next(r for r in archive["rows"] if all(r[k] == v for k, v in case.items()))
            # This reference is read only for reporting, never for selection.
            row["audit_reference"] = refrow["reference"]
            shapes = [(len(left.states[t]), len(right.states[t])) for t in range(T+1)]
            row["layer_pair_counts"] = [int(np.prod(s)) for s in shapes[:-1]]
            plans = [None]*T
            U = [None]*(T+1)
            U[T] = np.zeros(shapes[T])
            maxres = 0.0
            pair_calls = 0
            dense_entries_constructed = 0
            tick = time.perf_counter()
            for t in range(T-1, -1, -1):
                check()
                M = costs[t]+U[t+1]
                order = _orders(M)
                U[t] = np.empty(shapes[t]); plans[t] = []
                for i, a in enumerate(left.kernels[t]):
                    check()
                    for j, b in enumerate(right.kernels[t]):
                        val, dense = _ordered_policy(a, b, M, order)
                        p = pack(dense)
                        maxres = max(maxres, residual(p, a, b))
                        plans[t].append(p); U[t][i, j] = val
                        pair_calls += 1; dense_entries_constructed += M.size
            initial, dense = _ordered_policy(left.initial, right.initial, U[0])
            rootplan = pack(dense)
            maxres = max(maxres, residual(rootplan, left.initial, right.initial))
            row.update(initial_upper=initial, initial_relative_excess=(initial-row["audit_reference"])/row["audit_reference"],
                       initial_policy_seconds=time.perf_counter()-tick, initial_pair_evaluations=pair_calls,
                       initial_svd_calls=T+1, dense_plan_entries_constructed=dense_entries_constructed,
                       stored_positive_edges=sum(len(p[2]) for layer in plans for p in layer),
                       initial_max_marginal_residual=maxres)
            if abs(initial-refrow["levels"][0]["upper"]) > 1e-8:
                raise RuntimeError("Initial policy differs from historical identical-input policy")

            def occupation(policy, rp):
                occ = np.zeros(shapes[0]); occ[rp[0], rp[1]] = rp[2]
                occupations = [occ]
                total = 0.0; visits = 0; edges = 0
                lm, rm = left.initial, right.initial
                for t in range(T):
                    check()
                    nxt = np.zeros(shapes[t+1])
                    for i, j in np.argwhere(occ > 0):
                        p = policy[t][int(i)*shapes[t][1]+int(j)]
                        np.add.at(nxt, (p[0], p[1]), occ[i, j]*p[2])
                        visits += 1; edges += len(p[2])
                    lm = lm@left.kernels[t]; rm = rm@right.kernels[t]
                    if max(np.max(np.abs(nxt.sum(1)-lm)), np.max(np.abs(nxt.sum(0)-rm))) > 1e-8:
                        raise RuntimeError("Occupation marginals failed")
                    total += float(np.sum(nxt*costs[t]))
                    occupations.append(nxt); occ = nxt
                return occupations, total, visits, edges

            tick = time.perf_counter()
            occ, fwd, visits, edges = occupation(plans, rootplan)
            if abs(fwd-initial) > 1e-8: raise RuntimeError("Initial forward target mismatch")
            row.update(initial_occupation_seconds=time.perf_counter()-tick,
                       initial_occupation_pair_visits=visits, initial_occupation_edge_visits=edges)
            for budget in (4, 16):
                check(); tick = time.perf_counter()
                newplans = [list(layer) for layer in plans]
                newU = [None]*(T+1); newU[T] = U[T].copy()
                counters = Counters(); layers = []; scans = 0; scan_edges = 0
                scan_seconds = solve_seconds = score_seconds = 0.0
                for t in range(T-1, -1, -1):
                    check(); st = time.perf_counter()
                    M = costs[t]+newU[t+1]
                    oldvalues = np.array([value(p, M) for p in plans[t]]).reshape(shapes[t])
                    scans += len(plans[t]); scan_edges += sum(len(p[2]) for p in plans[t])
                    scan_seconds += time.perf_counter()-st
                    st = time.perf_counter()
                    heuristic_lower = free_lower(M, left.kernels[t], right.kernels[t])
                    score = occ[t]*np.maximum(oldvalues-heuristic_lower, 0)
                    ranked = np.argsort(-score.ravel(), kind="stable")
                    selected = [int(idx) for idx in ranked[:budget] if score.ravel()[idx] > 0]
                    score_seconds += time.perf_counter()-st
                    improved = 0
                    for idx in selected:
                        check(); i, j = divmod(idx, shapes[t][1]); st = time.perf_counter()
                        val, dense, _, _, _ = transport_plan_and_dual(left.kernels[t][i], right.kernels[t][j], M, counters)
                        p = pack(dense)
                        err = residual(p, left.kernels[t][i], right.kernels[t][j])
                        maxres = max(maxres, err)
                        if err > 1e-8: raise RuntimeError("Replacement marginal violation")
                        if val < oldvalues[i, j]:
                            newplans[t][idx] = p; oldvalues[i, j] = val; improved += 1
                        solve_seconds += time.perf_counter()-st
                    newU[t] = oldvalues
                    if float(np.max(newU[t]-U[t])) > 1e-8: raise RuntimeError("Upper pointwise increased")
                    layers.append(dict(t=t, selected=len(selected), improved=improved,
                        selected_initial_mass=float(occ[t].ravel()[selected].sum()),
                        selected_score=float(score.ravel()[selected].sum()),
                        all_score=float(score.sum()), score_matrix_entries=int(M.size)))
                check(); st = time.perf_counter()
                val, dense, _, _, _ = transport_plan_and_dual(left.initial, right.initial, newU[0], counters)
                newroot = pack(dense)
                maxres = max(maxres, residual(newroot, left.initial, right.initial))
                if value(rootplan, newU[0]) < val: newroot = rootplan
                root_seconds = time.perf_counter()-st
                st = time.perf_counter(); verified = [None]*(T+1); verified[T] = U[T]
                for t in range(T-1, -1, -1):
                    check(); M = costs[t]+verified[t+1]
                    verified[t] = np.array([value(p, M) for p in newplans[t]]).reshape(shapes[t])
                    if np.max(np.abs(verified[t]-newU[t])) > 1e-8: raise RuntimeError("Reevaluation mismatch")
                final = value(newroot, verified[0])
                _, fwd, visits, edges = occupation(newplans, newroot)
                if abs(fwd-final) > 1e-8 or final > initial+1e-8 or maxres > 1e-8:
                    raise RuntimeError("Final policy numerical correctness gate failed")
                reeval_seconds = time.perf_counter()-st
                row["levels"].append(dict(budget_per_layer=budget, upper=final,
                    relative_excess=(final-row["audit_reference"])/row["audit_reference"],
                    upper_excess_removed_fraction=(initial-final)/(initial-row["audit_reference"]),
                    below_target_excess=(final-row["audit_reference"])/row["audit_reference"] <= 0.005,
                    total_improvement_seconds=time.perf_counter()-tick,
                    local_solve_calls=sum(l["selected"] for l in layers), root_solve_calls=1,
                    linprog_calls=counters.linprog_calls, local_solve_seconds=solve_seconds,
                    root_solve_seconds=root_seconds, policy_scan_seconds=scan_seconds,
                    score_seconds=score_seconds, reevaluation_seconds=reeval_seconds,
                    scan_pair_evaluations=scans, scan_edge_evaluations=scan_edges,
                    full_backward_reevaluation_pairs=sum(len(p) for p in newplans),
                    forward_reevaluation_pair_visits=visits, forward_reevaluation_edge_visits=edges,
                    max_marginal_residual=maxres, forward_backward_absolute_error=abs(fwd-final), layers=layers))
                print(json.dumps(dict(case=case, budget=budget, upper=final, relative_excess=row["levels"][-1]["relative_excess"])), flush=True)
            row["status"] = "completed"
        result["status"] = "completed"
    except TimeoutError as exc:
        result["status"] = "budget_stopped"; result["stop_reason"] = str(exc)
    finally:
        result["total_wall_seconds"] = time.perf_counter()-started
        (OUT / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps(dict(status=result["status"], total_wall_seconds=result["total_wall_seconds"])))


if __name__ == "__main__":
    freeze() if "--freeze" in sys.argv else run()
