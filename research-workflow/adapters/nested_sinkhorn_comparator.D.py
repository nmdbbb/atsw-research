"""Lane D: certified nested/adapted Sinkhorn comparator on the tiny common-model targets.

EXTENDS ``nested_sinkhorn_probe`` (imported, not rewritten): its ``round_plan``,
``entropy``, ``path_entropy`` and ``unfold`` are reused unchanged. What this file
adds is a *two-sided root certificate* and honest work/time accounting.

Model contract (from ``common_model``): paths are (samples, T+1) including time
zero; the objective sums stage costs at times 1..T with NO time-zero cost; the
two explicit initial distributions are coupled by a root OT problem with zero
stage cost. Nothing here selects a modal root.

Certificate semantics
---------------------
Let ``V_t(i,j) = OT(K^A_t(i,.), K^B_t(j,.); c_{t+1} + V_{t+1})`` and
``V = OT(mu^A, mu^B; V_0)``. Two facts drive the certificate:

1. ``OT(a,b;.)`` is monotone nondecreasing in the cost matrix entrywise. So if
   ``Lo_{t+1} <= V_{t+1} <= Up_{t+1}`` entrywise then every local problem solved
   with ``c+Lo_{t+1}`` (resp. ``c+Up_{t+1}``) brackets the local true value.
2. At each node, a dual-feasible pair for ``c+Lo_{t+1}`` gives a LOWER bound and
   an exactly feasible plan evaluated against ``c+Up_{t+1}`` gives an UPPER bound.

The Sinkhorn potential ``g`` is turned into a dual-feasible pair by the
c-transform ``phi_i = min_j (c+Lo)_{ij} - g_j``, and the feasibility inequality
``phi_i + g_j <= (c+Lo)_{ij}`` is then RE-VERIFIED numerically and shifted down by
the observed violation if any. The Sinkhorn plan is repaired to feasibility by the
probe's ``round_plan``; the residual marginal infeasibility ``eta`` (L1) is measured
and an outward slack ``2*eta*max(c+Up)`` is added to the upper bound, since moving
at most ``eta`` mass to reach an exactly feasible plan changes the cost by at most
``eta * max(cost)`` and doubling covers both the removal and the re-insertion.

Therefore ``[root_lower, root_upper]`` is a bound AT THE ROOT for the finite-model
value, obtained by valid propagation -- not a per-node measured discrepancy, and
not a comparison against any reference. The LP reference is computed only AFTER the
comparator finishes and is never available to it.

Limits, stated once and not weakened elsewhere: all arithmetic is float64. The
inequality *structure* is exact and the two slack terms above are verified
quantities, but floating-point rounding of the summations themselves is NOT
outward-rounded. This is a numerically audited certificate, not an interval-
arithmetic proof. No SOTA, frontier-eligibility or performance claim follows from
this file; the eps schedule is a development choice, and the LP reference
``exact_dp`` is itself a numerical solve, so containment is validation.

Run: python -B adapters/nested_sinkhorn_comparator.D.py
Writes: runs/cycle_1/D/sinkhorn_tiny.json  (create-new only; refuses to overwrite)
"""

from pathlib import Path
import hashlib
import json
import platform
import sys
import time

import numpy as np
import scipy
from scipy.special import logsumexp

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from common_model import build_window_model, exact_dp, stage_cost  # noqa: E402
import nested_sinkhorn_probe as probe  # noqa: E402

EPS_SCHEDULE = (5e-2, 1e-2, 5e-3, 1e-3, 5e-4, 1e-4)

