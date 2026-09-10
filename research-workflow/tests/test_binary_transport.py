import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'adapters'))
from binary_transport import binary_coupling,BinaryLayer
from common_model import _transport_value

class BinaryTests(unittest.TestCase):
    def test_random_against_independent_lp(self):
        rng=np.random.default_rng(102609)
        for _ in range(40):
            m=int(rng.integers(2,12));a=rng.random(2);a/=a.sum();b=rng.random(m);b/=b.sum()
            C=rng.normal(size=(2,m));o=binary_coupling(a,b,C)
            self.assertAlmostEqual(o['value'],_transport_value(a,b,C),places=9)
            self.assertLessEqual(o['dual_violation'],0.)
            self.assertLess(o['numerical_gap'],1e-10)

    def test_tiny_mass_ties_boundary_and_bad_order(self):
        o=binary_coupling([1e-15,1-1e-15],[.5,.5],np.zeros((2,2)))
        self.assertEqual(o['plan'][0].sum(),1e-15)
        self.assertEqual(o['value'],0.)
        o=binary_coupling([.5,.5],[.5,.5],[[0.,2.],[1.,0.]])
        np.testing.assert_array_equal(o['plan'],np.diag([.5,.5]))
        with self.assertRaises(ValueError):binary_coupling([.5,.5],[.5,.5],[[0.,2.],[1.,0.]],[1,0])

    def test_reuse_different_masses_transpose_and_matrix_version(self):
        C=np.array([[1.,8.],[4.,2.],[3.,7.]])
        layer=BinaryLayer(C,True)
        for a in ([.2,.3,.5],[.6,.1,.3]):
            o=layer.solve([0,1,2],a,[0,1],[.4,.6])
            self.assertAlmostEqual(o['value'],_transport_value(np.array(a),np.array([.4,.6]),C),places=10)
        self.assertEqual(layer.counts['cache_hits'],1)
        C[:]=0
        self.assertGreater(layer.solve([0,1,2],[.2,.3,.5],[0,1],[.4,.6])['value'],0)
        fresh=BinaryLayer(C,True)
        self.assertEqual(fresh.solve([0,1,2],[.2,.3,.5],[0,1],[.4,.6])['value'],0)
