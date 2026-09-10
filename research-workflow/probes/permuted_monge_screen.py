"""Exact represented-matrix Monge dispatch under shared/private SVD ordering."""
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'probes'),str(ROOT/'adapters')]
import binary_transport_screen as base
from support_monge import monge_value
from policy_pool_candidate import _orders
OUT=ROOT/'runs/cycle_2/permuted_monge_screen'
FILES=base.FILES+['probes/permuted_monge_screen.py','adapters/support_monge.py','adapters/policy_pool_candidate.py',
 'runs/cycle_2/support_monge_screen/manifest.json','runs/cycle_2/support_monge_screen/results.json']

def freeze():
    OUT.mkdir(parents=True,exist_ok=True)
    m=dict(schema='permuted-monge-screen-v1',cases=base.CASES,T=5,paths_per_side=128,seed=1000,shift=0.,
      modes=['identity','shared_SVD','shared_then_local_SVD'],design='posthoc original-order failures known; freeze before new order evaluation',
      method='Same directbinary exact numerical DP. Identity Monge first. For failed general supports, test restricted full-layer SVD order and its reversed-right orientation; final arm additionally tests local SVD two orientations. Fraction-exact check before NW, else identical LP.',
      gate='shared_SVD avoids >=20% of identity baseline remaining LP on EACH case; otherwise reject shared-order research premise on this screen. Local improvements remain private-work baseline only.',
      deadline_seconds=60,deadline_rule='cooperative each layer/128parentpairs and general dispatch; finish nativeoperation no repeat/downsize',
      checks='all DP tables and roots match identity arm and archived roots within1e-8',
      accounting='includes global SVD each layer, rank construction, support extraction/reordering, exact checks, private SVDs, snapshots/root; separate SVD/check counts and times; support-order source not free',
      nonclaims=['No new Monge theorem or SVD-policy novelty','NW floating tiny-mass limitation retained','No outward root certificate or statistical speed claim'],
      hashes={p:base.digest(p) for p in FILES})
    with (OUT/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(m,indent=2)+'\n')

