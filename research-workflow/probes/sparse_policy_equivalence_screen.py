"""Frozen, bounded SAME-policy implementation diagnostic; no certificate claim."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "adapters"), str(ROOT / "probes")]
from common_model import build_window_model, stage_cost
from policy_pool_candidate import Counters, _orders, _ordered_policy, evaluate_policy, nw_plan
from policy_pool_common_smoke import paths

OUT = ROOT / "runs/cycle_2/sparse_policy_screen"
CASES = [dict(process="ar1", k=1, delta=0.5, cost="squared"),
         dict(process="second_order_nonmonotone", k=2, delta=0.18, cost="absolute")]
FILES = ["probes/sparse_policy_equivalence_screen.py", "adapters/sparse_ordered_policy.py",
         "adapters/policy_pool_candidate.py", "adapters/common_model.py", "generators.py",
         "probes/policy_pool_common_smoke.py", "runs/cycle_2/upper_policy_screen/manifest.json",
         "runs/cycle_2/upper_policy_screen/results.json"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze():
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "manifest.json"
    if target.exists():
        raise RuntimeError("Frozen manifest already exists")
    manifest = dict(schema="sparse-same-policy-screen-v1", frozen_before_execution=True,
        cases=CASES, T=5, paths_per_side=128, seed=1000, shift=0.0,
        budget_seconds=60, budget_rule="cooperative check before each layer and each 128 pairs; finish current native operation; no downsize or rerun",
        dense_repeats=1, sparse_repeats=2, shared_dense_matrix_verification_repeats=1,
        timing="fresh same-run dense evaluate_policy; full sparse backward/root construction includes stage costs, original _orders, support preparation and coupling evaluation; excludes model generation, imports and independent verification",
        verification="all tables/root on SAME prescribed dense continuation matrix and global orders; also two autonomous sparse backwards; at most six evenly spaced plans per layer plus root; independent tiny-flow/tie/nonDirac/normalization fixtures",
        gates=dict(value_absolute_tolerance=1e-10, marginal_absolute_tolerance=2e-12,
                   same_orientation_plan_tolerance=2e-12),
        decision="integrate only as development baseline if numerical equivalence and cheaper implementation supported; otherwise retain unintegrated",
        nonclaims=["not bytewise-identical policy", "not full end-to-end certificate timing", "not new tree mechanism", "not speed/SOTA/held-out claim"],
        hashes={name: digest(ROOT / name) for name in FILES})
    target.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(dict(status="frozen", manifest_sha256=digest(target))))


def dense_plan(result, shape):
    plan = np.zeros(shape)
    np.add.at(plan, (result.rows, result.cols), result.masses)
    return plan


def residual(result, a, b):
    a, b = np.asarray(a)/np.sum(a), np.asarray(b)/np.sum(b)
    return max(float(np.max(np.abs(np.bincount(result.rows, weights=result.masses, minlength=len(a))-a))),
               float(np.max(np.abs(np.bincount(result.cols, weights=result.masses, minlength=len(b))-b))),
               max(0.0, -float(np.min(result.masses, initial=0))))


def compare_pair(result, a, b, matrix, orders):
    ref_value, ref_plan = _ordered_policy(a, b, matrix, orders)
    actual = dense_plan(result, matrix.shape)
    candidates = []
    for right in orders[1:]:
        plan = np.zeros_like(matrix)
        plan[np.ix_(orders[0], right)] = nw_plan(np.asarray(a)[orders[0]], np.asarray(b)[right])
        candidates.append(plan)
    orientation_error = min(float(np.max(np.abs(actual-p))) for p in candidates)
    out = dict(value_error=abs(result.value-ref_value), marginal_residual=residual(result, a, b),
               selected_plan_error=float(np.max(np.abs(actual-ref_plan))),
               nearest_original_orientation_error=orientation_error,
               bitwise_plan_equal=bool(np.array_equal(actual, ref_plan)),
               bitwise_value_equal=bool(result.value == ref_value))
    if out["value_error"] > 1e-10 or out["marginal_residual"] > 2e-12 or orientation_error > 2e-12:
        raise RuntimeError("Pair equivalence failed: " + str(out))
    return out


def run():
    from sparse_ordered_policy import prepare_layer
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for name, expected in manifest["hashes"].items():
        if digest(ROOT / name) != expected:
            raise RuntimeError("Frozen input changed: " + name)
    result = dict(schema="sparse-same-policy-results-v1", manifest_sha256=digest(manifest_path),
                  status="running", cases=[], fixtures=[], python=platform.python_version(),
                  numpy=np.__version__, platform=platform.platform())
    started = time.perf_counter()

    def check():
        if time.perf_counter()-started > 60:
            raise TimeoutError("Cooperative 60-second complete execution budget reached")

    def sparse_backward(left, right, cost, prescribed=None):
        values = [None]*(left.horizon+1)
        values[-1] = np.zeros((len(left.states[-1]), len(right.states[-1])))
        counts = {}; pair_calls = 0; samples = []
        def merge(part):
            for key, val in part.items():
                counts[key] = max(counts.get(key, 0), val) if key.startswith("max_") else counts.get(key, 0)+val
        for t in range(left.horizon-1, -1, -1):
            check()
            child = values[t+1] if prescribed is None else prescribed[t+1]
            matrix = stage_cost(left.representatives[t+1], right.representatives[t+1], cost)+child
            # This is the original global SVD ordering, before any support restriction.
            orders = _orders(matrix)
            layer = prepare_layer(matrix, left.kernels[t], right.kernels[t], orders=orders)
            merge(layer.counts)
            counts["policy_svd_calls"] = counts.get("policy_svd_calls", 0)+1
            shape = (len(left.states[t]), len(right.states[t]))
            values[t] = np.empty(shape)
            sample_indices = set(np.linspace(0, int(np.prod(shape))-1, min(6, int(np.prod(shape))), dtype=int))
            for i, a in enumerate(left.kernels[t]):
                for j, b in enumerate(right.kernels[t]):
                    if pair_calls % 128 == 0: check()
                    item = layer.evaluate(i, j)
                    values[t][i, j] = item.value; pair_calls += 1
                    merge(item.counts)
                    if prescribed is not None and i*shape[1]+j in sample_indices:
                        samples.append(dict(t=t, i=i, j=j, **compare_pair(item, a, b, matrix, orders)))
        root_matrix = values[0] if prescribed is None else prescribed[0]
        root_layer = prepare_layer(root_matrix, [left.initial], [right.initial], orders=_orders(root_matrix))
        root = root_layer.evaluate(0, 0)
        for part in (root_layer.counts, root.counts):
            merge(part)
        counts["policy_svd_calls"] = counts.get("policy_svd_calls", 0)+1
        if prescribed is not None:
            samples.append(dict(t="root", **compare_pair(root, left.initial, right.initial, root_matrix, _orders(root_matrix))))
        return root.value, values, counts, samples

    try:
        # Explicit fixtures include non-Dirac root laws and tiny positive flow;
        # timing cases alone have deterministic initial laws.
        rng = np.random.default_rng(290910)
        fixture_inputs = [
            (np.array([1e-15, 0, 1-1e-15]), np.array([1e-15, 1-1e-15, 0]), np.arange(9.0).reshape(3, 3), "tiny_positive"),
            (np.array([2.0, 0, 3.0]), np.array([0, 7.0, 3.0]), np.zeros((3, 3)), "ties_unnormalized_nonDirac"),
        ]
        for k in range(20):
            a = rng.integers(0, 8, 7).astype(float); b = rng.integers(0, 8, 6).astype(float)
            a[0] += 1; b[0] += 1
            fixture_inputs.append((a, b, np.abs(rng.normal(size=(7, 6))), "random_"+str(k)))
        for a, b, matrix, name in fixture_inputs:
            check()
            orders = (np.arange(len(a)), np.arange(len(b)), np.arange(len(b))[::-1]) if name == "tiny_positive" else _orders(matrix)
            item = prepare_layer(matrix, [a], [b], orders=orders).evaluate(0, 0)
            row = dict(name=name, **compare_pair(item, a, b, matrix, orders))
            if name == "tiny_positive":
                row["positive_flow_below_1e12"] = bool(np.any((item.masses > 0)&(item.masses < 1e-12)))
                if not row["positive_flow_below_1e12"]: raise RuntimeError("Tiny positive flow dropped")
            result["fixtures"].append(row)
        for case in CASES:
            check(); tick = time.perf_counter()
            x, y = paths(case["process"])
            left = build_window_model(x, k=case["k"], delta=case["delta"], shift=0.0)
            right = build_window_model(y, k=case["k"], delta=case["delta"], shift=0.0)
            row = dict(**case, model_hashes=[left.model_hash, right.model_hash],
                       path_model_seconds=time.perf_counter()-tick,
                       pair_counts=[len(left.states[t])*len(right.states[t]) for t in range(left.horizon)])
            result["cases"].append(row)
            check(); tick = time.perf_counter()
            dense_root, _, dense_values = evaluate_policy(left, right, case["cost"], Counters())
            row.update(dense_construction_seconds=time.perf_counter()-tick, dense_root=dense_root)
            check(); row["sparse_repeats"] = []
            for repeat in range(2):
                tick = time.perf_counter()
                root, values, counts, _ = sparse_backward(left, right, case["cost"])
                seconds = time.perf_counter()-tick
                errors = [float(np.max(np.abs(a-b))) for a, b in zip(values, dense_values)]
                item = dict(repeat=repeat, construction_seconds=seconds, root=root, root_error=abs(root-dense_root),
                            table_max_errors=errors, all_tables_bitwise_equal=all(np.array_equal(a,b) for a,b in zip(values,dense_values)), counts=counts)
                item["numerical_equivalence_passed"] = max(errors+[item["root_error"]]) <= 1e-10
                row["sparse_repeats"].append(item)
                check()
            tick = time.perf_counter()
            root, values, counts, samples = sparse_backward(left, right, case["cost"], prescribed=dense_values)
            errors = [float(np.max(np.abs(a-b))) for a, b in zip(values, dense_values)]
            row["shared_matrix_verification"] = dict(seconds=time.perf_counter()-tick, root_error=abs(root-dense_root),
                table_max_errors=errors, sampled_plans=samples, counts=counts)
            row["shared_matrix_verification"]["numerical_equivalence_passed"] = max(errors+[abs(root-dense_root)]) <= 1e-10
            row["dense_over_sparse_ratios"] = [row["dense_construction_seconds"]/r["construction_seconds"] for r in row["sparse_repeats"]]
            print(json.dumps(dict(case=case, dense_seconds=row["dense_construction_seconds"], ratios=row["dense_over_sparse_ratios"])), flush=True)
        passed = all(r["shared_matrix_verification"]["numerical_equivalence_passed"] and all(s["numerical_equivalence_passed"] for s in r["sparse_repeats"]) for r in result["cases"])
        result["status"] = "completed_numerical_equivalence_only" if passed else "completed_equivalence_rejected"
    except TimeoutError as exc:
        result["status"] = "budget_stopped"; result["stop_reason"] = str(exc)
    except Exception as exc:
        result["status"] = "verification_failed"; result["stop_reason"] = repr(exc)
        raise
    finally:
        result["total_wall_seconds"] = time.perf_counter()-started
        (OUT / "results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
        print(json.dumps(dict(status=result["status"], total_wall_seconds=result["total_wall_seconds"])), flush=True)


if __name__ == "__main__":
    freeze() if "--freeze" in sys.argv else run()
