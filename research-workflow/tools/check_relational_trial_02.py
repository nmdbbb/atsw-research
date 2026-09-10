"""Rational checks for a known causal-prefix baseline; no performance evidence."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import hashlib
import json
from check_relational_trial_01 import exact_transport, tree_cost


def prefix_masses(law):
    out = {(): F(1)}
    for path, mass in law.items():
        for depth in range(1, len(path)+1):
            h = path[:depth]
            out[h] = out.get(h, F(0)) + mass
    return out


def causal_tree(left, right, weights):
    a, b = prefix_masses(left), prefix_masses(right)
    matched = {(): F(1)}
    total = F(0)
    for h in sorted((set(a) | set(b)) - {()}, key=lambda h: (len(h), h)):
        parent = h[:-1]
        m = F(0)
        if a.get(parent, 0) and b.get(parent, 0):
            m = matched[parent]*min(a.get(h, F(0))/a[parent], b.get(h, F(0))/b[parent])
        matched[h] = m
        weight = weights[h] if isinstance(weights, dict) else weights[len(h)-1]
        total += weight*(a.get(h,F(0))+b.get(h,F(0))-2*m)
    return total, matched


def marginal(law, t):
    out = {}
    for path, mass in law.items():
        out[path[t]] = out.get(path[t], F(0))+mass
    return sorted(out.items())


def quantile_cost(a, b, power):
    a,b = [list(x) for x in a], [list(x) for x in b]
    i=j=0; value=F(0)
    while i<len(a) and j<len(b):
        mass=min(a[i][1],b[j][1])
        value+=mass*abs(a[i][0]-b[j][0])**power
        a[i][1]-=mass; b[j][1]-=mass
        if not a[i][1]: i+=1
        if not b[j][1]: j+=1
    assert i==len(a) and j==len(b)
    return value


def ranges(laws, power):
    return [(max(path[t] for law in laws for path in law)-
             min(path[t] for law in laws for path in law))**power for t in (0,1)]


def bounds(a,b,caps,power):
    upper,_=causal_tree(a,b,[x/2 for x in caps])
    lower=sum((quantile_cost(marginal(a,t),marginal(b,t),power) for t in (0,1)),F(0))
    return lower,upper


def main():
    def fair(paths): return {tuple(map(F,path)):F(1,2) for path in paths}
    laws={
        'Q':fair([(0,0),(0,F(1,4))]),
        'B':fair([(0,0),(F(1,8),F(1,4))]),
        'C_low':fair([(0,0),(0,F(3,8))]),
        'C_high':fair([(0,0),(0,F(3,4))])}
    checks=[]
    for a,b in combinations(laws,2):
        la,lb=laws[a],laws[b]
        value,_=causal_tree(la,lb,[F(1),F(1)])
        reference=exact_transport(tuple(la),tuple(lb),tree_cost,True)
        assert value==reference
        # A different positive weight at every prefix checks more than depth weights.
        prefixes=sorted((set(prefix_masses(la))|set(prefix_masses(lb)))-{()})
        weights={h:F(i+1,7) for i,h in enumerate(prefixes)}
        def weighted_cost(x,y):
            return sum((w for h,w in weights.items() if (x[:len(h)]==h)!=(y[:len(h)]==h)),F(0))
        weighted,_=causal_tree(la,lb,weights)
        assert weighted==exact_transport(tuple(la),tuple(lb),weighted_cost,True)
        for power in (1,2):
            lower,upper=bounds(la,lb,ranges(laws.values(),power),power)
            cost=lambda x,y:sum((abs(u-v)**power for u,v in zip(x,y)),F(0))
            exact=exact_transport(tuple(la),tuple(lb),cost,True)
            assert lower<=exact<=upper
            checks.append({'pair':[a,b],'power':power,'lower':str(lower),'exact':str(exact),'upper':str(upper)})
    u=fair([(0,0),(0,1)]);v=fair([(0,0),(1,1)])
    assert causal_tree(u,v,[F(1),F(1)])[0]==F(5,2)
    qa={(F(0),F(0)):F(3,4),(F(0),F(1)):F(1,4)}
    far=fair([(0,3),(0,4)])
    cap=ranges([u,qa,far],1)
    _,near_u=bounds(u,qa,cap,1)
    far_l,_=bounds(u,far,cap,1)
    assert near_u==1 and far_l==3 and near_u<far_l
    out={'kind':'exact_analytic_baseline_checks','blind_preregistered':False,
         'performance_or_statistical_evidence':False,
         'source':'tools/check_relational_trial_02.py',
         'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'dependency':'tools/check_relational_trial_01.py',
         'dependency_sha256':hashlib.sha256(Path(__file__).with_name('check_relational_trial_01.py').read_bytes()).hexdigest(),
         'depth_and_node_weight_formula_checks':12,'numeric_bound_checks':checks,
         'nonvacuous_separated_fixture':{'near_upper':str(near_u),'far_lower':str(far_l),'certified_order':True},
         'limits':'Small explicit prefix laws only; compact k-window recursion reviewed on paper, not implemented here. No novelty, coverage or speed claim.'}
    print(json.dumps(out,indent=2))


if __name__=='__main__': main()