def run():
    if (OUT/'results.json').exists():raise RuntimeError('preserve result')
    m=json.loads((OUT/'manifest.json').read_bytes())
    for p,h in m['hashes'].items():
        if base.digest(p)!=h:raise RuntimeError('source changed: '+p)
    old=json.loads((ROOT/'runs/cycle_2/support_monge_screen/results.json').read_bytes())
    if old['manifest_sha256']!=base.digest('runs/cycle_2/support_monge_screen/manifest.json'):raise RuntimeError('old manifest mismatch')
    started=time.perf_counter();result=dict(status='running',cases=[],manifest_sha256=base.digest('runs/cycle_2/permuted_monge_screen/manifest.json'))
    def check():
        if time.perf_counter()-started>60:raise TimeoutError('60s budget')
    try:
        for case in base.CASES:
            check();tick=time.perf_counter();x,y=base.paths(case['process'])
            left,right=[base.build_window_model(z,k=case['k'],delta=case['delta'],shift=0.) for z in(x,y)]
            row=dict(**case,model_seconds=time.perf_counter()-tick,arms=[]);result['cases'].append(row)
            ref=next(r for r in old['cases'] if all(r[k]==v for k,v in case.items()))
            if [left.model_hash,right.model_hash]!=ref['model_hashes']:raise RuntimeError('model mismatch')
            identity_tables=None
            for mode in m['modes']:
                counts=dict(identity_accepted=0,shared_accepted=0,local_accepted=0,LP_calls=0,global_SVD_calls=0,local_SVD_calls=0,
                            global_SVD_seconds=0.,local_SVD_seconds=0.,exact_check_calls=0,exact_adjacent_checks=0,dyadic_entries=0,
                            exact_check_NW_seconds=0.,support_rank_sorts=0)
                original=base._transport_value;original_binary=base.BinaryLayer
                # base.solve dispatches after support restriction; lookup uses that
                # immutable layer's original transition rows and column supports.
                state={};sequence=list(range(left.horizon-1,-1,-1))+[-1]
                class Layer(original_binary):
                    def __init__(self,M,reuse=False):
                        super().__init__(M,reuse);t=sequence.pop(0)
                        A=left.initial[None,:] if t==-1 else left.kernels[t]
                        B=right.initial[None,:] if t==-1 else right.kernels[t]
                        # Reproduce only the general-call sequence; singletons and
                        # binary cases never reach the patched LP routine.
                        sa=[np.flatnonzero(a>0) for a in A];sb=[np.flatnonzero(b>0) for b in B]
                        state['general_supports']=iter((r,c) for r in sa for c in sb if min(len(r),len(c))>2)
                        if mode!='identity':
                            tick=time.perf_counter();orders=_orders(M);ranks=[]
                            for order in orders[:2]:
                                rank=np.empty(len(order),int);rank[order]=np.arange(len(order));ranks.append(rank)
                            state['ranks']=ranks;counts['global_SVD_calls']+=1;counts['global_SVD_seconds']+=time.perf_counter()-tick
                def attempt(a,b,M):
                    tick=time.perf_counter();v,c=monge_value(a,b,M)
                    counts['exact_check_NW_seconds']+=time.perf_counter()-tick
                    counts['exact_check_calls']+=1;counts['exact_adjacent_checks']+=c['adjacent_checks'];counts['dyadic_entries']+=c['dyadic_entries']
                    return v
                def dispatch(a,b,M):
                    check();rows,cols=next(state['general_supports'])
                    if M.shape!=(len(rows),len(cols)):raise RuntimeError('support dispatch sequence mismatch')
                    v=attempt(a,b,M)
                    if v is not None:counts['identity_accepted']+=1;return v
                    if mode!='identity':
                        rr,cc=state['ranks'];ri=np.argsort(rr[rows],kind='stable');ci=np.argsort(cc[cols],kind='stable')
                        counts['support_rank_sorts']+=2
                        for cj in (ci,ci[::-1]):
                            v=attempt(a[ri],b[cj],M[np.ix_(ri,cj)])
                            if v is not None:counts['shared_accepted']+=1;return v
                    if mode=='shared_then_local_SVD':
                        tick=time.perf_counter();ri,ci,rev=_orders(M);counts['local_SVD_calls']+=1;counts['local_SVD_seconds']+=time.perf_counter()-tick
                        for cj in (ci,rev):
                            v=attempt(a[ri],b[cj],M[np.ix_(ri,cj)])
                            if v is not None:counts['local_accepted']+=1;return v
                    counts['LP_calls']+=1;return original(a,b,M)
                with patch.object(base,'BinaryLayer',Layer),patch.object(base,'_transport_value',dispatch):
                    tables,arm=base.solve(left,right,case['cost'],'binary_per_pair',check)
                if identity_tables is None:identity_tables=tables
                err=max(float(np.max(abs(a-b))) for a,b in zip(tables,identity_tables))
                if max(err,abs(arm['root']-ref['candidate']['root']))>1e-8:raise RuntimeError('original target mismatch')
                arm.update(order_mode=mode,dispatch=counts,table_error=err);row['arms'].append(arm)
            initial,shared,local=row['arms']
            row.update(status='completed',shared_LP_saved_fraction=1-shared['dispatch']['LP_calls']/initial['dispatch']['LP_calls'])
            row['shared_gate_passed']=row['shared_LP_saved_fraction']>=.2
            print(json.dumps(dict(case=case,LP=[a['dispatch']['LP_calls'] for a in row['arms']],times=[a['seconds'] for a in row['arms']],gate=row['shared_gate_passed'])),flush=True)
        result.update(status='completed',both_shared_gates_passed=all(r['shared_gate_passed'] for r in result['cases']))
    except TimeoutError as exc:result.update(status='budget_stopped',reason=str(exc))
    except Exception as exc:result.update(status='failed',reason=repr(exc));raise
    finally:
        result['total_seconds']=time.perf_counter()-started
        with (OUT/'results.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps(dict(status=result['status'],seconds=result['total_seconds'])),flush=True)

if __name__=='__main__':freeze() if '--freeze' in sys.argv else run()
