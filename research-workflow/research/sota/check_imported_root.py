"""Reproduce the imported k=2 root-target defect without running its benchmarks.

Criteria declared before execution:
* With X=[[0,0,0],[0,0,0],[0,2,0]], Y=0, delta=1 and shift=.5,
  the intended original-root squared adapted cost is exactly 4/3: Y is
  deterministic, so no coupling decision can change E[sum_t X_t**2].
* The archived builder must reproduce its reported defect: one transition
  rather than two and a modal-root continuation value of zero.

Only build_k2 and dp_generic FunctionDef AST nodes are compiled. No archive
imports or main code execute. The local OT oracle is a@M@b and is exact
here because every Y marginal is a singleton. A successful reproduction
does NOT pass the original target-equivalence gate: this script records
that gate as failed. If the input source changes, review the recorded hash.
"""

import ast
import hashlib
import json
from pathlib import Path

import numpy as np


def run():
    script = Path(__file__).resolve()
    workflow = script.parents[2]
    source = workflow / 'inputs' / 'atsw_repo' / 'certify' / 'run_all_cells.py'
    source_bytes = source.read_bytes()
    module = ast.parse(source_bytes.decode('utf-8-sig'))
    wanted = {'build_k2', 'dp_generic'}
    definitions = [node for node in module.body
                   if isinstance(node, ast.FunctionDef) and node.name in wanted]
    assert {node.name for node in definitions} == wanted
    namespace = {'np': np}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(source), 'exec'),
         namespace)

    x = np.array([[0., 0., 0.], [0., 0., 0.], [0., 2., 0.]])
    y = np.zeros_like(x)
    reps_a, kernels_a, root_a = namespace['build_k2'](x, 1., .5)
    reps_b, kernels_b, root_b = namespace['build_k2'](y, 1., .5)
    assert all(kernel.shape[1] == 1 for kernel in kernels_b)
    observed, pairs = namespace['dp_generic'](
        reps_a, kernels_a, reps_b, kernels_b,
        lambda a, b, matrix: float(a @ matrix @ b), root_a, root_b)
    expected = 4 / 3
    direct = float(np.mean(np.sum((x - y) ** 2, axis=1)))
    assert direct == expected
    assert len(kernels_a) == len(kernels_b) == 1
    assert observed == 0.0
    record = {
        'diagnostic': 'imported_k2_modal_root_omits_first_random_step',
        'status': 'defect_reproduced',
        'target_equivalence_gate': 'FAIL',
        'intended_horizon': 2,
        'returned_transition_count': len(kernels_a),
        'analytic_original_root_cost_exact': '4/3',
        'analytic_original_root_cost_float': expected,
        'archived_modal_root_cost': observed,
        'absolute_target_error': expected - observed,
        'evaluated_node_pairs': pairs,
        'archive_source_relative': str(source.relative_to(workflow)),
        'archive_source_sha256': hashlib.sha256(source_bytes).hexdigest(),
        'diagnostic_sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
        'executed_archive_definitions': sorted(wanted),
        'archive_module_imported': False,
        'benchmark_main_executed': False,
        'pot_used': False,
        'interpretation': 'A candidate and reference sharing this builder can '
                          'agree while both compute the wrong root target.'
    }
    output = script.with_name('imported_root_counterexample.json')
    output.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    run()