# Stopping rule, declared before the run with its rationale, not tuned after it.
# The Sinkhorn plan is repaired to exact feasibility before it is used, so the raw
# marginal residual r only has to be small RELATIVE to the entropic bias it sits
# inside: it perturbs the upper bound by at most O(r * max cost), while the
# entropic bias of the plan itself is O(eps). Chasing r below a fixed fraction of
# eps therefore buys nothing, and for degenerate local problems it is unaffordable
# (Sinkhorn's contraction rate is 1 - exp(-range/eps), which at small eps leaves an
# effectively sublinear O(1/iterations) decay).
#
# No stagnation/early-exit heuristic is used, deliberately. These local problems
# show a LONG PLATEAU: the marginal residual sits at a constant value for
# Theta(1/eps) iterations and then drops quickly. Any "no progress" rule cuts the
# run inside that plateau and silently returns a badly unconverged plan, which
# loosens the upper bound (it never invalidates it). The iteration budget is
# therefore explicit and its exhaustion is counted and reported.
RESIDUAL_FRACTION = 1e-2
ABSOLUTE_RESIDUAL_FLOOR = 1e-12
ITERATION_BUDGET = 250000


def marginal_tolerance(eps):
    return max(ABSOLUTE_RESIDUAL_FLOOR, RESIDUAL_FRACTION * eps)
MATCH_TOLERANCE = 1e-9
RELATIVE_TARGET = 0.005


class WorkCounter:
    """Separate counters: subproblems solved, Sinkhorn iterations, audits."""

    def __init__(self):
        self.subproblems = 0
        self.iterations = 0
        self.cap_hits = 0
        self.tolerance_stops = 0
        self.hardest = None  # (iterations, a, b, matrix) of the costliest subproblem
        self.total_raw_marginal_l1 = 0.0
        self.max_raw_marginal_residual = 0.0
        self.max_repaired_marginal_residual = 0.0
        self.max_dual_feasibility_violation = 0.0
        self.total_upper_outward_slack = 0.0
        self.max_local_interval_width = 0.0

    def asdict(self):
        return {'subproblems_solved': self.subproblems,
                'sinkhorn_iterations': self.iterations,
                'iteration_budget_exhausted_count': self.cap_hits,
                'tolerance_stops': self.tolerance_stops,
                'hardest_subproblem_iterations':
                    0 if self.hardest is None else self.hardest[0],
                'total_raw_marginal_l1_before_repair': self.total_raw_marginal_l1,
                'max_raw_marginal_residual': self.max_raw_marginal_residual,
                'max_repaired_marginal_residual': self.max_repaired_marginal_residual,
                'max_dual_feasibility_violation_before_shift':
                    self.max_dual_feasibility_violation,
                'total_upper_outward_slack': self.total_upper_outward_slack,
                'max_local_interval_width': self.max_local_interval_width}


def sinkhorn_log(a, b, matrix, eps, cap=ITERATION_BUDGET, tolerance=None):
    """Log-domain symmetric Sinkhorn. Returns potentials, plan and work done.

    Same recursion as the probe's ``local_sinkhorn``, with three changes made for
    this comparator: both potentials are returned, the budget/tolerance live in
    this file (the probe's fixed development choices are not reinterpreted), and
    the stopping reason is reported so the work counts stay interpretable.

    Two float64 facts, both measured on these fixtures rather than assumed:
    the plan is reconstructed as ``exp((f_i+g_j-M_ij)/eps)``, so rounding in the
    exponent is amplified by ``1/eps`` and the attainable marginal residual floors
    at roughly ``machine_eps/eps``; and the residual sits on a constant plateau for
    Theta(1/eps) iterations before dropping. Wherever the iteration stops, both
    root bounds remain valid -- the lower bound is re-verified dual-feasible and the
    upper bound is evaluated on a repaired feasible plan -- so stopping early costs
    tightness only.
    """
    if tolerance is None:
        tolerance = marginal_tolerance(eps)
    f, g = np.zeros(len(a)), np.zeros(len(b))
    loga, logb = np.log(a), np.log(b)
    plan = None
    residual = np.inf
    iterations = 0
    reason = 'budget_exhausted'
    for iterations in range(1, cap + 1):
        f = eps * (loga - logsumexp((g[None, :] - matrix) / eps, axis=1))
        g = eps * (logb - logsumexp((f[:, None] - matrix) / eps, axis=0))
        plan = np.exp((f[:, None] + g[None, :] - matrix) / eps)
        residual = max(float(np.max(np.abs(plan.sum(axis=1) - a))),
                       float(np.max(np.abs(plan.sum(axis=0) - b))))
        if residual <= tolerance:
            reason = 'tolerance'
            break
    return f, g, plan, iterations, residual, reason


