# H_D02 opportunity gate: defer the current dense-face implementation

Date: 2026-09-09. This is an exploratory diagnostic after the existing fixture
results, not hypothesis registration or confirmation. The decision is to stop
investment in the current dense-face implementation, dynamic-comparator adapter
and large grid. The mathematical mechanism remains valid; this screen does not
reject all optimal-face reuse or establish a lower bound.

## Evidence and provenance

The manifest was written before this measurement and locks the probe,
generators, common model, clamped recurrence, frozen design and H_D01 prior-art
review by SHA-256. Candidate `monotone_reuse.py` was never imported.

- Manifest: `runs/cycle_2/hd02_opportunity/manifest.json`.
- Results: `runs/cycle_2/hd02_opportunity/results.json`.
- Complete local update trace, including old/new costs, marginals, incumbent
  plans and reduced costs: `runs/cycle_2/hd02_opportunity/trace.jsonl`.
- Probe: `probes/hd02_opportunity_screen.py`.

All eight cells completed in 8.86 seconds, within the declared 60-second wall
budget. The cells use both frozen process families and the established paired
parameters, both costs, k=1/2, development seed 1000, T=3, 16 paths per side,
delta=0.5 and shift=0. They are deliberately tiny, outside full-domain coverage.

The workload uses the actual clamped Bellman recurrence, with zero values at
inactive nodes and the dummy root always active. At phase 1/2/3/4, node (t,i,j)
is active when `(17*i + 31*j + 13*t) % 4 < phase`. This produces cumulative
approximately 25/50/75/100% activation. Each instrumented phase was checked
against `solve_clamped_subsolution`: 32/32 root and full-table replays agree to
1e-8. This is a declared diagnostic schedule, **not an implemented H_C02 search
policy** and not synthetic perturbations passed off as controller updates.

## Results

| Family | k | Cost | Revisits | Changed | Support hits | Numerical face rescues |
|---|---:|---|---:|---:|---:|---:|
| AR1 | 1 | squared | 163 | 64 | 61 | 0 |
| AR1 | 1 | absolute | 163 | 64 | 63 | 0 |
| AR1 | 2 | squared | 364 | 56 | 54 | 0 |
| AR1 | 2 | absolute | 364 | 56 | 55 | 0 |
| second order | 1 | squared | 105 | 43 | 41 | 0 |
| second order | 1 | absolute | 105 | 43 | 40 | 0 |
| second order | 2 | squared | 269 | 40 | 33 | 0 |
| second order | 2 | absolute | 269 | 40 | 36 | 2 |
| Total | | | 1802 | 406 | 383 | 2 |

Of the revisits, 1396 had no local cost change and 23 changed events missed the
cached support. Face search concerns the remaining 383 support hits. Fresh
weighted OT increased numerically in 381; its smallest increase was 0.025,
at least 6.67 million times the declared comparison tolerance in every such
case. Two hits admitted independently replayed old-face flows that avoid
strictly positive updates. Both are 2x2 blocks in second-order/k2/absolute,
at phase 2, nodes (1,4,1) and (1,4,5). Each allowed graph contains 3 of 4 edges.
Their marginal and old-objective residuals were zero in float arithmetic.

This is 2/383 = **0.52% of hits**, 2/406 = 0.49% of changed events and 2/1802 =
0.11% of all revisits. Only 336/1802 revisits and 159/383 hits had at least two
positive masses on both sides; the rescue rate within nontrivial hits is
2/159 = **1.26%**. Many tiny empirical transitions are deterministic, so the
pooled percentage alone would overstate how informative this screen is.

A positive update covers a whole positive-mass row or column in 232/383 hits,
making avoidance impossible on the represented float update graph regardless
of the old face. Mean numerical old-face density is 83.9% across hits and
61.3% across nontrivial hits. Large tight graphs do not imply alternative
flows avoiding these particular updates.

## Timing proxy, not a speed result

The diagnostic spent 7.043 seconds in all 2984 cold weighted-OT calls, including
2.812 seconds for 1182 initial node solves. Revisited support-hit calls took
0.892 seconds; the two rescued calls took 0.005812 seconds. Thus even assigning
zero cost to detecting and repairing these opportunities corresponds to only
**0.65% of the observed hit-call time**, or 0.083% of all cold weighted-OT time.
Among nontrivial hit calls the fraction is 1.47% of 0.396 seconds.

These fractions are optimistic **numerical timing proxies conditional on this
trace and kernel**, not rigorous bounds on another solver, another schedule or
all possible reuse mechanisms. In particular this probe sends deterministic
blocks through LP too, whereas a proper OT kernel can evaluate them directly.
The two zero-objective face LP audits already took 0.004905 seconds, before
charging graph construction, witness validation, indexing or unsuccessful
searches on the other hits. No actual candidate savings were measured.

Controller materialization plus trace construction took 0.388 seconds;
independent clamped-recurrence audits took 1.414 seconds. These are diagnostic
costs, not an optimized controller measurement. Generator/model setup and all
other overhead are included in the reported 8.86-second screen wall time.

## What remains unresolved

1. **Exactness.** HiGHS uses primal/dual tolerances of 1e-10 and explicit marginal
   replay at 1e-10. Objective comparisons use scaled 1e-9; face edges use tightness
   1e-10 but updates must equal zero literally. Even apparent unchanged values
   and zero floating residuals are not exact arithmetic or outward certificates.
   Both rescues remain `numerical_face_rescue_unresolved_exact`; there were no
   additional tiny-increment/nonmonotone ambiguity flags. No production
   acceptance decision follows from this oracle.
2. **Schedule.** Batched activation can hit more of an optimal face at once than
   single-node, locality-driven search. T=3 and 16 paths cannot establish the
   workload of a useful controller at T=50 or at finer grids.
3. **Witness policy.** The instrumented reference replaces its cached plan with
   fresh HiGHS output on every scheduled backup, including unchanged costs and
   support misses. H_D01 could retain the incumbent in those cases. Tie handling
   changes subsequent hit opportunities. These data are conditional on the
   frozen fresh-solve witness policy and are not a replay of an implemented
   retained-plan H_D01 controller.
4. **Comparators and novelty.** No dynamic OT adapter was built or benchmarked.
   Standard sensitivity, flow reoptimization and selected-action reverse
   dependencies remain the relevant prior art, as explained in
   `ledger/inbox/B/H_D01_prior_art_review.md`. Lack of an adapter is not a win.
5. **Original prediction.** The draft's 25% threshold applies to declared
   degenerate fixtures. Applying it retrospectively as a formal falsification
   threshold on these natural cells would be invalid. The two natural rescues
   show possibility; they do not pass the draft prediction or establish value.

## Investment decision and reopening gate

Do not spend the next step implementing a dynamic-flow comparator or scaling
this dense-face candidate. The best-case numerical opportunity is small under
the measured schedule, and even the successful feasibility audits cost almost
as much as their avoided cold solves. This is sufficient to defer that
investment, while insufficient to declare the general mechanism impossible.

Reopening requires a concrete controller-specific reason to expect substantially
more useful opportunity: a specified locality-aware activation schedule, fixed
retained-plan tie handling, and a cheap way to identify affected nontrivial
blocks. The smallest missing empirical piece is a trace from that actual
controller with event denominators and changed-block costs. Evaluate optimistic
opportunity on that trace before implementing additional flow machinery. Any
eventual candidate comparison must charge graph construction, feasible-flow
repair, arithmetic certification, cache/index maintenance and fallbacks on
failures, with the same trace and local reoptimization baseline.

No additional run, registration, shared ledger/status edit, SOTA claim or
full-domain conclusion was made in this task.
