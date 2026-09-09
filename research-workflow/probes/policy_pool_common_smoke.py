"""Small target-equivalence smoke for the generalized archived candidate.

The reference is used only after each candidate solve for auditing.  This is a
development correctness/coverage check, not a timing benchmark, certificate
claim or SOTA comparison.  Run only with the frozen companion manifest present.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "adapters")]

import generators  # noqa: E402
from common_model import build_window_model, exact_dp  # noqa: E402
from policy_pool_candidate import solve_model  # noqa: E402

T = 5
N = 128
SEED = 1000
DELTAS = (0.5, 0.18)
KS = (1, 2)
COSTS = ("squared", "absolute")
PROCESSES = ("ar1", "second_order_nonmonotone")
BUDGETS = (4, 16)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def params(process):
    if process == "ar1":
        return ({"a": 0.7, "sigma": 1.0}, {"a": 0.55, "sigma": 1.15})
    return ({"b": 0.55, "c": 0.95, "w": 1.7, "d": -0.45, "sigma": 0.7},
            {"b": 0.4, "c": 0.95, "w": 1.7, "d": -0.2, "sigma": 0.85})


def paths(process):
    sa, sb = np.random.SeedSequence(SEED).spawn(2)
    pa, pb = params(process)
    generate = generators.FAMILIES[process]
    return (generate(T, N, np.random.default_rng(sa), **pa),
            generate(T, N, np.random.default_rng(sb), **pb))


def main():
    manifest_path = ROOT / "runs" / "cycle_2" / "policy_pool_smoke_manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("frozen smoke manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if digest(__file__) != manifest["probe_sha256"]:
        raise RuntimeError("probe changed after smoke manifest was frozen")
    if digest(ROOT / "adapters" / "policy_pool_candidate.py") != manifest["candidate_sha256"]:
        raise RuntimeError("candidate changed after smoke manifest was frozen")
    rows = []
    started = time.perf_counter()
    for process in PROCESSES:
        left_paths, right_paths = paths(process)
        for delta in DELTAS:
            for k in KS:
                left = build_window_model(left_paths, k=k, delta=delta, shift=0.0)
                right = build_window_model(right_paths, k=k, delta=delta, shift=0.0)
                for cost in COSTS:
                    reference_started = time.perf_counter()
                    reference = exact_dp(left, right, cost)
                    reference_seconds = time.perf_counter() - reference_started
                    candidate = solve_model(left, right, cost, budgets=BUDGETS)
                    levels = candidate["levels"]
                    valid = all(level["lower"] <= reference + 1e-8
                                and reference <= level["upper"] + 1e-8
                                and level["root_dual_feasibility_violation"] <= 0
                                for level in levels)
                    if not valid:
                        raise RuntimeError("candidate interval/residual gate failed")
                    rows.append({
                        "process": process, "delta": delta, "k": k, "cost": cost,
                        "reference": reference,
                        "reference_seconds": reference_seconds,
                        "candidate_status": candidate["status"],
                        "levels": levels,
                        "numerical_reference_contained": valid
                    })
                    print(process, delta, k, cost,
                          f"gap16={levels[-1]['relative_root_width']:.4g}", flush=True)
    result = {
        "schema": "policy-pool-common-smoke-v1",
        "manifest_sha256": digest(manifest_path),
        "scientific_scope": "development_correctness_smoke_not_SOTA",
        "all_numerical_references_contained": all(
            row["numerical_reference_contained"] for row in rows),
        "case_count": len(rows),
        "total_wall_seconds": time.perf_counter() - started,
        "rows": rows
    }
    output = ROOT / "runs" / "cycle_2" / "policy_pool_common_smoke.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                      encoding="utf-8")
    print(json.dumps({"output": str(output), "case_count": len(rows),
                      "all_contained": result["all_numerical_references_contained"]}, indent=2))


if __name__ == "__main__":
    main()