def certified_local(a, b, lower_cost, upper_cost, driving_cost, eps, counter):
    """One local subproblem -> a verified two-sided bracket for its OT value.

    ``lower_cost``/``upper_cost`` must already bracket the true local cost matrix
    (i.e. c + Lo_child and c + Up_child). ``driving_cost`` is what Sinkhorn is
    actually run on; validity does not depend on that choice.
    """
    f, g, raw_plan, iterations, residual, reason = sinkhorn_log(
        a, b, driving_cost, eps)
    counter.subproblems += 1
    counter.iterations += iterations
    counter.cap_hits += int(reason == 'budget_exhausted')
    counter.tolerance_stops += int(reason == 'tolerance')
    if counter.hardest is None or iterations > counter.hardest[0]:
        counter.hardest = (iterations, a.copy(), b.copy(), driving_cost.copy())
    counter.max_raw_marginal_residual = max(
        counter.max_raw_marginal_residual, residual)
    # Deficit accounting: this is what the feasibility repair has to move, and it
    # is the mechanism that floors the certified upper bound.
    counter.total_raw_marginal_l1 += (
        float(np.sum(np.abs(raw_plan.sum(axis=1) - a)))
        + float(np.sum(np.abs(raw_plan.sum(axis=0) - b))))

    # LOWER: c-transform of g against lower_cost, then verify the dual
    # inequality and shift phi down by any observed violation.
    phi = np.min(lower_cost - g[None, :], axis=1)
    violation = float(np.min(lower_cost - phi[:, None] - g[None, :]))
    counter.max_dual_feasibility_violation = max(
        counter.max_dual_feasibility_violation, -min(0.0, violation))
    if violation < 0.0:
        phi = phi + violation
    lower = float(a @ phi + b @ g)
    lower = max(0.0, lower)  # stage costs are nonnegative, so V >= 0

    # UPPER: repair the plan to feasibility (probe's exact-arithmetic formula),
    # measure the remaining L1 marginal infeasibility, add an outward slack.
    plan = probe.round_plan(raw_plan, a, b)
    if not np.isfinite(plan).all() or plan.min() < 0.0:
        raise RuntimeError('feasibility repair produced an invalid plan')
    eta = (float(np.sum(np.abs(plan.sum(axis=1) - a)))
           + float(np.sum(np.abs(plan.sum(axis=0) - b))))
    repaired_residual = max(float(np.max(np.abs(plan.sum(axis=1) - a))),
                            float(np.max(np.abs(plan.sum(axis=0) - b))))
    counter.max_repaired_marginal_residual = max(
        counter.max_repaired_marginal_residual, repaired_residual)
    slack = 2.0 * eta * float(np.max(upper_cost))
    counter.total_upper_outward_slack += slack
    upper = float(np.sum(plan * upper_cost)) + slack

    # Entropic nested value, propagated only to drive the next layer's Sinkhorn.
    entropic = float(a @ f + b @ g + eps * (1.0 - raw_plan.sum()))

    if upper < lower:
        # A crossed bracket would invalidate the certificate; keep it visible
        # instead of clipping it away.
        counter.max_local_interval_width = max(
            counter.max_local_interval_width, upper - lower)
        raise RuntimeError(f'local bracket crossed: lower={lower} upper={upper}')
    counter.max_local_interval_width = max(
        counter.max_local_interval_width, upper - lower)
    return lower, upper, entropic


def _layer(left_rows, right_rows, cost, lo_child, up_child, en_child, eps, counter):
    shape = (len(left_rows), len(right_rows))
    lo, up, en = (np.empty(shape) for _ in range(3))
    lower_cost, upper_cost = cost + lo_child, cost + up_child
    driving_cost = cost + en_child
    for i, row_a in enumerate(left_rows):
        support_a = row_a > 0
        a = row_a[support_a].copy()
        a /= a.sum()  # corrects summation roundoff only
        for j, row_b in enumerate(right_rows):
            support_b = row_b > 0
            b = row_b[support_b].copy()
            b /= b.sum()
            ix = np.ix_(support_a, support_b)
            lo[i, j], up[i, j], en[i, j] = certified_local(
                a, b, lower_cost[ix], upper_cost[ix], driving_cost[ix],
                eps, counter)
    return lo, up, en


