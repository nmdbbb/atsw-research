"""Bounded structural census for forced-node affine elimination; no OT solves."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "adapters"), str(ROOT / "probes")]
from common_model import build_window_model
from policy_pool_common_smoke import paths
OUT = ROOT / "runs/cycle_2/forced_frontier_census"
CASES = [dict(process="ar1", k=1, delta=.5, cost="squared"),
         dict(process="second_order_nonmonotone", k=2, delta=.18, cost="absolute")]
FILES = ["probes/forced_frontier_census.py", "generators.py",
         "adapters/common_model.py", "probes/policy_pool_common_smoke.py"]
SECONDS = 20
WORK_CAP = 1_000_000
def digest(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
def freeze():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = dict(
        schema="forced-frontier-census-v1", frozen_before_run=True,
        cases=CASES, T=5, paths_per_side=128, seed=1000, shift=0.0,
        budget=dict(seconds=SECONDS, union_input_entries=WORK_CAP,
                    rule="cooperative; partial result on first hit; no downsize or retry"),
        method=("node(t,i,j) is forced iff either positive transition support has size one; "
                "terminal zero has empty frontier; other nodes are unique boundary symbols; "
                "backward set unions compile first nonforced descendants"),
        counts=("global forced transition support-product and dynamic incidences and union inputs; all-forced "
                "compiled nnz; unique forced values directly requested by nonforced parents or root; "
                "their forced dependency closure, direct incidences, and compiled nnz"),
        declared_gate=("reject per-entry materialization footprint iff directly demanded compiled "
                       "frontier nnz exceeds direct forced incidences of its dependency closure; otherwise "
                       "candidate survives footprint gate only"),
        dynamic_comparator=("also compare with required dynamic incidences: edges whose child frontier "
                            "is nonempty; exact_dp skips singleton LPs and empty-frontier constants cache once"),
        interpretation=("structural elementary variable elimination, not novelty; optimistic support "
                        "footprint omits coefficients, constants, local OT feasibility, rounding, all "
                        "read costs, solver work, and any performance or speed claim"),
        hashes={name: digest(name) for name in FILES})
    with (OUT / "manifest.json").open("x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(manifest, indent=2) + "\n")
class BudgetStop(Exception):
    pass
def census(left, right, check, row):
    T = left.horizon
    shapes = [(len(left.states[t]), len(right.states[t])) for t in range(T + 1)]
    supports = [([np.flatnonzero(x > 0) for x in left.kernels[t]],
                 [np.flatnonzero(x > 0) for x in right.kernels[t]]) for t in range(T)]
    forced = [np.zeros(s, dtype=bool) for s in shapes]
    for t, (sa, sb) in enumerate(supports):
        forced[t] = (np.array([len(x) == 1 for x in sa])[:, None] |
                     np.array([len(x) == 1 for x in sb])[None, :])
    forced[T][:] = True
    boundary = {}
    next_symbol = 0
    for t in range(T):
        for i, j in np.argwhere(~forced[t]):
            boundary[(t, int(i), int(j))] = next_symbol
            next_symbol += 1
    frontiers = [dict() for _ in range(T + 1)]
    for i, j in np.ndindex(shapes[T]):
        frontiers[T][(i, j)] = frozenset()
    direct_all = dynamic_all = union_inputs = processed = 0
    per_layer = [None] * (T + 1)
    per_layer[T] = dict(layer=T, forced_nodes=int(forced[T].sum()), nonforced_nodes=0,
                        direct_forced_incidences=0, dynamic_forced_incidences=0, union_input_entries=0,
                        compiled_frontier_nnz=0, max_frontier_width=0)
    for t in range(T - 1, -1, -1):
        layer_direct = layer_dynamic = layer_inputs = layer_nnz = layer_max = 0
        sa, sb = supports[t]
        for i, j in np.argwhere(forced[t]):
            check(processed)
            merged = set()
            for a in sa[int(i)]:
                for b in sb[int(j)]:
                    direct_all += 1; layer_direct += 1
                    if t + 1 == T or forced[t + 1][a, b]:
                        child = frontiers[t + 1][(int(a), int(b))]
                    else:
                        child = (boundary[(t + 1, int(a), int(b))],)
                    add = len(child)
                    check(processed + add)
                    processed += add; union_inputs += add; layer_inputs += add
                    if add: dynamic_all += 1; layer_dynamic += 1
                    merged.update(child)
            item = frozenset(merged)
            frontiers[t][(int(i), int(j))] = item
            layer_nnz += len(item); layer_max = max(layer_max, len(item))
        per_layer[t] = dict(layer=t, forced_nodes=int(forced[t].sum()),
                            nonforced_nodes=int((~forced[t]).sum()),
                            direct_forced_incidences=layer_direct,
                            dynamic_forced_incidences=layer_dynamic,
                            union_input_entries=layer_inputs,
                            compiled_frontier_nnz=layer_nnz,
                            max_frontier_width=layer_max)
    assert all(not x for x in frontiers[T].values())
    assert all(key not in frontiers[t] for t in range(T) for key in
               ((int(i), int(j)) for i, j in np.argwhere(~forced[t])))
    demanded = set()
    def demand(t, i, j):
        if forced[t][i, j]: demanded.add((t, int(i), int(j)))
    for t in range(T):
        sa, sb = supports[t]
        for i, j in np.argwhere(~forced[t]):
            check(processed)
            for a in sa[int(i)]:
                for b in sb[int(j)]: demand(t + 1, int(a), int(b))
    ia, ib = np.flatnonzero(left.initial > 0), np.flatnonzero(right.initial > 0)
    root_frontier = set()
    for i in ia:
        for j in ib:
            demand(0, int(i), int(j))
            if forced[0][i, j]: root_frontier.update(frontiers[0][(int(i), int(j))])
            else: root_frontier.add(boundary[(0, int(i), int(j))])
    direct_demanded_nnz = sum(len(frontiers[t][(i, j)]) for t, i, j in demanded)
    closure, stack, closure_direct, closure_dynamic = set(), list(demanded), 0, 0
    while stack:
        check(processed)
        node = stack.pop()
        if node in closure: continue
        closure.add(node); t, i, j = node
        if t == T: continue
        sa, sb = supports[t]
        for a in sa[i]:
            for b in sb[j]:
                closure_direct += 1
                child = (t + 1, int(a), int(b))
                active = (not forced[t + 1][a, b] or
                          bool(frontiers[t + 1][(int(a), int(b))]))
                closure_dynamic += int(active)
                if forced[t + 1][a, b] and child not in closure: stack.append(child)
    closure_nnz = sum(len(frontiers[t][(i, j)]) for t, i, j in closure)
    gate_reject = direct_demanded_nnz > closure_direct
    row.update(status="completed", shapes=shapes, total_nodes=sum(a*b for a, b in shapes),
               total_forced_nodes=sum(int(x.sum()) for x in forced),
               total_nonforced_nodes=sum(int((~x).sum()) for x in forced),
               boundary_symbols=next_symbol, direct_forced_incidences_all=direct_all,
               dynamic_forced_incidences_all=dynamic_all,
               union_input_entries=union_inputs,
               compiled_frontier_nnz_all=sum(x["compiled_frontier_nnz"] for x in per_layer),
               max_frontier_width=max(x["max_frontier_width"] for x in per_layer),
               per_layer=per_layer, root_first_boundary_width=len(root_frontier),
               directly_demanded_forced_nodes=len(demanded),
               directly_demanded_frontier_nnz=direct_demanded_nnz,
               demanded_forced_dependency_closure_nodes=len(closure),
               demanded_closure_direct_forced_incidences=closure_direct,
               demanded_closure_dynamic_forced_incidences=closure_dynamic,
               demanded_closure_compiled_frontier_nnz=closure_nnz,
               gate_reject=gate_reject,
               dynamic_comparator_reject=direct_demanded_nnz > closure_dynamic,
               all_edges_gate_is_optimistic=True,
               gate_verdict="reject" if gate_reject else "survives_footprint_gate_only")
def run():
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    if (OUT / "results.json").exists(): raise RuntimeError("preserve existing result")
    for name, expected in manifest["hashes"].items():
        if digest(name) != expected: raise RuntimeError("source changed: " + name)
    old = json.loads((ROOT / "runs/cycle_2/policy_pool_smoke_manifest.json").read_text())
    for key, name in [("probe_sha256", FILES[3]), ("generators_sha256", FILES[1]),
                      ("common_model_sha256", FILES[2])]:
        if old[key] != digest(name): raise RuntimeError("old manifest pin mismatch: " + name)
    started = time.perf_counter()
    result = dict(schema="forced-frontier-census-results-v1",
                  manifest_sha256=digest("runs/cycle_2/forced_frontier_census/manifest.json"),
                  status="running", cases=[], union_work_cap=WORK_CAP)
    completed_work = 0
    def check(work):
        if completed_work + work > WORK_CAP: raise BudgetStop("union_input_entries cap")
        if time.perf_counter() - started > SECONDS: raise BudgetStop("cooperative seconds cap")
    try:
        for case in CASES:
            check(0)
            row = dict(**case, status="running"); result["cases"].append(row)
            x, y = paths(case["process"])
            models = [build_window_model(z, k=case["k"], delta=case["delta"], shift=0.) for z in (x, y)]
            row["model_hashes"] = [z.model_hash for z in models]
            census(*models, check, row)
            completed_work += row["union_input_entries"]
        result["status"] = "completed"
    except BudgetStop as exc:
        result.update(status="budget_stopped_partial", reason=str(exc))
        result["cases"][-1].update(status="budget_stopped_partial", reason=str(exc))
    except Exception as exc:
        result.update(status="failed", reason=repr(exc)); raise
    finally:
        result["total_seconds"] = time.perf_counter() - started
        result["interpretation"] = manifest["interpretation"]
        with (OUT / "results.json").open("x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(json.dumps(dict(status=result["status"], seconds=result["total_seconds"]), indent=2))
if __name__ == "__main__":
    freeze() if "--freeze" in sys.argv else run()
