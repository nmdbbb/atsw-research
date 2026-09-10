"""Support-only development audit at frozen horizons/path counts; no OT/grid."""
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'adapters'),str(ROOT/'probes')]
import generators
from common_model import build_window_model
from policy_pool_common_smoke import paths
OUT=ROOT/'runs/cycle_2/support_scale_audit'
CASES=[dict(process='ar1',k=1,delta=.5),dict(process='second_order_nonmonotone',k=2,delta=.18)]
FILES=['probes/support_scale_audit.py','generators.py','adapters/common_model.py','probes/policy_pool_common_smoke.py',
       'frozen_design.json','frozen_design_amendment_1.json','runs/cycle_2/binary_transport_screen/results.json']

def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()

def summary(X,k,delta,check):
    bins=np.floor(X/delta).astype(np.int64);codes=[];sizes=[]
    for t in range(X.shape[1]):
        check();states,inverse=np.unique(bins[:,max(0,t-k+1):t+1],axis=0,return_inverse=True)
        codes.append(inverse);sizes.append(len(states))
    rows=[]
    for t in range(X.shape[1]-1):
        check();edges=np.unique(np.column_stack((codes[t],codes[t+1])),axis=0)
        degree=np.bincount(edges[:,0],minlength=sizes[t])
        if (degree==0).any():raise RuntimeError('observed state has no successors')
        rows.append(dict(states=sizes[t],singleton=int(np.sum(degree==1)),binary=int(np.sum(degree==2)),
                         general=int(np.sum(degree>2)),edges=len(edges),max_degree=int(degree.max())))
    return rows

def paircounts(A,B):
    layers=[]
    for t,(a,b) in enumerate(zip(A,B)):
        total=a['states']*b['states'];nonforced=(a['states']-a['singleton'])*(b['states']-b['singleton'])
        general=a['general']*b['general']
        layers.append(dict(t=t,total=total,forced=total-nonforced,binary=nonforced-general,general=general))
    totals={key:sum(x[key] for x in layers) for key in ('total','forced','binary','general')}
    return dict(layers=layers,totals=totals,binary_fraction_nonforced=totals['binary']/(totals['binary']+totals['general']),forced_fraction=totals['forced']/totals['total'])

def freeze():
    OUT.mkdir(parents=True,exist_ok=True)
    m=dict(schema='support-scale-audit-v1',cases=CASES,seed=1000,shift=0.,T=50,
      design='posthoc structural extrapolation audit at frozen path counts4000/8000; one development seed/shift only; no cost-dependent solver output',
      method='unique history and transition-code pairs give exact positive support counts without dense kernels or pair enumeration; compare against common_model on old T5n128 first',
      gate='Binary-direct route survives support-coverage screen iff binary fraction among nonforced>=20% on both T50 cases. No savings/time/certificate claim from support counts.',
      deadline_seconds=30,deadline_rule='cooperative at each history/layer; no rerun/downsize',
      hashes={p:digest(p) for p in FILES})
    with (OUT/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(m,indent=2)+'\n')

def run():
    if (OUT/'results.json').exists():raise RuntimeError('preserve results')
    m=json.loads((OUT/'manifest.json').read_bytes())
    for p,h in m['hashes'].items():
        if digest(p)!=h:raise RuntimeError('changed source: '+p)
    design=json.loads((ROOT/'frozen_design.json').read_bytes());amend=json.loads((ROOT/'frozen_design_amendment_1.json').read_bytes())
    old=json.loads((ROOT/'runs/cycle_2/binary_transport_screen/results.json').read_bytes())
    start=time.perf_counter();result=dict(status='running',cases=[],manifest_sha256=digest('runs/cycle_2/support_scale_audit/manifest.json'))
    def check():
        if time.perf_counter()-start>30:raise TimeoutError('30s structural audit budget')
    try:
        for case in CASES:
            x,y=paths(case['process']);tiny=[summary(z,case['k'],case['delta'],check) for z in(x,y)]
            for z,rows in zip((x,y),tiny):
                model=build_window_model(z,k=case['k'],delta=case['delta'],shift=0.)
                for K,r in zip(model.kernels,rows):
                    degrees=np.count_nonzero(K>0,axis=1)
                    if [len(K),int(sum(degrees==1)),int(sum(degrees==2)),int(sum(degrees>2)),int(degrees.sum())]!=[r[k] for k in ('states','singleton','binary','general','edges')]:raise RuntimeError('independent model support mismatch')
            small=paircounts(*tiny)
            ref=next(r for r in old['cases'] if all(r[k]==v for k,v in case.items()))['arms'][1]['counts']
            if small['totals']['binary']!=ref['binary_calls'] or small['totals']['general']!=ref['LP_calls']:raise RuntimeError('archived support count mismatch')
            n=design['grid']['paths_per_side'][str(case['delta'])];T=design['grid']['T'];seeds=np.random.SeedSequence(1000).spawn(2)
            params=amend['two_sided_sampling_convention'][case['process']]
            big=[];hashes=[]
            for side,seed in zip(('side_A','side_B'),seeds):
                check();X=generators.FAMILIES[case['process']](T,n,np.random.default_rng(seed),**params[side])
                hashes.append(hashlib.sha256(X.tobytes()).hexdigest());big.append(summary(X,case['k'],case['delta'],check))
            large=paircounts(*big)
            row=dict(**case,T=T,paths_per_side=n,seed=1000,shift=0.,tiny=small,full_horizon=large,
                     sides=big,path_array_sha256=hashes,small_model_verification='passed',coverage_gate_passed=large['binary_fraction_nonforced']>=.2)
            result['cases'].append(row)
            print(json.dumps(dict(case=case,n=n,T=T,tiny_binary_fraction=small['binary_fraction_nonforced'],T50_binary_fraction=large['binary_fraction_nonforced'],T50_forced_fraction=large['forced_fraction'],gate=row['coverage_gate_passed'])),flush=True)
        result.update(status='completed',both_cases_coverage_gate_passed=all(r['coverage_gate_passed'] for r in result['cases']))
    except TimeoutError as exc:result.update(status='budget_stopped',reason=str(exc))
    except Exception as exc:result.update(status='failed',reason=repr(exc));raise
    finally:
        result['total_seconds']=time.perf_counter()-start
        with (OUT/'results.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps(dict(status=result['status'],seconds=result['total_seconds'])),flush=True)

if __name__=='__main__':freeze() if '--freeze' in sys.argv else run()