def certified_nested_sinkhorn(left, right, cost, eps):
    """Backward nested Sinkhorn carrying a valid lower/upper pair to the root.

    The LP reference is never read here. Returns the root bracket plus the work
    counters for THIS eps level only.
    """
    if left.horizon != right.horizon:
        raise ValueError('models must have the same horizon')
    counter = WorkCounter()
    shape = (len(left.states[-1]), len(right.states[-1]))
    lo, up, en = (np.zeros(shape) for _ in range(3))
    for t in range(left.horizon - 1, -1, -1):
        cost_matrix = stage_cost(left.representatives[t + 1],
                                 right.representatives[t + 1], cost)
        lo, up, en = _layer(left.kernels[t], right.kernels[t], cost_matrix,
                            lo, up, en, eps, counter)
        if (lo > up + 1e-12).any():
            raise RuntimeError(f'layer {t} bracket crossed')
    # Root: explicit initial distributions, zero stage cost at time zero.
    lo, up, en = _layer(left.initial[None, :], right.initial[None, :],
                        np.zeros_like(lo), lo, up, en, eps, counter)
    left_entropy, right_entropy = probe.path_entropy(left), probe.path_entropy(right)
    return {'_hardest_subproblem': counter.hardest,
            'root_lower': float(lo[0, 0]), 'root_upper': float(up[0, 0]),
            'root_entropic_value': float(en[0, 0]),
            'entropy_bias_upper_reference': eps * (left_entropy + right_entropy),
            'path_entropy_left': left_entropy, 'path_entropy_right': right_entropy,
            **counter.asdict()}


def cost_law_probe(a, b, matrix, eps_list=(1e-3, 3e-4, 1e-4), budget=250000):
    """Measure iterations-to-tolerance versus eps on ONE local subproblem.

    This is the mechanism measurement behind the width/work tradeoff: the root
    interval width is O(eps), so if iterations-to-tolerance grows like 1/eps then
    the work needed for a root interval of width w grows like 1/w. The probe
    reports the raw counts and the products; it does not assume the law.
    """
    rows = []
    for eps in eps_list:
        tolerance = marginal_tolerance(eps)
        started = time.perf_counter()
        _, _, _, iterations, residual, reason = sinkhorn_log(
            a, b, matrix, eps, cap=budget, tolerance=tolerance)
        rows.append({'epsilon': eps, 'tolerance': tolerance,
                     'iterations': iterations, 'final_residual': residual,
                     'stop_reason': reason,
                     'iterations_times_epsilon': iterations * eps,
                     'seconds': time.perf_counter() - started})
    reached = [r for r in rows if r['stop_reason'] == 'tolerance']
    products = [r['iterations_times_epsilon'] for r in reached]
    return {'subproblem_shape': [len(a), len(b)],
            'left_marginal': a.tolist(), 'right_marginal': b.tolist(),
            'driving_cost_matrix': matrix.tolist(),
            'levels': rows,
            'iterations_times_epsilon_range':
                [min(products), max(products)] if products else None,
            'product_is_constant_within_1_percent': bool(
                products and (max(products) - min(products)) <= 0.01 * max(products)),
            'extrapolated_iterations_for_epsilon_1e-9':
                (sum(products) / len(products)) / 1e-9 if products else None,
            'interpretation': 'iterations-to-tolerance ~ C/epsilon on this '
                              'subproblem; combined with an O(epsilon) root '
                              'interval width this makes the work for a width-w '
                              'certificate scale like 1/w'}


