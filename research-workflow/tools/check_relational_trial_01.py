"""Exact two-leaf proof checks, not a benchmark or a general adapted-OT solver.

Each law has two equally weighted, distinct, length-two paths. Every coupling is
[[z,1/2-z],[1/2-z,z]], 0<=z<=1/2. Bicausal prefix constraints are affine in z.
We intersect them exactly and minimize the linear cost at the feasible endpoints.
Optional common-model replay is numerical and reported separately.
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import sys


HALF = F(1, 2)
ROOT = Path(__file__).resolve().parents[1]


def coupling_entry(i, j):
    return (F(1), F(0)) if i == j else (F(-1), HALF)


def add(entries):
    entries = list(entries)
    return tuple(sum((entry[k] for entry in entries), F(0)) for k in (0, 1))


def groups(law):
    return [tuple(i for i in range(2) if law[i][0] == value)
            for value in sorted({path[0] for path in law})]


def exact_transport(left, right, cost, bicausal):
    assert len(left) == len(right) == 2
    assert all(len(path) == 2 for path in (*left, *right))
    assert left[0] != left[1] and right[0] != right[1]
    equations = []
    if bicausal:
        # pi(X_path=i, Y_prefix=J) = mu(i|X_prefix) pi(X_prefix,Y_prefix).
        for ig in groups(left):
            for jg in groups(right):
                block = add(coupling_entry(i, j) for i in ig for j in jg)
                for i in ig:
                    row = add(coupling_entry(i, j) for j in jg)
                    equations.append(tuple(row[k] - block[k] / len(ig) for k in (0, 1)))
                # Reverse causality, with nu(j|Y_prefix).
                for j in jg:
                    col = add(coupling_entry(i, j) for i in ig)
                    equations.append(tuple(col[k] - block[k] / len(jg) for k in (0, 1)))
    fixed = set()
    for slope, intercept in equations:
        if slope:
            fixed.add(-intercept / slope)
        else:
            assert intercept == 0, 'Inconsistent bicausal constraint'
    assert len(fixed) <= 1
    endpoints = sorted(fixed) if fixed else [F(0), HALF]
    assert all(0 <= z <= HALF for z in endpoints)
    values = []
    for z in endpoints:
        assert all(slope*z + intercept == 0 for slope, intercept in equations)
        pi = [[coupling_entry(i, j)[0]*z + coupling_entry(i, j)[1]
               for j in range(2)] for i in range(2)]
        assert all(sum(row) == HALF for row in pi)
        assert all(sum(pi[i][j] for i in range(2)) == HALF for j in range(2))
        values.append(sum((pi[i][j]*cost(left[i], right[j])
                           for i in range(2) for j in range(2)), F(0)))
    return min(values)


def masses(law):
    result = {}
    for path in law:
        for depth in (1, 2):
            prefix = path[:depth]
            result[prefix] = result.get(prefix, F(0)) + HALF
    return result


def tree_score(left, right, union_prefixes, weights=(F(1), F(1))):
    a, b = masses(left), masses(right)
    return sum((weights[len(prefix)-1] * abs(a.get(prefix, F(0))-b.get(prefix, F(0)))
                for prefix in union_prefixes), F(0))


def tree_cost(a, b):
    common = 0
    for x, y in zip(a, b):
        if x != y:
            break
        common += 1
    return F(4 - 2*common)


def main():
    laws = {
        'Q': ((F(0), F(0)), (F(0), F(1, 4))),
        'B': ((F(0), F(0)), (F(1, 8), F(1, 4))),
        'C_low': ((F(0), F(0)), (F(0), F(3, 8))),
        'C_high': ((F(0), F(0)), (F(0), F(3, 4))),
    }
    union = set().union(*(masses(law) for law in laws.values()))
    scores = {name: tree_score(laws['Q'], laws[name], union)
              for name in ('B', 'C_low', 'C_high')}
    assert scores == {'B': F(2), 'C_low': F(1), 'C_high': F(1)}
    exact = {}
    for power in (1, 2):
        cost = lambda a, b: sum((abs(x-y)**power for x, y in zip(a, b)), F(0))
        exact[power] = {name: exact_transport(laws['Q'], laws[name], cost, True)
                        for name in scores}
    assert exact[1] == {'B': F(3, 16), 'C_low': F(1, 16), 'C_high': F(1, 4)}
    assert exact[2] == {'B': F(5, 128), 'C_low': F(1, 128), 'C_high': F(1, 8)}
    assert scores['C_high'] < scores['B'] and exact[1]['C_high'] > exact[1]['B']
    u = ((F(0), F(0)), (F(0), F(1)))
    v = ((F(0), F(0)), (F(1), F(1)))
    tree_ordinary = exact_transport(u, v, tree_cost, False)
    tree_bicausal = exact_transport(u, v, tree_cost, True)
    assert tree_ordinary == F(2) and tree_bicausal == F(5, 2)
    assert tree_score(u, v, set(masses(u)) | set(masses(v))) == tree_ordinary

    # Independent existing float-DP implementation; not the exact proof above.
    sys.path.insert(0, str(ROOT))
    from adapters.common_model import build_window_model, exact_dp
    replay = []
    for k in (1, 2):
        models = {name: build_window_model([[0.0, *map(float, path)] for path in law],
                                           k=k, delta=1/8, shift=-1/16)
                  for name, law in laws.items()}
        for power, kind in ((1, 'absolute'), (2, 'squared')):
            for name in scores:
                value = exact_dp(models['Q'], models[name], cost=kind)
                error = abs(value - float(exact[power][name]))
                assert error <= 1e-12
                replay.append({'k': k, 'cost': kind, 'pair': ['Q', name],
                               'value': value, 'absolute_error': error})
    result = {
        'kind': 'exact_arithmetic_analytic_counterexample_check',
        'blind_preregistered': False,
        'statistical_or_performance_evidence': False,
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source': 'tools/check_relational_trial_01.py',
        'tree_edges': len(union),
        'tree_scores': {name: str(value) for name, value in scores.items()},
        'adapted_absolute': {name: str(value) for name, value in exact[1].items()},
        'adapted_squared': {name: str(value) for name, value in exact[2].items()},
        'same_tree_cost': {'ordinary': str(tree_ordinary), 'bicausal': str(tree_bicausal)},
        'numerical_common_model_replay': replay,
        'scope': 'Unit/depth-weighted prefix trie; not all trees, learned weights or statistical ranking.'
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
