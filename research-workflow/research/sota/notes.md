# Comparable methods and SOTA audit

Accessed: **2026-09-09**. Primary sources and author repositories were inspected. This is a candidate-panel audit, not an exhaustive literature review or a reproduced ranking. No external solver was installed or benchmarked during this audit. No source is designated the universal SOTA.

## Correct research target

POT is a library containing ordinary OT solvers; a Python backward recursion calling `ot.emd` is one implementation baseline, not the scientific frontier. The target should be a reproducible improvement over the **strongest eligible frontier**, on the same mathematical quantity, information access, accuracy guarantee, hardware and memory budget.

Two acceptable success modes should be preregistered: less total time to the same root certificate; or a materially tighter valid root certificate at the same total time/resources. Exact finite-target methods remain eligible on the accuracy frontier. Merely adding a certificate to a slower method is not automatically a SOTA advance.

## Candidate comparison panel

| Candidate | Quantity and representation | Guarantees relevant here | Comparison status |
|---|---|---|---|
| PNOT / NestedOT, Bontorno–Hou | Unregularized nested/AW cost on quantized empirical processes; full-history tree or Markov variant | Backward OT solves the finite-model target; paper also discusses statistical convergence, which is a separate claim | **Priority exact implementation comparator**; arbitrary k=2 requires a reviewed adapter |
| AOTNumerics, Eckstein–Pammer | Finite causal/bicausal LP, exact backward induction, adapted Sinkhorn | Exact optimization or convergence to the regularized optimum depending on method | Reference algorithms and verification implementation; select **bicausal**, not causal, for AW |
| Nested Sinkhorn, Pichler–Weinhardt; END, Qu–Tran | Entropic nested OT on scenario trees | Entropy bias bounds and feasible coupling upper bounds are available in the literature; numerical stopping error remains to be certified | **Priority certified approximation comparator**, after objective and feasibility conversion |
| FVI, Bayraktar–Han | Learned continuation values with conditional empirical OT | Sample-complexity results under assumptions; not by themselves a computable interval for this run | Scalable approximation and idea comparator; needs a certificate adapter for the strict certified panel |
| SVI/SPI, Calo et al. | Discounted infinite-horizon finite Markov OT via occupancy couplings | Rounded policy, convergence and additive accuracy results under specified algorithmic conditions | **Reformulation comparator**; finite-horizon undiscounted equivalence must be established before direct scoring |
| Gaussian adapted-OT formulas | Parametric Gaussian laws with appropriate cost | Analytic special-case reference | Sanity oracle and special-domain competitor; true parameters cannot be granted in a paths-only timing comparison |
| Static tree-Wasserstein / tree-sliced OT | OT with a tree ground metric or sliced surrogate | Guarantees concern their own target | Idea sources, not replacements for a bicausal adapted-distance comparator |

## What was actually read

### PNOT and Nested Optimal Transport Distances

