import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'adapters'))
from support_monge import monge_predicate,monge_value
from common_model import _transport_value

class SupportMongeTests(unittest.TestCase):
    def test_positive_dyadic_violation_not_rounded_away(self):
        M=np.array([[1.,1.],[1.,np.nextafter(1.,2.)]])
        self.assertFalse(monge_predicate(M)[0])
        self.assertTrue(monge_predicate(np.ones((3,4)))[0])

    def test_both_convex_costs_and_tiny_mass_against_lp(self):
        rng=np.random.default_rng(91026)
        for power in (1,2):
            for _ in range(10):
                x=np.sort(rng.integers(-10,11,4));y=np.sort(rng.integers(-10,11,5))
                C=np.abs(x[:,None]-y[None,:]).astype(float)**power
                a=rng.random(4);a/=a.sum();b=rng.random(5);b/=b.sum()
                value,_=monge_value(a,b,C)
                self.assertIsNotNone(value)
                self.assertAlmostEqual(value,_transport_value(a,b,C),places=9)
        value,_=monge_value([1e-15,1-1e-15],[.5,.5],np.array([[0.,1.],[1.,0.]]))
        self.assertAlmostEqual(value,.5-1e-15,places=15)

    def test_continuation_can_break_structure(self):
        stage=(np.arange(3)[:,None]-np.arange(3)[None,:])**2
        continuation=np.zeros((3,3));continuation[1,1]=10
        self.assertTrue(monge_predicate(stage)[0])
        self.assertFalse(monge_predicate(stage+continuation)[0])
