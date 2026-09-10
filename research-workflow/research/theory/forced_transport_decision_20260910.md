# Forced transport baseline and the next structural question

Date: 2026-09-10. This is a bounded development diagnostic, not a new hypothesis
or an outward root certificate. Historical source, manifests and results remain unchanged.

## Question and mathematical boundary

Does the lower baseline leave avoidable slack where a coupling is uniquely fixed?
If either normalized transition marginal has singleton positive support,
`OT(M;a,b)=a^T M b` for every matrix M. Applying this identity to
`M=stage_cost+lower_child` gives a valid local lower in exact arithmetic; induction
retains the original-target lower at the root. It does not make a surrogate
continuation exact. The selected local solver already handles such cases; the
omission was automatic coverage before selecting a limited shared-dual pool.

The new adapter detects support using `>0`, with no tiny-mass deletion. It uses
the existing normalization convention. Its roundoff guard is heuristic;
arbitrary-scale input robustness and outward feasibility are not established.
The independent review is in `forced_transport_review_20260910.md`.

## Frozen screen and result

The two previously selected cases retain T5, 128 paths per side, seed1000, shift0.
The script inserts only this rule into the existing `free_lower` during an
otherwise unchanged `lower_sweep`; generic selection and floors remain active.
Both arms use the same sparse SVD upper and its actual forward occupation.
The whole screen took 1.633 seconds including setup and every executed arm,
excluding imports/provenance/reference production. No exact DP was rerun.

The declared first gate was a B0 lift of at least 5% of the archived reference.
Both cases passed, permitting the historical B4-then-B16 schedule. The original
arm reproduced its archived B4 and B16 root lowers exactly on both cases.

| Quantity | Coarse AR1 k1 delta0.5 squared | Fine nonlinear k2 delta0.18 absolute |
|---|---:|---:|
| Forced pair coverage per sweep | 204/747 (27.31%) | 33,939/35,006 (96.95%) |
| B0 lower, old to augmented | 0.148731 to 0.448886 | 0.089248 to 1.420175 |
| B16 lower, old to augmented | 3.246985 to 3.375624 | 2.402723 to 2.762202 |
| Fraction of reference deficit removed at B16 | 21.83% | 34.28% |
| Selected local calls, each arm | 82 | 82 |
| Actual LP calls, old to augmented | 76 to 82 | 31 to 70 |
| B4+B16 sweep seconds, old to augmented | 0.169 to 0.181 | 0.092 to 0.437 |
| Added forced cost-entry reads over both sweeps | 2,142 | 90,138 |

Equal selection budgets are not equal work. Changing scores changes which shared
duals are obtained; the augmented B16 is not generally guaranteed to dominate the
old B16. This run gives tighter lower bounds, but no speed advantage. Its counts
are narrow operation proxies, not complete primitive arithmetic accounting.

Combining the new lowers posthoc with archived improved feasible-policy uppers on
the identical model gives numerical widths 13.73% and 31.42%, respectively
(previously 18.24% and 51.08%). This combination is not an integrated solver run.
The original unchanged uppers instead give 14.88% and 47.73%. All are above 0.5%.

## Decision

Retain the forced-value rule as a correctness/reference baseline for future
comparisons. Do not promote the current loop implementation as faster, tune its
kernel further, increase budgets, or reopen lower-only interval reuse from this result.

The next bounded question is whether forced states can be eliminated from the
recurrence with fewer dependency incidences. Exact affine substitution through
forced states is standard finite-DAG variable elimination. It may create a larger
boundary coefficient table. A no-OT frontier census will test that footprint before
any compressed solver is built; coefficient construction and root assembly remain
obligations even if support counts improve. This is not yet a novel tree mechanism.

Artifacts: `adapters/forced_transport_lower.py`, `probes/forced_transport_screen.py`,
`runs/cycle_2/forced_transport_screen/{manifest,results}.json`.
Three focused tests compare forced cases with the existing local solver, exhibit
missed slack, and preserve tiny positive support. Independent review checked all
source pins, archived reproduction, numerical scope and the selection-work caveat.

## Frontier census and final stop decision

The separately frozen no-OT census completed in 0.210 seconds. Each forced node
is expanded only to its first nonforced descendants; terminal-zero descendants
contribute no boundary symbol. Boundary IDs retain time and both state identities.
The demanded entries are unique child-table entries used by nonforced parents,
plus original-root demands. The direct comparator evaluates their full forced
dependency closure. Compiled links count only demanded entries, not redundant
intermediate tables. This is set support arithmetic, not coefficient computation.

| Dependency count | Coarse | Fine |
|---|---:|---:|
| Nonforced nodes | 543 | 1,067 |
| Direct forced incidences in required closure | 1,071 | 45,069 |
| Direct dynamic incidences after caching constants | 646 | 2,730 |
| Compiled boundary incidences for demanded entries | 709 | 2,080 |
| Union input entries processed in compilation | 709 | 2,930 |
| Maximum frontier width | 15 | 5 |

Both pass the initial all-edge footprint gate. The fairer dynamic comparator,
also declared before execution, rejects coarse expansion (9.75% more links).
Fine expansion saves 650/2,730 = 23.81% of this restricted dynamic-incidence count.
It does not save 96.95% of OT solves: `common_model._transport_value` already
skips LP when either support is singleton. Empty-frontier chains can be cached
once even without coefficient expansion, so counting them as repeated work would
overstate the advantage. Local OT, matrix construction, coefficient construction,
storage, static costs, invalidation and numerical certification remain unmeasured.

**Stop this implementation direction for now.** Retain the forced lower as a
numerical reference and the census as scoped evidence. Do not build an expanded
solver, register novelty, increase budgets, or run a large grid. Reopening needs
an actual repeated-update workload showing the remaining dynamic propagation
cost is material after constant caching, with construction charged and an
independently justified route to reducing the root gap. A favorable fine-cell
support count alone does not meet that gate. This is neither a universal
impossibility result nor completion of the original scientific objective.

The theorist reviewed exact affine substitution and its limits. Root reviewed the
census source before freezing, corrected the demanded-entry/closure comparison
and global work cap, then ran it once. Two independent hand-DAG checks verified
stopping at nonforced boundaries, original-root demands and terminal-only chains.
Full unit suite: 79 pass; legacy pins remain 24 matching plus one historical.

Routing actually used: Astra/high with a fresh short context for the mathematical
and independent implementation review; Sol/high with a fresh short context for
the census draft. Sol was interrupted after a bounded wait without a completion
report; its on-disk draft was recovered, reviewed and executed by root. No Sol
completed-run claim is made. Root handled integration and the bounded numerical
screen. No token-saving percentage is inferred without usage measurements.
