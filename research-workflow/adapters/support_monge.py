"""Exact dyadic Monge predicate plus numerical NW transport; baseline only."""
from fractions import Fraction
import numpy as np
from policy_pool_candidate import nw_plan


def monge_predicate(matrix):
    """Certify adjacent inequalities exactly for the supplied float64 entries.

    This certifies matrix structure, not marginal arithmetic or a root interval.
    No tolerance replaces a strictly positive cross-difference with zero.
    """
    M=np.asarray(matrix,float)
    if M.ndim!=2 or not M.size or not np.isfinite(M).all():
        raise ValueError('finite nonempty matrix required')
    cache={};checks=0
    def q(i,j):
        if (i,j) not in cache:cache[i,j]=Fraction(float(M[i,j]))
        return cache[i,j]
    for i in range(len(M)-1):
        for j in range(M.shape[1]-1):
            checks+=1
            if q(i,j)+q(i+1,j+1)>q(i,j+1)+q(i+1,j):
                return False,dict(adjacent_checks=checks,dyadic_entries=len(cache),first_violation=[i,j])
    return True,dict(adjacent_checks=checks,dyadic_entries=len(cache),first_violation=None)


def monge_value(a,b,matrix):
    """Return a numerical NW value only after the exact represented-matrix gate."""
    M=np.asarray(matrix,float);passed,counts=monge_predicate(M)
    if not passed:return None,counts
    a,b=np.asarray(a,float),np.asarray(b,float)
    if M.shape!=(len(a),len(b)):raise ValueError('shape mismatch')
    plan=nw_plan(a,b)
    return float(np.sum(plan*M)),counts
