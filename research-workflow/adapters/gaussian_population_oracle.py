"""Gaussian population AW2 squared oracle; not a finite-model solver reference.

Gunasingam--Wong, Theorem 1.1, arXiv:2404.06625v4 / 10.1214/25-ECP654.
Natural filtration, scalar coordinates and sum of squared stage costs only.
Formulas are evaluated in float64, not outward-rounded certificates.
"""
from __future__ import annotations

import numpy as np


def ar1_factor(T, a, sigma):
    """Innovation Cholesky factor for X_1..X_T given deterministic X_0=0.

    Omitting the shared deterministic zero coordinate preserves the target
    and avoids applying the nondegenerate theorem to a singular covariance.
    """
    if isinstance(T, (bool, np.bool_)) or not isinstance(T, (int, np.integer)) or T < 1:
        raise ValueError("T must be a positive integer")
    if not np.isfinite(a) or not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("a must be finite and sigma strictly positive finite")
    factor = np.zeros((T, T))
    for j in range(T):
        factor[j:, j] = sigma * np.power(float(a), np.arange(T-j))
    if not np.isfinite(factor).all():
        raise ValueError("innovation factor overflow")
    return factor


def gaussian_aw2_from_factors(left, right, mean_left=None, mean_right=None):
    """Return population AW2², sequential KR cost and KR suboptimality gap.

    Inputs are lower Cholesky factors, NOT arbitrary covariance square roots.
    The sign-aligned sum of squares avoids cancellation in the trace formula.
    """
    left, right = np.asarray(left, float), np.asarray(right, float)
    if left.ndim != 2 or left.shape[0] == 0 or left.shape[0] != left.shape[1] or right.shape != left.shape:
        raise ValueError("factors must be matching nonempty square matrices")
    for factor in (left, right):
        if (not np.isfinite(factor).all() or np.any(np.triu(factor, 1) != 0)
                or np.any(np.diag(factor) <= 0)):
            raise ValueError("require finite lower Cholesky factors with positive diagonal")
    T = len(left)
    means = []
    for mean in (mean_left, mean_right):
        mean = np.zeros(T) if mean is None else np.asarray(mean, float)
        if mean.shape != (T,) or not np.isfinite(mean).all():
            raise ValueError("means must be finite vectors matching T")
        means.append(mean)
    dots = np.sum(left * right, axis=0)  # diag(L.T @ M)
    signs = np.where(dots < 0, -1.0, 1.0)
    mean_cost = float(np.sum((means[0]-means[1])**2))
    aw2 = mean_cost + float(np.sum((left-right*signs[None, :])**2))
    kr2 = mean_cost + float(np.sum((left-right)**2))
    gap = float(4*np.sum(np.maximum(-dots, 0)))
    if not np.isfinite([aw2, kr2, gap]).all():
        raise ValueError("oracle objective overflow")
    return {"aw2_squared": aw2, "kr_squared": kr2, "kr_gap": gap,
            "innovation_column_products": dots.tolist(),
            "kr_is_optimal_by_sign_condition": bool(np.all(dots >= 0))}


def ar1_population(T, a_left=0.7, sigma_left=1.0, a_right=0.55, sigma_right=1.15):
    return gaussian_aw2_from_factors(ar1_factor(T, a_left, sigma_left),
                                    ar1_factor(T, a_right, sigma_right))
