# Forced-transport baseline review, 2026-09-10

The proposed insertion is sound as a float64 numerical diagnostic. It is an
omitted elementary baseline, not a new transport or reuse mechanism.

For normalized nonnegative marginals, if either positive support has size one,
the unique feasible coupling is a b^T. Thus OT(M)=a^T M b for every finite M.
Detect positive support with >0, not array length or a numerical sparsity cutoff.
Zero-mass coordinates impose no transport; all-zero marginals are invalid.

With M=c+ell_child and ell_child<=V_child, monotonicity gives
a^T M b=OT(M)<=OT(c+V_child). Backward induction from terminal zero preserves
the original-target lower bound, and the unchanged initial-law root OT preserves
it at the root. This is exact for the lower-continuation surrogate, not necessarily
for the true continuation. Keep the original upper policy and its occupation.
Use a maximum with existing lower values/floors; valid floors remain lower bounds
on V. Local subsolution residual identities additionally require floors compatible
with current child tables, as in a monotone sequence of sweeps.

The common builder divides transition counts by positive row totals. Existing OT
routines additionally normalize positive masses for summation roundoff. Match that
convention in forced expectations; do not silently accept missing probability mass
or threshold tiny positive probabilities. Direct products and existing free_lower
are not outward rounded. Retain the numerical-only status and scale-aware checks.

The old free_lower is not exact in general on these pairs: for
M=[[0,0],[0,1]], a=[0,1], b=[1/2,1/2], all its unguarded candidates are zero,
whereas OT(M)=1/2. Guarding its shared dual does not close the gap. The selected
transport_plan_and_dual already has a singleton fast path, so the omission is
automatic application to every eligible pair before budgeted selection, not a
missing specialized local solver. Prior selected witnesses may already close
some particular eligible pairs.

Same B16 means the same maximum selected-pair calls, not equal arithmetic work
or equal LP count. Charge support detection, forced expectations and root work;
report selected calls, actual LP calls and elapsed time. Updating scores can change
which reusable witnesses B16 obtains, so final B16 dominance over old B16 is not
guaranteed. Do not additionally exclude forced pairs without declaring that separate
selection change: their duals can still help other pairs.

Cheapest gate: count forced pairs and nontrivial slack above old free_lower, then
compare old versus forced B0 on one declared tiny case. If root improvement is
material, one matched B16 comparison can establish the baseline's practical effect.
Verify against the existing numerical DP reference within stated tolerances.
For the requested fixed upper, the existing headroom failures still preclude a
0.5% target on those reference cases regardless of lower improvement. Stop at the
baseline diagnostic; do not reopen interval reuse, dependency maintenance, or a
lower-only solver program on the strength of this correction.

## Implementation verdict

Reviewed the adapter, frozen probe, tests and manifest/results without rerunning
the screen. All 11 pinned source/artifact hashes and the result's manifest hash
match. Archived B4 and B16 lowers reproduce exactly on both cases. All three
focused tests pass. Builder-normalized empirical marginals preserve the target;
the sparse upper is evaluated coherently with its own occupation and is shared
between arms. Both B0 gates pass: lifts/reference are 7.8244% and 38.5634%.

B16 lowers improve 3.246985->3.375624 and 2.402723->2.762202, removing 21.8344%
and 34.2837% of reference deficits. Each matched schedule uses 82 selections;
actual LP calls rise 76->82 and 31->70. Sweep times rise .169->.181s and
.092->.437s. Fixed-upper widths remain 14.8783% and 47.7312%; posthoc archived
improved-upper widths remain 13.7330% and 31.4164%. No 0.5% success follows.

No blocker for this bounded numerical diagnostic. Record minor reporting limits:
`pairs_with_lift_gt_1e10` actually tests >1e-10; work counters are narrow counts,
not total scans/operations. The adapter's normalization can overflow or underflow
on arbitrary extreme unnormalized inputs, potentially changing support; this does
not affect these empirical probability rows and is not a general robust-input
guarantee. Its guard is explicitly heuristic. Source pins support reproducibility,
not independent proof of when freezing occurred. Preserve these frozen artifacts.

## Forced-state elimination question

Exact substitution is sound on the finite acyclic Bellman graph: a forced node equals its expected immediate stage cost plus its unique coupling's weighted child values. Recursively substitute only forced children, retaining a constant and nonnegative coefficients on the first nonforced boundary. Sum coefficients of repeated boundary states; preserve state/time identity, all path costs, positive masses and terminal contributions. Terminal-zero omission can make retained coefficient mass less than one. At nonforced parents substitute each continuation entry, retaining the same OT marginal constraints. Include the original initial-law root, eliminating it only if forced. No population oracle is needed.

This is ordinary affine substitution/variable elimination in a DAG, without a novelty claim. Expansion can destroy sharing and introduce many boundary dependencies; construction, coefficient storage, contraction/update work, nonforced matrix assembly and root work all count. A support census uses exact positivity/union membership, never thresholding small probabilities; structural counts alone need no OT solve.

Predeclare the direct sparse dependency-incidence count and the fully expanded distinct boundary-incidence count over the same required nodes/entries. If expansion exceeds that baseline or its work cap, reject this proposed incidence-reduction route without constructing a solver. That rejection concerns the declared route/metric, not every conceivable implementation. Zero fill-in proves only no new structural dependency growth under that definition; it proves neither runtime savings, arithmetic accuracy, improved upper-policy quality nor a 0.5% certificate. Even a favorable census is only permission for a separately justified work comparison, not evidence of solver advantage.
