"""Posthoc population diagnostic using archived references; no new OT solves."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters"))
from gaussian_population_oracle import ar1_population

MANIFEST = "runs/cycle_2/policy_pool_smoke_manifest.json"
SOURCE = "runs/cycle_2/policy_pool_common_smoke.json"
OUTPUT = ROOT / "runs/cycle_2/gaussian_population_audit_20260910.json"


def digest(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def audit():
    manifest = json.loads((ROOT / MANIFEST).read_bytes())
    source = json.loads((ROOT / SOURCE).read_bytes())
    if source["manifest_sha256"] != digest(MANIFEST):
        raise ValueError("archived result/manifest mismatch")
    for key, name in {
        "generators_sha256": "generators.py",
        "probe_sha256": "probes/policy_pool_common_smoke.py",
        "common_model_sha256": "adapters/common_model.py",
    }.items():
        if manifest[key] != digest(name):
            raise ValueError(f"archived source changed: {name}")
    grid = manifest["grid"]
    if (grid["T"], grid["paths_per_side"], grid["seed"], grid["shift"]) != (5, 128, 1000, 0.0):
        raise ValueError("scope differs from the manually reviewed generator/probe")
    population = ar1_population(grid["T"])
    value = population["aw2_squared"]
    rows = []
    for row in source["rows"]:
        if row["process"] != "ar1" or row["cost"] != "squared":
            continue
        finite = row["reference"]
        rows.append({"k": row["k"], "delta": row["delta"],
                     "finite_float64_dp_value": finite, "population_aw2_squared": value,
                     "signed_discrepancy": finite-value,
                     "finite_to_population_ratio": finite/value})
    if len(rows) != 4 or {(r["k"], r["delta"]) for r in rows} != {(k,d) for k in (1,2) for d in (0.5,0.18)}:
        raise ValueError("unexpected archived coverage")
    files = [MANIFEST, SOURCE, "generators.py", "adapters/common_model.py",
             "probes/policy_pool_common_smoke.py", "adapters/gaussian_population_oracle.py",
             "probes/gaussian_population_audit.py"]
    return {
        "schema": "gaussian-population-audit-v1", "date": "2026-09-10",
        "design": "posthoc diagnostic; source data existed before this question",
        "source_hashes": {name: digest(name) for name in files},
        "formula_source": "https://arxiv.org/html/2404.06625v4#S1.Thmtheorem1",
        "parameters": {"left": {"a": 0.7, "sigma": 1.0}, "right": {"a": 0.55, "sigma": 1.15},
                       "initial_state": 0, "cost": "sum squared differences over t=1..T"},
        "archived_coverage": {key: grid[key] for key in ("T", "paths_per_side", "seed", "shift")},
        "population_values": {str(T): ar1_population(T) for T in (5, 8, 50)},
        "rows": rows,
        "limits": ["True parameters enter audit only, never the paths-only candidate.",
                   "Finite-minus-population is one realized total pipeline discrepancy, not expected bias.",
                   "Sampling, quantization and window errors are not separated by this audit.",
                   "Population KR optimality does not certify the finite quantized model or SVD/NW policy.",
                   "Only T5 has archived comparisons here; T8/T50 are population formulas only.",
                   "Float64 formula evaluation is not an outward-rounded certificate; no absolute-cost or nonlinear-family oracle."],
        "decision": "retain finite solver target; use oracle as separate population diagnostic; no large grid or smoothing promotion",
    }


if __name__ == "__main__":
    result = audit()
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if OUTPUT.exists() and OUTPUT.read_text(encoding="utf-8") != payload:
        raise RuntimeError("existing audit differs; preserve history and create a new revision")
    if not OUTPUT.exists():
        OUTPUT.write_text(payload, encoding="utf-8")
    print(json.dumps({"population": {T: p["aw2_squared"] for T,p in result["population_values"].items()},
                      "rows": result["rows"]}, indent=2))
