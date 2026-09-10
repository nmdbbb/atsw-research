"""One exact finite diagnostic, not a preregistered benchmark or population test."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib
import json


def fixture():
    out = {}
    for name in ('Q', 'A', 'B'):
        law = {}
        for bit, tail in product((0, 1), repeat=2):
            early = (F(0), F(bit, 4)) if name != 'A' else (F(bit, 8), F(bit, 4))
            shift = F(1, 4) if name == 'B' else F(0)
            law[(F(0), *early, F(0), F(0), F(4*tail)+shift, F(-4*tail)+shift)] = F(1, 4)
        out[name] = law
    return out


def model(law, k):
    horizon = len(next(iter(law)))-1
    masses = [{} for _ in range(horizon+1)]
    edges = [{} for _ in range(horizon)]
    for path, mass in law.items():
        states = [path[max(0, t-k+1):t+1] for t in range(horizon+1)]
        for t, state in enumerate(states):
            masses[t][state] = masses[t].get(state, F(0))+mass
        for t in range(horizon):
            row = edges[t].setdefault(states[t], {})
            row[states[t+1]] = row.get(states[t+1], F(0))+mass
    kernels = [{state: {child: weight/masses[t][state] for child, weight in row.items()}
                for state, row in layer.items()} for t, layer in enumerate(edges)]
    return masses, kernels


def reconstructed(masses, kernels):
    paths = {(state[-1],): mass for state, mass in masses[0].items()}
    for t, layer in enumerate(kernels):
        width = len(next(iter(layer)))
        new = {}
        for path, mass in paths.items():
            for child, probability in layer[path[-width:]].items():
                extended = (*path, child[-1])
                new[extended] = new.get(extended, F(0))+mass*probability
        paths = new
    return paths


def resets(models):
    result = []
    for t in range(1, len(models[0][0])-1):
        supports = [set(masses[t]) for masses, _ in models]
        if all(len(s) == 1 and s == supports[0] for s in supports):
            result.append(t)
    return result


def prefix_upper(left, right, caps, reset_times):
    lm, lk = left
    rm, rk = right
    assert lm[0] == rm[0] and len(lm[0]) == 1
    matched = dict(lm[0]); value = F(0); entries = 0
    for t, cap in enumerate(caps, 1):
        new = {}
        for state, mass in matched.items():
            a, b = lk[t-1].get(state, {}), rk[t-1].get(state, {})
            for child in a.keys() & b.keys():
                entries += 1
                new[child] = new.get(child, F(0))+mass*min(a[child], b[child])
        matched = new
        value += cap*(1-sum(matched.values(), F(0)))
        if t in reset_times:
            assert lm[t] == rm[t] and len(lm[t]) == 1
            matched = dict(lm[t])
    return value, entries


def transport(a, b, cost):
    """Independent exact local reference: enumerate 2x2 polytope endpoints."""
    x, y = list(a), list(b)
    assert 1 <= len(x) <= 2 and 1 <= len(y) <= 2
    if len(x) == 1:
        return sum((mass*cost(x[0], child) for child, mass in b.items()), F(0))
    if len(y) == 1:
        return sum((mass*cost(child, y[0]) for child, mass in a.items()), F(0))
    av, bv = a[x[0]], b[y[0]]
    def objective(z):
        return (z*cost(x[0], y[0])+(av-z)*cost(x[0], y[1])+
                (bv-z)*cost(x[1], y[0])+(1-av-bv+z)*cost(x[1], y[1]))
    return min(objective(max(F(0), av+bv-1)), objective(min(av, bv)))


def exact_full_history(left, right, power):
    """Bicausal reference on the original full-prefix laws, no reset shortcut."""
    horizon = len(next(iter(left)))-1
    def row(law, prefix):
        found = [(path, mass) for path, mass in law.items() if path[:len(prefix)] == prefix]
        denominator = sum((mass for _, mass in found), F(0))
        out = {}
        for path, mass in found:
            child = (*prefix, path[len(prefix)])
            out[child] = out.get(child, F(0))+mass/denominator
        return out
    @lru_cache(None)
    def solve(x, y):
        if len(x) == horizon+1:
            return F(0)
        return transport(row(left, x), row(right, y),
                         lambda u, v: abs(u[-1]-v[-1])**power+solve(u, v))
    return solve((F(0),), (F(0),))


def marginal(law, t):
    out = {}
    for path, mass in law.items():
        out[path[t]] = out.get(path[t], F(0))+mass
    return out


def main():
    laws = fixture(); results = []
    for k in (1, 2):
        models = {name: model(law, k) for name, law in laws.items()}
        for name in laws:
            assert reconstructed(*models[name]) == laws[name]
        reset_times = resets(list(models.values()))
        assert 4 in reset_times
        if k == 2:
            assert 3 not in reset_times  # Current coordinate is zero, history is not reset.
        for power in (1, 2):
            caps = [(max(path[t] for law in laws.values() for path in law)-
                     min(path[t] for law in laws.values() for path in law))**power for t in range(1, 7)]
            near = exact_full_history(laws['Q'], laws['A'], power)
            far = exact_full_history(laws['Q'], laws['B'], power)
            old, old_work = prefix_upper(models['Q'], models['A'], caps, [])
            new, new_work = prefix_upper(models['Q'], models['A'], caps, reset_times)
            lower = sum((transport(marginal(laws['Q'], t), marginal(laws['B'], t),
                                   lambda x, y: abs(x-y)**power) for t in range(1, 7)), F(0))
            near_lower = sum((transport(marginal(laws['Q'], t), marginal(laws['A'], t),
                                        lambda x, y: abs(x-y)**power) for t in range(1, 7)), F(0))
            assert near == (F(3, 16) if power == 1 else F(5, 128))
            assert far == lower == (F(1, 2) if power == 1 else F(1, 8))
            assert new == (F(1, 4) if power == 1 else F(7, 128))
            assert near_lower < near <= new < lower <= old
            results.append(dict(k=k, power=power, reset_times=reset_times,
                                exact_near=str(near), exact_far=str(far), marginal_near=str(near_lower),
                                old_upper=str(old), reset_upper=str(new), far_lower=str(lower),
                                old_resolves=False, reset_resolves=True,
                                matched_edge_visits_old=old_work, matched_edge_visits_reset=new_work))
    print(json.dumps({'task_id': 'geometry_condition_screen_01', 'kind': 'finite_rational_diagnostic',
                      'preregistered': False, 'performance_or_coverage_claim': False,
                      'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'checks': results,
                      'limits': 'One chosen family, T=6, four paths per law. Full-history reference is evaluator only. No general fast implementation, novelty or population claim.'}, indent=2))


if __name__ == '__main__':
    main()
