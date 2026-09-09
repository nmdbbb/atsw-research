"""Independent analytic target checks; no archive or benchmark imports."""

from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapters.common_model import build_window_model, exact_dp, stage_cost


def model(paths, k=1):
    # Integer-valued paths remain exactly at their cell representatives.
    return build_window_model(paths, k=k, delta=1.0, shift=0.5)


class CommonModelTests(unittest.TestCase):
    def test_imported_root_counterexample_both_memories_and_costs(self):
        x = [[0, 0, 0], [0, 0, 0], [0, 2, 0]]
        y = np.zeros((3, 3))
        for k in (1, 2):
            left, right = model(x, k), model(y, k)
            self.assertEqual(left.horizon, 2)
            self.assertEqual(len(left.representatives), 3)
            self.assertAlmostEqual(exact_dp(left, right), 4 / 3)
            self.assertAlmostEqual(exact_dp(left, right, 'absolute'), 2 / 3)

    def test_non_degenerate_initial_law_requires_root_transport(self):
        left = model([[0, 0], [0, 0], [0, 0], [1, 2]], k=2)
        right = model([[0, 0], [1, 2], [1, 2], [1, 2]], k=2)
        np.testing.assert_allclose(left.initial, [0.75, 0.25])
        np.testing.assert_allclose(right.initial, [0.25, 0.75])
        # Half the mass necessarily crosses between final values 0 and 2.
        self.assertAlmostEqual(exact_dp(left, right), 2.0)
        self.assertAlmostEqual(exact_dp(left, right, 'absolute'), 1.0)

    def test_initial_coupling_can_cross_and_initial_cost_is_excluded(self):
        left = model([[-10, -2], [10, 2]], k=2)
        right = model([[-100, 2], [100, -2]], k=2)
        # Cross-coupling initial labels aligns both future values at zero cost.
        for cost in ('squared', 'absolute'):
            self.assertAlmostEqual(exact_dp(left, right, cost), 0.0)
            self.assertAlmostEqual(exact_dp(model([[10, 0]]),
                                           model([[100, 0]]), cost), 0.0)

    def test_single_transition_is_not_dropped(self):
        for k in (1, 2, 5):
            left, right = model([[0, 0], [0, 2]], k), model([[0, 0]], k)
            self.assertEqual(left.horizon, 1)
            self.assertAlmostEqual(exact_dp(left, right), 2.0)
            self.assertAlmostEqual(exact_dp(left, right, 'absolute'), 1.0)

    def test_true_second_order_information_changes_distance(self):
        # Time two merges current values. Its previous value predicts time
        # three. First-order models forget this signal; second-order retains it.
        x = [[0, -1, 0, -1], [0, 1, 0, 1]]
        y = [[0, -1, 0, 1], [0, 1, 0, -1]]
        self.assertAlmostEqual(exact_dp(model(x, 1), model(y, 1)), 0.0)
        self.assertAlmostEqual(exact_dp(model(x, 2), model(y, 2)), 4.0)
        self.assertAlmostEqual(exact_dp(model(x, 2), model(y, 2), 'absolute'), 2.0)
        # k>=all available history gives the same full-history value here.
        self.assertAlmostEqual(exact_dp(model(x, 4), model(y, 4)), 4.0)

    def test_window_support_and_current_output(self):
        built = model([[0, -1, 0, 1], [0, 1, 0, -1]], 2)
        for t, transition in enumerate(built.kernels):
            np.testing.assert_allclose(transition.sum(axis=1), 1)
            for i, j in np.argwhere(transition > 0):
                self.assertEqual(built.states[t][i, -1],
                                 built.states[t + 1][j, 0])
        np.testing.assert_array_equal(built.representatives[2], [0, 0])
        np.testing.assert_array_equal(stage_cost([0, 2], [1], 'absolute'), [[1], [1]])

    def test_model_hash_and_invalid_inputs(self):
        built = model([[0, 1], [0, 2]], 2)
        reordered = model([[0, 2], [0, 1]], 2)
        self.assertEqual(built.model_hash, reordered.model_hash)
        self.assertNotEqual(built.model_hash, model([[0, 1], [0, 2]], 1).model_hash)
        for invalid in ([], [[float('nan'), 0]]):
            with self.assertRaises(ValueError):
                build_window_model(invalid)
        for k in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                build_window_model([[0, 1]], k=k)
        with self.assertRaises(ValueError):
            exact_dp(model([[0, 1]]), model([[0, 1, 2]]))
        with self.assertRaises(ValueError):
            build_window_model([[0, 1]], delta=0)


if __name__ == '__main__':
    unittest.main()
