# Interval reuse: defer the cache; resolve the fixed-policy upper bottleneck

Date: 2026-09-10. Independent bounded skeptic review. This file is the only
artifact written by this lane. No solver, hypothesis registration, benchmark,
H_D02 trace rerun, shared status edit or ledger edit was performed.

**Decision:** nonzero-gap monotone reuse is a valid generic optimization in
exact arithmetic, but a new interval-cache implementation is not the next
useful step for the existing policy-pool candidate. Its unchanged upper policy
already prevents the requested 0.5% root width on every stored smoke case,
according to the available numerical evidence. Improve and independently
evaluate a feasible upper policy before investing in a lower-only cache.

## What was checked

Read `objective.json` revision 2; `HD02_opportunity_decision.md` and its saved
results/trace schema; `HD02_independent_audit_20260909.md`;
`ledger/inbox/B/H_D01_prior_art_review.md`; `adapters/common_model.py`;
`adapters/policy_pool_candidate.py`; the root-propagation discussion in
`research/theory/block_bounds_review.md`; and
`probes/policy_pool_common_smoke.py`. Read, but did not rerun,
`runs/cycle_2/policy_pool_common_smoke.json`.

The H_D02 trace is conditional on a declared phased activation schedule and
freshly replaced HiGHS witnesses, not a retained-plan production controller.
Its two numerical face rescues among 383 support hits establish neither a
general impossibility nor the opportunity for an approximate interval cache.
The latter permits positive incumbent increments and therefore concerns a
different rule. H_D02's strict local exact reference also cannot be plugged
directly into a float controller without resolving its numerical contract.

## Local interval and original-target obligations

For fixed transport marginals, let a cached coupling `p` be feasible and dual
potentials be feasible for `C_old`. With `Delta >= 0`, those same witnesses give

```
d_old <= OT(C_old + Delta) <= <p,C_old> + <p,Delta>.
```

The old primal need not be optimal. Its old primal-dual gap must be included.
The update must be monotone with respect to the matrix actually certified by
the cached dual, including every intervening event. A selected support hit
therefore need not force an immediate solve if a valid remaining gap budget
exists. This escapes H_D02's zero-increment condition, not standard LP
sensitivity or interval dynamic programming.

If the matrix is `c + L_child`, the displayed upper bounds `OT(c+L_child)`,
which is a surrogate lower Bellman problem. It does **not** bound the original
continuation. Given pointwise `L_child <= V_child <= U_child`, a valid feasible
policy upper at the parent is

```
<p,c+U_child> = <p,c+L_child> + <p,U_child-L_child>.
```

Dropping the second term reproduces the statement-fidelity error the project
explicitly excludes. The dummy initial-law root must also use a feasible
coupling; no time-zero stage cost is added.

The theorist's alternative residual identity is valid under its stated
coherence conditions. For a complete fixed feasible policy `p`, final Bellman
subsolution `ell`, terminal `ell=0`, and residuals
`r_n=<p_n,c+ell_child>-ell_n`, backward telescoping gives

```
U_p(root)-ell_root = sum_n occupation_p(n) * r_n,
```

including the dummy root residual. It is an identity for **that one final
policy and subsolution**. It is not a universal mass bound over all policies,
and does not permit summing stale per-event gaps, mixing occupancies from
different policies, or dropping inactive-node residuals. A global Bellman
subsolution/dual condition is still needed for `ell_root <= V_root`.

Numerical feasibility remains separate from this proof. In current code,
`_make_feasible` checks inequalities with a float guard; dot products, Bellman
addition, marginal normalization and upper evaluation are not outward rounded.
Primal residual acceptance is not exact primal feasibility. Rounding or repair
may add tiny positive support and alter cache/index dependencies. The module
correctly declares a numerical enclosure candidate, not a mathematical
certificate. Reusing its witnesses preserves that limitation.

## Prior-art decision

The H_D01 review already identifies elementary objective sensitivity, reused
min-cost-flow primal/dual information and selected-action reverse dependencies.
The proposed nonzero-gap extension does not by itself add a transport-specific
sharing operation.

