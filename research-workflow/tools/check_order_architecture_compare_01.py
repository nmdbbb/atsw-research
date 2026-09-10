"""Exact algebraic discriminator on one finite contractive Markov family."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json


def law(rho, shift=F(0), reversal=False):
    # Common deterministic time zero omitted from costs. After time 1 every
    # continuation is deterministic and the first coordinate identifies the bit.
    return tuple(tuple(shift + sign*(F(1) if t == 0 else
                       (-1 if reversal else 1)*rho**t) for t in range(4))
                 for sign in (-1, 1))


def values(a, b, power):
    cost = lambda x, y: sum((abs(u-v)**power for u, v in zip(x, y)), F(0))
    diag = (cost(a[0], b[0])+cost(a[1], b[1]))/2
    anti = (cost(a[0], b[1])+cost(a[1], b[0]))/2
    # All first-stage couplings are bicausal: future coordinates are functions
    # of that law's first coordinate. The 2x2 polytope extrema are diag/anti.
    return {'kr': diag, 'exact': min(diag, anti), 'anti': anti}


def main():
    rho = F(9, 10)
    q, a, b = law(rho), law(rho, reversal=True), law(rho, F(9, 8))
    positive = law(rho, F(1, 4))
    rows = []
    for p in (1, 2):
        qa, qb = values(q, a, p), values(q, b, p)
        ordered = values(q, positive, p)
        assert ordered['kr'] == ordered['exact'] == 4*F(1, 4)**p
        assert ordered['exact'] < qb['exact']
        assert qa['exact'] == F(2)**p
        assert qb['exact'] == qb['kr'] == 4*F(9, 8)**p
        assert qa['exact'] < qb['exact'] < qa['kr']
        errors = [F(0), 2*rho, 2*rho**2, 2*rho**3]
        uniform_upper = sum((e**p for e in errors), F(0))
        assert uniform_upper == qa['kr']
        delta_s = qb['kr']-qa['kr']
        regret_a, regret_b = qa['kr']-qa['exact'], qb['kr']-qb['exact']
        assert delta_s + regret_a-regret_b == qb['exact']-qa['exact'] > 0
        rows.append({'power': p, 'near_exact': str(qa['exact']), 'near_kr': str(qa['kr']),
                     'far_exact_and_kr': str(qb['exact']),
                     'uniform_coupling_upper_near': str(uniform_upper),
                     'kr_order_reversed': True, 'bound_separation_unresolved': True,
                     'positive_ordered_core_exact_near': str(ordered['exact']),
                     'signed_score_gap': str(delta_s), 'near_regret': str(regret_a),
                     'exact_distance_gap': str(qb['exact']-qa['exact'])})
    print(json.dumps({'task_id': 'order_architecture_compare_01',
                      'kind': 'finite_rational_algebraic_diagnostic',
                      'preregistered': False, 'coverage_or_speed_claim': False,
                      'rho': str(rho), 'horizon': 4, 'paths_per_law': 2,
                      'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      'checks': rows,
                      'limits': 'Ordered core and one sign-reversal boundary of one k=1 family. No stochastic continuation after the first draw; ordinary and bicausal feasible path couplings coincide here. No population, arbitrary k=2, novelty, coverage or performance conclusion.'}, indent=2))


if __name__ == '__main__':
    main()
