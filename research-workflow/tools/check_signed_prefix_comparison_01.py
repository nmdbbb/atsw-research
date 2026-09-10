"""Exact rational construction checks, not a statistical or speed probe."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib
import json


def fixture(d, b):
    laws = {name: {} for name in ('Q', 'A', 'B')}
    for j, ell, n in product((-1, 1), repeat=3):
        q2, a2 = d*j+ell, j+ell
        for name, path in (
            ('Q', (F(0), F(j, 2), F(q2), F(4*q2+n))),
            ('A', (F(0), F(j), F(a2), F(4*a2+n))),
            ('B', (F(0), b*j, F(a2), F(4*a2+n))),
        ):
            laws[name][path] = F(1, 8)
    return laws


def row(law, prefix):
    out = {}
    for path, mass in law.items():
        if path[:len(prefix)] == prefix:
            child = path[len(prefix)]
            out[child] = out.get(child, F(0))+mass
    total = sum(out.values(), F(0))
    return {x: mass/total for x, mass in out.items()}


def local(a, b, cost, maximize=False):
    xs, ys = sorted(a), sorted(b)
    assert len(xs) == len(ys) == 2
    av, bv = a[xs[0]], b[ys[0]]
    vals = []
    for z in (max(F(0), av+bv-1), min(av, bv)):
        weights = (z, av-z, bv-z, 1-av-bv+z)
        vals.append(sum((w*cost(x, y) for w, (x, y) in
                         zip(weights, product(xs, ys))), F(0)))
    return (max if maximize else min)(vals)


def nested(a, b, horizon=3, signed_scale=None, markov=False, maximize=False):
    calls = 0
    # For these explicitly Markov fixtures, any history ending at a state has
    # the same next row. Check this separately; then cache by current pair.
    reps = {}
    for name, law in (('a', a), ('b', b)):
        for path in law:
            for t in range(3):
                key = (name, t, path[t]); prefix = path[:t+1]
                if key in reps:
                    assert row(law, reps[key]) == row(law, prefix)
                reps[key] = prefix

    @lru_cache(None)
    def solve(t, x, y):
        nonlocal calls
        if t == horizon:
            return F(0)
        calls += 1
        px = reps['a', t, x] if markov else x
        py = reps['b', t, y] if markov else y
        def cost(u, v):
            immediate = (u-v)**2
            if signed_scale is not None:
                immediate = (u-signed_scale*v)**2-(u-v)**2 if t == 0 else F(0)
            return immediate+solve(t+1, u if markov else (*x, u),
                                   v if markov else (*y, v))
        return local(row(a, px), row(b, py), cost, maximize)
    start = F(0) if markov else (F(0),)
    value = solve(0, start, start)
    return value, calls


def assignment(a, b):
    """Independent ordinary path OT oracle: uniform assignment via subset DP."""
    xs, ys = list(a), list(b)
    assert len(xs) == len(ys) == 8
    assert set(a.values()) == set(b.values()) == {F(1, 8)}
    costs = [[sum(((u-v)**2 for u, v in zip(x, y)), F(0)) for y in ys] for x in xs]
    @lru_cache(None)
    def solve(mask):
        i = mask.bit_count()
        if i == len(xs):
            return F(0)
        return min(costs[i][j]+solve(mask | (1 << j))
                   for j in range(len(ys)) if not mask & (1 << j))
    return solve(0)/8


def marginal(law, t):
    out = {}
    for path, mass in law.items():
        out[path[t]] = out.get(path[t], F(0))+mass
    return out


def marginal_lower(a, b):
    total = F(0)
    for t in range(1, 4):
        xs, ys = sorted(marginal(a, t).items()), sorted(marginal(b, t).items())
        i = j = 0; av = xs[0][1]; bv = ys[0][1]
        while i < len(xs) and j < len(ys):
            mass = min(av, bv); total += mass*(xs[i][0]-ys[j][0])**2
            av -= mass; bv -= mass
            if av == 0:
                i += 1
                if i < len(xs): av = xs[i][1]
            if bv == 0:
                j += 1
                if j < len(ys): bv = ys[j][1]
    return total


def check_map(a, b, scale):
    assert scale != 0
    pushed = {(p[0], scale*p[1], *p[2:]): mass for p, mass in a.items()}
    assert pushed == b and len(pushed) == len(a)
    # Explicit edge counts for a production layerwise verification, no free
    # suffix check inferred from the known fixture generator.
    edges = set()
    for p in a:
        for t in range(3): edges.add((t, p[t], p[t+1]))
    return len(edges)


def main():
    out = []
    for name, d, scale in (('positive', 0, F(3, 2)),
                           ('matched_marginals', 1, F(-1)),
                           ('reversed_query_future', -1, F(-1))):
        laws = fixture(d, scale); q, a, b = (laws[n] for n in ('Q', 'A', 'B'))
        edges = check_map(a, b, scale)
        da, ca = nested(q, a, markov=True); db, cb = nested(q, b, markov=True)
        assert da == nested(q, a)[0] and db == nested(q, b)[0]
        lo, cs = nested(q, a, horizon=1, signed_scale=scale, markov=True)
        hi, _ = nested(q, a, horizon=1, signed_scale=scale, markov=True, maximize=True)
        assert lo <= db-da <= hi
        oa, ob = assignment(q, a), assignment(q, b)
        la, lb = marginal_lower(q, a), marginal_lower(q, b)
        assert la <= oa <= da and lb <= ob <= db
        if name == 'positive':
            assert lo == F(3, 4) and da < db and lb <= da and oa < da
        else:
            assert all(marginal(a,t)==marginal(b,t) for t in range(4))
            assert lo == -2 and hi == 2 and da != db
            assert (da, db) == ((F(1,4), F(9,4)) if d == 1 else (F(9,4), F(1,4)))
            assert max(da-oa, db-ob)>0
        out.append({'case':name,'D_QA':str(da),'D_QB':str(db),'ordinary_QA':str(oa),
                    'ordinary_QB':str(ob),'marginal_L_QA':str(la),'marginal_L_QB':str(lb),
                    'signed_interval':[str(lo),str(hi)],'exact_gap':str(db-da),
                    'full_markov_transport_calls':[ca,cb],'signed_min_transport_calls':cs,
                    'candidate_map_edges_to_check':edges,'maps_checked_on_full_laws':True})
    print(json.dumps({'task_id':'signed_prefix_comparison_01','kind':'exact_constructed_diagnostic',
                      'preregistered':False,'performance_or_coverage_claim':False,
                      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'results':out,'limits':'One analytic three-parameter family, no random experiment. Binary reference transport dispatch uses zero generic LP calls. Work counts exclude input-building and verification and are not end-to-end speed or comparison against strongest early stopping.'},indent=2))


if __name__ == '__main__':
    main()
