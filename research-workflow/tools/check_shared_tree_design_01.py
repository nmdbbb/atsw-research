"""Executable AW1 shared-tree construction; fixed exact diagnostics, not a probe.

Input is rational finite-window models. Exact references are evaluator-only.
Version 0 deliberately uses a small anchor bank, no all-pairs transport table.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product, combinations
from math import lcm
from pathlib import Path
import hashlib
import json

from check_geometry_condition_screen_01 import model, transport, reconstructed
from check_geometry_condition_screen_01 import fixture as reset_fixture


class Tree:
    def __init__(self, nodes, root, edges, work, engine='dense', audit_dense=False):
        self.nodes, self.root, self.work = tuple(nodes), root, work
        self.engine, self.audit_dense = engine, audit_dense
        adjacent = {s: [] for s in nodes}
        for a, b, w in edges:
            assert w >= 0
            adjacent[a].append((b, w)); adjacent[b].append((a, w))
        self.parent, self.order = {root: (None, F(0))}, []
        stack = [root]
        while stack:
            s = stack.pop(); self.order.append(s)
            for child, w in adjacent[s]:
                if child not in self.parent:
                    self.parent[child] = (s, w); stack.append(child)
        assert len(self.order) == len(nodes) and len(edges) == len(nodes)-1
        if engine == 'virtual':
            self.tin = {s: i for i, s in enumerate(self.order)}
            sizes = {s: 1 for s in nodes}; self.root_distance = {}
            for s in self.order:
                par, length = self.parent[s]
                self.root_distance[s] = (self.root_distance[par] if par is not None else F(0))+length
            for s in reversed(self.order):
                par, _ = self.parent[s]
                if par is not None:
                    sizes[par] += sizes[s]
            self.tout = {s: self.tin[s]+sizes[s] for s in nodes}
            self.up = [{s: (self.parent[s][0] if self.parent[s][0] is not None else root) for s in nodes}]
            for _ in range(1, len(nodes).bit_length()):
                last = self.up[-1]; self.up.append({s: last[last[s]] for s in nodes})
            self.work['tree_index_entries'] += len(nodes)*len(self.up)

    def ot(self, a, b):
        """Exact subtree imbalance; dense audits are evaluator-only and optional."""
        self.work['tree_ot_calls'] += 1
        self.work['distribution_entries_read'] += len(a)+len(b)
        if self.engine == 'virtual':
            value = self._virtual(a, b)
            if self.audit_dense:
                assert value == self._dense(a, b)
                self.work['evaluator_dense_audit_nodes'] += len(self.nodes)
                self.work['evaluator_dense_audit_queries'] += 1
            return value
        self.work['tree_nodes_visited'] += len(self.nodes)
        return self._dense(a, b)

    def _dense(self, a, b):
        mass = {s: a.get(s, F(0))-b.get(s, F(0)) for s in self.nodes}
        value = F(0)
        for s in reversed(self.order):
            par, length = self.parent[s]
            if par is not None:
                value += length*abs(mass[s]); mass[par] += mass[s]
        assert mass[self.root] == 0
        return value

    def ancestor(self, a, b):
        return self.tin[a] <= self.tin[b] < self.tout[a]

    def lca(self, a, b):
        self.work['lca_queries'] += 1
        if self.ancestor(a, b):
            return a
        if self.ancestor(b, a):
            return b
        for table in reversed(self.up):
            self.work['lca_table_lookups'] += 1
            parent = table[a]
            if not self.ancestor(parent, b):
                a = parent
        return self.up[0][a]

    def _virtual(self, a, b):
        mass = dict(a)
        for s, probability in b.items():
            mass[s] = mass.get(s, F(0))-probability
        assert sum(mass.values(), F(0)) == 0
        mass = {s: p for s, p in mass.items() if p}
        self.work['signed_support_entries'] += len(mass)
        if not mass:
            return F(0)
        ordered = sorted(mass, key=self.tin.__getitem__)
        vertices = set(ordered); vertices.add(self.root)
        vertices.update(self.lca(a, b) for a, b in zip(ordered, ordered[1:]))
        vertices = sorted(vertices, key=self.tin.__getitem__)
        self.work['virtual_nodes_visited'] += len(vertices)
        stack, parent = [], {}
        for s in vertices:
            while stack and not self.ancestor(stack[-1], s):
                stack.pop()
            if stack:
                parent[s] = stack[-1]
            stack.append(s)
        flow = {s: mass.get(s, F(0)) for s in vertices}; value = F(0)
        for s in reversed(vertices[1:]):
            par = parent[s]
            value += abs(flow[s])*(self.root_distance[s]-self.root_distance[par])
            flow[par] += flow[s]
        assert vertices[0] == self.root and flow[self.root] == 0
        return value

    def distance(self, a, b):
        """Evaluator only: do not count as candidate tree queries."""
        path = {}; distance = F(0); node = a
        while node is not None:
            path[node] = distance
            node, length = self.parent[node]; distance += length
        distance = F(0); node = b
        while node not in path:
            node, length = self.parent[node]; distance += length
        return distance+path[node]


def median_topology(nodes, features):
    edges = []
    def build(items):
        if not items:
            return None
        width = len(features[items[0]])
        axis = max(range(width), key=lambda j:
                   max(features[s][j] for s in items)-min(features[s][j] for s in items))
        items = sorted(items, key=lambda s: (features[s][axis], s))
        middle = len(items)//2; hub = items[middle]
        for group in (items[:middle], items[middle+1:]):
            child = build(group)
            if child is not None:
                edges.append((hub, child))
        return hub
    return build(list(nodes)), edges


def feature_graph(nodes, features, median_edges):
    """At most (feature_count+1)*(N-1) edges, before deduplication."""
    links = {tuple(sorted(edge)) for edge in median_edges}
    for j in range(len(features[nodes[0]])):
        ordered = sorted(nodes, key=lambda s: (features[s][j], s))
        links.update(tuple(sorted(edge)) for edge in zip(ordered, ordered[1:]))
    return sorted(links)


def spanning_tree(nodes, weighted_edges):
    parent = {s: s for s in nodes}
    def find(s):
        while parent[s] != s:
            parent[s] = parent[parent[s]]; s = parent[s]
        return s
    chosen = []
    for a, b, w in sorted(weighted_edges, key=lambda edge: (edge[2], edge[0], edge[1])):
        x, y = find(a), find(b)
        if x != y:
            chosen.append((a, b, w)); parent[x] = y
    assert len(chosen) == len(nodes)-1
    return chosen


class SharedTrees:
    def __init__(self, models, anchor_count=4, bank='anchors', topology='median', engine='dense', audit_dense=False):
        assert bank in ('anchors', 'pair_min')
        assert topology in ('median', 'feature_mst')
        assert engine in ('dense', 'virtual')
        self.models, self.bank = models, bank
        self.T = len(next(iter(models.values()))[1])
        assert all(len(m[1]) == self.T for m in models.values())
        self.nodes = [sorted((name, s) for name, (m, _) in models.items() for s in m[t])
                      for t in range(self.T+1)]
        self.rows = [{(name, s): {(name, child): p for child, p in row.items()}
                      for name, (_, kernels) in models.items() for s, row in kernels[t].items()}
                     for t in range(self.T)]
        self.work = dict(tree_edges_built=0, tree_ot_calls=0, tree_nodes_visited=0,
                         distribution_entries_read=0, feature_edge_reads=0,
                         lower_distance_evaluations=0, exact_ot_calls=0,
                         pooled_states=sum(map(len, self.nodes)),
                         input_transition_entries=sum(len(row) for layer in self.rows for row in layer.values()))
        self.work.update(tree_index_entries=0, signed_support_entries=0,
                         virtual_nodes_visited=0, lca_queries=0, lca_table_lookups=0,
                         evaluator_dense_audit_nodes=0, evaluator_dense_audit_queries=0)
        self.graph_sizes = []
        self.trees, self.probes, self.ell = {}, {}, {}
        for t in range(self.T, -1, -1):
            nodes = self.nodes[t]
            if t == self.T:
                expectations = {s: () for s in nodes}
            else:
                count = len(self.probes[t+1][self.nodes[t+1][0]])
                expectations = {}
                for s in nodes:
                    row = self.rows[t][s]
                    expectations[s] = tuple(sum((p*self.probes[t+1][u][j] for u, p in row.items()), F(0))
                                             for j in range(count))
                    self.work['feature_edge_reads'] += len(row)*count
            def lower(a, b, t=t, expectations=expectations):
                self.work['lower_distance_evaluations'] += 1
                stage = abs(a[1][-1]-b[1][-1]) if t else F(0)
                return stage+max((abs(x-y) for x, y in zip(expectations[a], expectations[b])), default=F(0))
            self.ell[t] = lower
            features = {s: ((s[1][-1] if t else F(0)), *expectations[s]) for s in nodes}
            if t == self.T:
                ordered = sorted(nodes, key=lambda s: (s[1][-1], s))
                root = ordered[0]; links = list(zip(ordered, ordered[1:]))
            else:
                root, links = median_topology(nodes, features)
                if topology == 'feature_mst':
                    links = feature_graph(nodes, features, links)
            self.graph_sizes.append(dict(time=t, nodes=len(nodes), weighted_edges=len(links),
                                         complete_graph_edges=len(nodes)*(len(nodes)-1)//2))
            edges = []
            for a, b in links:
                w = abs(a[1][-1]-b[1][-1]) if t else F(0)
                if t != self.T:
                    w += self.trees[t+1].ot(self.rows[t][a], self.rows[t][b])
                edges.append((a, b, w))
            self.work['tree_edges_built'] += len(edges)  # Includes discarded candidates.
            if topology == 'feature_mst' and t != self.T:
                edges = spanning_tree(nodes, edges)
            self.trees[t] = Tree(nodes, root, edges, self.work, engine, audit_dense)
            # Deterministic farthest-first anchors in a computable lower metric.
            anchors = [root]
            distances = {s: [lower(s, root)] for s in nodes}
            while len(anchors) < min(anchor_count, len(nodes)):
                choice = max((s for s in nodes if s not in anchors),
                             key=lambda s: (min(distances[s]), s))
                anchors.append(choice)
                for s in nodes:
                    distances[s].append(lower(s, choice))
            self.probes[t] = {}
            for s in nodes:
                values = list(distances[s])
                if bank == 'pair_min':
                    values += [min(distances[s][i], distances[s][j])
                               for i, j in combinations(range(len(anchors)), 2)]
                self.probes[t][s] = tuple(values)

    def bounds(self, left, right):
        a = {(left, s): p for s, p in self.models[left][0][0].items()}
        b = {(right, s): p for s, p in self.models[right][0][0].items()}
        count = len(self.probes[0][self.nodes[0][0]])
        lower = max((abs(sum((p*self.probes[0][s][j] for s, p in a.items()), F(0))-
                         sum((p*self.probes[0][s][j] for s, p in b.items()), F(0)))
                     for j in range(count)), default=F(0))
        return lower, self.trees[0].ot(a, b)


def exact_reference(models, left, right):
    lm, lk = models[left]; rm, rk = models[right]; horizon = len(lk); calls = [0]
    @lru_cache(None)
    def future(t, s, r):
        stage = abs(s[-1]-r[-1]) if t else F(0)
        if t == horizon:
            return stage
        calls[0] += 1
        return stage+transport(lk[t][s], rk[t][r], lambda u, v: future(t+1, u, v))
    value = transport(lm[0], rm[0], lambda s, r: future(0, s, r))
    return value, calls[0]+1, future


def laws_from_paths(build):
    result = {name: {} for name in ('Q', 'A', 'B')}
    for j, l, n in product((-1, 1), repeat=3):
        for name, path in build(F(j), F(l), F(n)).items():
            path = tuple(map(F, path))
            result[name][path] = result[name].get(path, F(0))+F(1, 8)
    return result


def fixtures():
    return {
        'reconvergence': reset_fixture(),
        'information_timing': laws_from_paths(lambda j, l, n:
            dict(Q=(0, j, j, n), A=(0, j, l, j), B=(0, j, l, l))),
        'genuine_k2': laws_from_paths(lambda j, l, n:
            dict(Q=(0, j, 0, j), A=(0, j, 0, -j), B=(0, j, 0, l))),
    }


def ordinary_reference(a, b):
    """Evaluator-only rational uniform expansion plus exact assignment DP."""
    n = lcm(*(p.denominator for law in (a, b) for p in law.values()))
    x = [s for s, p in a.items() for _ in range(int(p*n))]
    y = [s for s, p in b.items() for _ in range(int(p*n))]
    assert len(x) == len(y) == n and n <= 8
    costs = [[sum((abs(u-v) for u, v in zip(s[1:], r[1:])), F(0)) for r in y] for s in x]
    @lru_cache(None)
    def solve(mask):
        i = mask.bit_count()
        if i == n:
            return F(0)
        return min(costs[i][j]+solve(mask | (1 << j)) for j in range(n) if not mask & (1 << j))
    return solve(0)/n, solve.cache_info().currsize


def run(bank='anchors', topology='median', engine='dense'):
    results = []
    for family, laws in fixtures().items():
        for k in (1, 2):
            models = {name: model(law, k) for name, law in laws.items()}
            candidate = SharedTrees(models, bank=bank, topology=topology, engine=engine, audit_dense=(engine == 'virtual'))
            pairs = {}
            for left, right in combinations(sorted(models), 2):
                low, up = candidate.bounds(left, right)
                value, calls, future = exact_reference(models, left, right)
                assert low <= value <= up, (family, k, left, right, low, value, up)
                ordinary, states = ordinary_reference(reconstructed(*models[left]), reconstructed(*models[right]))
                assert ordinary <= value
                pairs[left+right] = dict(lower=str(low), exact=str(value), upper=str(up), reference_ot_calls=calls,
                                        ordinary=str(ordinary), evaluator_assignment_states=states)
            candidate_work = dict(candidate.work)  # Before further evaluator-only checks.
            dense_audit = {key: candidate_work.pop(key) for key in ('evaluator_dense_audit_nodes', 'evaluator_dense_audit_queries')}
            # Audit every layer's domination and probe Lipschitz property. This
            # can be quadratic, but is evaluator work and never candidate input.
            audit_pairs = 0
            references = {(a, b): exact_reference(models, a, b)[2]
                          for a in models for b in models}
            for t, nodes in enumerate(candidate.nodes):
                for s, r in combinations(nodes, 2):
                    exact = references[s[0], r[0]](t, s[1], r[1]); audit_pairs += 1
                    assert candidate.trees[t].distance(s, r) >= exact
                    assert all(abs(x-y) <= exact for x, y in zip(candidate.probes[t][s], candidate.probes[t][r]))
            la, ua = F(pairs['AQ']['lower']), F(pairs['AQ']['upper'])
            lb, ub = F(pairs['BQ']['lower']), F(pairs['BQ']['upper'])
            verdict = 'A_closer' if ua < lb else 'B_closer' if ub < la else 'unresolved'
            if verdict != 'unresolved':
                assert (F(pairs['AQ']['exact']) < F(pairs['BQ']['exact'])) == (verdict == 'A_closer')
            marginals_equal = all(
                {x: sum(m for path, m in law.items() if path[t] == x)
                 for x in {path[t] for path in law}} ==
                {x: sum(m for path, m in laws['Q'].items() if path[t] == x)
                 for x in {path[t] for path in laws['Q']}}
                for law in laws.values() for t in range(len(next(iter(law)))))
            results.append(dict(family=family, k=k, bank=bank, topology=topology, engine=engine, pairs=pairs, query_order=verdict,
                                all_time_marginals_equal=marginals_equal,
                                reconstruction_equals_supplied_paths={name: reconstructed(*m) == laws[name] for name, m in models.items()},
                                candidate_work=candidate_work, evaluator_conditional_pairs=audit_pairs,
                                evaluator_dense_audit=dense_audit,
                                graph_sizes=candidate.graph_sizes,
                                state_counts=[len(layer) for layer in candidate.nodes]))
    return dict(task='shared_tree_design_01',kind='fixed_exact_diagnostic_not_benchmark',
                bank=bank,topology=topology,engine=engine,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                power=1,preregistered=False,coverage_or_runtime_claim=False,results=results,
                limits='Three hand-selected families, k1/k2, exact binary-row references. Candidate supports valid rational finite rows; audit reference is binary only. Cost counters are partial, bit growth and sorting not fully counted. No runtime, coverage or online insertion claim.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--bank', choices=['anchors', 'pair_min'], default='anchors')
    parser.add_argument('--topology', choices=['median', 'feature_mst'], default='median')
    parser.add_argument('--engine', choices=['dense', 'virtual'], default='dense')
    args = parser.parse_args()
    print(json.dumps(run(args.bank, args.topology, args.engine), indent=2))