[McMahan, Likhachev and Gordon, Bounded RTDP (2005)](https://www.cs.cmu.edu/~ggordon/mcmahan-likhachev-gordon.brtdp.pdf)
maintains upper/lower value bounds, focuses computation on relevant uncertain
states and provides anytime guarantees. This is direct architectural overlap;
the paper does not automatically supply a specialized finite-horizon OT
implementation or certify this code.

[Van Seijen and Sutton, Planning by Prioritized Sweeping with Small Backups
(2013)](https://proceedings.mlr.press/v28/vanseijen13.html) develops individual
successor-value backups and prioritized propagation. Consequently, incrementing
a cached coupling expectation through changed successors needs comparison with
ordinary incremental action-value maintenance. These source comparisons support
a conservative baseline classification, not a literature-completeness claim.

A contribution still needs an explicit shared transport update operation,
an amortized advantage beyond those baselines, or measured root-certified
benefit with all policy, index, detection, repair and fallback costs counted.
The root residual identity and a larger local skip count alone are insufficient.

## Independent zero-solve bottleneck diagnostic

The root suggested inspecting the existing smoke; this lane independently
parsed the JSON with Python's `json` and `statistics`, without importing a
solver or recomputing any OT. For every stored row, compute

```
g_upper = (levels[-1].upper - reference) / reference.
```

All 16 rows have exactly the same upper at both budget levels. Results:

| Saved-data metric | Result |
|---|---:|
| Cases | 16 |
| Minimum upper excess | 1.0874511527% |
| Median upper excess | 18.8236665192% |
| Maximum upper excess | 41.6004931670% |
| Cases above the requested 0.5% | 16/16 |

Scope: development seed 1000, T=5, 128 paths per side, shift zero, both process
families, both costs, k=1/2 and delta=0.5/0.18. This is selected existing smoke
data, not held-out confirmation or the original full domain.

For a genuinely feasible fixed `U` and true positive value `V`, every valid
positive lower `L<=V` satisfies

```
(U-L)/L >= (U-V)/V.
```

Thus a policy whose true excess exceeds 0.5% cannot achieve the requested
root width merely by improving or cheaply maintaining the lower. The stored
values give strong numerical evidence for this specific obstruction. Since
both reference and candidate evaluation use float arithmetic without outward
proof, the percentages are not an exact impossibility certificate. The
reference is audit-only and must never enter candidate selection or stopping.

This diagnostic is already sufficient to defer lower-only cache engineering
for the current fixed-policy architecture. It neither stops general upper/lower
search nor proves that cached intervals cannot help another controller.

## Smallest next operation, if development continues

Use one predeclared tiny cell and one feasible-policy improvement experiment,
with existing transport and policy-evaluation kernels. Do not implement a new
interval controller or dynamic-flow comparator first.

1. Save a coherent incumbent policy, its original-cost value tables, occupation
   and current lower tables. Select one nontrivial positive-occupation parent
   using the existing `occupation*(U-L)` priority and deterministic tie rule,
   without consulting a reference. This priority is a heuristic only.
2. Perform one local weighted OT on `c + U_child`, validate/repair its primal
   witness under an explicitly numerical development contract, and retain it
   only if its evaluated cost improves over the incumbent. Hold every other
   conditional coupling and the root coupling fixed.
3. Independently reevaluate the whole resulting policy on original costs.
   Measure actual `U_old(root)-U_new(root)`, local solver work, policy replay
   work and total time. As an audit, for a single changed conditional coupling
   with all descendants/ancestors fixed, check that the root decrease equals
   its *old-policy* occupation times its local policy-value decrease. This is
   a fixed-policy change identity, not a global optimum-gap bound.
4. Report the new root interval against a valid lower if available; otherwise
   retain the numerical-development label. Reference-based upper excess may
   be computed afterwards solely to diagnose the remaining upper bottleneck.

This answers whether one affordable, correctly targeted action improves the
part of the certificate that a lower-only cache cannot change. A positive
result justifies a tightly budgeted upper-policy improvement baseline; it is
not novelty. A failed selected patch rejects only that patch/selection, not
all policy improvement. A large root gain still needs a complete total-cost
comparison, outward certification and an additional structural mechanism
before a new research hypothesis or grid is justified.

The next task must state the expected decision before running. At present the
actionable decision is already **defer interval-cache implementation; focus on
the feasible upper policy**, preserving H_D01 as a standard optimization and
H_D02's scoped deferral.
