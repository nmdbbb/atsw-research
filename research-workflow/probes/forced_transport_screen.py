"""Bounded baseline omission screen. No historical artifacts are modified."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'adapters'),str(ROOT/'probes')]
import policy_pool_candidate as pool
from common_model import build_window_model,stage_cost
from sparse_ordered_policy import prepare_layer
from forced_transport_lower import forced_values
from policy_pool_common_smoke import paths

OUT=ROOT/'runs/cycle_2/forced_transport_screen'
CASES=[dict(process='ar1',k=1,delta=.5,cost='squared'),
       dict(process='second_order_nonmonotone',k=2,delta=.18,cost='absolute')]
FILES=['probes/forced_transport_screen.py','adapters/forced_transport_lower.py',
 'adapters/policy_pool_candidate.py','adapters/sparse_ordered_policy.py',
 'adapters/common_model.py','generators.py','probes/policy_pool_common_smoke.py',
 'runs/cycle_2/policy_pool_common_smoke.json','runs/cycle_2/policy_pool_smoke_manifest.json',
 'runs/cycle_2/upper_policy_screen/results.json','runs/cycle_2/upper_policy_screen/manifest.json']

def digest(name):
    return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

def freeze():
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=dict(schema='forced-transport-screen-v1',cases=CASES,
      design='posthoc two historical cases; freeze before new measurements',
      T=5,paths_per_side=128,seed=1000,shift=0.0,budget_seconds=60,
      budget_rule='cooperative checks each 128 policy pairs and before/after each lower sweep; finish current call, no rerun or downsizing',
      method='same sparse SVD upper/occupation; unchanged lower_sweep with only free_lower augmented on singleton-sided pairs; keep generic selection and floors',
      gate='B0 lower lift >= 0.05 times archived reference on a case permits matched old B4-then-B16 schedule on that case only; reference is audit/gate only',
      stop='One bounded screen. No higher budget, new hypothesis, cache mechanism or grid authorized.',
      claim='Numerical baseline diagnostic; known unique-coupling identity; not novelty, outward certificate or timing superiority',
      hashes={name:digest(name) for name in FILES})
    with (OUT/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(manifest,indent=2)+'\n')

def run():
    manifest=json.loads((OUT/'manifest.json').read_bytes())
    if (OUT/'results.json').exists(): raise RuntimeError('preserve existing result')
    for name,expected in manifest['hashes'].items():
        if digest(name)!=expected: raise RuntimeError('source changed: '+name)
    archive=json.loads((ROOT/'runs/cycle_2/policy_pool_common_smoke.json').read_bytes())
    old_manifest=json.loads((ROOT/'runs/cycle_2/policy_pool_smoke_manifest.json').read_bytes())
    assert archive['manifest_sha256']==digest('runs/cycle_2/policy_pool_smoke_manifest.json')
    for key,name in [('probe_sha256','probes/policy_pool_common_smoke.py'),('generators_sha256','generators.py'),
                     ('common_model_sha256','adapters/common_model.py'),('candidate_sha256','adapters/policy_pool_candidate.py')]:
        assert old_manifest[key]==digest(name),(key,name)
    improved=json.loads((ROOT/'runs/cycle_2/upper_policy_screen/results.json').read_bytes())
    assert improved['manifest_sha256']==digest('runs/cycle_2/upper_policy_screen/manifest.json')
    started=time.perf_counter()
    result=dict(manifest_sha256=digest('runs/cycle_2/forced_transport_screen/manifest.json'),
                status='running',cases=[],timing='includes paths/model, sparse upper/occupation and every executed sweep; excludes imports, provenance checks and external numerical references')
    def check():
        if time.perf_counter()-started>60: raise TimeoutError('cooperative 60s budget')
    try:
        for case in CASES:
            check(); tick=time.perf_counter()
            x,y=paths(case['process'])
            left,right=[build_window_model(z,k=case['k'],delta=case['delta'],shift=0.) for z in (x,y)]
            T=left.horizon
            shapes=[(len(left.states[t]),len(right.states[t])) for t in range(T+1)]
            costs=[stage_cost(left.representatives[t+1],right.representatives[t+1],case['cost']) for t in range(T)]
            ref=next(r for r in archive['rows'] if all(r[k]==v for k,v in case.items()))
            upr=next(r for r in improved['cases'] if all(r[k]==v for k,v in case.items()))
            assert upr['model_hashes']==[left.model_hash,right.model_hash]
            row=dict(**case,model_hashes=upr['model_hashes'],reference=ref['reference'],arms=[])
            result['cases'].append(row)
            U=[None]*(T+1); U[T]=np.zeros(shapes[T]); plans=[None]*T
            paircalls=0
            for t in range(T-1,-1,-1):
                check(); layer=prepare_layer(costs[t]+U[t+1],left.kernels[t],right.kernels[t])
                U[t]=np.empty(shapes[t]); plans[t]=[]
                for i,j in np.ndindex(shapes[t]):
                    if paircalls%128==0: check()
                    item=layer.evaluate(i,j); plans[t].append(item)
                    U[t][i,j]=item.value; paircalls+=1
            rp=prepare_layer(U[0],[left.initial],[right.initial]).evaluate(0,0)
            assert abs(rp.value-ref['levels'][0]['upper'])<1e-8
            occ=[np.zeros(shapes[0])]; np.add.at(occ[0],(rp.rows,rp.cols),rp.masses)
            lm,rm=left.initial,right.initial
            forward=0.; edgevisits=0
            for t in range(T):
                nxt=np.zeros(shapes[t+1])
                for i,j in np.argwhere(occ[t]>0):
                    p=plans[t][int(i)*shapes[t][1]+int(j)]
                    np.add.at(nxt,(p.rows,p.cols),occ[t][i,j]*p.masses)
                    edgevisits+=len(p.masses)
                lm=lm@left.kernels[t]; rm=rm@right.kernels[t]
                assert max(np.max(abs(nxt.sum(1)-lm)),np.max(abs(nxt.sum(0)-rm)))<1e-8
                forward+=float(np.sum(nxt*costs[t])); occ.append(nxt)
            assert abs(forward-rp.value)<1e-8
            row.update(shared_setup_seconds=time.perf_counter()-tick,initial_upper=rp.value,
                       policy_pairs=paircalls,occupation_edges=edgevisits)
            original_free=pool.free_lower
            def arm(forced,budgets):
                counters=pool.Counters(); details=[]; floors=None; levels=[]
                def augmented(M,A,B):
                    base=original_free(M,A,B)
                    mask,vals,counts=forced_values(M,A,B)
                    counts['pairs_with_lift_gt_1e10']=int(np.sum(mask & (vals-base>1e-10)))
                    details.append(counts)
                    return np.maximum(base,vals)
                begin=time.perf_counter()
                with patch.object(pool,'free_lower',augmented if forced else original_free):
                    for b in budgets:
                        check()
                        L,floors,_=pool.lower_sweep(left,right,case['cost'],U,occ,b,counters,floors)
                        check()
                        assert L<=ref['reference']+1e-8
                        assert all(np.max(a-u)<1e-8 for a,u in zip(floors,U))
                        levels.append(dict(budget=b,lower=L,root_width=(rp.value-L)/L if L>0 else None))
                out=dict(forced=forced,budgets=budgets,seconds=time.perf_counter()-begin,
                         levels=levels,counters=counters.as_dict(),forced_evaluation=details)
                row['arms'].append(out)
                return out
            base0,forced0=arm(False,[0]),arm(True,[0])
            lift=forced0['levels'][-1]['lower']-base0['levels'][-1]['lower']
            row['B0_lift_over_reference']=lift/ref['reference']
            row['matched_schedule_gate_passed']=lift>=.05*ref['reference']
            if row['matched_schedule_gate_passed']:
                base,forced=arm(False,[4,16]),arm(True,[4,16])
                assert abs(base['levels'][-1]['lower']-ref['levels'][-1]['lower'])<1e-8
                oldL,newL=base['levels'][-1]['lower'],forced['levels'][-1]['lower']
                row['B16_lower_deficit_removed_fraction']=(newL-oldL)/(ref['reference']-oldL)
                best_upper=upr['levels'][-1]['upper']
                row['posthoc_with_archived_improved_upper']=dict(upper=best_upper,lower=newL,
                    relative_width=(best_upper-newL)/newL if newL>0 else None,
                    scope='joint numerical bounds on identical finite model, not an integrated run or certificate')
            row['status']='completed'
            print(json.dumps(dict(case=case,B0_lift_over_reference=row['B0_lift_over_reference'],
                 matched_gate=row['matched_schedule_gate_passed'])),flush=True)
        result['status']='completed'
    except TimeoutError as e:
        result.update(status='budget_stopped',reason=str(e))
    except Exception as e:
        result.update(status='failed',reason=repr(e)); raise
    finally:
        result['total_seconds']=time.perf_counter()-started
        with (OUT/'results.json').open('x',encoding='utf-8',newline='\n') as f:
            f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps(dict(status=result['status'],seconds=result['total_seconds'])),flush=True)

if __name__=='__main__':
    freeze() if '--freeze' in sys.argv else run()
