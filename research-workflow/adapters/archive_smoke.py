"""Tiny import/integration smoke for the historical k=1 baseline only.

Declared before execution: T=2, 24 paths/side, seed123, delta2/shift0;
independent exact LP DP is used only to audit numerical interval containment
within 1e-9. No timing comparison, SOTA, general correctness or rigorous
floating-point certification is inferred. k=2 is excluded from this smoke
because its imported representation has a reproduced target bug, not from
the research objective. Do not execute any archive __main__ benchmark.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "inputs/atsw_repo"


def main():
    sys.path[:0] = [str(ARCHIVE / x) for x in ("algo", "certify", "probes")]
    import numpy as np
    import ot
    import scipy
    import kmarkov_driver as kd
    import run_all_cells as solver

    rng = np.random.default_rng(123)
    xa = kd.gen_paths(2, 24, rng, a=0.7)
    xb = kd.gen_paths(2, 24, rng, a=0.55, sigma=1.15)
    _, ra, ka = kd.build(xa, 2.0, 0.0)
    _, rb, kb = kd.build(xb, 2.0, 0.0)
    reference = kd.dp(ra, ka, rb, kb, kd.solve_lp)[0]
    result = solver.certified_solve(ra, ka, rb, kb, schedule=[(0.0, 4)])
    passed = result["L0"] <= reference + 1e-9 and reference <= result["U0"] + 1e-9
    report = {
        "kind": "small_k1_integration_smoke_not_benchmark",
        "status": "PASS" if passed else "FAIL",
        "T": 2, "paths": 24, "seed": 123, "delta": 2.0,
        "reference": reference, "result": result,
        "numpy_version": np.__version__, "scipy_version": scipy.__version__, "pot_version": ot.__version__,
        "source_sha256": hashlib.sha256((ARCHIVE / "certify/run_all_cells.py").read_bytes()).hexdigest(),
        "smoke_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "interpretation": "Only numerical interval containment and import integration checked. Target bug in k2 remains unresolved."
    }
    out = ROOT / "runs/cycle_0/archive_smoke.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
