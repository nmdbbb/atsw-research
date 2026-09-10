"""Two-row/column OT by fractional-knapsack ordering, numerical baseline only."""
from __future__ import annotations
import numpy as np


def binary_coupling(a,b,cost,order=None):
    """Solve positive-support 2-by-m OT and return local primal/dual witnesses.

    Inputs are represented probability vectors; normalize summation roundoff.
    No tolerance groups costs or deletes positive masses. Float64 only.
    """
    a,b=np.asarray(a,float),np.asarray(b,float);C=np.asarray(cost,float)
    if a.shape!=(2,) or b.ndim!=1 or not len(b) or C.shape!=(2,len(b)):
        raise ValueError('require 2-by-m cost and matching marginals')
    if any(not np.isfinite(x).all() for x in (a,b,C)) or (a<=0).any() or (b<=0).any():
        raise ValueError('require finite positive-support marginals and finite costs')
    if abs(a.sum()-1)>1e-10 or abs(b.sum()-1)>1e-10:
        raise ValueError('require probabilities')
    a=a/a.sum();b=b/b.sum();delta=C[0]-C[1]
    if order is None:order=np.argsort(delta,kind='stable')
    order=np.asarray(order)
    if order.shape!=b.shape or not np.issubdtype(order.dtype,np.integer) or not np.array_equal(np.sort(order),np.arange(len(b))):
        raise ValueError('invalid order')
    # Independently guard supplied cache ordering; this linear check is charged.
    if np.any(np.diff(delta[order])<0):raise ValueError('stale or incorrect order')
    x=np.zeros(len(b));remaining=float(a[0]);threshold=None
    for j in order:
        amount=min(remaining,float(b[j]));x[j]=amount;remaining-=amount
        threshold=float(delta[j])
        if remaining<=0:break
    if remaining>2e-12:raise RuntimeError('unallocated probability mass')
    plan=np.stack((x,b-x))
    alpha=np.array([threshold,0.]);beta=np.minimum(C[0]-threshold,C[1])
    violation=float(np.max(alpha[:,None]+beta[None,:]-C))
    guard=32*np.finfo(float).eps*max(1.,float(np.max(abs(C))),abs(threshold))
    beta-=max(violation,0.)+guard
    primal=float(np.sum(plan*C));dual=float(a@alpha+b@beta)
    marginal=float(max(np.max(abs(plan.sum(1)-a)),np.max(abs(plan.sum(0)-b))))
    if marginal>2e-12 or plan.min() < 0 or dual>primal+1e-10:
        raise RuntimeError('binary witness gate failed')
    return dict(value=primal,plan=plan,alpha=alpha,beta=beta,dual=dual,
                marginal_error=marginal,dual_violation=float(np.max(alpha[:,None]+beta[None,:]-C)),
                numerical_gap=primal-dual)


class BinaryLayer:
    """Immutable matrix with optional identical-support ordering reuse.

    New continuation matrices require a new object. Both modes share the same
    snapshot and per-call solver; caching only avoids repeated difference sorts.
    """
    def __init__(self,matrix,reuse=False):
        self.matrix=np.array(matrix,dtype=float,copy=True)
        if self.matrix.ndim!=2 or not self.matrix.size or not np.isfinite(self.matrix).all():
            raise ValueError('finite nonempty matrix required')
        self.matrix.flags.writeable=False
        self.reuse=reuse;self.cache={}
        self.counts=dict(calls=0,sort_calls=0,sort_entries=0,cache_hits=0,cache_key_entries=0,
                         order_validation_entries=0,cost_entries_read=0,matrix_snapshot_entries=int(self.matrix.size))

    def solve(self,rows,aa,cols,bb):
        rows,cols=np.asarray(rows,dtype=int),np.asarray(cols,dtype=int)
        if len(rows)!=2 and len(cols)!=2:raise ValueError('binary side required')
        transpose=len(rows)!=2
        C=self.matrix[np.ix_(rows,cols)]
        a,b=(bb,aa) if transpose else (aa,bb)
        if transpose:C=C.T
        key=(tuple(rows),tuple(cols),transpose) if self.reuse else None
        self.counts['calls']+=1
        if self.reuse:self.counts['cache_key_entries']+=len(rows)+len(cols)
        if self.reuse and key in self.cache:
            order=self.cache[key];self.counts['cache_hits']+=1
        else:
            order=np.argsort(C[0]-C[1],kind='stable')
            self.counts['sort_calls']+=1;self.counts['sort_entries']+=len(b)
            if self.reuse:self.cache[key]=order
        self.counts['order_validation_entries']+=len(b)
        self.counts['cost_entries_read']+=int(C.size)
        out=binary_coupling(a,b,C,order)
        if transpose:
            out['plan']=out['plan'].T
            out['alpha'],out['beta']=out['beta'],out['alpha']
        return out
