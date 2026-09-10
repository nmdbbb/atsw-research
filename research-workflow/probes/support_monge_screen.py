"""Same-kernel exact numerical DP ablation of support-local Monge dispatch."""
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
OUT=ROOT/'runs/cycle_2/support_monge_screen'
FILES=base.FILES+['probes/support_monge_screen.py','adapters/support_monge.py',
 'runs/cycle_2/binary_transport_screen/manifest.json','runs/cycle_2/binary_transport_screen/results.json']

def freeze():
    OUT.mkdir(parents=True,exist_ok=True)
    m=dict(schema='support-monge-screen-v1',cases=base.CASES,T=5,paths_per_side=128,seed=1000,shift=0.,
      design='posthoc local structural screen following binary-direct baseline; before timing, terminal Monge applicability known',
      method='Same binary_per_pair DP both arms; on remaining general support matrices, Fraction-exact adjacent Monge check then numeric NW if passed, otherwise identical LP fallback.',
      gate='Opportunity if at least20% of remaining general LP calls avoided on EACH case; one-repeat times descriptive, not speed claim.',
      deadline_seconds=45,deadline_rule='cooperative each layer/128pairs and before each structural check; no rerun/downsize',
      checks='all continuation tables and roots agree with current binary baseline and archived roots within1e-8',
      nonclaims=['classical Monge NW condition, not novelty','predicate exact on represented matrix; recurrence remains float64 without outward certificate','no full-grid or SOTA claim'],
      hashes={p:base.digest(p) for p in FILES})
    with (OUT/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(m,indent=2)+'\n')

def run():
    if (OUT/'results.json').exists():raise RuntimeError('preserve results')
    m=json.loads((OUT/'manifest.json').read_bytes())
    for p,h in m['hashes'].items():
        if base.digest(p)!=h:raise RuntimeError('source changed: '+p)
    old=json.loads((ROOT/'runs/cycle_2/binary_transport_screen/results.json').read_bytes())
    if old['manifest_sha256']!=base.digest('runs/cycle_2/binary_transport_screen/manifest.json'):raise RuntimeError('old manifest mismatch')
    started=time.perf_counter();result=dict(status='running',cases=[],manifest_sha256=base.digest('runs/cycle_2/support_monge_screen/manifest.json'))
    def check():
        if time.perf_counter()-started>45:raise TimeoutError('45s budget')
    try:
        for case in base.CASES:
            check();tick=time.perf_counter();x,y=base.paths(case['process'])
            left,right=[base.build_window_model(z,k=case['k'],delta=case['delta'],shift=0.) for z in (x,y)]
            row=dict(**case,model_seconds=time.perf_counter()-tick,model_hashes=[left.model_hash,right.model_hash]);result['cases'].append(row)
            reference=next(r for r in old['cases'] if all(r[k]==v for k,v in case.items()))
            if row['model_hashes']!=reference['model_hashes']:raise RuntimeError('model mismatch')
            tables,control=base.solve(left,right,case['cost'],'binary_per_pair',check)
            counts=dict(check_calls=0,accepted=0,rejected=0,adjacent_checks=0,dyadic_entries=0,check_and_NW_seconds=0.)
            original=base._transport_value
            def dispatch(a,b,M):
                check();tick=time.perf_counter();value,c=monge_value(a,b,M)
                counts['check_and_NW_seconds']+=time.perf_counter()-tick
                counts['check_calls']+=1;counts['adjacent_checks']+=c['adjacent_checks'];counts['dyadic_entries']+=c['dyadic_entries']
                if value is None:
                    counts['rejected']+=1;return original(a,b,M)
                counts['accepted']+=1;return value
            with patch.object(base,'_transport_value',dispatch):
                newtables,candidate=base.solve(left,right,case['cost'],'binary_per_pair',check)
            error=max(float(np.max(abs(a-b))) for a,b in zip(tables,newtables))
            rooterror=abs(candidate['root']-reference['arms'][0]['root'])
            if max(error,rooterror)>1e-8:raise RuntimeError('numerical target mismatch')
            # Base runner's LP_calls counts dispatch entries before this hook.
            row.update(control=control,candidate=candidate,dispatch=counts,table_max_error=error,root_error=rooterror,
                actual_candidate_LP_calls=counts['rejected'],general_LP_calls_avoided_fraction=counts['accepted']/counts['check_calls'],
                candidate_over_control_seconds=candidate['seconds']/control['seconds'],status='completed',
                counter_note='candidate.counts.LP_calls counts general dispatches, actual LP calls are dispatch.rejected')
            row['opportunity_gate_passed']=row['general_LP_calls_avoided_fraction']>=.2
            print(json.dumps(dict(case=case,LP_before=control['counts']['LP_calls'],LP_after=counts['rejected'],accepted=counts['accepted'],times=[control['seconds'],candidate['seconds']])),flush=True)
        result.update(status='completed',both_cases_opportunity_gate_passed=all(r['opportunity_gate_passed'] for r in result['cases']))
    except TimeoutError as exc:result.update(status='budget_stopped',reason=str(exc))
    except Exception as exc:result.update(status='failed',reason=repr(exc));raise
    finally:
        result['total_seconds']=time.perf_counter()-started
        with (OUT/'results.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps(dict(status=result['status'],seconds=result['total_seconds'])),flush=True)

if __name__=='__main__':freeze() if '--freeze' in sys.argv else run()
