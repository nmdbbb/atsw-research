"""Single fixed-policy selection ablation after residual concentration gate."""
from __future__ import annotations
import json
import time
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'probes'))
import root_gap_decomposition as d
pool=d.pool
OUT=ROOT/'runs/cycle_2/residual_priority_screen'
CASE=dict(process='second_order_nonmonotone',k=2,delta=.18,cost='absolute')
FILES=d.FILES+['probes/residual_priority_screen.py','runs/cycle_2/root_gap_decomposition/manifest.json','runs/cycle_2/root_gap_decomposition/results.json']

def prepare(check):
    x,y=d.paths(CASE['process'])
    left,right=[d.build_window_model(z,k=CASE['k'],delta=CASE['delta'],shift=0.) for z in (x,y)]
    T=left.horizon;shapes=[(len(left.states[t]),len(right.states[t])) for t in range(T+1)]
    costs=[d.stage_cost(left.representatives[t+1],right.representatives[t+1],CASE['cost']) for t in range(T)]
    U=[None]*(T+1);U[T]=np.zeros(shapes[T]);plans=[None]*T;calls=0
    for t in range(T-1,-1,-1):
        check();layer=d.prepare_layer(costs[t]+U[t+1],left.kernels[t],right.kernels[t])
        U[t]=np.empty(shapes[t]);plans[t]=[]
        for i,j in np.ndindex(shapes[t]):
            if calls%128==0:check()
            p=layer.evaluate(i,j);plans[t].append((p.rows,p.cols,p.masses));U[t][i,j]=p.value;calls+=1
    rp=d.prepare_layer(U[0],[left.initial],[right.initial]).evaluate(0,0)
    rootplan=(rp.rows,rp.cols,rp.masses)
    occ,forward=d.occupation(plans,rootplan,left,right,costs,shapes,check)
    if abs(forward-rp.value)>1e-8:raise RuntimeError('initial replay mismatch')
    newplans=[list(p) for p in plans];newU=[None]*(T+1);newU[T]=U[T]
    for t in range(T-1,-1,-1):
        check();M=costs[t]+newU[t+1]
        vals=np.array([d.value(p,M) for p in plans[t]]).reshape(shapes[t])
        score=occ[t]*np.maximum(vals-pool.free_lower(M,left.kernels[t],right.kernels[t]),0.)
        for idx in np.argsort(-score.ravel(),kind='stable')[:16]:
            if score.ravel()[idx]<=0:continue
            check();i,j=divmod(int(idx),shapes[t][1])
            v,dense,*_=pool.transport_plan_and_dual(left.kernels[t][i],right.kernels[t][j],M)
            p=d.pack(dense)
            if d.residual(p,left.kernels[t][i],right.kernels[t][j])>1e-8:raise RuntimeError('primal mismatch')
            if v<vals[i,j]:newplans[t][idx]=p;vals[i,j]=v
        newU[t]=vals
    _,dense,*_=pool.transport_plan_and_dual(left.initial,right.initial,newU[0]);nr=d.pack(dense)
    if d.value(rootplan,newU[0])<d.value(nr,newU[0]):nr=rootplan
    upper,verified=d.evaluate(newplans,nr,costs,shapes,check)
    newocc,forward=d.occupation(newplans,nr,left,right,costs,shapes,check)
    if max(abs(upper-forward),max(float(np.max(abs(a-b))) for a,b in zip(verified,newU)))>1e-8:raise RuntimeError('improved replay mismatch')
    return left,right,costs,shapes,newplans,newocc,upper,newU

def freeze():
    OUT.mkdir(parents=True,exist_ok=True)
    m=dict(schema='residual-priority-screen-v1',case=CASE,T=5,paths_per_side=128,seed=1000,shift=0.,
      design='one posthoc fine case selected by frozen top16 concentration gate; no coarse case or budget escalation',
      method='Same reconstructed improved B16 fixed policy and occupation, forced lower floor, B4 then B16. Change only score from mu*(U-lower) to mu*(pi(c+lower_child)-lower). Preserve shared dual updates and selected budgets.',
      primary_gate='new B16 lower gains >=5% of current-gap control root width in VALUE units: (Lnew-Lcontrol)/(U-Lcontrol)>=.05',
      deadline_seconds=30,deadline_rule='cooperative each layer/solve and every128 initialization pairs; finish native operation then stop; no retry',
      nonclaims=['known Bellman residual priority baseline, not novelty','quality gate, not equal wall time or speed proof','fixed upper remains inadequate for 0.5%','no diagnostic local OT q or exact reference enters selection'],
      hashes={p:d.digest(p) for p in FILES})
    with (OUT/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(m,indent=2)+'\n')