def run_case(paths_left, paths_right, k, delta, shift, cost):
    """One tiny instance, all eps levels. The candidate clock covers everything.

    ``construction_seconds`` is inside the reported end-to-end time; the LP
    reference is timed separately and is outside the candidate clock.
    """
    from_paths_start = time.perf_counter()
    left = build_window_model(paths_left, k, delta, shift)
    right = build_window_model(paths_right, k, delta, shift)
    construction_seconds = time.perf_counter() - from_paths_start

    levels = []
    hardest = None
    for eps in EPS_SCHEDULE:
        level_start = time.perf_counter()
        result = certified_nested_sinkhorn(left, right, cost, eps)
        solver_seconds = time.perf_counter() - level_start
        candidate = result.pop('_hardest_subproblem')
        if candidate is not None and (hardest is None or candidate[0] > hardest[0]):
            hardest = candidate
        cumulative_seconds = time.perf_counter() - from_paths_start
        width = result['root_upper'] - result['root_lower']
        relative = (width / result['root_lower']
                    if result['root_lower'] > 0 else None)
        levels.append({'epsilon': eps, **result, 'root_interval_width': width,
                       'relative_root_interval_width': relative,
                       'solver_and_certification_seconds': solver_seconds,
                       'standalone_end_to_end_seconds_from_paths':
                           construction_seconds + solver_seconds,
                       'cumulative_schedule_seconds_from_paths': cumulative_seconds})

    reference_start = time.perf_counter()
    reference = exact_dp(left, right, cost)
    reference_seconds = time.perf_counter() - reference_start

    for level in levels:
        level['contains_numerical_reference'] = bool(
            level['root_lower'] <= reference and reference <= level['root_upper'])
        level['reference_minus_lower'] = reference - level['root_lower']
        level['upper_minus_reference'] = level['root_upper'] - reference
        level['max_endpoint_deviation_from_reference'] = max(
            abs(level['root_lower'] - reference), abs(level['root_upper'] - reference))

    matched = [x for x in levels
               if x['contains_numerical_reference']
               and x['root_interval_width'] <= MATCH_TOLERANCE]
    relative_ok = [x for x in levels if x['relative_root_interval_width'] is not None
                   and x['relative_root_interval_width'] <= RELATIVE_TARGET]
    return {'k': k, 'cost': cost, 'delta': delta, 'shift': shift,
            'horizon': left.horizon,
            'left_model_hash': left.model_hash, 'right_model_hash': right.model_hash,
            'left_state_counts': [int(len(s)) for s in left.states],
            'right_state_counts': [int(len(s)) for s in right.states],
            'numerical_lp_reference': reference,
            'reference_seconds_outside_candidate_clock': reference_seconds,
            'representation_construction_seconds': construction_seconds,
            'total_schedule_seconds_from_paths':
                levels[-1]['cumulative_schedule_seconds_from_paths'],
            'total_subproblems_over_schedule':
                sum(x['subproblems_solved'] for x in levels),
            'total_iterations_over_schedule':
                sum(x['sinkhorn_iterations'] for x in levels),
            'subproblems_per_level': levels[0]['subproblems_solved'],
            'containment_holds_at_every_epsilon':
                all(x['contains_numerical_reference'] for x in levels),
            'brackets_are_monotone_in_epsilon': bool(
                all(levels[i + 1]['root_lower'] >= levels[i]['root_lower'] - 1e-12
                    and levels[i + 1]['root_upper'] <= levels[i]['root_upper'] + 1e-12
                    for i in range(len(levels) - 1))),
            'first_epsilon_matching_reference_within_1e-9':
                matched[0]['epsilon'] if matched else None,
            'seconds_to_1e-9_certificate_including_all_prior_epsilon':
                matched[0]['cumulative_schedule_seconds_from_paths'] if matched else None,
            'first_epsilon_meeting_0.005_relative_root_gap':
                relative_ok[0]['epsilon'] if relative_ok else None,
            'zero_value_instance_relative_gap_undefined':
                bool(levels[-1]['root_lower'] <= 0.0),
            'degenerate_bracket_closed_at_coarsest_epsilon':
                bool(levels[0]['root_interval_width'] <= MATCH_TOLERANCE),
            'levels': levels,
            '_hardest_subproblem': hardest}


