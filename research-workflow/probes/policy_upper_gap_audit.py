"""Analyze existing smoke evidence; no solver calls or candidate access to V*.

For fixed U and any valid 0 < L <= V, (U-L)/L >= (U-V)/V.
The archived V is a float64 DP reference, so this audit is a numerical
development diagnostic, not an outward-rounded proof about the full domain.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "runs/cycle_2/policy_pool_common_smoke.json"
OUTPUT = ROOT / "runs/cycle_2/policy_upper_gap_audit_20260910.json"


def audit():
    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes)
    epsilon = json.loads((ROOT / "objective.json").read_text(encoding="utf-8"))["target"]["epsilon"]
    rows = []
    for row in source["rows"]:
        reference = row["reference"]
        levels = row["levels"]
        if reference <= 0 or not levels:
            raise ValueError("This diagnostic requires positive reference and observed levels")
        upper = levels[0]["upper"]
        if any(level["upper"] != upper for level in levels):
            raise ValueError("The fixed-upper premise does not hold across observed levels")
        if any(not level["lower"] <= reference <= upper for level in levels):
            raise ValueError("Recorded intervals do not contain their numerical reference")
        floor = (upper - reference) / reference
        rows.append({
            **{key: row[key] for key in ("process", "k", "delta", "cost")},
            "reference": reference,
            "fixed_upper": upper,
            "conditional_relative_width_floor": floor,
            "exceeds_target": floor > epsilon,
            "last_lower_relative_deficit": (reference - levels[-1]["lower"]) / reference,
        })
    floors = [row["conditional_relative_width_floor"] for row in rows]
    return {
        "id": "policy_upper_gap_audit_20260910",
        "scope": "posthoc_existing_T5_128path_smoke_only_no_new_solves",
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "objective_sha256": hashlib.sha256((ROOT / "objective.json").read_bytes()).hexdigest(),
        "reference_kind": "float64_DP_not_outward_rounded",
        "formula": "For fixed U and valid 0<L<=V, (U-L)/L >= (U-V)/V",
        "epsilon": epsilon,
        "cases": len(rows),
        "fixed_upper_exceeds_target_cases": sum(row["exceeds_target"] for row in rows),
        "floor_min": min(floors),
        "floor_median": statistics.median(floors),
        "floor_max": max(floors),
        "decision": "Defer lower-only reuse engineering on this incumbent; a feasible-upper improvement route is required first.",
        "limits": [
            "No general impossibility result for interval reuse or other policies.",
            "The floor treats the numerical reference as V; it is not a rigorous numerical enclosure.",
            "No hypothesis registration, new performance run or SOTA claim.",
        ],
        "rows": rows,
    }


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2))
