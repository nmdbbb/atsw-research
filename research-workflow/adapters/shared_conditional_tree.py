"""Shared conditional-state tree certificates for rational finite-window AW1.

Candidate only: no reference OT, path enumeration, or diagnostic labels.
Input maps names to (time-layer state masses, conditional transition rows).
States are full k-window tuples; output is the last coordinate. Times1..T
are charged, time0 is uncharged. Probabilities must be valid normalized
rational distributions. This is an inspectable research prototype, not a
validated float-facing replacement for common_model. Rebuild for new batches.
"""
from fractions import Fraction as F
from itertools import combinations


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
    def __init__(self, models, anchor_count=4, bank='pair_min', topology='feature_mst', engine='virtual', audit_dense=False):
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


