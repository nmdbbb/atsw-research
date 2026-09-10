# Independent sparse-policy verification and bounded timing screen

Date: 2026-09-10. **Decision: retain and integrate as a development numerical
baseline for the existing policy. No new mechanism or certificate is established.**
The independent screen completed in 19.2662 seconds within its frozen cooperative
60-second budget. No grid or OT reference solve was run. Existing policy sources,
historical manifests/results, status and ledger were not changed by this lane.

## Evidence and reproducibility

New artifacts:

- `probes/sparse_policy_equivalence_screen.py`
- `runs/cycle_2/sparse_policy_screen/manifest.json`
- `runs/cycle_2/sparse_policy_screen/results.json`

Manifest SHA-256:
`07d739f2394a59cce9db22c4fe22f9905e6b06c6a29c0b88887723494e80fc07`.
Results SHA-256:
`72dc74706a8945e2ee9a3f73c22b246a7d1e18c29458ba87681e42322da5eeb2`.
The manifest was written before execution; every frozen source hash and the
results-to-manifest link were recomputed successfully after execution.

The two cases are exactly the previous upper-policy diagnostic's AR1, k=1,
delta=.5, squared and second-order nonmonotone, k=2, delta=.18, absolute cases:
T=5, 128 paths per side, seed 1000, shift zero. They are deliberately selected
development cases, not held-out or full-domain evidence. Path/model construction
is reported separately. Historical times were not used as the comparator.

## Independently checked object

The unchanged dense `evaluate_policy` was executed once per case, yielding every
continuation table and root. Two complete autonomous sparse backward recursions
then recomputed their own continuation matrices and original global SVD orders.
Every table entry and each root was compared with that dense execution. This
checks whether floating perturbations change later SVD orders enough to cause
policy drift; a local coupling comparison alone would not establish this.

A separate pass uses the dense continuation tables to prescribe exactly the same
full matrix at each layer. It applies the original `_orders` to this complete
matrix before restricting supports, and checks every resulting value table and
root. Global indices are retained. Twenty-six plans per case, including root,
are checked against unchanged dense `_ordered_policy` on the same matrix/orders;
plans must agree with one of the original two orientations within 2e-12 and their
objectives within 1e-10. Selected-orientation differences are explicitly saved.

| Check | AR1 coarse | Second order fine |
|---|---:|---:|
| Conditional parent pairs | 747 | 35,006 |
| Dense root upper | 3.8778588498921485 | 4.080633482728209 |
| Autonomous maximum table error | 1.4211e-14 | 2.6645e-15 |
| Autonomous root error | 4.4409e-16 | 0 |
| Same prescribed matrix maximum table error | 2.1317e-14 | 2.6645e-15 |
| Maximum sampled plan error | 2.7756e-16 | 1.1103e-16 |
| Maximum sampled marginal residual | 1.8042e-16 | 1.6654e-16 |
| Sampled plans bytewise equal | 8/26 | 21/26 |

All numerical gates passed. No sampled selected orientation differed materially.
Many plans and some values are not bytewise equal; the correct description is
**same mathematical policy with measured numerical equivalence**, not exact
implementation identity. There is no universal stability theorem for SVD orders
near degenerate singular values. Passing these cases does not authorize assuming
identity for all future inputs.

Twenty-two independent small fixtures checked unnormalized non-Dirac laws, zero
cost ties, zero-rich random marginals and tiny positive flow. The maximum marginal
residual was 1.6654e-16. A flow between zero and 1e-12 was retained explicitly;
there is no threshold pruning of positive support. Both timing cases have Dirac
initial laws, so the separate non-Dirac fixture is needed. The implementation
agent's separate recursion tests additionally cover non-Dirac roots for k=1/2
and both costs; this verifier inspected those tests without duplicating them.

## Numerical limits found by code review

The sparse kernel normalizes by scaling and `math.fsum`, then streams residual
mass. The old kernel normalizes with NumPy sums and intersects cumulative
intervals. These are the same construction in exact arithmetic but have different
roundoff and summation order. Exact ties use the first orientation, while nearly
tied objectives can choose different orientations numerically. Sample plan tests
explicitly allow either original orientation only when the objective also passes.

Finite nonnegative costs and marginals are required. Scaling helps avoid overflow
of the normalization sum; a positive mass that underflows during normalization is
rejected, not silently removed. This is not proof of support preservation across
all floating dynamic ranges. Streaming can finish one side with a tiny remainder
on the other: the kernel reports it and allows at most 2e-12. The largest observed
remainder across complete sparse construction was 2.7756e-16. Thus floating plans
are numerically feasible, not exact rational or outward-rounded witnesses. This
screen does not produce or validate a root lower certificate.

## Cost accounting and measured result

Dense time is the unchanged dense backward/root construction, including its
stage matrices and SVDs. Sparse times include the corresponding stage matrices,
all original SVDs, complete-matrix validation, full marginal support scans,
support sorting, both NW orientations and sparse objective evaluation, plus
counter accumulation. They do not exclude preparation to make the candidate look
cheaper. Independent sample-plan and prescribed-matrix verification are outside
the construction timer. Startup/imports, model generation, occupation, policy
improvement, lower construction and root certification are outside both timers.

| Case | Fresh dense, one run | Sparse run 1 | Sparse run 2 | Dense/sparse observed ratios |
|---|---:|---:|---:|---:|
| AR1 coarse | .057648 s | .019429 s | .019956 s | 2.89–2.97 |
| Second order fine | 13.602815 s | 1.906250 s | 1.780545 s | 7.14–7.64 |

There is one dense timing and two sparse timings, in fixed order. Cache, warmup
and machine effects are not statistically controlled. These numbers establish a
useful development signal about this initializer, not confidence intervals,
full end-to-end acceleration, a competitor comparison or a SOTA result.

The sparse construction still visits every parent pair and computes six global
SVDs per case. It validates 972/47,858 matrix entries and scans 1,613/75,934
marginal entries in preparation. It reads 13,110/100,446 cost entries across both
orientations and all parent/root evaluations, and allocates zero dense coupling
entries in that loop. Counts include root. Maximum-residual counters are
aggregated with maximum, not sum. These are implementation counters, not a
complete hardware work or allocation model.

## Decision relevance and stopping point

This removes an observed implementation expense from the ordinary feasible-policy
baseline while preserving its tested mathematical target. It does not reduce the
number of parent pairs, add sharing across Bellman problems or improve the
policy's mathematical upper bound. The existing upper and lower quality barriers
therefore remain. Integration should be explicitly a development baseline
selection; original frozen sources and historical results must remain intact.

No additional timing repetitions, microoptimization or grid are justified by this
screen. The next scientific step must change a root-bound-quality decision; a
faster initializer alone does not warrant promoting an interval cache or claiming
that the required certified relative root gap has been reached.
