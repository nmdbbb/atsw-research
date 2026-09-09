"""Analytic adversarial checks, independent of floating OT objective agreement."""
from fractions import Fraction
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "adapters"))
from monotone_reuse_reviewed import optimal_face_reuse, support_miss_reuse


class ReviewedReuseTests(unittest.TestCase):
    def fixture(self):
        return [np.array([.5, .5]), np.array([.5, .5]),
                np.zeros((2, 2)), np.zeros((2, 2)), np.diag([.5, .5]),
                np.zeros(2), np.zeros(2)]

    def test_support_miss_exact_fraction(self):
        args = self.fixture()
        args[2] = np.array([[.125, 3.0], [3.0, .25]])
        args[3] = np.array([[0., 1.], [1., 0.]])
        args[5] = np.array([.125, .25])
        result = support_miss_reuse(*args)
        self.assertTrue(result.reusable)
        self.assertEqual(result.value, Fraction(3, 16))
        self.assertIsInstance(result.value, Fraction)
        self.assertEqual(result.work.witness_edge_visits, 8)

    def test_face_repairs_degenerate_optimum(self):
        args = self.fixture()
        args[3] = np.eye(2)
        self.assertFalse(support_miss_reuse(*args).reusable)
        result = optimal_face_reuse(*args)
        self.assertTrue(result.reusable)
        np.testing.assert_array_equal(result.plan, [[0., .5], [.5, 0.]])
        self.assertEqual(result.work.face_edge_visits, 4)
        self.assertEqual(result.work.witness_edge_visits, 8)
        self.assertEqual(result.work.feasibility_variables, 2)
        self.assertEqual(result.work.feasibility_lp_calls, 1)
        self.assertEqual(result.work.feasibility_nonzeros, 4)
        self.assertEqual(result.work.rational_conversions, 24)
        self.assertEqual(result.tested_edges, 12)

    def test_original_decimal_small_mass_rejects(self):
        args = self.fixture()
        args[0] = np.array([1e-8, 1 - 1e-8])
        args[4] = np.array([[1e-8, 0.], [.5 - 1e-8, .5]])
        args[3] = np.array([[1., 1.], [0., 0.]])
        for fn in (support_miss_reuse, optimal_face_reuse):
            self.assertFalse(fn(*args).reusable)

    def test_dyadic_small_mass_cannot_be_dropped(self):
        args = self.fixture()
        small = 2. ** -27
        args[0] = np.array([small, 1 - small])
        args[4] = np.array([[small, 0.], [.5 - small, .5]])
        args[3] = np.array([[1., 1.], [0., 0.]])
        self.assertFalse(support_miss_reuse(*args).reusable)
        result = optimal_face_reuse(*args)
        self.assertFalse(result.reusable)
        self.assertEqual(result.work.feasibility_lp_calls, 1)
        # Independent bound: any feasible plan pays exactly 'small'.
        self.assertGreater(Fraction.from_float(small), 0)

    def test_forged_solver_success_requires_full_marginals(self):
        args = self.fixture()
        args[3] = np.eye(2)
        with patch("monotone_reuse_reviewed.linprog",
                   return_value=SimpleNamespace(success=True, x=np.array([0., .5]))):
            result = optimal_face_reuse(*args)
        self.assertFalse(result.reusable)
        self.assertIn("primal feasibility", result.reason)

    def test_every_positive_increment_including_subnormal_rejects(self):
        for tiny in (5e-11, np.nextafter(0., 1.)):
            args = self.fixture()
            args[3].fill(tiny)
            for fn in (support_miss_reuse, optimal_face_reuse):
                self.assertFalse(fn(*args).reusable)

    def test_negative_tiny_update_is_invalid(self):
        args = self.fixture()
        args[3][0, 0] = -np.nextafter(0., 1.)
        for fn in (support_miss_reuse, optimal_face_reuse):
            with self.assertRaises(ValueError):
                fn(*args)

    def test_near_tight_positive_reduced_cost_cannot_repair(self):
        args = self.fixture()
        args[2] = np.array([[0., 5e-11], [5e-11, 0.]])
        args[3] = np.eye(2)
        result = optimal_face_reuse(*args)
        self.assertFalse(result.reusable)
        self.assertEqual(result.work.feasibility_lp_calls, 0)
        self.assertEqual(result.tested_edges, 8)

    def test_nonfinite_each_input_is_invalid(self):
        for index in range(7):
            for bad in (np.nan, np.inf, -np.inf):
                args = self.fixture()
                args[index].flat[0] = bad
                with self.subTest(index=index, bad=bad):
                    for fn in (support_miss_reuse, optimal_face_reuse):
                        with self.assertRaises(ValueError):
                            fn(*args)

    def test_negative_marginal_or_plan_is_invalid(self):
        for index in (0, 1, 4):
            args = self.fixture()
            args[index].flat[0] = -1e-20
            with self.assertRaises(ValueError):
                optimal_face_reuse(*args)

    def test_wrong_dual_shape_is_invalid(self):
        args = self.fixture()
        args[5] = np.zeros(1)
        with self.assertRaises(ValueError):
            optimal_face_reuse(*args)

    def test_infeasible_or_suboptimal_cached_dual_rejects(self):
        for offset in (-np.nextafter(0., 1.), np.nextafter(0., 1.)):
            args = self.fixture()
            args[5][0] = offset
            result = optimal_face_reuse(*args)
            self.assertFalse(result.reusable)
            self.assertEqual(result.work.feasibility_lp_calls, 0)

    def test_zero_mass_rows_and_zero_total(self):
        args = self.fixture()
        args[0] = np.array([0., 1.])
        args[4] = np.array([[0., 0.], [.5, .5]])
        self.assertTrue(optimal_face_reuse(*args).reusable)
        args[0].fill(0.)
        args[1].fill(0.)
        args[4].fill(0.)
        args[3].fill(1.)
        result = optimal_face_reuse(*args)
        self.assertTrue(result.reusable)
        self.assertEqual(result.value, Fraction(0))
        self.assertEqual(result.work.feasibility_lp_calls, 0)


if __name__ == "__main__":
    unittest.main()
