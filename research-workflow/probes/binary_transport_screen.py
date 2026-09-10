"""Three-arm numerical DP baseline screen with binary-support order reuse."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'adapters'),str(ROOT/'probes')]
from binary_transport import BinaryLayer
from common_model import build_window_model,stage_cost,_transport_value
from policy_pool_common_smoke import paths
OUT=ROOT/'runs/cycle_2/binary_transport_screen'
CASES=[dict(process='ar1',k=1,delta=.5,cost='squared'),dict(process='second_order_nonmonotone',k=2,delta=.18,cost='absolute')]
FILES=['probes/binary_transport_screen.py','adapters/binary_transport.py','adapters/common_model.py',
 'generators.py','probes/policy_pool_common_smoke.py','runs/cycle_2/policy_pool_smoke_manifest.json','runs/cycle_2/policy_pool_common_smoke.json']

def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def freeze():
    OUT.mkdir(parents=True,exist_ok=True)
    m=dict(schema='binary-transport-screen-v1',cases=CASES,T=5,paths_per_side=128,seed=1000,shift=0.,
      design='posthoc two selected historical cases; structural count known before design; freeze before timings',
      arms=['LP','binary_per_pair','binary_shared_support'],
      method='Full original-target backward DP, singleton exact expectation in all arms, identical general LP fallback; binary arms use same local solver, differ only cache of order for identical support pair and immutable matrix.',
      deadline_seconds=60,deadline_rule='cooperative each layer and128 parentpairs; no rerun or downsize',
      checks='every table agrees with same-run LP within1e-8 and root matches archived numerical DP within1e-8; binary primal/dual local gates active',
      opportunity_gate='shared-support arm saves at least20% of binary sort calls vs binary-per-pair on EACH case; passing is structural opportunity only, not speed or novelty',
      nonclaims=['not exact arithmetic or outward certificate','binary special-case algorithm is a baseline; novelty unestablished','one repeat per arm, fixed order, no speed significance or SOTA claim'],
      timing='models constructed once and reported separately; each arm includes stage-costs, support preparation, matrix snapshots, binary order lookup/validation, local solves, and root; validation outside each arm separately charged',
      hashes={p:digest(p) for p in FILES})
    with (OUT/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(m,indent=2)+'\n')

def solve(left,right,cost,mode,check):
    tick=time.perf_counter();T=left.horizon
    V=[None]*(T+1);V[T]=np.zeros((len(left.states[T]),len(right.states[T])))
    counts=dict(parentpairs=0,singleton_calls=0,LP_calls=0,binary_calls=0,sort_calls=0,sort_entries=0,cache_hits=0,
                cache_key_entries=0,order_validation_entries=0,cost_entries_read=0,matrix_snapshot_entries=0,marginal_entries_scanned=0)
    maxres=maxdual=maxgap=0.;layer_counts=[]
    def supports(K):
        out=[];counts['marginal_entries_scanned']+=int(K.size)
        for a in K:
            ix=np.flatnonzero(a>0);mass=a[ix].copy();mass/=mass.sum();out.append((ix,mass))
        return out
    def layer(M,A,B):
        nonlocal maxres,maxdual,maxgap
        a_support,b_support=supports(A),supports(B)
        binary=BinaryLayer(M,mode=='binary_shared_support') if mode!='LP' else None
        values=np.empty((len(A),len(B)))
        for i,(rows,aa) in enumerate(a_support):
            for j,(cols,bb) in enumerate(b_support):
                if counts['parentpairs']%128==0:check()
                counts['parentpairs']+=1
                if min(len(rows),len(cols))==1:
                    values[i,j]=float(aa@M[np.ix_(rows,cols)]@bb);counts['singleton_calls']+=1
                elif binary is not None and min(len(rows),len(cols))==2:
                    o=binary.solve(rows,aa,cols,bb);values[i,j]=o['value'];counts['binary_calls']+=1
                    maxres=max(maxres,o['marginal_error']);maxdual=max(maxdual,o['dual_violation']);maxgap=max(maxgap,o['numerical_gap'])
                else:
                    values[i,j]=_transport_value(aa,bb,M[np.ix_(rows,cols)]);counts['LP_calls']+=1
        if binary is not None:
            for k,v in binary.counts.items():
                if k!='calls':counts[k]+=v
            layer_counts.append(binary.counts)
        return values
    for t in range(T-1,-1,-1):
        check();M=stage_cost(left.representatives[t+1],right.representatives[t+1],cost)+V[t+1]
        V[t]=layer(M,left.kernels[t],right.kernels[t])
    root=float(layer(V[0],left.initial[None,:],right.initial[None,:])[0,0])
    return V,dict(mode=mode,root=root,seconds=time.perf_counter()-tick,counts=counts,
                  layers=layer_counts,max_binary_marginal_error=maxres,max_binary_dual_violation=maxdual,max_binary_numerical_gap=maxgap)

def run():
    if (OUT/'results.json').exists():raise RuntimeError('preserve results')
    m=json.loads((OUT/'manifest.json').read_bytes())
    for p,h in m['hashes'].items():
        if digest(p)!=h:raise RuntimeError('changed source: '+p)
    archive=json.loads((ROOT/'runs/cycle_2/policy_pool_common_smoke.json').read_bytes())
    old=json.loads((ROOT/'runs/cycle_2/policy_pool_smoke_manifest.json').read_bytes())
    if archive['manifest_sha256']!=digest('runs/cycle_2/policy_pool_smoke_manifest.json'):raise RuntimeError('archive mismatch')
    for key,p in [('probe_sha256','probes/policy_pool_common_smoke.py'),('generators_sha256','generators.py'),('common_model_sha256','adapters/common_model.py')]:
        if old[key]!=digest(p):raise RuntimeError('archived source mismatch')
    started=time.perf_counter();result=dict(status='running',cases=[],manifest_sha256=digest('runs/cycle_2/binary_transport_screen/manifest.json'))
    def check():
        if time.perf_counter()-started>60:raise TimeoutError('60s budget')
    try:
        for case in CASES:
            check();tick=time.perf_counter();x,y=paths(case['process'])
            left,right=[build_window_model(z,k=case['k'],delta=case['delta'],shift=0.) for z in(x,y)]
            row=dict(**case,model_hashes=[left.model_hash,right.model_hash],model_seconds=time.perf_counter()-tick,arms=[]);result['cases'].append(row)
            ref=next(r['reference'] for r in archive['rows'] if all(r[k]==v for k,v in case.items()))
            ref_tables=None;validation=0.
            for mode in m['arms']:
                V,arm=solve(left,right,case['cost'],mode,check);row['arms'].append(arm)
                tick=time.perf_counter()
                if ref_tables is None:ref_tables=V
                err=max(float(np.max(abs(a-b))) for a,b in zip(V,ref_tables))
                arm.update(table_max_error=err,archived_root_error=abs(arm['root']-ref))
                if max(err,arm['archived_root_error'])>1e-8:raise RuntimeError('target equivalence failed')
                validation+=time.perf_counter()-tick
            independent,shared=row['arms'][1:]
            row.update(validation_seconds=validation,sort_calls_saved_fraction=1-shared['counts']['sort_calls']/independent['counts']['sort_calls'],
              shared_over_independent_seconds=shared['seconds']/independent['seconds'],status='completed')
            row['opportunity_gate_passed']=row['sort_calls_saved_fraction']>=.2
            print(json.dumps(dict(case=case,sort_saved=row['sort_calls_saved_fraction'],times=[a['seconds'] for a in row['arms']],LP_calls=[a['counts']['LP_calls'] for a in row['arms']])),flush=True)
        result['status']='completed';result['both_cases_opportunity_gate_passed']=all(c['opportunity_gate_passed'] for c in result['cases'])
    except TimeoutError as exc:result.update(status='budget_stopped',reason=str(exc))
    except Exception as exc:result.update(status='failed',reason=repr(exc));raise
    finally:
        result['total_seconds']=time.perf_counter()-started
        with (OUT/'results.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps(dict(status=result['status'],seconds=result['total_seconds'])),flush=True)

if __name__=='__main__':freeze() if '--freeze' in sys.argv else run()
