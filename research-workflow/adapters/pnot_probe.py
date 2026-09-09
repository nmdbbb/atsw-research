"""Preregistered tiny audit of original PNOT C++, written before execution.

Scope: source revision 9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a;
five fixed handcrafted fixtures in runs/cycle_1/pnot_cases.json; p=1,2;
one native thread; no performance claims or full-grid execution.

Before running, source was inspected: pnot/{__init__,solver,py_solver,utils}.py,
setup.py, pyproject.toml, src/{wrapper,solver,utils,emd_wrap,printer,main}.cpp,
distribution/EMD headers and relevant network-simplex status/iteration code.
No author Python solver, package initializer, or benchmark main is executed.

Primary pass rule: compiled original Nested with markovian=True must equal
the independent common-model scipy.optimize.linprog DP to absolute 1e-9 on
the four deterministic-root fixtures, for both powers. Native quantized
cells and normalized conditional kernels must equal the common k=1 model.
The analytic first-cost control has values 2/3 and 4/3. Source model units
are additive V=AW_p^p, so the returned scalar is never rooted.

Target-separation rules, fixed in the JSON before execution: k=1 and k=2
differ on second_order_matters; k=2 and full history differ on
full_history_is_not_k2; stock PNOT selects a single root on the random
initial-law fixture whereas common_model couples the initial laws. These
last executions are deliberate ineligible diagnostic calls, never scores.

Backend is a CLI invoking original C++ Nested, using the existing MSYS2
UCRT64 g++ (or an explicit --compiler). Build files remain under pnot_native.
The source snapshot is never edited. A forced <chrono> include is the sole
source-compatibility workaround, recorded in the build command; the pinned
solver.cpp uses chrono without including it. OpenMP remains enabled.
No Python fallback, package installation, or toolchain installation exists.

Reject any nonzero process exit, nonfinite result, or original native warning
'OT is not solved optimally'. Native PNOT discards solver statuses, couplings,
and duals after warning, so scalar agreement is only a numerical audit, NOT
a certificate or qualification for the certified comparison frontier.

Preprocessing uses the common builder's integer cells times delta, followed
by transpose to (T+1, samples). This avoids re-deriving the grid boundaries:
common representatives differ from these values by the same shift+delta/2
on both sides. Absolute and squared pair costs are translation invariant.
The native quantization must preserve every supplied cell exactly here.

Run: python research-workflow/adapters/pnot_probe.py
Outputs: pnot_result.json, pnot_build.json, pnot_native/* beside the fixture.
An unavailable backend writes status BLOCKED and exits 2; failed gates write
FAIL and exit 1. PASS remains DEVELOPMENT_NUMERICAL_AUDIT_ONLY.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

from common_model import build_window_model, exact_dp


REVISION = '9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a'
BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / 'third_party' / 'nestedot'
RUNS = BASE / 'runs' / 'cycle_1'
TOLERANCE = 1e-9

# The harness delegates model construction and DP to original source functions.
HARNESS = r'''
#include <Eigen/Dense>
#include <iostream>
#include <iomanip>
#include <map>
#include <set>
#include <vector>
#include "header_dist.h"
Eigen::MatrixXd path2adaptedpath(const Eigen::MatrixXd&, double);
void v_set_add(const Eigen::MatrixXd&, std::set<double>&);
Eigen::MatrixXi quantize_path(Eigen::MatrixXd&, std::map<double,int>&);
Eigen::MatrixXi sort_qpath(const Eigen::MatrixXi&);
std::vector<std::map<std::vector<int>,std::map<int,int>>>
qpath2mu_x(Eigen::MatrixXi&, const bool&);
std::vector<ConditionalDistribution> mu_x2kernel_x(
    std::vector<std::map<std::vector<int>,std::map<int,int>>>&);
double Nested(Eigen::MatrixXd&, Eigen::MatrixXd&, double, const bool&, int, int, bool);

void dump(const char* label, Eigen::MatrixXd& paths, double delta,
          bool markov, std::map<double,int>& v2q, std::vector<double>& q2v) {
    Eigen::MatrixXd adapted = path2adaptedpath(paths, delta);
    for (int t=0; t<adapted.rows(); ++t)
        for (int i=0; i<adapted.cols(); ++i)
            std::cout << "QUANT " << label << " " << t << " " << i
                      << " " << adapted(t,i) << "\n";
    Eigen::MatrixXi qpath = sort_qpath(quantize_path(adapted,v2q).transpose());
    auto law = qpath2mu_x(qpath,markov);
    auto kernels = mu_x2kernel_x(law);
    for (int t=0; t<kernels.size(); ++t)
        for (int i=0; i<kernels[t].nc; ++i) {
            std::cout << "COND " << label << " " << t << " " << i;
            for (int code : kernels[t].conds[i]) std::cout << " " << q2v[code];
            std::cout << "\n";
            auto& dist = kernels[t].dists[i];
            for (int j=0; j<dist.values.size(); ++j)
                std::cout << "EDGE " << label << " " << t << " " << i
                          << " " << q2v[dist.values[j]] << " " << dist.weights[j]
                          << "\n";
        }
}

int main() {
    int times, nx, ny, markov_int, power;
    double delta;
    if (!(std::cin >> times >> nx >> ny >> delta >> markov_int >> power)) return 3;
    if (times<2 || nx<1 || ny<1 || !(delta>0) || (power!=1 && power!=2)) return 4;
    Eigen::MatrixXd X(times,nx),Y(times,ny);
    for (int t=0;t<times;++t) for(int i=0;i<nx;++i) if(!(std::cin>>X(t,i))) return 5;
    for (int t=0;t<times;++t) for(int i=0;i<ny;++i) if(!(std::cin>>Y(t,i))) return 6;
    std::cout << std::setprecision(17);
    bool markov = markov_int != 0;
    auto ax=path2adaptedpath(X,delta), ay=path2adaptedpath(Y,delta);
    std::set<double> values; v_set_add(ax,values); v_set_add(ay,values);
    std::map<double,int> v2q; std::vector<double> q2v;
    for(double v:values) { v2q[v]=q2v.size(); q2v.push_back(v); }
    dump("X",X,delta,markov,v2q,q2v); dump("Y",Y,delta,markov,v2q,q2v);
    double value = Nested(X,Y,delta,markov,1,power,false);
    std::cout << "VALUE " << value << "\n";
}
'''


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def native_run(executable, compiler, case, power, markov):
    delta, shift = case['delta'], case['shift']
    left, right = (np.asarray(case[key], dtype=float) for key in ('left', 'right'))
    cells = [np.floor((paths-shift)/delta).astype(np.int64) for paths in (left,right)]
    inputs = [np.ascontiguousarray((q*delta).T) for q in cells]
    payload = f'{left.shape[1]} {len(left)} {len(right)} {delta:.17g} {int(markov)} {power}\n'
    payload += '\n'.join(' '.join(f'{v:.17g}' for v in item.ravel()) for item in inputs)
    started = time.perf_counter()
    run = subprocess.run([str(executable)], input=payload, text=True,
                         capture_output=True, cwd=compiler.parent, timeout=30)
    elapsed = time.perf_counter()-started
    if run.returncode or 'OT is not solved optimally' in run.stdout + run.stderr:
        raise RuntimeError(f'native solve rejected: {run.returncode}; {run.stdout}; {run.stderr}')
    quantized = {'X': np.empty_like(inputs[0]), 'Y': np.empty_like(inputs[1])}
    conditions, edges, values = {}, {}, []
    for line in run.stdout.splitlines():
        fields = line.split()
        if fields[0] == 'QUANT':
            _, label, t, i, value = fields
            quantized[label][int(t),int(i)] = float(value)
        elif fields[0] == 'COND':
            _, label, t, i, *history = fields
            conditions[(label,int(t),int(i))] = tuple(int(round(float(v)/delta)) for v in history)
        elif fields[0] == 'EDGE':
            _, label, t, i, value, weight = fields
            edges.setdefault((label,int(t),int(i)), {})[int(round(float(value)/delta))] = float(weight)
        elif fields[0] == 'VALUE':
            values.append(float(fields[1]))
        else:
            raise RuntimeError(f'unexpected native output: {line}')
    if len(values) != 1 or not np.isfinite(values[0]):
        raise RuntimeError('missing or invalid native result')
    for label, input_values in zip(('X','Y'),inputs):
        np.testing.assert_array_equal(quantized[label],input_values)
    if markov:
        for label, paths in zip(('X','Y'),(left,right)):
            model = build_window_model(paths,k=1,delta=delta,shift=shift)
            for t, kernel in enumerate(model.kernels):
                actual = {history: edges[key] for key,history in conditions.items()
                          if key[:2] == (label,t)}
                expected = {tuple(model.states[t][i]):
                            {int(model.states[t+1][j,-1]): float(weight)
                             for j,weight in enumerate(row) if weight>0}
                            for i,row in enumerate(kernel)}
                if actual.keys() != expected.keys():
                    raise AssertionError('native conditional-state keys differ')
                for history, distribution in expected.items():
                    if actual[history].keys() != distribution.keys():
                        raise AssertionError('native successor keys differ')
                    for state, weight in distribution.items():
                        if abs(actual[history][state]-weight)>1e-14:
                            raise AssertionError('native conditional probabilities differ')
    return values[0], elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',type=Path,default=Path('C:/msys64/ucrt64/bin/g++.exe'))
    args = parser.parse_args()
    dataset_path = RUNS / 'pnot_cases.json'
    dataset = json.loads(dataset_path.read_text(encoding='utf-8'))
    provenance = json.loads((SOURCE/'AUDIT_PROVENANCE.json').read_text(encoding='utf-8'))
    if provenance['revision'] != REVISION:
        raise RuntimeError('source revision mismatch')
    source_paths = [*sorted((SOURCE/'src').rglob('*.*')),
                    *sorted((SOURCE/'pnot').glob('*.py')), SOURCE/'setup.py',SOURCE/'pyproject.toml']
    source_hashes = {str(path.relative_to(SOURCE)):sha256(path) for path in source_paths}
    report = {'status':'PENDING','scope':'DEVELOPMENT_NUMERICAL_AUDIT_ONLY',
              'backend':'original_pnot_cpp_Nested_via_CLI','python_fallback':False,
              'revision':REVISION,'source_sha256':source_hashes,
              'probe_sha256':sha256(__file__),'dataset_sha256':sha256(dataset_path),
              'native_threads':1,'certificate_frontier_eligible':False,
              'units':'V=AW_p^p','cases':[]}
    if not args.compiler.is_file():
        report.update(status='BLOCKED',reason=f'Existing compiler not found: {args.compiler}')
        write_json(RUNS/'pnot_result.json',report)
        return 2
    native_dir = RUNS/'pnot_native'
    native_dir.mkdir(exist_ok=True)
    harness_path, executable = native_dir/'pnot_harness.cpp', native_dir/'pnot_harness.exe'
    harness_path.write_text(HARNESS,encoding='utf-8')
    command = [str(args.compiler),'-O2','-std=c++17','-fopenmp','-include','chrono',
               '-I'+str(SOURCE/'extern'),'-I'+str(SOURCE/'src'/'include'),str(harness_path),
               *[str(SOURCE/'src'/name) for name in ('solver.cpp','utils.cpp','emd_wrap.cpp','printer.cpp')],
               '-o',str(executable)]
    compiler_version = subprocess.run([str(args.compiler),'--version'],capture_output=True,text=True,timeout=10)
    started = time.perf_counter()
    build = subprocess.run(command,capture_output=True,text=True,cwd=args.compiler.parent,timeout=120)
    write_json(RUNS/'pnot_build.json',{'command':command,'compiler_version':compiler_version.stdout,
               'returncode':build.returncode,'stdout':build.stdout,'stderr':build.stderr,
               'seconds':time.perf_counter()-started,'harness_sha256':sha256(harness_path),
               'compatibility_change':'forced include chrono; original source bytes unchanged'})
    if build.returncode:
        report.update(status='BLOCKED',reason='Native build failed; see pnot_build.json')
        write_json(RUNS/'pnot_result.json',report)
        return 2
    report['executable_sha256'] = sha256(executable)
    try:
        for case in dataset['cases']:
            models = {}
            for memory in (1,2,len(case['left'][0])):
                models[memory] = tuple(build_window_model(case[side],k=memory,
                                      delta=case['delta'],shift=case['shift'])
                                      for side in ('left','right'))
            deterministic_root = all(len(model.initial)==1 for model in models[1])
            for power,cost in ((1,'absolute'),(2,'squared')):
                common = {f'k{k}_{cost}':exact_dp(*models[k],cost=cost) for k in (1,2)}
                common[f'full_{cost}'] = exact_dp(*models[len(case['left'][0])],cost=cost)
                native, elapsed = native_run(executable,args.compiler,case,power,True)
                if deterministic_root and abs(native-common[f'k1_{cost}'])>TOLERANCE:
                    raise AssertionError(f"{case['name']}: k1 mismatch")
                common[f'stock_{cost}'] = native
                native_full = None
                if case['name'] in ('second_order_matters','full_history_is_not_k2'):
                    native_full, _ = native_run(executable,args.compiler,case,power,False)
                    if abs(native_full-common[f'full_{cost}'])>TOLERANCE:
                        raise AssertionError('full-history diagnostic mismatch')
                for key, expected in case['expected'].items():
                    if key.endswith('_'+cost) and abs(common[key]-expected)>TOLERANCE:
                        raise AssertionError(f"{case['name']}: preregistered {key} failed")
                report['cases'].append({'name':case['name'],'cost':cost,'reference':common,
                    'native_markov_value':native,'native_full_history_value':native_full,
                    'native_quantization_and_k1_kernels_equal':True,
                    'k1_comparator_target_eligible':deterministic_root,
                    'ineligible_reason':None if deterministic_root else 'stock selects one initial state',
                    'absolute_k1_difference':abs(native-common[f'k1_{cost}']),
                    'native_process_seconds_diagnostic_only':elapsed,
                    'model_hashes_k1':[model.model_hash for model in models[1]]})
        if any(sha256(SOURCE/name)!=digest for name,digest in source_hashes.items()):
            raise AssertionError('source snapshot changed during probe')
        report['status'] = 'PASS'
        report['qualified_full_domain_comparator'] = False
    except Exception as error:
        report.update(status='FAIL',reason=f'{type(error).__name__}: {error}')
    write_json(RUNS/'pnot_result.json',report)
    print(json.dumps({'status':report['status'],'scope':report['scope'],
                      'native_calls_recorded':len(report['cases']),
                      'certificate_frontier_eligible':False,'result':str(RUNS/'pnot_result.json')}))
    return 0 if report['status']=='PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
