# Independent verification of the upper-policy development screen

Date: 2026-09-10. **Verdict: pass for a numerical development diagnostic;
not a certified root interval or a performance/novelty result.** No full screen
or OT solve was rerun by this verifier. The review combined structural code
inspection, frozen source/provenance checks and independent arithmetic checks
on saved results. Only this report was written by this lane.

Reviewed artifacts:

- `probes/upper_policy_improvement_screen.py`
- `runs/cycle_2/upper_policy_screen/manifest.json`
- `runs/cycle_2/upper_policy_screen/results.json`
- Original smoke probe, manifest and results, plus the unchanged common-model,
  generator and policy-pool adapter sources.

## Correctness of the evaluated object

Each budget starts independently from the same stored SVD policy. At a layer,
the retained parent plans are first evaluated against `c+newU_child`. Selected
replacements solve that same upper-continuation problem, and are accepted only
when their evaluated cost decreases. Induction therefore gives pointwise
nonincrease relative to the initial policy, in exact arithmetic with feasible
couplings. The implementation explicitly checks the numerical counterpart.

The score uses initial-policy occupation times the difference between the
retained policy cost and `free_lower(c+newU_child)`. This latter quantity is a
lower bound for a local *upper-continuation* OT problem, not a lower bound on
the original continuation. It is used only for ranking; this is legitimate.
The algorithm never presents this score or an occupation-weighted score sum
as a global optimality certificate.

After the backward pass the script solves the initial-law root OT, compares
its result with the retained root coupling evaluated on `newU[0]`, and keeps
the cheaper policy. The root is included even though both measured inputs
have only one state pair at time zero. Thus these two cases do not exercise a
nontrivial initial-law coupling.

The final check evaluates every stored conditional plan backward on original
stage costs, and separately propagates its occupation forward and accumulates
costs at times 1 through T. No time-zero cost is added. Backward tables are
checked against those used during improvement. This is the correct original
finite-model policy value, rather than the value of a lower surrogate.

Stored plans are indexed coherently by `i*number_of_right_states+j`. Packing
and sparse evaluation retain all nonzero entries; no positive-mass threshold
is used to discard small flow. Root and conditional marginal residuals are
checked, as are propagated marginal laws. Retaining an old plan is safe for
fixed marginals; continuation changes only its value.

## Numerical and evidence limits

The gates allow residuals up to 1e-8. `pack` uses `np.nonzero`, so its support
can include a tolerated negative solver value. Consequently names such as
`stored_positive_edges` should be read as stored nonzero edges unless exact
nonnegativity has independently been established. This is not a proof that
the floating policy is exactly feasible. Actual recorded worst marginal/
nonnegativity residuals are 4.025e-16 and 3.331e-16 in the two cases.

There is no outward rounding, exact rational primal repair, or certified error
accumulation. Guarded local duals do not close those gaps. The screen does not
compute a valid new root lower certificate. `below_target_excess=true` means
only that the measured upper lies within 0.5% of an audit reference; it is not
a certified stopping test.

The maximum saved forward/backward objective disagreement is 4.441e-16.
This verifier inspected the two evaluation paths and checked their recorded
gates and arithmetic; it did not independently reproduce the full numerical
policy execution. Complete policy witnesses are not stored in the result
JSON, so independent witness replay would require another execution or an
additional witness artifact. The present task intentionally avoided that
duplicated computation.

## Reference identity and absence of oracle selection

Current generator, common-model, original candidate and original smoke-probe
hashes match the historical manifest. The archived results reference the
actual historical manifest hash. The new manifest hashes all those files and
the new script; this verifier independently recomputed every new hash and
checked the results-to-manifest link.

The script imports the original hash-validated path generator and uses the
same process parameters, seed, T, sample count, k, delta, cost and zero shift.
It also checks the reconstructed initial upper against the archived initial
upper. This supports reuse of the numerical reference on the same represented
target. It does not turn the historical float64 DP value into an exact oracle.

The reference scalar is loaded before the improvement loop, but data flow
uses it only for report fields. Neither ranking, plan replacement, solve
budgets nor termination depends on it. The initial-upper identity gate uses
the archived candidate value, not the optimum, to detect target drift.

## Saved results independently checked

| Case | Initial upper excess | B=4 | B=16 |
|---|---:|---:|---:|
| AR1, k=1, delta=.5, squared | 1.087451% | .387300% | .079675% |
| Second order, k=2, delta=.18, absolute | 18.235840% | 6.958112% | 5.178390% |

Both levels call 17/65 local transport operations respectively, plus one
root operation. `linprog_calls` is correctly separate because deterministic
blocks use the direct kernel path. Sums of per-layer selected calls, reported
relative excess, upper nonincrease and residual gates agree with the saved
data. Both cases completed within the declared cooperative 60-second cap;
the recorded complete screen wall time is 19.9468 seconds.

These are two deliberately selected development cases, T=5 and 128 paths per
side, seed 1000, one shift. Neither held-out evidence nor full-domain coverage
is supplied. B=16 is an independent restart, not an extension of B=4.

## Cost accounting and resulting decision

Actual improvement time includes local solves, root solve, all policy scans,
score computation, backward and forward reevaluation, and loop overhead.
Initial policy construction, path/model construction and initial occupation
are reported separately. They must be added for a standalone interpretation.
The corresponding phase sums are approximately .151/.230 seconds for the
coarse case and 19.156/19.241 seconds for the fine case at B=4/B=16. These sums
exclude startup provenance I/O and small outer bookkeeping and are not a
new end-to-end benchmark.

In particular, the fine case spends 18.713 seconds constructing the initial
policy before its .424/.509-second improvement. Quoting only improvement
time would hide the dominant work. The 35,006 parent scans and full backward
replays in that case also remain real computation despite few local solves.

Primitive counters are diagnostic, not exhaustive: the dense-entry counter
adds one matrix size per initial parent, while the two-orientation policy
routine constructs additional arrays; root construction is also absent from
that counter. Local dual construction scans and internal LP work are captured
by timings but not completely enumerated as primitive counts. No allocation,
arc-work reduction or speed claim is supported by these counters alone.

The outcome justifies retaining ordinary feasible-policy improvement as an
engineering baseline. It removes the measured upper barrier on the easy case
but leaves it above 5% on the harder case. It does not justify promoting an
interval cache, starting a large grid, claiming 0.5% certification or calling
the familiar policy-improvement operation a new structural contribution.

For the frozen diagnostic, no correctness repair or rerun is required. Any
promotion would first require an audited numerical certificate, a useful
root lower alongside the upper, fuller cost comparison and explicit treatment
of the dominant initial-policy construction. Preserve the frozen code and
state the accounting and numerical limitations in the decision report.
