"""Correctness fixtures for the H_C01 active-subsolution formulation."""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "adapters"))
from common_model import build_window_model, exact_dp
from global_subsolution import (
    future_marginal_subsolution,
    solve_active_subsolution, solve_clamped_subsolution,
    verify_subsolution, zero_subsolution,
)


def model(paths, k=1):
    return build_window_model(paths, k=k, delta=1.0, shift=0.5)


class GlobalSubsolutionTests(unittest.TestCase):
    def fixtures(self):
        yield (model([[0, 0, 0], [0, 2, 0], [1, 0, 2]], 1),
               model([[0, 2, 0], [1, 0, 0], [1, 2, 2]], 1))
        yield (model([[0, -1, 0, -1], [0, 1, 0, 1]], 2),
               model([[0, -1, 0, 1], [0, 1, 0, -1]], 2))

    def test_zero_is_subsolution_for_registered_costs(self):
        for left, right in self.fixtures():
            for cost in ("squared", "absolute"):
                ok, audit = verify_subsolution(
                    left, right, cost, zero_subsolution(left, right))
                self.assertTrue(ok, audit)

    def test_all_active_recovers_exact_dp(self):
        for left, right in self.fixtures():
            for cost in ("squared", "absolute"):
                result = solve_active_subsolution(left, right, cost)
                self.assertAlmostEqual(result.lower, exact_dp(left, right, cost), places=7)
                self.assertEqual(result.work.inactive_pair_nodes, 0)
                self.assertGreater(result.work.successor_constraints, 0)

    def test_partial_activity_stays_below_exact(self):
        for left, right in self.fixtures():
            masks = []
            for t in range(left.horizon):
                mask = np.zeros((len(left.states[t]), len(right.states[t])), dtype=bool)
                mask.flat[0] = True
                masks.append(mask)
            for cost in ("squared", "absolute"):
                result = solve_active_subsolution(left, right, cost, active=masks)
                self.assertLessEqual(result.lower, exact_dp(left, right, cost) + 1e-8)
                self.assertGreater(result.work.inactive_pair_nodes, 0)

    def test_global_lp_equals_same_active_same_h_clamped_dp(self):
        for left, right in self.fixtures():
            masks = []
            for t in range(left.horizon):
                ii, jj = np.indices((len(left.states[t]), len(right.states[t])))
                masks.append((ii + 2 * jj + t) % 3 == 0)
            for cost in ("squared", "absolute"):
                global_result = solve_active_subsolution(
                    left, right, cost, active=masks)
                clamped = solve_clamped_subsolution(
                    left, right, cost, active=masks)
                self.assertAlmostEqual(global_result.lower, clamped.lower, places=7)
                self.assertEqual(global_result.work.active_pair_nodes,
                                 clamped.work.active_pair_nodes)
                self.assertEqual(global_result.work.successor_constraints,
                                 clamped.work.successor_cost_entries)

    def test_future_marginal_cost_is_valid_and_monotone_in_depth(self):
        for left, right in self.fixtures():
            for cost in ("squared", "absolute"):
                previous = zero_subsolution(left, right)
                for depth in (1, 2, 3):
                    h, work = future_marginal_subsolution(
                        left, right, cost, depth)
                    ok, audit = verify_subsolution(left, right, cost, h)
                    self.assertTrue(ok, audit)
                    for old, new in zip(previous, h):
                        self.assertTrue(np.all(new >= old - 1e-12))
                    self.assertGreater(work["one_time_transport_calls"], 0)
                    previous = h

    def test_terminal_baseline_is_enforced(self):
        left, right = next(self.fixtures())
        malformed = list(zero_subsolution(left, right))
        malformed[-1][...] = 1.0
        with self.assertRaises(ValueError):
            solve_active_subsolution(left, right, h=malformed)
        with self.assertRaises(ValueError):
            solve_clamped_subsolution(left, right, h=malformed)

    def test_delayed_alternative_defeats_occupation_mask_even_with_h2(self):
        e = 1 / 8
        left = build_window_model([[0, 0, 0, 0], [e, e, e, 2]],
                                  k=1, delta=e, shift=e / 2)
        right = build_window_model([[0, 0, 0, 1], [e, e, e, 3]],
                                   k=1, delta=e, shift=e / 2)
        active = [np.eye(2, dtype=bool) for _ in range(3)]
        for cost, expected in (("absolute", 0.25), ("squared", 0.03125)):
            h, _ = future_marginal_subsolution(left, right, cost, 2)
            global_result = solve_active_subsolution(left, right, cost, h, active)
            clamped = solve_clamped_subsolution(left, right, cost, h, active)
            self.assertAlmostEqual(exact_dp(left, right, cost), 1.0)
            self.assertAlmostEqual(global_result.lower, expected)
            self.assertAlmostEqual(global_result.lower, clamped.lower)

    def test_dummy_root_handles_non_dirac_initial_laws(self):
        left = model([[0, 0], [0, 0], [0, 0], [1, 2]], 2)
        right = model([[0, 0], [1, 2], [1, 2], [1, 2]], 2)
        for cost, expected in (("squared", 2.0), ("absolute", 1.0)):
            result = solve_active_subsolution(left, right, cost)
            self.assertAlmostEqual(result.lower, expected, places=7)
            self.assertEqual(result.work.root_constraints, 5)

    def test_inactive_nodes_do_not_delete_successor_alternatives(self):
        left, right = next(self.fixtures())
        masks = [np.ones((len(left.states[t]), len(right.states[t])), dtype=bool)
                 for t in range(left.horizon)]
        masks[-1][...] = False
        result = solve_active_subsolution(left, right, "absolute", active=masks)
        exact = exact_dp(left, right, "absolute")
        self.assertLessEqual(result.lower, exact + 1e-8)
        # Active parents still instantiate every positive-support cross arc.
        expected = 0
        for t in range(left.horizon):
            for i, j in np.argwhere(masks[t]):
                expected += int(np.count_nonzero(left.kernels[t][i]) *
                                np.count_nonzero(right.kernels[t][j]))
        self.assertEqual(result.work.successor_constraints, expected)


if __name__ == "__main__":
    unittest.main()