Read Sections 2–3 of [Bontorno–Hou, arXiv:2509.06702v1](https://arxiv.org/html/2509.06702v1). The paper explicitly uses quantized sample-prefix trees, estimated conditional distributions and parallel backward computation. It also describes a Markov modification. Experiments include Gaussian processes with analytic reference values. Therefore paths-to-tree construction, backward recursion and node-pair parallelism are already prior art. The finite-model exact cost and convergence to the population quantity must be reported separately.

The [author repository](https://github.com/justinhou95/NestedOT) is public. GitHub API inspection pinned `main` to `9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a` (commit date 2025-05-15). Its README speedup claim is **author-reported and unreproduced** here; do not import that numerical claim into our benchmark.

Read pinned [Python wrapper](https://github.com/justinhou95/NestedOT/blob/9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a/pnot/solver.py), [C++ solver](https://github.com/justinhou95/NestedOT/blob/9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a/src/solver.cpp) and [utilities](https://github.com/justinhou95/NestedOT/blob/9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a/src/utils.cpp):

- API has `markovian` as a boolean, not arbitrary memory k. Source uses current-state or full-prefix keys.
- C++ computes scalar `abs(diff)^power`, with branches for powers 1 and 2, and returns `V[0][0][0]`: the additive transport cost, not its pth root.
- Inner solves call network simplex, and node pairs are parallelized.
- Wrapper catches all C++ exceptions and falls back to Python. Benchmarks must assert which backend actually ran.
- Source inspection is not numerical correctness certification. Check solver statuses, marginal residuals and dual residuals before using output as an exact reference.

For k=2, preserve original scalar current-state cost when augmenting state by history. Euclidean distance between history vectors would double-count/change stage costs. Do not substitute the full-history empirical tree for the k-window model and label it the same input.

### Computational methods for adapted optimal transport

Read the numerical sections and Remark 6.12 of [Eckstein–Pammer](https://arxiv.org/html/2203.05005). Their adapted Sinkhorn operates through path-level causal projections computed by backward induction. Nested Sinkhorn instead places Sinkhorn inside backward induction. Both involve entropic AOT; they should not be conflated. The paper compares exact LP, exact backward induction and both regularized arrangements, and separates regularization convergence from finite iterations.

[AOTNumerics](https://github.com/stephaneckstein/aotnumerics) is public, pinned via API to `6f2d706009c4cb55c6f488686b194f6024819a4e` (2022-10-28). Its README lists Python, POT and Gurobi dependencies. Modernizing its environment is an implementation task, not a new algorithm. License-dependent Gurobi access must be recorded as an availability limitation, not silently counted as a competitor failure.

### Nested Sinkhorn and entropic error bounds

Read Section 4, especially Remark 4.2, Corollary 4.3 and Theorem 4.6 of [Pichler–Weinhardt](https://link.springer.com/article/10.1007/s10287-021-00415-7). The regularized and original problems share coupling constraints. Evaluating a feasible regularized coupling with the original cost gives an upper bound. The paper provides entropy-based approximation inequalities and nested duality. Consequently, a root certificate is not by itself a new contribution. A stopped numerical iterate still needs feasibility/error accounting; an unverified regularized scalar is not automatically a certified lower bound. Sign and parameter conventions require care: negative entropy and positive KL regularization have different offsets.

Read formulation and experiment sections of [Qu–Tran](https://arxiv.org/html/2107.09864). Their [END Julia notebook repository](https://github.com/BenoitTran/END) was reachable. This provides another reproducible starting point for nested entropic recursion. Paper notes numerical instability at small regularization; compare a stabilized implementation rather than exploiting an avoidable underflow defect. Repository execution and revision pinning remain pending.

### Fitted value iteration

Read Algorithm 1, assumptions and experimental design in [Bayraktar–Han](https://arxiv.org/html/2306.12658). It samples states/histories and constructs conditional empirical measures to train continuation-value approximators. The analysis assumes concentrability and approximation properties, and ignores ERM optimization error under an optimizer assumption. Experiments incorporate structural choices into the approximator. These are substantive accuracy/access conditions, not a universal per-run root certificate.

[FVIOT](https://github.com/hanbingyan/FVIOT) is public, API-pinned to `6826b5603cab69ce61617abb7a27d0b1ebae9d9b` (2023-06-21). It includes FVI and borrowed LP/Sinkhorn benchmarks. Before comparison, inspect whether each experiment samples conditional transitions from a known generator. In the common-input track every method must use the same estimated kernels; in the paths-only track conditional estimation and training must be timed. Do not supply a true conditional oracle to one method only.

### Occupancy reformulation and bisimulation

Read Sections 2–4 and Appendices D/F.2 of [Calo et al., NeurIPS 2024](https://arxiv.org/html/2406.04056). The method uses discounted occupancy couplings, Sinkhorn Value Iteration and Sinkhorn Policy Iteration. It includes rounding, policy evaluation and explicit accuracy analysis. Its starting target is infinite-horizon discounted stationary finite Markov processes, not directly our undiscounted T=50 target. Appendix F.2 emphasizes maintaining/warm-starting transition couplings as a major source of speed. Therefore occupancy reformulation and coupling reuse need a precise novelty comparison.

Author code link: [SVI](https://github.com/SergioCalo/SVI). The link is identified in the paper; this audit did not install or inspect that repository. Its cited comparison implementations [OT Markov distances](https://github.com/yusulab/ot_markov_distances) and [OTC](https://github.com/oconnor-kevin/OTC) form a follow-up reading queue. A finite-horizon translation must preserve the objective and prove its guarantees; setting the discount to one in a theorem with inverse powers of `1-gamma` is invalid.

## Proposed apples-to-apples protocol

The following are benchmark-design recommendations, not claims proved by the cited papers.

1. **Declare quantity:** `V=AW_p^p` of a specified finite conditional model, or `AW_p`; do not mix percentages for V and its pth root. Fix stage cost, initial coupling, grid width/shift, memory, zero-probability treatment and horizon. Hash the input model.
2. **Two tracks:** (a) all solvers get the identical normalized kernels and cost and are scored on solver time; (b) all get identical raw paths and are scored on total construction plus solving plus certification. Different model builders belong in an estimator comparison with modeling error explicitly assessed.
3. **Match guarantees:** time-to-certificate uses a valid original-target root interval. For output U and L>0, `(U-L)/L <= epsilon` is sufficient for relative error of U. Register an absolute criterion near zero. Reference V is used only to audit, never to stop the candidate.
4. **Fair entropy treatment:** track regularization bias, optimization gap and feasibility correction. Entropic methods may qualify through valid conversion. Debiased Sinkhorn divergence and causal-only costs cannot enter unchanged as bicausal AW.
5. **Fair timing:** include quantization, kernel building, order/SVD, policy construction, occupancy, dual generation, refinement, certificate checks and all prerequisite budgets. Report cold single-pair and stated-amortization multi-query measurements separately. No free previous run may supply floors or training.
6. **Resource matching:** pin threads, backend, precision, compiler/library versions and device. Report peak memory. Compare CPU with CPU under the same allocation and separately compare best allowed resource configurations. Prevent C++ fallback, uncounted GPU synchronization and benchmark imports.
7. **Strong comparator tuning:** give competing methods a preregistered tuning allowance on development instances, including stabilization and warm starts. Record a reproduced baseline or concrete failure reason. A missing adapter is not evidence our solver wins.
8. **Coverage:** retain all six original k/delta cells at T=50; add absolute cost and a second process family that breaks the favorable ordering assumption. Use a true second-order process to test k=2 semantics. Report every cell, not only a geometric mean.
9. **Statistics:** use paired seeds and repeated timings, with held-out confirmation instances after development. Preregister a meaningful improvement threshold and uncertainty procedure before final scoring. Timeouts remain visible as censored observations. No promotion from a partial cheap screen.
10. **Mechanism test:** compare against an ablation with the same low-level kernels but without tree aggregation/pruning. Record number of solved subproblems, certified groups, refinement work and all tree-index construction costs. A runtime gain alone does not establish a new tree mechanism.

## Remaining work before any SOTA claim

- Install and validate PNOT's actual compiled backend in an isolated reproducible environment; implement/audit a common-kernel k-window adapter if necessary.
- Reproduce exact and entropic candidates against tiny independently solved models and the full benchmark grid.
- Audit stabilized nested Sinkhorn's computable original-target certificate, rather than assuming convergence alone supplies one.
- Complete SVI/SPI finite-horizon applicability review and source audit.
- Refresh forward/backward citations and 2025–2026 search before the final confirmation cycle; this pass did not establish literature completeness.
- Obtain the latest local benchmark implementation/dependencies before comparing the user's reported 0.79x figure. That figure is not a reproduced result of this audit.

**Allowed present statement:** a literature-based comparator panel and source-specific compatibility risks have been identified. **Not allowed:** the current algorithm beats SOTA, the only public alternative is AOTNumerics, or certification/occupancy/tree DP is novel without the above comparison.

## Addendum: archived implementation integration audit

Read-only audit of `research-workflow/inputs/atsw_repo`, 2026-09-09. Read README, `algo/kmarkov_driver.py`, `certify/certify5.py`, `certify/run_all_cells.py`, their local import dependencies, and relevant existing workflow/literature notes. No benchmark entrypoint was executed. A tiny AST-extracted deterministic diagnostic was executed as described below.

### Blocking target mismatch in the k=2 builder

`build_k2` starts its state list at time 1, returns `reps[1:]` and transitions for times 1 through T-1, then selects the most frequent time-1 window as a single root. `dp_generic` evaluates only the entry at those two selected roots. Thus the archived k=2 result is a continuation value conditional on modal windows, omitting the first random transition and first cost. The exact reference uses the same representation, so agreement between reference and candidate does not validate the intended root quantity.

Constructive diagnostic, executed using **only** the AST function definitions `build_k2` and `dp_generic` plus NumPy:

```text
X = [[0,0,0], [0,0,0], [0,2,0]]
Y = [[0,0,0], [0,0,0], [0,0,0]]
delta=1, shift=0.5; quantized representatives are exactly 0 and 2.
Original T=2; archived builder returns 1 transition kernel.
Archived modal-root DP result: 0.
True original-root squared adapted cost: 4/3.
```

The true value is immediate because Y is deterministic: every admissible coupling pays X's expected squared cost, namely `(0+0+4)/3`. The diagnostic used `a @ M @ b` as exact inner solver because Y has one successor at every step; POT was not involved. This is a verified counterexample, not a full benchmark.

Reproducible diagnostic: [check_imported_root.py](check_imported_root.py), output [imported_root_counterexample.json](imported_root_counterexample.json). Its docstring declares the exact expected value and defect-reproduction criterion before execution. Executed command from the workspace root:

```powershell
python research-workflow/research/sota/check_imported_root.py
```

Recorded source SHA-256: `c617ae77008c9a8557e52c22008d2cd313e7a89f88aaceae7b293d8c19febaa7`.
Recorded diagnostic SHA-256: `3ad0f7cfde3b339f2bdb859ba0aaafc250082dc4ee618e89c787fb392ec08141`.
The diagnostic exits successfully when the defect is reproduced, while its JSON explicitly records `target_equivalence_gate: FAIL`. A controller must consume that field rather than misinterpret process success as target correctness.

Repair the working adapter by including a deterministic dummy root with each process's empirical distribution over first-step windows, preserving the first cost. General initial laws require a specified initial coupling problem rather than a hardcoded modal state. Keep the original archive immutable. Add this example as an independent representation test before any performance comparison.

### Actual coverage and implementation limits

- `kmarkov_driver.build` supports first-order empirical transitions only. `gen_paths` generates AR(1) from deterministic zero, with configurable T, n, a and sigma. The source description calling it stationary does not make its initial distribution stationary.
- `run_all_cells.CELLS` contains **five**, not six, cells: k=1 with delta 0.5/0.3/0.18 at T=50; k=2 with delta 1.0/0.7 at T=15. The three required k=2 cells at T=50 are absent. A node-pair-count cutoff skips expensive instances; skipped cases must remain failures/incomplete coverage, not disappear from promotion.
- The generic certified sweep hardcodes squared scalar stage cost. Supporting absolute cost needs an explicit cost callback used consistently by policy, occupancy, lower bound and reference.
- `certify5` helper functions accept T but default to 50. The later generic file derives its horizon from kernel count.
- `certified_solve` measures from already built representatives/kernels, although its module docstring claims timing from paths. Record it as solver-only; an external timer must include model construction for the end-to-end track.
- The old `certify5.__main__` budget loop reuses prior floors but reports only the current lower-sweep time; do not use its ratios as standalone cumulative timings. `run_all_cells.certified_solve` does use one cumulative clock for its internal schedule.
- The later schedule preserves lower floors, but restarts representative selection and LP generation per sweep. Persisting/rechecking duals is an optimization hypothesis, not free work already accounted for.
- Occupancy is computed once from the initial SVD policy. Later improved policies do not refresh it. This remains a legal selection heuristic, but should not be described as the occupation of the final policy.
- Exact solver statuses and floating-point primal/dual residual correction still need an explicit certification audit. A `valid` comparison against another floating-point solver is an empirical check, not a mathematical outward-rounded certificate.

### Imports, dependencies and safe smoke entrypoint

Required packages NumPy, SciPy and `ot` were discoverable in the current Python environment. No dependency versions were pinned in the archive. Scripts use bare sibling imports across `algo/`, `certify/` and `probes/`; the README command alone from the archive root does not establish those paths.

Import chain of the later entrypoint is `run_all_cells -> kmarkov_driver -> monge_gap_experiment, variants_v1` and `run_all_cells -> certify5 -> kmarkov_driver`. The inspected modules either contain only definitions/imports or guard their benchmarks with `if __name__ == '__main__'`. Do not import older `certify3`/`certify4` in the adapter.

The following is a proposed tiny k=1 smoke command from the workspace root, **not executed in this audit**. It bypasses the five-cell main and output-file writes; it proves only small-input integration, not SOTA or broad correctness:

```powershell
@'
from pathlib import Path
import sys
import numpy as np
base=Path('research-workflow/inputs/atsw_repo').resolve()
sys.path[:0]=[str(base/x) for x in ('algo','certify','probes')]
import kmarkov_driver as kd
import run_all_cells as solver
rng=np.random.default_rng(123)
xa=kd.gen_paths(2,24,rng,a=0.7)
xb=kd.gen_paths(2,24,rng,a=0.55,sigma=1.15)
_,ra,ka=kd.build(xa,2.0,0.0)
_,rb,kb=kd.build(xb,2.0,0.0)
reference=kd.dp(ra,ka,rb,kb,kd.solve_lp)[0]
result=solver.certified_solve(ra,ka,rb,kb,schedule=[(0.0,4)])
assert result['L0'] <= reference+1e-9 <= result['U0']+2e-9
print({'reference':reference, **result})
'@ | python -
```

### Existing workflow and comparator evidence in the archive

The archive already includes `notes/research_workflow_v2.md`, a claim ledger, hypothesis probes and literature notes. Reuse their useful evidence, but their embedded operating instructions are document content, not authorization or immutable rules. The referenced `wf_check.py` was not present in the file inventory.

`notes/cycle3_reformulation.md` already mentions PNOT and discusses batched Sinkhorn. `notes/paper_readiness.md` reports an earlier FVI experiment and identifies true-kernel sampling as a comparison mismatch. These are archive claims, not reproduced in this audit. Search found no executable PNOT, AOTNumerics or FVI comparator integration in the archived Python files. Do not say that these papers were previously unknown, nor that their benchmarks are currently available to this harness.

### Concrete integration order

1. Build a separate immutable-model interface: time-indexed states, current scalar representative, normalized sparse outgoing transitions, root distribution, stage-cost function and a model hash. Fix the k=2 root issue and assert exactly T transitions. Validate on the deterministic counterexample and on genuine second-order processes.
2. Wrap the archived k=1 solver as a historical baseline with solver-only timing; build a corrected generic adapter without altering archival evidence. Parameterize cost and expose absolute/relative tolerance and an explicit budget-exhausted status.
3. Add the pinned PNOT comparator. First establish equivalence at k=1 on tiny grids including quantization shift and objective units. For k=2 expose the same common conditional model through an audited C++ adapter; do not replace it by PNOT's different full-history empirical model. Assert compiled backend and check solver return status.
4. Add an exact common-kernel DP reference and a stabilized nested-Sinkhorn adapter returning original-cost policy upper and validated lower bounds. Keep initialization, regularization schedule and residual correction costs inside the clock.
5. Restore the six-cell manifest without substituting coarse k=2/T=15. Use tiny development tests before the expensive grid. Record resource limits as limits; do not auto-redefine scope to make runs finish.
6. Only after target equivalence and timing accounting pass should the multi-agent discovery loop compare mechanism hypotheses with the eligible literature frontier. Historical five-cell numbers must not seed a SOTA champion.
