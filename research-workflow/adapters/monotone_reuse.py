"""Exact-witness probes for monotone local transport-cost updates.

These routines audit reusable primal/dual certificates on one OT block.  They
are fixture tools, not outward-rounded production certificates.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


@dataclass(frozen=True)
class ReuseResult:
    reusable: bool
    value: float | None
    plan: np.ndarray | None
    tested_edges: int
    reason: str


def _audit_inputs(a, b, matrix, delta, plan, alpha, beta, tol):
    a, b = np.asarray(a, float), np.asarray(b, float)
    matrix, delta = np.asarray(matrix, float), np.asarray(delta, float)
    plan = np.asarray(plan, float)
    alpha, beta = np.asarray(alpha, float), np.asarray(beta, float)
    if matrix.shape != (len(a), len(b)) or delta.shape != matrix.shape or plan.shape != matrix.shape:
        raise ValueError("matrix, update and plan shapes do not match marginals")
    if (delta < -tol).any():
        raise ValueError("reuse rule requires a nonnegative update")
    if (np.max(np.abs(plan.sum(1) - a)) > tol or
            np.max(np.abs(plan.sum(0) - b)) > tol or plan.min(initial=0) < -tol):
        raise ValueError("cached primal is infeasible")
    if np.max(alpha[:, None] + beta[None, :] - matrix) > tol:
        raise ValueError("cached dual is infeasible")
    primal = float(np.sum(plan * matrix))
    dual = float(a @ alpha + b @ beta)
    if abs(primal - dual) > tol * max(1.0, abs(primal), abs(dual)):
        raise ValueError("cached witnesses do not establish old optimality")
    return a, b, matrix, np.maximum(delta, 0.0), plan, alpha, beta, dual


def support_miss_reuse(a, b, matrix, delta, plan, alpha, beta, tol=1e-10):
    """Reuse the cached plan when its expected monotone increment is zero."""
    a, b, matrix, delta, plan, alpha, beta, dual = _audit_inputs(
        a, b, matrix, delta, plan, alpha, beta, tol)
    increment = float(np.sum(plan * delta))
    if increment > tol:
        return ReuseResult(False, None, None, int(np.count_nonzero(plan > tol)),
                           "cached support is hit")
    return ReuseResult(True, dual, plan.copy(), int(np.count_nonzero(plan > tol)),
                       "old primal-dual equality survives")


def optimal_face_reuse(a, b, matrix, delta, plan, alpha, beta, tol=1e-10):
    """Search the old zero-reduced-cost face for a plan avoiding the update.

    Feasibility is solved only on edges that are dual-tight for the old problem
    and have zero increment.  A feasible plan has old dual value and incurs no
    update, hence certifies the new optimum without solving the updated OT.
    """
    a, b, matrix, delta, plan, alpha, beta, dual = _audit_inputs(
        a, b, matrix, delta, plan, alpha, beta, tol)
    reduced = matrix - alpha[:, None] - beta[None, :]
    allowed = (reduced <= tol) & (delta <= tol)
    allowed &= (a[:, None] > 0) & (b[None, :] > 0)
    edges = np.argwhere(allowed)
    if not len(edges):
        return ReuseResult(False, None, None, 0, "no unchanged dual-tight edge")
    rows, cols, data = [], [], []
    for q, (i, j) in enumerate(edges):
        rows.extend((int(i), len(a) + int(j)))
        cols.extend((q, q))
        data.extend((1.0, 1.0))
    constraints = coo_matrix((data, (rows, cols)),
                             shape=(len(a) + len(b), len(edges))).tocsr()
    result = linprog(np.zeros(len(edges)), A_eq=constraints,
                     b_eq=np.concatenate((a, b)), bounds=(0, None), method="highs")
    if not result.success:
        return ReuseResult(False, None, None, len(edges),
                           "unchanged old optimal face cannot carry the marginals")
    repaired = np.zeros_like(matrix)
    repaired[edges[:, 0], edges[:, 1]] = result.x
    if abs(float(np.sum(repaired * (matrix + delta))) - dual) > 10 * tol:
        raise RuntimeError("face-reuse witness failed objective audit")
    return ReuseResult(True, dual, repaired, len(edges),
                       "alternative old-optimal plan avoids the update")
