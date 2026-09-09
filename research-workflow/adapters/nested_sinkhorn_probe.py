"""Tiny independent nested-Sinkhorn development probe, not author-code reproduction.

Uses the SAME finite-window model, with a random-initial root OT and scalar
stage costs at times 1..T. Tests k-DAG/unfolded-tree equivalence. All arithmetic
is float64: residuals and LP containment are numerical audits, NOT outward
certificates. No performance/frontier qualification follows from this probe.

Run from workspace root: python -B research-workflow/adapters/nested_sinkhorn_probe.py
Fixtures are the existing PNOT development fixtures; their preregistration
claim is not inherited. epsilon=0.05 and tolerance=1e-8 are fixed development
choices, not the objective's 0.005 relative certification threshold.
"""

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy
from scipy.special import logsumexp

from common_model import build_window_model, exact_dp, stage_cost


def entropy(probability):
    p = np.asarray(probability)
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))


def path_entropy(model):
    occupancy = model.initial.copy()
    result = entropy(occupancy)
    for kernel in model.kernels:
        result += sum(w * entropy(row) for w, row in zip(occupancy, kernel))
        occupancy = occupancy @ kernel
    return float(result)


def round_plan(plan, a, b):
    """Exact-arithmetic row/column downscale + rank-one deficit repair formula.

    This FLOAT evaluation only audits residuals. It does not make the returned
    binary floats an exactly feasible plan for exact normalized marginals.
    """
    row = plan.sum(axis=1)
    x = np.minimum(1.0, np.divide(a, row, out=np.ones_like(a), where=row > 0))
    repaired = x[:, None] * plan
    column = repaired.sum(axis=0)
    y = np.minimum(1.0, np.divide(b, column, out=np.ones_like(b), where=column > 0))
    repaired *= y[None, :]
    ra = np.maximum(0.0, a - repaired.sum(axis=1))
    rb = np.maximum(0.0, b - repaired.sum(axis=0))
    missing = float(ra.sum())
    if missing > 0 and rb.sum() > 0:
        # The two deficit sums coincide in exact arithmetic. The numerical
        # imbalance is intentionally retained in the reported residual.
        repaired += np.outer(ra, rb) / missing
    return repaired


def local_sinkhorn(a, b, matrix, eps, cap=2000, tolerance=5e-11):
    f, g = np.zeros(len(a)), np.zeros(len(b))
    loga, logb = np.log(a), np.log(b)
    for iterations in range(1, cap + 1):
        f = eps * (loga - logsumexp((g[None, :] - matrix) / eps, axis=1))
        g = eps * (logb - logsumexp((f[:, None] - matrix) / eps, axis=0))
        plan = np.exp((f[:, None] + g[None, :] - matrix) / eps)
        residual = max(float(np.max(np.abs(plan.sum(axis=1) - a))),
                       float(np.max(np.abs(plan.sum(axis=0) - b))))
        if residual <= tolerance:
            break
    # f+eps/2, g+eps/2 are the potentials for x log x, without the -x term.
    dual = float(a @ f + b @ g + eps * (1.0 - plan.sum()))
    repaired = round_plan(plan, a, b)
    after = max(float(np.max(np.abs(repaired.sum(axis=1) - a))),
                float(np.max(np.abs(repaired.sum(axis=0) - b))))
    if not np.isfinite(repaired).all() or after > 1e-8 or repaired.min() < 0:
        raise RuntimeError('numerical feasibility repair failed')
    return repaired, g, dual, iterations, residual, after


def nested_probe(left, right, cost, eps=0.05):
    """Return numerical witnesses; the LP reference is never supplied here."""
    shape = (len(left.states[-1]), len(right.states[-1]))
    E, L, U, EP = [np.zeros(shape) for _ in range(4)]
    stats = {'local_solves': 0, 'iterations': 0, 'iteration_cap_hits': 0,
             'max_raw_marginal_residual': 0.0, 'max_repaired_marginal_residual': 0.0}

    def layer(ka, kb, c, E, L, U, EP):
        arrays = [np.empty((len(ka), len(kb))) for _ in range(4)]
        for i, aa in enumerate(ka):
            ia = aa > 0
            a = aa[ia].copy(); a /= a.sum()
            for j, bb in enumerate(kb):
                ib = bb > 0
                b = bb[ib].copy(); b /= b.sum()
                ix = np.ix_(ia, ib)
                ce, cl, cu, cp = [(c + v)[ix] for v in (E, L, U, EP)]
                q, g, de, it, before, after = local_sinkhorn(a, b, ce, eps)
                alpha = np.min(cl - g[None, :], axis=1)
                arrays[0][i, j] = de
                arrays[1][i, j] = max(0.0, float(a @ alpha + b @ g))
                arrays[2][i, j] = float(np.sum(q * cu))
                arrays[3][i, j] = float(np.sum(q * cp) - eps * entropy(q))
                stats['local_solves'] += 1
                stats['iterations'] += it
                stats['iteration_cap_hits'] += int(it == 2000)
                stats['max_raw_marginal_residual'] = max(stats['max_raw_marginal_residual'], before)
                stats['max_repaired_marginal_residual'] = max(stats['max_repaired_marginal_residual'], after)
        return arrays

    for t in range(left.horizon - 1, -1, -1):
        c = stage_cost(left.representatives[t + 1], right.representatives[t + 1], cost)
        E, L, U, EP = layer(left.kernels[t], right.kernels[t], c, E, L, U, EP)
    E, L, U, EP = layer(left.initial[None, :], right.initial[None, :],
                         np.zeros_like(E), E, L, U, EP)
    ha, hb = path_entropy(left), path_entropy(right)
    lower = max(0.0, float(L[0, 0]), float(E[0, 0]) + eps * max(ha, hb))
    return {'numeric_lower': lower, 'numeric_upper': float(U[0, 0]),
            'numeric_unregularized_dual_lower': float(L[0, 0]),
            'numeric_entropic_lower': float(E[0, 0]),
            'numeric_policy_entropic_upper': float(EP[0, 0]),
            'numeric_policy_path_entropy': float((U[0, 0] - EP[0, 0]) / eps),
            'path_entropy_left': ha, 'path_entropy_right': hb,
            'entropy_bias_upper': eps * (ha + hb), 'epsilon': eps,
            'certificate_frontier_eligible': False, **stats}


