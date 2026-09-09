from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters"))

import policy_pool_candidate as candidate  # noqa: E402
from common_model import build_window_model, exact_dp  # noqa: E402


class PolicyPoolCandidateTests(unittest.TestCase):
    def setUp(self):
        self.left_paths = np.array([
            [-1.0, -0.5, 0.0, 0.5],
            [-1.0, 0.5, 0.5, 1.0],
            [1.0, 0.5, 0.0, -0.5],
            [1.0, 1.5, 1.0, 0.5],
        ])
        self.right_paths = np.array([
            [-1.0, -0.5, 0.5, 1.0],
            [-1.0, 0.5, 0.0, -0.5],
            [1.0, 0.5, 1.0, 1.5],
            [1.0, 1.5, 0.5, 0.0],
        ])

    def test_sparse_support_dual_is_globally_feasible(self):
        matrix = np.array([[0.2, 3.0, 1.0], [2.0, 0.1, 4.0], [1.5, 2.0, 0.3]])
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([0.0, 0.25, 0.75])
        primal, plan, alpha, beta, dual = candidate.transport_plan_and_dual(a, b, matrix)
        self.assertLessEqual(float(np.max(alpha[:, None] + beta[None, :] - matrix)), 0.0)
        self.assertLessEqual(dual, primal + 1e-12)
        np.testing.assert_allclose(plan.sum(1), a)
        np.testing.assert_allclose(plan.sum(0), b)

    def test_full_pair_budget_recovers_reference_for_both_k_and_costs(self):
        for k in (1, 2):
            left = build_window_model(self.left_paths, k=k, delta=0.5, shift=0.0)
            right = build_window_model(self.right_paths, k=k, delta=0.5, shift=0.0)
            budget = max(len(left.states[t]) * len(right.states[t])
                         for t in range(left.horizon))
            for cost in ("squared", "absolute"):
                reference = exact_dp(left, right, cost)
                result = candidate.solve_model(left, right, cost, budgets=(budget,))
                level = result["levels"][0]
                self.assertLessEqual(level["lower"], reference + 1e-8)
                self.assertLessEqual(reference, level["upper"] + 1e-8)
                self.assertAlmostEqual(level["lower"], reference, places=8)
                self.assertLessEqual(level["root_dual_feasibility_violation"], 0.0)

    def test_from_paths_runs_all_frozen_shifts(self):
        result = candidate.solve_from_paths(
            self.left_paths, self.right_paths, k=2, delta=0.5,
            cost="absolute", budgets=(0,), shifts=None)
        self.assertEqual([r["shift"] for r in result["shifts"]], [0.0, 0.1667, 0.3333])
        self.assertEqual(len(result["aggregate_levels"]), 1)
        self.assertGreater(result["outer_wall_seconds"], 0.0)
        self.assertEqual(result["timing_boundary"],
                         "from_paths_including_all_requested_shifts_and_warmup_levels")


if __name__ == "__main__":
    unittest.main()
