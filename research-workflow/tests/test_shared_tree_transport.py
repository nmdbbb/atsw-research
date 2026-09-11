"""Correctness of the sparse primitive on roots, zero edges and interior mass."""
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapters.shared_conditional_tree import Tree


class VirtualTreeTransportTests(unittest.TestCase):
    def make_tree(self, count, edges):
        work = dict(tree_ot_calls=0, distribution_entries_read=0, tree_nodes_visited=0,
                    tree_index_entries=0, signed_support_entries=0, virtual_nodes_visited=0,
                    lca_queries=0, lca_table_lookups=0,
                    evaluator_dense_audit_nodes=0, evaluator_dense_audit_queries=0)
        return Tree(list(range(count)), 0, edges, work, 'virtual', True)

    def test_singleton_and_cancelled_mass(self):
        tree = self.make_tree(1, [])
        self.assertEqual(tree.ot({0: F(1)}, {0: F(1)}), 0)
        self.assertEqual(tree.work['virtual_nodes_visited'], 0)

    def test_zero_length_chain_and_interior_mass(self):
        tree = self.make_tree(5, [(0, 1, F(0)), (1, 2, F(2)), (2, 3, F(0)), (3, 4, F(3))])
        self.assertEqual(tree.ot({0: F(1)}, {1: F(1)}), 0)
        self.assertEqual(tree.ot({1: F(1, 2), 3: F(1, 2)}, {2: F(1)}), 1)
        self.assertEqual(tree.ot({1: F(1, 3), 4: F(2, 3)}, {0: F(1, 3), 2: F(2, 3)}), 2)

    def test_branching_lca_all_dirac_pairs_and_dense_masses(self):
        tree = self.make_tree(9, [(0, 1, F(0)), (0, 2, F(2)), (1, 3, F(3)), (1, 4, F(0)),
                                  (2, 5, F(1)), (2, 6, F(4)), (4, 7, F(2)), (4, 8, F(0))])
        self.assertEqual(tree.lca(7, 8), 4)
        self.assertEqual(tree.lca(7, 5), 0)
        for a in tree.nodes:
            for b in tree.nodes:
                self.assertEqual(tree.ot({a: F(1)}, {b: F(1)}), tree.distance(a, b))
        a = {i: F(i+1, 45) for i in tree.nodes}
        b = {i: F(9-i, 45) for i in tree.nodes}
        self.assertEqual(tree.ot(a, b), tree.ot(b, a))
        tree.audit_dense = False
        before = tree.work['evaluator_dense_audit_queries']
        self.assertEqual(tree.ot(a, b), tree._dense(a, b))
        self.assertEqual(before, tree.work['evaluator_dense_audit_queries'])


if __name__ == '__main__':
    unittest.main()
