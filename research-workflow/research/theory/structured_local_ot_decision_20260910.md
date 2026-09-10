# Structured local transport: baselines improve, broad research gates fail

Date: 2026-09-10. Decision: retain direct binary and strict support-Monge dispatch
as numerical engineering baselines; do not promote their screened reuse/coverage
claims into a new research mechanism. Stop this bounded cycle and publish its checkpoint.
The original root-certificate/SOTA objective remains open.

## Exact local route instead of fixed-upper priority tuning

With two supported rows, set d_j=C_0j-C_1j and allocate row-zero mass greedily in
ascending d_j, each column capacity b_j. This solves fractional knapsack. At its
threshold lambda, u=(lambda,0), v_j=min(C_0j-lambda,C_1j) is a dual witness in
exact arithmetic. The transposed rule handles two supported columns.

The implementation keeps singleton expectations and the same general LP fallback.
Caching uses identical ordered support pairs and a copied immutable continuation
matrix; changing matrix requires a new cache. Independent tests cover different
masses, transpose, ties, tiny first mass, stale order and 40 random LP comparisons.
This elementary local rule is not claimed as novel.

Three arms ran once on each historical T5/n128/seed1000/shift0 case. Every table
agreed with same-run LP within 1e-8; roots matched archived numerical references.

| Case | All-general LP calls | Binary-direct LP calls | LP / binary-direct / shared-cache seconds | Binary delta sorts avoided by cache |
|---|---:|---:|---|---:|
| AR1, k1, delta0.5, squared | 543 | 411 | 1.074 / 0.864 / 0.909 | 1.52% |
| Nonlinear, k2, delta0.18, absolute | 1,067 | 308 | 2.206 / 0.847 / 0.860 | 2.24% |

The cache fails its frozen >=20% sort-avoidance gate on both cases. The direct
binary formula accounts for the useful reduction in LP calls. Times include the
arm's support preparation, stage matrices, snapshots and root, but shared model
construction is reported separately. Fixed-order single repeats establish neither
statistical speed advantage nor SOTA. `sort_calls` counts delta argsorts only:
permutation validation also sorts the permutation, and is included in time.

## Exact support-Monge dispatch

The second screen checks adjacent Monge inequalities on the CURRENT continuation
cost matrix restricted to actual positive supports. Each float entry is converted
to Fraction before arithmetic, so a one-ULP positive defect is not rounded away.
Adjacent inequalities telescope to all Monge inequalities. If they hold, the
classical NW coupling is optimal for normalized marginals in exact arithmetic.
Otherwise the identical LP fallback runs. This is distinct from claiming a tight
one-sided bound on a whole global continuation matrix.

| Case | Remaining LP calls before / after | Passed support checks | Baseline / dispatch seconds |
|---|---|---:|---|
| Coarse | 411 / 164 | 247 (60.10%) | 0.832 / 0.391 |
| Fine | 308 / 298 | 10 (3.25%) | 0.849 / 0.829 |

All tables/roots again matched within 1e-8. The frozen >=20%-on-each-case gate
fails on fine. No broad promotion follows from the coarse result.
The candidate runner's inherited `LP_calls` counts entries into general dispatch;
actual LP calls equal `dispatch.rejected`, as explicitly recorded in results.

Two numerical/provenance limitations prevent overclaiming. The NW helper uses
cumulative floating sums: an interior tiny mass can disappear through rounding,
despite the residual tolerance passing. Thus the exact predicate does not turn
the recurrence into an outward certificate. Its helper source was omitted from
the screen's explicit dependency list. Supplemental verification finds it matches
the historical smoke candidate pin exactly:
`fd1987a1e93e604029c4de155c8229e14f3c0ccc320bd834027db67cd5b99008`.
The frozen manifest was not retroactively edited. The binary implementation also
does not guard all overflow in derived arithmetic on arbitrarily extreme finite
costs; only the tested finite scales are accepted as numerical baseline evidence.

## Could nearly-Monge matrices rescue the fine case?

For exact positive adjacent defects delta_ij, let F_ij be their two-dimensional
prefix sum. Then M-F is Monge and no greater than M. Its NW optimizer pi gives
`OT(M) in [<pi,M-F>, <pi,M>]`, of local width `<pi,F> <= sum delta`.
An exact interval also requires exact normalized marginals and exact plan arithmetic.

A separately frozen audit computed only the defect sums; every DP value still
used the baseline LP. Of 164 strict rejections on coarse, zero had defect sum in
(0,1e-10]. Of 298 fine rejections, only 12 did (4.03%). The frozen 20% fine gate
fails, so no local interval fixture or relaxed solver was built. This does not
reverse the earlier negative global-envelope result or establish a root certificate.

## Cheap check at the actual horizon and path counts

A final support-only audit used T50, development seed1000, shift0, and the frozen
path counts 4,000/8,000 with the declared two-sided parameters. It did not build
dense kernels, solve OT, run the development benchmark grid or access confirmation
seeds. Unique history/transition-code counts give exact positive support sizes.
Independent checks matched the common model and prior dispatch counts on both
small fixtures before the larger structural measurement.

| Structural quantity | Coarse | Fine |
|---|---:|---:|
| Binary fraction among nonforced, T5/n128 | 24.31% | 71.13% |
| Binary fraction among nonforced, T50/frozen n | 10.23% | 27.62% |
| Forced fraction of all transition pairs, T50 | 15.10% | 39.19% |

These fractions are cost-independent. Initial-law root is excluded from transition
counts; in these zero-start cases it adds one forced solve. The >=20%-on-both-cases
coverage gate fails. Joint changes in horizon and sample size prevent attributing
the difference to horizon alone. One seed/shift does not establish full-domain
rates or runtime savings. The count audit took 0.839 seconds.

## Integration and next question

The four bounded runs took 6.764, 2.906, 1.798 and 0.839 seconds respectively;
they are different diagnostic costs, not aggregate candidate performance. Six
new test methods bring the full suite to 85 passing tests. Legacy pins remain
24 matching plus one historical; new source/result pins were also checked.
Independent reviewer checked formulas, code boundaries, the tests, support-count
identities, sampling parameters and artifact hashes. See `binary_transport_review_20260910.md`.
Prior-art matching remains incomplete; the Monge reference found was only
abstract-accessible. Neither common algorithm is a novelty claim.

Keep the stronger numerical exact-DP baselines available. Do not spend another
cycle on identical-support order caching, a relaxed Monge interval with this
1e-10 gate, or tiny-support extrapolation. Before another algorithm prototype,
require a mechanism that reduces work in the still-general support problems
and controls original-root upper/lower error; compare against these baseline
dispatches, not an all-LP Python implementation. This is a change in comparator
strength and evidence, not completion or a universal impossibility theorem.

Routing: one fresh-context Astra/high reviewer, root implementation and execution;
short follow-ups reused the reviewer for bounded independent checks. No extra
agent fan-out, external service, quota probe or hidden background job was launched.
