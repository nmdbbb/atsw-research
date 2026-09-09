from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters"))
from monotone_reuse import optimal_face_reuse, support_miss_reuse
from common_model import _transport_value
from policy_pool_candidate import transport_plan_and_dual


class MonotoneReuseTests(unittest.TestCase):
    def witness(self, matrix):
        a = b = np.array([0.5, 0.5])
        _, plan, alpha, beta, _ = transport_plan_and_dual(a, b, matrix)
        return a, b, plan, alpha, beta

    def test_support_miss_reuses_exactly(self):
        matrix = np.array([[0.0, 3.0], [3.0, 0.0]])
        a, b, plan, alpha, beta = self.witness(matrix)
        delta = np.array([[0.0, 1.0], [2.0, 0.0]])
        result = support_miss_reuse(a, b, matrix, delta, plan, alpha, beta)
        self.assertTrue(result.reusable)
        self.assertAlmostEqual(result.value, 0.0)

    def test_optimal_face_repairs_hit_cached_plan(self):
        matrix = np.zeros((2, 2))
        a, b, plan, alpha, beta = self.witness(matrix)
        # Hit whichever degenerate optimum HiGHS selected; the opposite
        # permutation remains in the old optimal face.
        delta = (plan > 1e-12).astype(float)
        self.assertFalse(support_miss_reuse(
            a, b, matrix, delta, plan, alpha, beta).reusable)
        repaired = optimal_face_reuse(a, b, matrix, delta, plan, alpha, beta)
        self.assertTrue(repaired.reusable)
        self.assertAlmostEqual(repaired.value, 0.0)
        self.assertAlmostEqual(float(np.sum(repaired.plan * delta)), 0.0)

    def test_face_repair_falls_back_when_increase_is_unavoidable(self):
        matrix = np.zeros((2, 2))
        a, b, plan, alpha, beta = self.witness(matrix)
        delta = np.ones((2, 2))
        result = optimal_face_reuse(a, b, matrix, delta, plan, alpha, beta)
        self.assertFalse(result.reusable)

    def test_invalid_cached_witness_is_rejected(self):
        matrix = np.zeros((2, 2))
        a, b, plan, alpha, beta = self.witness(matrix)
        plan = plan.copy(); plan[0, 0] += 0.1
        with self.assertRaises(ValueError):
            support_miss_reuse(a, b, matrix, np.zeros((2, 2)),
                               plan, alpha, beta)

    def test_reuse_decisions_match_fresh_ot_on_random_fixtures(self):
        rng = np.random.default_rng(20260909)
        accepted = 0
        for _ in range(50):
            a = rng.dirichlet(np.ones(3))
            b = rng.dirichlet(np.ones(3))
            matrix = rng.integers(0, 4, size=(3, 3)).astype(float)
            _, plan, alpha, beta, _ = transport_plan_and_dual(a, b, matrix)
            delta = rng.integers(0, 2, size=(3, 3)).astype(float)
            result = optimal_face_reuse(a, b, matrix, delta,
                                        plan, alpha, beta)
            if result.reusable:
                accepted += 1
                self.assertAlmostEqual(result.value,
                                       _transport_value(a, b, matrix + delta),
                                       places=8)
        self.assertGreater(accepted, 0)


if __name__ == "__main__":
    unittest.main()