def unfold(model):
    """Unfold MODEL transitions, never replace them by raw empirical prefixes."""
    paths = [(i,) for i in range(len(model.states[0]))]
    states = [np.asarray(paths, dtype=np.int64)]
    reps = [model.representatives[0].copy()]
    kernels = []
    for t, kernel in enumerate(model.kernels):
        children = [(row, path + (int(j),), kernel[path[-1], j])
                    for row, path in enumerate(paths)
                    for j in np.flatnonzero(kernel[path[-1]] > 0)]
        outgoing = np.zeros((len(paths), len(children)))
        for col, (row, path, mass) in enumerate(children):
            outgoing[row, col] = mass
        paths = [path for _, path, _ in children]
        states.append(np.asarray(paths, dtype=np.int64))
        reps.append(np.asarray([model.representatives[t + 1][p[-1]] for p in paths]))
        kernels.append(outgoing)
    return replace(model, states=tuple(states), representatives=tuple(reps), kernels=tuple(kernels))


def main():
    base = Path(__file__).resolve().parents[1]
    fixtures = base / 'runs/cycle_1/pnot_cases.json'
    fixture_bytes = fixtures.read_bytes()
    rows = []
    for case in json.loads(fixture_bytes)['cases']:
        for k in (1, 2):
            started = time.perf_counter()
            left, right = [build_window_model(case[key], k, case['delta'], case['shift'])
                           for key in ('left', 'right')]
            model_seconds = time.perf_counter() - started
            ta, tb = unfold(left), unfold(right)
            for cost in ('absolute', 'squared'):
                started = time.perf_counter()
                row = nested_probe(left, right, cost)
                solver_seconds = time.perf_counter() - started
                tree = nested_probe(ta, tb, cost)
                reference = exact_dp(left, right, cost)
                tree_reference = exact_dp(ta, tb, cost)
                expected = case['expected'].get(f'k{k}_{cost}')
                difference = max(abs(row[field] - tree[field]) for field in
                                 ('numeric_lower', 'numeric_upper', 'numeric_entropic_lower'))
                passed = (row['numeric_lower'] <= reference + 1e-8
                          and reference <= row['numeric_upper'] + 1e-8
                          and difference <= 1e-8 and abs(reference-tree_reference) <= 1e-8
                          and (expected is None or abs(reference-expected) <= 1e-8))
                if not passed:
                    raise AssertionError((case['name'], k, cost, row, reference, tree_reference))
                rows.append({'case': case['name'], 'k': k, 'cost': cost,
                             'horizon': left.horizon, 'left_model_hash': left.model_hash,
                             'right_model_hash': right.model_hash, 'numerical_reference': reference,
                             'unfolded_tree_reference': tree_reference,
                             'dag_tree_witness_max_difference': difference,
                             'construction_seconds': model_seconds, 'solver_seconds': solver_seconds,
                             'end_to_end_development_seconds': model_seconds + solver_seconds,
                             'development_audit_pass': passed, **row})
    payload = {'schema': 'nested-sinkhorn-development-v1',
               'implementation': 'independent_reimplementation_not_author_code',
               'scientific_preregistration': 'not_claimed_development_only',
               'certification': 'float64_numerical_audit_only_no_outward_rounding',
               'qualified_full_domain_comparator': False, 'certificate_frontier_eligible': False,
               'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'common_model_sha256': hashlib.sha256((base/'adapters/common_model.py').read_bytes()).hexdigest(),
               'fixture_sha256': hashlib.sha256(fixture_bytes).hexdigest(),
               'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__,
               'timing_scope': 'development_only; diagnostics/oracles outside candidate timer; no warmup',
               'cases': rows}
    output = base/'runs/cycle_1/nested_sinkhorn_result.json'
    if output.exists():
        raise FileExistsError('preserve prior evidence; choose a new run filename')
    output.write_text(json.dumps(payload, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'output': str(output), 'development_rows': len(rows),
                      'all_pass': all(x['development_audit_pass'] for x in rows),
                      'certificate_frontier_eligible': False}))


if __name__ == '__main__':
    main()