def main():
    base = _HERE.parent
    fixtures = base / 'runs/cycle_1/pnot_cases.json'
    fixture_bytes = fixtures.read_bytes()
    cases = json.loads(fixture_bytes)['cases']
    rows = []
    for case in cases:
        for k in (1, 2):
            for cost in ('absolute', 'squared'):
                row = run_case(case['left'], case['right'], k, case['delta'],
                               case['shift'], cost)
                rows.append({'case': case['name'], **row})

    # Cost-law probe on the globally costliest local subproblem seen above.
    hardest, owner = None, None
    for row in rows:
        candidate = row.pop('_hardest_subproblem')
        if candidate is not None and (hardest is None or candidate[0] > hardest[0]):
            hardest, owner = candidate, f"{row['case']}|k{row['k']}|{row['cost']}"
    probe_start = time.perf_counter()
    law = cost_law_probe(hardest[1], hardest[2], hardest[3])
    law['seconds_total'] = time.perf_counter() - probe_start
    law['extracted_from_instance'] = owner
    law['observed_iterations_in_main_grid'] = hardest[0]

    try:
        import ot
        pot_version = ot.__version__
    except Exception:  # pragma: no cover - recorded as unavailable, not skipped
        pot_version = 'unavailable'

    matched_rows = [x for x in rows
                    if x['first_epsilon_matching_reference_within_1e-9'] is not None]
    payload = {
        'schema': 'nested-sinkhorn-certified-comparator-D-v1',
        'lane': 'D',
        'implementation': 'independent_reimplementation_extending_nested_sinkhorn_probe',
        'scientific_preregistration': 'not_claimed_comparator_qualification_only',
        'certificate_kind': 'two_sided_bound_at_root_by_valid_propagation',
        'two_sided_certificate_available': True,
        'two_sided_certificate_reason':
            'Available, and the run reports whether it actually held. The argument '
            'has two ingredients and neither is a measured error at a node. (i) OT '
            'is monotone nondecreasing in its cost matrix entrywise, so bracketing '
            'the continuation value brackets every local value, and the bracket '
            'propagates backward from t=T through the explicit root OT on the two '
            'initial laws. (ii) At each node a lower bound comes from a pair that is '
            'dual-FEASIBLE for c+Lo_child (the c-transform of the Sinkhorn column '
            'potential, with the inequality re-verified and shifted down by any '
            'observed violation), and an upper bound from a PRIMAL-FEASIBLE plan '
            'evaluated against c+Up_child (the repaired Sinkhorn plan, plus an '
            'outward slack 2*eta*max(cost) for its measured L1 marginal residual). '
            'Neither ingredient needs the Sinkhorn iteration to have converged, so a '
            'stopped iterate still yields a valid root interval; only the WIDTH '
            'depends on convergence. What is NOT available is a tight one: see '
            'summary and cost_law_probe.',
        'certificate_construction': {
            'lower': 'c-transform of the Sinkhorn column potential against c+Lo_child, '
                     'dual inequality re-verified and shifted down by any violation',
            'upper': 'rounded feasible plan evaluated against c+Up_child, plus '
                     '2*eta*max(cost) outward slack for the measured L1 marginal residual',
            'validity_argument': 'entrywise monotonicity of OT in its cost matrix, '
                                 'applied backward from t=T to the explicit root OT',
            'not_a_local_node_error': True,
            'reference_value_available_to_candidate': False},
        'arithmetic_limits': 'float64; inequality structure and both slack terms are '
                             'verified quantities, but summation rounding is not '
                             'outward-rounded. Numerically audited certificate, not '
                             'interval arithmetic.',
        'objective_units': 'V = sum of stage costs at t=1..T on the finite window model; '
                           'no time-zero cost; explicit initial laws coupled at the root.',
        'timing_scope': 'candidate clock starts at raw paths and includes model '
                        'construction, all Sinkhorn solves, plan repair and '
                        'certification; the LP reference and all diagnostics are '
                        'outside it; no warm start between epsilon levels (cold start '
                        'per level, cumulative schedule time also reported)',
        'qualified_full_domain_comparator': False,
        'certificate_frontier_eligible': False,
        'epsilon_schedule': list(EPS_SCHEDULE),
        'stopping_rule': {
            'iteration_budget_per_subproblem': ITERATION_BUDGET,
            'marginal_tolerance': f'max({ABSOLUTE_RESIDUAL_FLOOR}, '
                                  f'{RESIDUAL_FRACTION}*epsilon)',
            'stagnation_heuristic': 'none, deliberately: the residual plateaus for '
                                    'Theta(1/epsilon) iterations before dropping, so '
                                    'a no-progress rule cuts inside the plateau and '
                                    'returns an unconverged plan',
            'rationale': 'the plan is repaired to exact feasibility before use, so '
                         'the raw marginal residual only needs to be small relative '
                         'to the O(epsilon) entropic bias it sits inside; validity of '
                         'both bounds does not depend on where the iteration stops'},
        'match_tolerance': MATCH_TOLERANCE,
        'relative_target': RELATIVE_TARGET,
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'probe_sha256': hashlib.sha256(
            (base / 'adapters/nested_sinkhorn_probe.py').read_bytes()).hexdigest(),
        'common_model_sha256': hashlib.sha256(
            (base / 'adapters/common_model.py').read_bytes()).hexdigest(),
        'fixture_sha256': hashlib.sha256(fixture_bytes).hexdigest(),
        'python': platform.python_version(),
        'numpy': np.__version__, 'scipy': scipy.__version__, 'pot': pot_version,
        'summary': {
            'instances': len(rows),
            'containment_holds_everywhere': all(
                x['containment_holds_at_every_epsilon'] for x in rows),
            'instances_matching_reference_within_1e-9': len(matched_rows),
            'instances_not_matching_within_1e-9': [
                x['case'] + f"|k{x['k']}|{x['cost']}" for x in rows
                if x['first_epsilon_matching_reference_within_1e-9'] is None],
            'largest_final_root_interval_width': max(
                x['levels'][-1]['root_interval_width'] for x in rows),
            'largest_final_max_endpoint_deviation': max(
                x['levels'][-1]['max_endpoint_deviation_from_reference'] for x in rows),
            'total_subproblems_all_instances': sum(
                x['total_subproblems_over_schedule'] for x in rows),
            'total_iterations_all_instances': sum(
                x['total_iterations_over_schedule'] for x in rows),
            'total_candidate_seconds_all_instances': sum(
                x['total_schedule_seconds_from_paths'] for x in rows),
            'iteration_budget_exhausted_anywhere': any(
                level['iteration_budget_exhausted_count'] > 0
                for x in rows for level in x['levels']),
            'max_raw_marginal_residual_anywhere': max(
                level['max_raw_marginal_residual']
                for x in rows for level in x['levels']),
            'max_repaired_marginal_residual_anywhere': max(
                level['max_repaired_marginal_residual']
                for x in rows for level in x['levels']),
            'max_dual_feasibility_violation_anywhere': max(
                level['max_dual_feasibility_violation_before_shift']
                for x in rows for level in x['levels']),
            'zero_value_instances': [
                x['case'] + f"|k{x['k']}|{x['cost']}" for x in rows
                if x['zero_value_instance_relative_gap_undefined']],
            'instances_whose_bracket_was_already_closed_at_epsilon_5e-2': [
                x['case'] + f"|k{x['k']}|{x['cost']}" for x in rows
                if x['degenerate_bracket_closed_at_coarsest_epsilon']],
            'match_within_1e-9_is_not_evidence_of_epsilon_to_zero_convergence':
                'On instances whose local problems are degenerate (deterministic '
                'transitions or tied cost rows) the bracket is already exactly '
                'closed at epsilon=5e-2, so a 1e-9 match there reflects the '
                'instance, not convergence of the method.'},
        'cost_law_probe': law,
        'cases': rows}

    output = base / 'runs/cycle_1/D/sinkhorn_tiny.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'x', encoding='utf-8') as handle:
        handle.write(json.dumps(payload, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'output': str(output), **payload['summary']}, indent=2))


if __name__ == '__main__':
    main()
