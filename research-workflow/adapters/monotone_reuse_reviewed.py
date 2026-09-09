"""Conservative local OT witness fixture; not a production/root certificate.

Inputs are converted to binary64 and those represented numbers are interpreted
as exact rationals. No numerical tolerance establishes feasibility, tightness,
or equality. ``value`` is an exact Fraction, never a rounded scalar certificate.
Independently normalized float marginals and ordinary LP witnesses often fail
this contract: rejection requests fallback and does NOT prove non-reusability.
HiGHS proposes a witness only. Exact verification decides acceptance.

Counters expose dense work and LP construction, not equivalent machine costs.
Fraction arithmetic and fresh LP setup make this a correctness fixture only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


@dataclass
class WorkCounts:
    input_scalar_entries: int = 0
    rational_conversions: int = 0
    witness_edge_visits: int = 0
    face_edge_visits: int = 0
    repaired_dense_entries: int = 0
    feasibility_lp_calls: int = 0
    feasibility_variables: int = 0
    feasibility_nonzeros: int = 0


@dataclass(frozen=True)
class ReuseResult:
    reusable: bool
    value: Fraction | None
    plan: np.ndarray | None
    reason: str
    work: WorkCounts = field(default_factory=WorkCounts)

    @property
    def tested_edges(self):
        """All audited/classified edge visits, NOT only surviving edges."""
        return self.work.witness_edge_visits + self.work.face_edge_visits


def _rational(array, work):
    work.rational_conversions += array.size
    return np.array([Fraction.from_float(float(x)) for x in array.flat],
                    dtype=object).reshape(array.shape)


def _inputs(a, b, matrix, delta, plan, alpha, beta, work):
    arrays = [np.asarray(x, dtype=float) for x in
              (a, b, matrix, delta, plan, alpha, beta)]
    a, b, matrix, delta, plan, alpha, beta = arrays
    if a.ndim != 1 or b.ndim != 1 or not a.size or not b.size:
        raise ValueError("marginals must be nonempty vectors")
    shape = (a.size, b.size)
    if any(x.shape != shape for x in (matrix, delta, plan)):
        raise ValueError("matrix, update and plan shapes must match marginals")
    if alpha.shape != a.shape or beta.shape != b.shape:
        raise ValueError("dual shapes must match marginals")
    work.input_scalar_entries = sum(x.size for x in arrays)
    if any(not np.isfinite(x).all() for x in arrays):
        raise ValueError("all inputs must be finite")
    if any((x < 0).any() for x in (a, b, delta, plan)):
        raise ValueError("marginals, update and plan must be nonnegative")
    return arrays, [_rational(x, work) for x in arrays]


def _witness(a, b, matrix, delta, plan, alpha, beta, work,
             require_zero_update=False):
    """Exact primal/dual check, including every marginal and support edge."""
    m, n = matrix.shape
    rows, cols = [Fraction(0)] * m, [Fraction(0)] * n
    primal = increment = Fraction(0)
    dual_feasible = nonnegative = True
    for i in range(m):
        for j in range(n):
            work.witness_edge_visits += 1
            mass = plan[i, j]
            nonnegative &= mass >= 0
            rows[i] += mass
            cols[j] += mass
            primal += mass * matrix[i, j]
            increment += mass * delta[i, j]
            dual_feasible &= alpha[i] + beta[j] <= matrix[i, j]
    if not nonnegative or rows != list(a) or cols != list(b):
        return None, "primal feasibility not certified exactly"
    dual = sum((a[i] * alpha[i] for i in range(m)), Fraction(0))
    dual += sum((b[j] * beta[j] for j in range(n)), Fraction(0))
    if not dual_feasible or primal != dual:
        return None, "old optimality not certified exactly"
    if require_zero_update and increment != 0:
        return None, "positive update on witness support"
    return dual, None


def _prepare(a, b, matrix, delta, plan, alpha, beta):
    work = WorkCounts()
    arrays, rational = _inputs(a, b, matrix, delta, plan, alpha, beta, work)
    if sum(rational[0], Fraction(0)) != sum(rational[1], Fraction(0)):
        return arrays, rational, work, None, "represented marginal totals differ"
    value, reason = _witness(*rational, work)
    return arrays, rational, work, value, reason


def support_miss_reuse(a, b, matrix, delta, plan, alpha, beta):
    arrays, rational, work, value, reason = _prepare(
        a, b, matrix, delta, plan, alpha, beta)
    if reason:
        return ReuseResult(False, None, None, reason, work)
    value, reason = _witness(*rational, work, require_zero_update=True)
    if reason:
        return ReuseResult(False, None, None, reason, work)
    return ReuseResult(True, value, arrays[4].copy(),
                       "exact represented-input primal-dual certificate", work)


def optimal_face_reuse(a, b, matrix, delta, plan, alpha, beta):
    arrays, rational, work, value, reason = _prepare(
        a, b, matrix, delta, plan, alpha, beta)
    if reason:
        return ReuseResult(False, None, None, reason, work)
    qa, qb, qm, qd, qp, qalpha, qbeta = rational
    m, n = qm.shape
    edges = []
    for i in range(m):
        for j in range(n):
            work.face_edge_visits += 1
            if (qm[i, j] == qalpha[i] + qbeta[j] and qd[i, j] == 0
                    and qa[i] > 0 and qb[j] > 0):
                edges.append((i, j))
    # The empty plan is a certificate for the allowed zero-total problem.
    if sum(qa, Fraction(0)) == 0:
        return ReuseResult(True, value, arrays[4].copy(), "zero total mass", work)
    if not edges:
        return ReuseResult(False, None, None, "no unchanged exact-tight edge", work)
    rows, cols = [], []
    for q, (i, j) in enumerate(edges):
        rows.extend((i, m + j))
        cols.extend((q, q))
    constraints = coo_matrix((np.ones(2 * len(edges)), (rows, cols)),
                             shape=(m + n, len(edges))).tocsr()
    work.feasibility_lp_calls = 1
    work.feasibility_variables = len(edges)
    work.feasibility_nonzeros = 2 * len(edges)
    result = linprog(np.zeros(len(edges)), A_eq=constraints,
                     b_eq=np.concatenate(arrays[:2]), bounds=(0, None),
                     method="highs")
    if not result.success:
        return ReuseResult(False, None, None,
                           "LP supplied no candidate; exact infeasibility unproved", work)
    if (np.shape(result.x) != (len(edges),)
            or not np.isfinite(result.x).all() or (result.x < 0).any()):
        return ReuseResult(False, None, None, "invalid LP candidate", work)
    repaired = np.zeros_like(arrays[2])
    work.repaired_dense_entries = repaired.size
    for q, (i, j) in enumerate(edges):
        repaired[i, j] = result.x[q]
    value, reason = _witness(qa, qb, qm, qd, _rational(repaired, work),
                             qalpha, qbeta, work, require_zero_update=True)
    if reason:
        return ReuseResult(False, None, None, "LP candidate: " + reason, work)
    return ReuseResult(True, value, repaired,
                       "exact represented-input alternative-face certificate", work)
