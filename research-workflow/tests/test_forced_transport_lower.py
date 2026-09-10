import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"adapters"))
from forced_transport_lower import forced_values
from policy_pool_candidate import transport_plan_and_dual, free_lower


class ForcedTransportTests(unittest.TestCase):
    def test_both_orientations_against_lp(self):
        rng=np.random.default_rng(2910)
        for _ in range(12):
            M=rng.uniform(0,20,(3,4))
            A=np.array([[0,2,0],rng.uniform(0.1,1,3)])
            B=np.array([[0,0,3,0],rng.uniform(0.1,1,4)])
            mask,values,counts=forced_values(M,A,B)
            np.testing.assert_array_equal(mask,[[True,True],[True,False]])
            self.assertEqual(counts['forced_pairs'],3)
            for i,j in np.argwhere(mask):
                ref=transport_plan_and_dual(A[i],B[j],M)[0]
                self.assertLessEqual(values[i,j],ref+1e-12)
                self.assertAlmostEqual(values[i,j],ref,places=10)

    def test_old_relaxation_can_miss_forced_value(self):
        M=np.array([[9.,1.],[1.,9.]])
        A=B=np.eye(2)
        mask,values,_=forced_values(M,A,B)
        self.assertTrue(mask.all())
        self.assertGreater(values[0,0]-free_lower(M,A,B)[0,0],7.9)

    def test_tiny_mass_is_not_dirac_and_zero_row_rejected(self):
        A=np.array([[1.,1e-15]])
        B=np.array([[.4,.6]])
        self.assertFalse(forced_values(np.ones((2,2)),A,B)[0].any())
        with self.assertRaises(ValueError):
            forced_values(np.ones((2,2)),np.zeros((1,2)),B)
