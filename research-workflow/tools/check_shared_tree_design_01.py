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


import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapters.shared_conditional_tree import Tree, SharedTrees


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
                candidate_sha256=hashlib.sha256((Path(__file__).resolve().parents[1]/'adapters/shared_conditional_tree.py').read_bytes()).hexdigest(),
                reference_dependency_sha256=hashlib.sha256((Path(__file__).parent/'check_geometry_condition_screen_01.py').read_bytes()).hexdigest(),
                power=1,preregistered=False,coverage_or_runtime_claim=False,results=results,
                limits='Three hand-selected families, k1/k2, exact binary-row references. Candidate supports valid rational finite rows; audit reference is binary only. Cost counters are partial, bit growth and sorting not fully counted. No runtime, coverage or online insertion claim.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--bank', choices=['anchors', 'pair_min'], default='anchors')
    parser.add_argument('--topology', choices=['median', 'feature_mst'], default='median')
    parser.add_argument('--engine', choices=['dense', 'virtual'], default='dense')
    args = parser.parse_args()
    print(json.dumps(run(args.bank, args.topology, args.engine), indent=2))