def run():
    if (OUT/'results.json').exists():raise RuntimeError('preserve results')
    m=json.loads((OUT/'manifest.json').read_bytes())
    for p,h in m['hashes'].items():
        if d.digest(p)!=h:raise RuntimeError('source changed: '+p)
    diag=json.loads((ROOT/'runs/cycle_2/root_gap_decomposition/results.json').read_bytes())
    if diag['manifest_sha256']!=d.digest('runs/cycle_2/root_gap_decomposition/manifest.json'):raise RuntimeError('diagnostic pin mismatch')
    old=next(r for r in diag['cases'] if all(r[k]==v for k,v in CASE.items()))
    if not old['concentration_gate_passed']:raise RuntimeError('concentration gate failed')
    started=time.perf_counter();result=dict(status='running',case=CASE,arms=[],manifest_sha256=d.digest('runs/cycle_2/residual_priority_screen/manifest.json'))
    def check():
        if time.perf_counter()-started>30:raise TimeoutError('30s budget')
    try:
        left,right,costs,shapes,plans,occ,upper,U=prepare(check)
        if abs(upper-old['upper'])>1e-8 or [left.model_hash,right.model_hash]!=old['model_hashes']:raise RuntimeError('archived policy endpoint/model mismatch')
        result.update(shared_setup_seconds=time.perf_counter()-started,upper=upper,model_hashes=old['model_hashes'])
        reference=next(r['reference'] for r in json.loads((ROOT/'runs/cycle_2/forced_transport_screen/results.json').read_bytes())['cases'] if all(r[k]==v for k,v in CASE.items()))
        for local_score in (False,True):
            tick=time.perf_counter();floors=None;counters=pool.Counters();levels=[];scan_edges=0;scan_pairs=0;min_signed=0.
            for budget in (4,16):
                L=[None]*(left.horizon+1);L[-1]=np.zeros(shapes[-1])
                for t in range(left.horizon-1,-1,-1):
                    check();M=costs[t]+L[t+1]
                    lt=np.maximum(pool.free_lower(M,left.kernels[t],right.kernels[t]),d.forced_values(M,left.kernels[t],right.kernels[t])[1])
                    if floors is not None:lt=np.maximum(lt,floors[t])
                    bound=U[t]
                    if local_score:
                        bound=np.zeros(shapes[t])
                        for i,j in np.argwhere(occ[t]>0):
                            p=plans[t][int(i)*shapes[t][1]+int(j)]
                            bound[i,j]=d.value(p,M);scan_pairs+=1;scan_edges+=len(p[2])
                    seen=set()
                    for _ in range(budget):
                        check();signed=bound-lt
                        min_signed=min(min_signed,float(signed[occ[t]>0].min(initial=0)))
                        if min_signed < -1e-8:raise RuntimeError('local residual negative')
                        score=occ[t]*np.maximum(signed,0.)
                        for pair in seen:score[pair]=-np.inf
                        i,j=np.unravel_index(int(np.argmax(score)),score.shape)
                        if not np.isfinite(score[i,j]):break
                        seen.add((i,j));counters.selected_pair_solves+=1
                        _,_,alpha,beta,_=pool.transport_plan_and_dual(left.kernels[t][i],right.kernels[t][j],M,counters)
                        lt=np.maximum(lt,(left.kernels[t]@alpha)[:,None]+(right.kernels[t]@beta)[None,:])
                    L[t]=np.minimum(lt,U[t])
                _,_,_,_,lower=pool.transport_plan_and_dual(left.initial,right.initial,L[0],counters)
                if lower>reference+1e-8:raise RuntimeError('lower exceeds reference')
                floors=L;levels.append(dict(budget=budget,lower=lower,relative_width=(upper-lower)/lower))
            # Independent control path uses the unmodified lower_sweep implementation.
            result['arms'].append(dict(local_residual_score=local_score,levels=levels,seconds=time.perf_counter()-tick,
                selected_calls=counters.selected_pair_solves,LP_calls=counters.linprog_calls,score_plan_pairs=scan_pairs,score_plan_edges=scan_edges,min_signed_residual=min_signed))
        check();tick=time.perf_counter();base=pool.free_lower
        def augmented(M,A,B):return np.maximum(base(M,A,B),d.forced_values(M,A,B)[1])
        L=None
        with d.patch.object(pool,'free_lower',augmented):
            for b in (4,16):
                independent,L,_=pool.lower_sweep(left,right,CASE['cost'],U,occ,b,pool.Counters(),L)
        control=result['arms'][0]['levels'][-1]['lower'];new=result['arms'][1]['levels'][-1]['lower']
        if abs(independent-control)>1e-8:raise RuntimeError('control implementation mismatch')
        result.update(independent_control_check_seconds=time.perf_counter()-tick,independent_control_error=abs(independent-control),
            root_gap_fraction_removed=(new-control)/(upper-control),quality_gate_passed=(new-control)/(upper-control)>=.05,status='completed')
    except TimeoutError as exc:result.update(status='budget_stopped',reason=str(exc))
    except Exception as exc:result.update(status='failed',reason=repr(exc));raise
    finally:
        result['total_seconds']=time.perf_counter()-started
        with (OUT/'results.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps(result,indent=2))

if __name__=='__main__':freeze() if '--freeze' in sys.argv else run()
