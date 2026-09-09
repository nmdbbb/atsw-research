"""Independent small correctness audit; development evidence, not a benchmark.

The feasibility oracle enumerates rational Hall inequalities, not an LP.
The reviewed adapter treats each supplied binary64 number as an exact rational.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import importlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters"))


def q(x):
    return Fraction(float(x))


def hall_feasible(a, b, allowed):
    """Exact capacitated bipartite feasibility, all row subsets (tiny only)."""
    aa, bb = list(map(q, a)), list(map(q, b))
    if sum(aa) != sum(bb):
        return False
    for mask in range(1 << len(a)):
        rows = [i for i in range(len(a)) if mask & (1 << i)]
        cols = [j for j in range(len(b)) if any(allowed[i, j] for i in rows)]
        if sum(aa[i] for i in rows) > sum(bb[j] for j in cols):
            return False
    return True


def audit_plan(result, a, b, matrix, delta, value):
    assert result.reusable
    p = [[q(x) for x in row] for row in result.plan]
    assert all(x >= 0 for row in p for x in row)
    assert [sum(row) for row in p] == list(map(q, a))
    assert [sum(p[i][j] for i in range(len(a))) for j in range(len(b))] == list(map(q, b))
    actual = sum(p[i][j] * (q(matrix[i, j]) + q(delta[i, j]))
                 for i in range(len(a)) for j in range(len(b)))
    assert actual == value == result.value


def main():
    module_name = sys.argv[1] if len(sys.argv) > 1 else "monotone_reuse_reviewed"
    new = importlib.import_module(module_name)
    old = importlib.import_module("monotone_reuse")
    from policy_pool_candidate import transport_plan_and_dual

    report = {"purpose": "independent local correctness and compatibility gate",
              "registration": "unregistered development audit; no speed or SOTA claim",
              "module": module_name,
              "module_sha256": hashlib.sha256(Path(new.__file__).read_bytes()).hexdigest(),
              "oracle": "exact Fraction arithmetic and exhaustive rational Hall inequalities"}
    a = b = np.array([0.5, 0.5])
    matrix = np.zeros((2, 2))
    plan = np.diag(a)
    alpha = beta = np.zeros(2)

    # Positive updates, however tiny, cannot be called exactly zero.
    tiny = np.full((2, 2), 5e-11)
    tiny_results = {}
    for name in ("support_miss_reuse", "optimal_face_reuse"):
        result = getattr(new, name)(a, b, matrix, tiny, plan, alpha, beta)
        assert not result.reusable
        tiny_results[name] = {"old_false_acceptance": bool(getattr(old, name)(
            a, b, matrix, tiny, plan, alpha, beta).reusable), "reviewed_rejected": True}
    report["positive_tiny_update"] = tiny_results

    # Dyadic version isolates residual tolerance from unequal exact mass totals.
    mass = 2.0 ** -27
    aa = np.array([mass, 1.0 - mass])
    pp = np.array([[mass, 0.0], [0.5 - mass, 0.5]])
    delta = np.array([[1.0, 1.0], [0.0, 0.0]])
    result = new.optimal_face_reuse(aa, b, matrix, delta, pp, alpha, beta)
    assert not result.reusable
    original = old.optimal_face_reuse(aa, b, matrix, delta, pp, alpha, beta)
    report["dyadic_unavoidable_small_mass"] = {
        "exact_updated_value": str(q(mass)),
        "old_false_acceptance": bool(original.reusable),
        "reviewed_rejected": True, "reason": result.reason}

    rng = np.random.default_rng(721909)
    decisions = Counter()
    for _ in range(64):
        aa = rng.multinomial(16, [1/3] * 3) / 16
        bb = rng.multinomial(16, [1/3] * 3) / 16
        al = rng.integers(-3, 4, 3).astype(float)
        be = rng.integers(-3, 4, 3).astype(float)
        mm = al[:, None] + be[None, :]
        dd = rng.integers(0, 2, (3, 3)).astype(float)
        pp = np.outer(aa, bb)
        expected = hall_feasible(aa, bb, dd == 0)
        result = new.optimal_face_reuse(aa, bb, mm, dd, pp, al, be)
        if result.reusable:
            assert expected, "false acceptance against exact Hall oracle"
            value = sum(q(x) * q(y) for x, y in zip(aa, al)) + sum(
                q(x) * q(y) for x, y in zip(bb, be))
            audit_plan(result, aa, bb, mm, dd, value)
        decisions["true_accept" if expected and result.reusable else
                  "safe_false_reject" if expected else "true_reject"] += 1
    report["dyadic_additive_cost_hall_screen"] = dict(decisions)

    unique_matrix = np.array([[0.0, 1.0], [1.0, 0.0]])
    unique_delta = np.eye(2)
    assert not new.optimal_face_reuse(a, b, unique_matrix, unique_delta,
                                     plan, alpha, beta).reusable
    report["unique_optimum_support_hit"] = "correctly rejected"

    # Isolate strictly suboptimal upstream duals with exactly feasible masses.
    _, pp, al, be, _ = transport_plan_and_dual(a, b, matrix)
    gap = sum(q(pp[i, j]) * q(matrix[i, j]) for i in range(2) for j in range(2)) - (
        sum(q(x) * q(y) for x, y in zip(a, al)) + sum(q(x) * q(y) for x, y in zip(b, be)))
    assert gap > 0
    result = new.optimal_face_reuse(a, b, matrix, matrix, pp, al, be)
    assert not result.reusable
    report["upstream_dual_guard_only"] = {"exact_gap": str(gap), "rejected": True,
                                           "reason": result.reason}

    # Independent exact total mass compatibility; no LP is required here.
    mass_equal = 0
    for _ in range(64):
        aa = rng.dirichlet(np.ones(3))
        bb = rng.dirichlet(np.ones(3))
        mass_equal += sum(map(q, aa)) == sum(map(q, bb))
    report["ordinary_float_mass_screen"] = {
        "cases": 64, "exact_equal_total_mass": mass_equal,
        "exact_unequal_total_mass": 64 - mass_equal,
        "interpretation": "Unequal binary64 totals make the exact-input transport problem infeasible; numerical normalization does not silently change this target."}
    report["verdict"] = "pass_local_exact_fixture_gate_only; revise_before_controller_promotion"
    report["limits"] = ["Not a root certificate or population guarantee",
                        "Does not establish completeness on all floating solver outputs",
                        "Current upstream guarded duals are incompatible even with dyadic masses",
                        "No timing/work advantage measured; no broad float transport adapter built"]
    target = ROOT / "runs/cycle_2/hd02_review/verification.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
