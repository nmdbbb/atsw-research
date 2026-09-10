"""Posthoc local defect census; all DP values still use the baseline solver."""
from fractions import Fraction
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'probes'))
import binary_transport_screen as base
OUT=ROOT/'runs/cycle_2/local_monge_defect_audit'
FILES=base.FILES+['probes/local_monge_defect_audit.py','adapters/policy_pool_candidate.py',
 'runs/cycle_2/binary_transport_screen/results.json','runs/cycle_2/support_monge_screen/manifest.json',
 'runs/cycle_2/support_monge_screen/results.json']

def freeze():
    OUT.mkdir(parents=True,exist_ok=True)
    m=dict(schema='local-monge-defect-audit-v1',cases=base.CASES,T=5,paths_per_side=128,seed=1000,shift=0.,
      design='posthoc after strict Monge screen; expected roundoff-scale violations not yet measured',
      method='On each general support matrix in directbinary DP, sum exact positive adjacent dyadic defects; always use unchanged LP for DP values. No candidate consumes the defect.',
      threshold='1e-10 exact rational',gate='At least20% of strict-rejected general support matrices have positive defect sum<=1e-10 on fine case permits local exact-interval fixture only, not solver/grid promotion.',
      deadline_seconds=30,deadline_rule='cooperative per matrix and layer; finish current operation; no repeat/downsize',
      mathematical_bound='Fij=sum_{k<i,l<j}positive_defect_kl makes M-F Monge and <=M. Exact NW yields local width<NW,F><=sum positive defects. Requires exact normalized marginals for exact interval; census only measures matrices.',
      hashes={p:base.digest(p) for p in FILES})
    with (OUT/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(m,indent=2)+'\n')

def run():
    if (OUT/'results.json').exists():raise RuntimeError('preserve result')
    m=json.loads((OUT/'manifest.json').read_bytes())
    for p,h in m['hashes'].items():
        if base.digest(p)!=h:raise RuntimeError('source changed: '+p)
    old=json.loads((ROOT/'runs/cycle_2/binary_transport_screen/results.json').read_bytes())
    started=time.perf_counter();result=dict(status='running',cases=[],manifest_sha256=base.digest('runs/cycle_2/local_monge_defect_audit/manifest.json'))
    def check():
        if time.perf_counter()-started>30:raise TimeoutError('30s budget')
    try:
        for case in base.CASES:
            check();x,y=base.paths(case['process'])
            left,right=[base.build_window_model(z,k=case['k'],delta=case['delta'],shift=0.) for z in(x,y)]
            row=dict(**case,defects=[],matrix_audit_seconds=0.);result['cases'].append(row)
            original=base._transport_value
            def audit(a,b,M):
                check();tick=time.perf_counter()
                Q=[[Fraction(float(v)) for v in line] for line in M]
                total=sum((max(Fraction(0),Q[i][j]+Q[i+1][j+1]-Q[i][j+1]-Q[i+1][j]) for i in range(len(Q)-1) for j in range(len(Q[0])-1)),Fraction(0))
                row['matrix_audit_seconds']+=time.perf_counter()-tick
                row['defects'].append(dict(shape=list(M.shape),sum_positive_defects=float(total),sum_exact=str(total),
                    strict_monge=total==0,positive_below_threshold=0<total<=Fraction(1,10**10)))
                return original(a,b,M)
            with patch.object(base,'_transport_value',audit):
                _,arm=base.solve(left,right,case['cost'],'binary_per_pair',check)
            ref=next(c for c in old['cases'] if all(c[k]==v for k,v in case.items()))
            error=abs(arm['root']-ref['arms'][0]['root'])
            if error>1e-8:raise RuntimeError('root mismatch')
            zeros=sum(d['strict_monge'] for d in row['defects']);tiny=sum(d['positive_below_threshold'] for d in row['defects']);rejected=len(row['defects'])-zeros
            row.update(status='completed',strict_monge=zeros,strict_rejected=rejected,positive_small=tiny,
                fraction_rejected_small=tiny/rejected if rejected else 0.,root_error=error,arm=arm)
            row['local_fixture_gate_passed']=case['k']==2 and row['fraction_rejected_small']>=.2
            print(json.dumps({k:row[k] for k in ('process','strict_rejected','positive_small','fraction_rejected_small','local_fixture_gate_passed')}),flush=True)
        result['status']='completed'
    except TimeoutError as exc:result.update(status='budget_stopped',reason=str(exc))
    except Exception as exc:result.update(status='failed',reason=repr(exc));raise
    finally:
        result['total_seconds']=time.perf_counter()-started
        with (OUT/'results.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps(dict(status=result['status'],seconds=result['total_seconds'])),flush=True)

if __name__=='__main__':freeze() if '--freeze' in sys.argv else run()
