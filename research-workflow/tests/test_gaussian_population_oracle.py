from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "adapters"))
from gaussian_population_oracle import ar1_factor, ar1_population, gaussian_aw2_from_factors


class GaussianPopulationTests(unittest.TestCase):
    def test_one_step_and_mean_cost(self):
        result = gaussian_aw2_from_factors([[2]], [[3]], [1], [4])
        self.assertEqual(result["aw2_squared"], 10)
        self.assertEqual(result["kr_gap"], 0)

    def test_identical_laws_and_nonstationary_start(self):
        factor = ar1_factor(5, 0.7, 1.0)
        self.assertEqual((factor @ factor.T)[0, 0], 1.0)
        self.assertEqual(gaussian_aw2_from_factors(factor, factor)["aw2_squared"], 0)
        self.assertTrue(np.allclose(np.diag(factor @ factor.T),
                                    [sum(0.7**(2*j) for j in range(t)) for t in range(1, 6)]))

    def test_negative_column_gap_and_sign_flip_coupling(self):
        left = np.array([[1., 0.], [2., 1.]])
        right = np.array([[1., 0.], [-2., 1.]])
        result = gaussian_aw2_from_factors(left, right)
        self.assertEqual(result["aw2_squared"], 4)
        self.assertEqual(result["kr_squared"], 16)
        self.assertEqual(result["kr_gap"], 12)
        self.assertFalse(result["kr_is_optimal_by_sign_condition"])

    def test_ar1_independent_synchronous_recursion(self):
        # Independent variance/covariance recursion under common innovations.
        vx = vy = cov = total = 0.0
        for _ in range(50):
            vx = 0.7**2 * vx + 1
            vy = 0.55**2 * vy + 1.15**2
            cov = 0.7*0.55*cov + 1.15
            total += vx + vy - 2*cov
        result = ar1_population(50)
        self.assertAlmostEqual(result["aw2_squared"], total, places=11)
        self.assertEqual(result["kr_gap"], 0)

    def test_invalid_factor_and_horizon(self):
        for T in (0, True, 1.5):
            with self.assertRaises(ValueError): ar1_factor(T, 0.7, 1)
        for matrix in ([[0]], [[float("nan")]], [[1, 1], [0, 1]]):
            with self.assertRaises(ValueError): gaussian_aw2_from_factors(matrix, matrix)


if __name__ == "__main__":
    unittest.main()
