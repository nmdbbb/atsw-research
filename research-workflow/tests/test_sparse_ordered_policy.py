from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters"))

from common_model import build_window_model, stage_cost
from policy_pool_candidate import _ordered_policy, _orders, evaluate_policy, Counters
from sparse_ordered_policy import prepare_layer


class SparseOrderedPolicyTests(unittest.TestCase):
    def assert_matches(self, a, b, matrix, orders=None):
        if orders is None:
            orders = _orders(matrix)
        reference_value, reference_plan = _ordered_policy(a, b, matrix, orders)
        layer = prepare_layer(matrix, [a], [b], orders)
        result = layer.evaluate(0, 0)
        actual = np.zeros_like(matrix)
        np.add.at(actual, (result.rows, result.cols), result.masses)
        np.testing.assert_allclose(actual.sum(1), a / np.sum(a), atol=2e-12)
        np.testing.assert_allclose(actual.sum(0), b / np.sum(b), atol=2e-12)
        np.testing.assert_allclose(result.value, reference_value, rtol=2e-12, atol=2e-12)
        np.testing.assert_allclose(actual, reference_plan, rtol=2e-12, atol=2e-12)
        self.assertTrue(np.all(result.masses > 0))
        self.assertLessEqual(len(result.masses), np.count_nonzero(a) + np.count_nonzero(b) - 1)
        self.assertLessEqual(result.counts["nw_steps"], 2 * (np.count_nonzero(a) + np.count_nonzero(b) - 1))
        self.assertEqual(result.counts["cost_entries_read"], result.counts["emitted_edges"])
        self.assertEqual(result.counts["dense_plan_entries_allocated"], 0)
        return result

    def test_random_zero_rich_marginals(self):
        rng = np.random.default_rng(712)
        for _ in range(60):
            n, m = rng.integers(2, 35, size=2)
            matrix = rng.uniform(0, 10, size=(n, m))
            a, b = rng.random(n), rng.random(m)
            a[rng.random(n) < .8] = 0
            b[rng.random(m) < .8] = 0
            a[rng.integers(n)] += .1
            b[rng.integers(m)] += .1
            self.assert_matches(a, b, matrix)

    def test_ties_keep_first_orientation(self):
        # Binary-exact masses keep the equal-objective tie exact in both codes.
        a, b = np.array([.25, 0, .75]), np.array([.5, .25, 0, .25])
        orders = (np.array([2, 0, 1]), np.array([3, 1, 2, 0]), np.array([0, 2, 1, 3]))
        for matrix in (np.zeros((3, 4)), np.full((3, 4), 2.),
                       np.arange(3.)[:, None] + np.arange(4.)[None, :]):
            self.assert_matches(a, b, matrix, orders)

    def test_tiny_positive_mass_is_not_pruned(self):
        a = np.array([1e-20, .25, .75])
        b = np.array([.5, .5])
        orders = (np.arange(3), np.arange(2), np.arange(2)[::-1])
        result = self.assert_matches(a, b, np.ones((3, 2)), orders)
        np.testing.assert_allclose(result.masses[result.rows == 0].sum(), 1e-20,
                                   rtol=1e-15, atol=0)

    def test_singleton_and_preparation_counts(self):
        matrix = np.arange(300., dtype=float).reshape(20, 15)
        a, b = np.eye(20)[7], np.eye(15)[11]
        layer = prepare_layer(matrix, [a, a], [b])
        self.assertEqual(layer.counts["marginal_entries_scanned"], 55)
        self.assertEqual(layer.counts["positive_entries_sorted"], 3)
        self.assertEqual(layer.counts["matrix_entries_validated"], 300)
        result = layer.evaluate(1, 0)
        self.assertEqual(result.value, matrix[7, 11])
        self.assertEqual(result.counts["nw_steps"], 2)
        self.assertEqual(result.counts["cost_entries_read"], 2)

    def test_invalid_inputs_and_orders_rejected(self):
        matrix = np.ones((2, 2))
        for bad in ([np.nan, 1], [np.inf, 1], [-1e-30, 1], [0, 0], [1]):
            with self.assertRaises(ValueError):
                prepare_layer(matrix, [bad], [[.5, .5]])
        for bad in (np.array([[np.nan]]), np.array([[np.inf]]), np.array([[-1e-30]])):
            with self.assertRaises(ValueError):
                prepare_layer(bad, [[1]], [[1]])
        with self.assertRaises(ValueError):
            prepare_layer(matrix, [[1, 1]], [[1, 1]], ([0, 0], [0, 1], [1, 0]))
        with self.assertRaises(ValueError):
            prepare_layer(matrix, [[1, 1]], [[1, 1]], ([0, 1], [0, 1], [0, 1]))

    def test_backward_policy_and_nontrivial_root(self):
        x = np.array([[-1, -.5, 0, .5], [-1, .5, .5, 1],
                      [1, .5, 0, -.5], [1, 1.5, 1, .5]], dtype=float)
        y = np.array([[-1, -.5, .5, 1], [-1, .5, 0, -.5],
                      [1, .5, 1, 1.5], [1, 1.5, .5, 0]], dtype=float)
        for k in (1, 2):
            left = build_window_model(x, k=k, delta=.5, shift=0.)
            right = build_window_model(y, k=k, delta=.5, shift=0.)
            self.assertGreater(np.count_nonzero(left.initial), 1)
            for cost in ("absolute", "squared"):
                expected, _, reference_tables = evaluate_policy(left, right, cost, Counters())
                values = [None] * (left.horizon + 1)
                values[-1] = np.zeros_like(reference_tables[-1])
                for t in range(left.horizon - 1, -1, -1):
                    matrix = stage_cost(left.representatives[t + 1], right.representatives[t + 1], cost) + values[t + 1]
                    layer = prepare_layer(matrix, left.kernels[t], right.kernels[t])
                    values[t] = np.array([[layer.evaluate(i, j).value
                                           for j in range(len(right.kernels[t]))]
                                          for i in range(len(left.kernels[t]))])
                    np.testing.assert_allclose(values[t], reference_tables[t], atol=2e-12)
                result = self.assert_matches(left.initial, right.initial, values[0])
                np.testing.assert_allclose(result.value, expected, atol=2e-12)


if __name__ == "__main__":
    unittest.main()
