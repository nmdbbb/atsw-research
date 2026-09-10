"""Posthoc Bellman residual attribution on reconstructed, archived endpoints."""
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
from common_model import build_window_model,stage_cost,_transport_value
from sparse_ordered_policy import prepare_layer
from forced_transport_lower import forced_values
from policy_pool_common_smoke import paths
from upper_policy_improvement_screen import pack,value,residual
OUT=ROOT/'runs/cycle_2/root_gap_decomposition'
CASES=[dict(process='ar1',k=1,delta=.5,cost='squared'),
       dict(process='second_order_nonmonotone',k=2,delta=.18,cost='absolute')]
FILES=['probes/root_gap_decomposition.py','adapters/common_model.py','generators.py',
 'adapters/policy_pool_candidate.py','adapters/forced_transport_lower.py',
 'adapters/sparse_ordered_policy.py','probes/policy_pool_common_smoke.py',
 'probes/upper_policy_improvement_screen.py',
 'runs/cycle_2/forced_transport_screen/manifest.json','runs/cycle_2/forced_transport_screen/results.json',
 'runs/cycle_2/upper_policy_screen/manifest.json','runs/cycle_2/upper_policy_screen/results.json']

def digest(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def freeze():
    OUT.mkdir(parents=True,exist_ok=True)
    m=dict(schema='root-gap-decomposition-v1',cases=CASES,T=5,paths_per_side=128,seed=1000,shift=0.,
      design='posthoc localization; new diagnostic design frozen before execution; no hypothesis registration',
      deadline_seconds=60,deadline_rule='cooperative before each layer/local solve and every128 initialization pairs, finish native operation; no rerun/downsize',
      method='Reconstruct forced B4/B16 lower and independently improved B16 upper; same archived model/endpoints gates. Decompose occupied residual pi(c+Lnext)-L into q-L and pi(c+Lnext)-q, q=local numerical OT.',
      gate='If top16 nonforced contributions explain at least80% of total root gap, permit design of one targeted-selection probe, not automatic run. Otherwise do not escalate local-repair budget on concentration premise.',
      nonclaims=['Attribution is not actual repair gain','policy regret is relative to lower surrogate, not true-value advantage',
                 'OT calls are privileged diagnostic cost, not free candidate information','No outward certificate, novelty, speed or full-domain claim'],
      hashes={p:digest(p) for p in FILES})
    with (OUT/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(m,indent=2)+'\n')

def evaluate(plans,rootplan,costs,shapes,check):
    T=len(costs); tables=[None]*(T+1);tables[T]=np.zeros(shapes[T])
    for t in range(T-1,-1,-1):
        check();M=costs[t]+tables[t+1]
        tables[t]=np.array([value(p,M) for p in plans[t]]).reshape(shapes[t])
    return value(rootplan,tables[0]),tables

def occupation(plans,rootplan,left,right,costs,shapes,check):
    occ=[np.zeros(shapes[0])];np.add.at(occ[0],rootplan[:2],rootplan[2])
    lm,rm=left.initial,right.initial;total=0.
    for t in range(left.horizon):
        check();nxt=np.zeros(shapes[t+1])
        for i,j in np.argwhere(occ[t]>0):
            p=plans[t][int(i)*shapes[t][1]+int(j)]
            np.add.at(nxt,p[:2],occ[t][i,j]*p[2])
        lm=lm@left.kernels[t];rm=rm@right.kernels[t]
        if max(np.max(abs(nxt.sum(1)-lm)),np.max(abs(nxt.sum(0)-rm)))>1e-8:
            raise RuntimeError('occupation marginal mismatch')
        total+=float(np.sum(nxt*costs[t]));occ.append(nxt)
    return occ,total

def run():
    if (OUT/'results.json').exists():raise RuntimeError('preserve existing result')
    m=json.loads((OUT/'manifest.json').read_bytes())
    for p,h in m['hashes'].items():
        if digest(p)!=h:raise RuntimeError('source changed: '+p)
    archives={}
    for name in ('forced_transport_screen','upper_policy_screen'):
        d='runs/cycle_2/'+name+'/'
        a=json.loads((ROOT/(d+'results.json')).read_bytes())
        if a['manifest_sha256']!=digest(d+'manifest.json'):raise RuntimeError('archive manifest mismatch')
        for p,h in json.loads((ROOT/(d+'manifest.json')).read_bytes())['hashes'].items():
            if digest(p)!=h:raise RuntimeError('archive source mismatch: '+p)
        archives[name]=a
    started=time.perf_counter();result=dict(status='running',cases=[],manifest_sha256=digest('runs/cycle_2/root_gap_decomposition/manifest.json'))
    def check():
        if time.perf_counter()-started>60:raise TimeoutError('60s budget')
    try:
        for case in CASES:
            tick=time.perf_counter();check()
            x,y=paths(case['process'])
            left,right=[build_window_model(z,k=case['k'],delta=case['delta'],shift=0.) for z in (x,y)]
            T=left.horizon;shapes=[(len(left.states[t]),len(right.states[t])) for t in range(T+1)]
            costs=[stage_cost(left.representatives[t+1],right.representatives[t+1],case['cost']) for t in range(T)]
            old={name:next(r for r in a['cases'] if all(r[k]==v for k,v in case.items())) for name,a in archives.items()}
            model_hashes=[left.model_hash,right.model_hash]
            if any(r['model_hashes']!=model_hashes for r in old.values()):raise RuntimeError('model mismatch')
            row=dict(**case,model_hashes=model_hashes);result['cases'].append(row)
            U=[None]*(T+1);U[T]=np.zeros(shapes[T]);plans=[None]*T
            calls=0
            for t in range(T-1,-1,-1):
                check();layer=prepare_layer(costs[t]+U[t+1],left.kernels[t],right.kernels[t])
                U[t]=np.empty(shapes[t]);plans[t]=[]
                for i,j in np.ndindex(shapes[t]):
                    if calls%128==0:check()
                    p=layer.evaluate(i,j);plans[t].append((p.rows,p.cols,p.masses));U[t][i,j]=p.value;calls+=1
            rp=prepare_layer(U[0],[left.initial],[right.initial]).evaluate(0,0)
            rootplan=(rp.rows,rp.cols,rp.masses)
            occ,forward=occupation(plans,rootplan,left,right,costs,shapes,check)
            if abs(forward-rp.value)>1e-8 or abs(rp.value-old['forced_transport_screen']['initial_upper'])>1e-8:raise RuntimeError('initial endpoint mismatch')
            base=pool.free_lower
            def augmented(M,A,B):return np.maximum(base(M,A,B),forced_values(M,A,B)[1])
            L=None;counters=pool.Counters()
            with patch.object(pool,'free_lower',augmented):
                for b in (4,16):
                    check();Lroot,L,_=pool.lower_sweep(left,right,case['cost'],U,occ,b,counters,L)
            targetL=next(a for a in old['forced_transport_screen']['arms'] if a['forced'] and a['budgets']==[4,16])['levels'][-1]['lower']
            if abs(Lroot-targetL)>1e-8:raise RuntimeError('lower endpoint mismatch')
            newplans=[list(p) for p in plans];newU=[None]*(T+1);newU[T]=U[T]
            for t in range(T-1,-1,-1):
                check();M=costs[t]+newU[t+1]
                vals=np.array([value(p,M) for p in plans[t]]).reshape(shapes[t])
                score=occ[t]*np.maximum(vals-base(M,left.kernels[t],right.kernels[t]),0.)
                for idx in np.argsort(-score.ravel(),kind='stable')[:16]:
                    if score.ravel()[idx]<=0:continue
                    check();i,j=divmod(int(idx),shapes[t][1])
                    v,dense,*_=pool.transport_plan_and_dual(left.kernels[t][i],right.kernels[t][j],M)
                    p=pack(dense)
                    if residual(p,left.kernels[t][i],right.kernels[t][j])>1e-8:raise RuntimeError('replacement primal mismatch')
                    if v<vals[i,j]:newplans[t][idx]=p;vals[i,j]=v
                newU[t]=vals
            _,dense,*_=pool.transport_plan_and_dual(left.initial,right.initial,newU[0]);nr=pack(dense)
            if value(rootplan,newU[0])<value(nr,newU[0]):nr=rootplan
            upper,verified=evaluate(newplans,nr,costs,shapes,check)
            newocc,forward=occupation(newplans,nr,left,right,costs,shapes,check)
            if max(abs(upper-forward),abs(upper-old['upper_policy_screen']['levels'][-1]['upper']),max(float(np.max(abs(a-b))) for a,b in zip(verified,newU)))>1e-8:raise RuntimeError('improved endpoint mismatch')
            records=[];local_calls=lp_calls=0
            def add(t,i,j,a,b,M,plan,lower,mass):
                nonlocal local_calls,lp_calls
                check();forced=np.count_nonzero(a)>0 and (np.count_nonzero(a)==1 or np.count_nonzero(b)==1)
                q=_transport_value(a,b,M);local_calls+=1;lp_calls+=int(not forced)
                slack=q-lower;regret=value(plan,M)-q
                if min(slack,regret)<-1e-8:raise RuntimeError('negative decomposition component')
                records.append(dict(t=t,i=i,j=j,mass=float(mass),forced=bool(forced),
                    weighted_slack=float(mass*slack),weighted_regret=float(mass*regret),weighted_total=float(mass*(slack+regret))))
            add(-1,0,0,left.initial,right.initial,L[0],nr,Lroot,1.)
            for t in range(T):
                M=costs[t]+L[t+1]
                for i,j in np.argwhere(newocc[t]>0):
                    add(t,int(i),int(j),left.kernels[t][i],right.kernels[t][j],M,newplans[t][int(i)*shapes[t][1]+int(j)],L[t][i,j],newocc[t][i,j])
            total=sum(r['weighted_total'] for r in records);gap=upper-Lroot
            if abs(total-gap)>1e-8:raise RuntimeError('telescoping mismatch')
            ranked=sorted((r for r in records if not r['forced']),key=lambda r:-r['weighted_total'])
            def coverage(n):return sum(r['weighted_total'] for r in ranked[:n])/gap
            def needed(frac):
                s=0.
                for n,r in enumerate(ranked,1):
                    s+=r['weighted_total']
                    if s>=frac*gap:return n
                return None
            row.update(status='completed',lower=Lroot,upper=upper,relative_width=gap/Lroot,
                weighted_slack=sum(r['weighted_slack'] for r in records),weighted_regret=sum(r['weighted_regret'] for r in records),
                weighted_forced_residual=sum(r['weighted_total'] for r in records if r['forced']),
                local_diagnostic_calls=local_calls,diagnostic_lp_calls=lp_calls,
                top16_fraction=coverage(16),top32_fraction=coverage(32),count_for_50percent=needed(.5),count_for_90percent=needed(.9),
                concentration_gate_passed=coverage(16)>=.8,telescoping_error=abs(total-gap),
                layer_totals=[dict(t=t,slack=sum(r['weighted_slack'] for r in records if r['t']==t),regret=sum(r['weighted_regret'] for r in records if r['t']==t)) for t in range(-1,T)],
                records=records,seconds=time.perf_counter()-tick)
            print(json.dumps({k:row[k] for k in ('process','relative_width','top16_fraction','count_for_90percent','concentration_gate_passed','seconds')}),flush=True)
        result['status']='completed'
    except TimeoutError as exc:result.update(status='budget_stopped',reason=str(exc))
    except Exception as exc:result.update(status='failed',reason=repr(exc));raise
    finally:
        result['total_seconds']=time.perf_counter()-started
        with (OUT/'results.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps(dict(status=result['status'],seconds=result['total_seconds'])),flush=True)

if __name__=='__main__':freeze() if '--freeze' in sys.argv else run()
