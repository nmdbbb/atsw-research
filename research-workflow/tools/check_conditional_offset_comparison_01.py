"""Exact finite-law diagnostic with a bounded k-window structural recognizer."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib
import json

from check_signed_prefix_comparison_01 import local, row, nested, assignment, marginal
from check_geometry_condition_screen_01 import model, reconstructed


def law(tag, shift, noise_direction, scale=100, component_noise=False, late_noise_width=4):
    result = {}
    for j, ell, n in product((-1, 1), repeat=3):
        direction = -noise_direction if component_noise and j == 1 else noise_direction
        path = (F(0), tag*j, shift*j+scale*ell,
                4*shift*j+direction*4*scale*ell+late_noise_width*scale*n)
        result[path] = F(1, 8)
    return result


def centered_components(law):
    groups = {}
    coordinates_read = 0
    for path, mass in law.items():
        groups.setdefault(path[1], {})[path] = mass
        coordinates_read += len(path)-1
    weights, means, common = {}, {}, None
    for tag, paths in sorted(groups.items()):
        weight = sum(paths.values(), F(0)); weights[tag] = weight
        mean = tuple(sum((mass*p[t] for p, mass in paths.items()), F(0))/weight
                     for t in range(1, len(next(iter(paths)))))
        means[tag] = mean
        residual = {}
        for p, mass in paths.items():
            z = tuple(p[t]-mean[t-1] for t in range(2, len(p)))
            residual[z] = residual.get(z, F(0))+mass/weight
        if common is None: common = residual
        elif common != residual: raise ValueError('component-dependent residual law')
    return weights, means, common, coordinates_read


def compare(q, a, b):
    qw, qm, qr, qc = centered_components(q)
    aw, am, ar, ac = centered_components(a)
    bw, bm, br, bc = centered_components(b)
    if ar != br: raise ValueError('candidate residual laws differ')
    def cost(x, y): return sum(((u-v)**2 for u,v in zip(x,y)), F(0))
    sa = local(qw, aw, lambda i,j: cost(qm[i],am[j]))
    sb = local(qw, bw, lambda i,j: cost(qm[i],bm[j]))
    return {'scores':(sa,sb),'gap':sb-sa,'input_coordinates_read':qc+ac+bc,
            'root_transport_calls':2,'residual_transport_calls':0}, qr, ar


def centered_model(masses, kernels):
    """Check centered conditional k-window laws without enumerating paths."""
    weights, means, common = {}, {}, None
    edge_visits = 0
    horizon = len(kernels)
    assert masses[0] == {(F(0),): F(1)}
    for initial, weight in sorted(masses[1].items()):
        tag = initial[-1]; weights[tag] = weight
        distributions = {1: {initial:F(1)}}
        for t in range(1,horizon):
            new = {}
            for state, mass in distributions[t].items():
                for child, probability in kernels[t][state].items():
                    edge_visits += 1
                    new[child] = new.get(child,F(0))+mass*probability
            distributions[t+1] = new
        mean = {0:F(0), **{t:sum((state[-1]*mass for state,mass in dist.items()),F(0))
                            for t,dist in distributions.items()}}
        means[tag] = tuple(mean[t] for t in range(1,horizon+1))
        def center(state,t):
            return tuple(value-mean[t-len(state)+1+j] for j,value in enumerate(state))
        signature=[]
        for t in range(1,horizon):
            layer=[]
            for state in distributions[t]:
                children=[]
                for child,probability in kernels[t][state].items():
                    edge_visits += 1
                    children.append((center(child,t+1),probability))
                layer.append((center(state,t),tuple(sorted(children))))
            signature.append(tuple(sorted(layer)))
        signature=tuple(signature)
        if common is None: common=signature
        elif common != signature: raise ValueError('component-dependent residual model')
    return weights,means,common,edge_visits


def compare_models(models):
    pieces={name:centered_model(*m) for name,m in models.items()}
    qw,qm,_,_=pieces['Q']; aw,am,ar,_=pieces['A']; bw,bm,br,_=pieces['B']
    if ar != br: raise ValueError('candidate residual models differ')
    cost=lambda x,y:sum(((u-v)**2 for u,v in zip(x,y)),F(0))
    sa=local(qw,aw,lambda i,j:cost(qm[i],am[j]))
    sb=local(qw,bw,lambda i,j:cost(qm[i],bm[j]))
    return sb-sa,sum(p[3] for p in pieces.values())


def residual_reference(a, b):
    a={(F(0), *p):m for p,m in a.items()}; b={(F(0), *p):m for p,m in b.items()}
    @lru_cache(None)
    def solve(x,y):
        if len(x)==len(next(iter(a))): return F(0)
        return local(row(a,x),row(b,y),lambda u,v:(u-v)**2+solve((*x,u),(*y,v)))
    return solve((F(0),),(F(0),))


def main():
    results=[]
    initial_laws=[law(tag,1,direction,late_noise_width=1)
                  for tag,direction in ((F(1,2),1),(F(1),-1),(F(-1),-1))]
    initial_control=[]
    for x in initial_laws[1:]:
        v=nested(initial_laws[0],x,markov=True)[0]
        ordinary=assignment(initial_laws[0],x)
        assert v==ordinary
        initial_control.append(str(v))
    a=law(F(1),1,-1); b=law(F(-1),1,-1)
    for d in (1,-1):
        q=law(F(1,2),d,1)
        candidate,z,w=compare(q,a,b)
        da,ca=nested(q,a,markov=True); db,cb=nested(q,b,markov=True)
        assert da==nested(q,a)[0] and db==nested(q,b)[0]
        common=residual_reference(z,w)
        sa,sb=candidate['scores']
        assert common==40000 and (da,db)==(common+sa,common+sb)
        assert candidate['gap']==db-da==2*d
        assert all(marginal(a,t)==marginal(b,t) for t in range(4))
        oa,ob=assignment(q,a),assignment(q,b)
        assert max(da-oa,db-ob)>0
        model_checks=[]
        for k in (1,2):
            models={name:model(x,k) for name,x in (('Q',q),('A',a),('B',b))}
            for name,x in (('Q',q),('A',a),('B',b)):
                assert reconstructed(*models[name])==x
            gap,visits=compare_models(models)
            assert gap==db-da
            model_checks.append({'k':k,'gap':str(gap),'propagation_and_signature_edge_visits':visits,
                                 'path_enumeration_inside_recognizer':False})
        results.append({'query_shift_sign':d,'D_QA':str(da),'D_QB':str(db),
                        'ordinary_QA':str(oa),'ordinary_QB':str(ob),
                        'component_scores':[str(sa),str(sb)],'exact_gap':str(db-da),
                        'common_residual_reference_only':str(common),
                        'candidate_residual_transport_calls':candidate['residual_transport_calls'],
                        'candidate_root_transport_calls':2,'supplied_path_coordinate_count':candidate['input_coordinates_read'],
                        'model_recognition':model_checks,
                        'full_markov_transport_calls':[ca,cb]})
    q=law(F(1,2),1,1); bad_b=law(F(-1),1,1)
    # Same one-time marginals, but the centered temporal law differs. Blindly
    # cancelling it reverses the true order: A costs 40000.25, bad B costs 2.25.
    assert all(marginal(b,t)==marginal(bad_b,t) for t in range(4))
    try: compare(q,a,bad_b)
    except ValueError as exc: assert str(exc)=='candidate residual laws differ'
    else: raise AssertionError('bad common-residual assumption accepted')
    for k in (1,2):
        try: compare_models({name:model(x,k) for name,x in (('Q',q),('A',a),('B',bad_b))})
        except ValueError as exc: assert str(exc)=='candidate residual models differ'
        else: raise AssertionError('model recognizer accepted unequal residuals')
    bad_value=nested(q,bad_b,markov=True)[0]
    assert bad_value==F(9,4)<nested(q,a,markov=True)[0]
    try: centered_components(law(F(-1),1,-1,component_noise=True))
    except ValueError as exc: assert str(exc)=='component-dependent residual law'
    else: raise AssertionError('component-dependent residual accepted')
    for k in (1,2):
        bad=law(F(-1),1,-1,component_noise=True)
        try: centered_model(*model(bad,k))
        except ValueError as exc: assert str(exc)=='component-dependent residual model'
        else: raise AssertionError('model recognizer accepted component dependence')
    skew_q={p:(F(1,16) if p[1]<0 else F(3,16)) for p in q}
    skew_gap=nested(skew_q,b,markov=True)[0]-nested(skew_q,a,markov=True)[0]
    for k in (1,2):
        gap,_=compare_models({name:model(x,k) for name,x in (('Q',skew_q),('A',a),('B',b))})
        assert gap==skew_gap
    source=Path(__file__)
    dependency=source.with_name('check_signed_prefix_comparison_01.py')
    print(json.dumps({'task_id':'conditional_offset_comparison_01',
                      'kind':'exact_constructed_diagnostic','preregistered':False,
                      'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                      'reference_dependency_sha256':hashlib.sha256(dependency.read_bytes()).hexdigest(),
                      'results':results,'assumption_controls':{
                          'equal_marginals_unequal_residual_law':'rejected; ignoring it reverses ordering',
                          'bad_B_exact_value':str(bad_value),'component_dependent_residual':'rejected by path and k=1,2 model checks',
                          'unequal_initial_query_weights_gap':str(skew_gap)},
                      'initial_fixture_control':{'late_noise_width':1,
                          'adapted_equals_ordinary':initial_control,
                          'repair':'Width 1 failed the intended adapted-specific evidence gate; width 4 introduces overlapping final supports. Both remain exact constructed cases, no blind confirmation.'},
                      'model_builder_dependency_sha256':hashlib.sha256(source.with_name('check_geometry_condition_screen_01.py').read_bytes()).hexdigest(),
                      'limits':'Model recognizer propagates conditional masses and compares centered k-window kernels without reconstructing paths. Fixture model construction, reference reconstruction and exact OT are diagnostic oracles, not free algorithm inputs. No empirical coverage, measured speed or novelty claim; validation on this finite family is not broad implementation certification.'},indent=2))


if __name__=='__main__': main()
