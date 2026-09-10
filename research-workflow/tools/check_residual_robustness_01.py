"""Exact robustness diagnostic, no random sweep or performance probe."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import hashlib
import json

from check_signed_prefix_comparison_01 import local, nested
from check_geometry_condition_screen_01 import model, reconstructed
from check_conditional_offset_comparison_01 import centered_components, centered_model, residual_reference


def laws(sigma, e):
    assert sigma>2 and 0<=e<sigma/2
    result={name:{} for name in ('Q','A','B')}
    for j,l,n in product((-1,1),repeat=3):
        for name,path in (
            ('Q',(F(0),F(j,2),j+sigma*l,4*j+4*sigma*l+4*sigma*n)),
            ('A',(F(0),F(j),j+sigma*l,4*j-4*sigma*l+4*sigma*n)),
            ('B',(F(0),F(-j),j+(sigma-e)*l,4*j-4*sigma*l+4*sigma*n)),
        ):
            result[name][path]=F(1,8)
    return result


def residual_witness(a,b,sigma,e):
    # Invertible coordinate scaling of first residual value, identity on second.
    # Pushforward and information preservation checked, not inferred by OT label.
    scale=(sigma-e)/sigma
    assert scale>0
    pushed={(scale*p[0],p[1]):mass for p,mass in a.items()}
    assert pushed==b and len(pushed)==len(a)
    cost=sum((mass*((scale-1)*p[0])**2 for p,mass in a.items()),F(0))
    assert cost==e**2
    return cost


def norm2(law):
    return sum((mass*sum((x*x for x in p),F(0)) for p,mass in law.items()),F(0))


def query_witness(z,w):
    # Supplied adapted invertible map, checked by exact full-law pushforward.
    pushed={(-p[0],p[1]):mass for p,mass in z.items()}
    assert pushed==w and len(pushed)==len(z)
    return sum((mass*4*p[0]**2 for p,mass in z.items()),F(0))


def root_score(q,x):
    qw,qm,_,_=q; xw,xm,_,_=x
    return local(qw,xw,lambda i,j:sum(((u-v)**2 for u,v in zip(qm[i],xm[j])),F(0)))


def main():
    results=[]
    # Declared algebraic controls, not a search/sweep used as coverage evidence.
    cases=(('exact',F(100),F(0)),('certified_small',F(100),F(1,1000)),
           ('conservative_abstention',F(100),F(1,500)),
           ('near_boundary_witness',F(100),F(1,200)),
           ('wrong_naive_order',F(100),F(1,100)),('exact_tie',F(201,40),F(1,10)))
    for name,sigma,e in cases:
        x=laws(sigma,e); q,a,b=(x[n] for n in ('Q','A','B'))
        pieces={n:centered_components(law) for n,law in x.items()}
        z,wa,wb=(pieces[n][2] for n in ('Q','A','B'))
        witness_cost=residual_witness(wa,wb,sigma,e)
        sa,sb=root_score(pieces['Q'],pieces['A']),root_score(pieces['Q'],pieces['B'])
        assert (sa,sb)==(F(1,4),F(9,4))
        radius2=norm2(z)+norm2(wa)
        assert radius2==66*sigma**2 and witness_cost<=radius2
        m=sb-sa
        # Uses input moments + validated witness, no exact residual radius.
        certified=(m+witness_cost>0 and (m+witness_cost)**2>4*radius2*witness_cost)
        query_radius2=query_witness(z,wa)
        assert witness_cost<=query_radius2
        witness_certified=(m+witness_cost>0 and
                           (m+witness_cost)**2>4*query_radius2*witness_cost)
        # Exact oracle below is diagnostic only, excluded from certificate inputs.
        da=nested(q,a,markov=True)[0]; db=nested(q,b,markov=True)[0]
        assert da==nested(q,a)[0] and db==nested(q,b)[0]
        r0=residual_reference(z,wa); re=residual_reference(z,wb)
        assert r0==4*sigma**2 and re==(2*sigma-e)**2
        assert residual_reference(wa,wb)==e**2
        gap=db-da
        assert gap==m-4*sigma*e+e**2 and da==sa+r0 and db==sb+re
        assert not certified or gap>0
        assert not witness_certified or gap>0
        for k in (1,2):
            for n,law in x.items():
                mm=model(law,k)
                assert reconstructed(*mm)==law
                mw,means,_,_=centered_model(*mm)
                assert mw==pieces[n][0] and means==pieces[n][1]
        if name=='exact_tie': assert gap==0 and not certified and not witness_certified
        if name=='wrong_naive_order': assert gap<0 and not certified and not witness_certified
        if name in ('conservative_abstention','near_boundary_witness'):
            assert gap>0 and not certified and witness_certified
        if name in ('exact','certified_small'): assert certified
        results.append({'case':name,'sigma':str(sigma),'epsilon':str(e),
                        'input_moment_radius_squared':str(radius2),
                        'verified_query_witness_cost':str(query_radius2),
                        'verified_residual_witness_cost':str(witness_cost),
                        'mean_score_gap':str(m),'exact_target_gap':str(gap),
                        'moment_certificate':'A_closer' if certified else 'unresolved',
                        'two_witness_certificate':'A_closer' if witness_certified else 'unresolved',
                        'naive_score_wrong':gap<0,'model_law_checks':[1,2]})
    source=Path(__file__)
    dependencies=['check_signed_prefix_comparison_01.py','check_geometry_condition_screen_01.py',
                  'check_conditional_offset_comparison_01.py']
    print(json.dumps({'task_id':'residual_robustness_01','kind':'exact_algebraic_diagnostic',
                      'preregistered':False,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                      'dependency_sha256':{n:hashlib.sha256(source.with_name(n).read_bytes()).hexdigest() for n in dependencies},
                      'results':results,'limits':'One finite Markov family and declared rational controls. Model checks on k2 do not establish genuinely second-order usefulness. Both witnesses are supplied and exact path pushforwards verified; scalable model-level witness discovery, floating certification, broad coverage and speed are not implemented/claimed. Exact reference solves are diagnostic, not inputs to either certificate.'},indent=2))


if __name__=='__main__': main()
