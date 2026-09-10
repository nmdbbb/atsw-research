# Independent final review: permuted Monge screen

Date: 2026-09-10. Reviewer did not author the probe. No benchmark was rerun,
and no historical code, manifest, or result was edited.

**Verdict: approve the scoped failed-gate conclusion.** No implementation
blocker was found. Close this ordering screen as unsuccessful under its frozen
gate; this does not complete the broader research objective.

Reviewed `probes/permuted_monge_screen.py`, `binary_transport_screen.py`
(`solve`), `adapters/binary_transport.py`, `common_model.py` (`_transport_value`),
`support_monge.py`, and `policy_pool_candidate.py` (`_orders`, `nw_plan`),
the screen manifest/results, support-Monge predecessor, prior binary/Monge
review, and `permuted_monge_checkpoint_20260910.md`.

For permutations r,c, relabeling a coupling by P'[i,j]=P[r[i],c[j]] is a
bijection of feasible couplings for marginals a[r],b[c] and costs M[r,c],
preserving objective value in exact arithmetic. Both shared and private paths
apply precisely those marginal and matrix permutations. Inverting each global
permutation into ranks and sorting ranks restricted to positive supports gives
the intended restricted order. Reversing the right order is a valid second
candidate. SVD merely proposes orders; it cannot bypass the exact predicate.

The support iterator follows the pinned solver's row-major parent-pair loops:
both use `flatnonzero(a > 0)` and only `min(support sizes) > 2` enters the
patched general dispatcher. Singletons and binary pairs do not consume it.
Layer construction follows T-1,...,0,-1, with -1 using both initial laws.
The root therefore has the correct mapping even for general initial support;
these archived cases exercise a singleton root, not a general-root fixture.
Shape checking alone would not detect every future traversal change, but the
current pinned traversal agrees exactly. Missing broader coverage is declared
scope, not a discovered bug or a prerequisite to this negative conclusion.

Each arm/layer constructs its own binary matrix snapshot and fresh ranks from
that layer's stage-plus-continuation matrix; nothing reuses an earlier matrix
version. General slices come from the same unchanged local matrix. Continuation
tables may differ by floating roundoff between arms, so this is a comparison of
complete recurrences with the same kernel, not bitwise identical matrices.

The adjacent Monge predicate converts individual binary64 entries to Fraction
before addition/comparison; adjacent inequalities imply all rectangle
inequalities. NW is optimal after a passed predicate in exact arithmetic.
Actual normalization, cumulative sums, plan construction and values remain
floating point. Interior tiny masses can disappear while the 2e-12 marginal
gate passes, and large finite scales can overflow arithmetic. Reordering can
also change rounding. Numerical table/root agreement supplies no outward
certificate or universal finite-input guarantee; inherited limitations remain.

All arms use the same `binary_per_pair` kernel, singleton rule, identity-first
Monge check and original LP fallback. Shared arms charge six global SVDs
(including root) and rank preparation; the last arm adds private SVDs only
after shared failures. Support extraction, permutation copies, checks, NW,
snapshots and root work lie inside arm time. Models are constructed once and
reported separately; equivalence validation lies outside arm timing and inside
whole-screen time. The whole screen completed in 3.841 seconds.

The nested `counts.LP_calls` is a general-dispatch proxy: 411 and 308 in every
arm. Actual LP calls are `dispatch.LP_calls`; every fallback on these positive
general supports reaches one `linprog` call. Independent arithmetic checks
confirmed that acceptance categories plus actual LPs equal the proxy, and
singleton + binary + general counts equal all parent pairs.

| Case | Identity / shared / shared+private actual LPs | Shared saving |
|---|---|---|
| Coarse AR1, squared | 164 / 164 / 161 | 0% |
| Fine nonlinear, absolute | 298 / 293 / 287 | 1.678% |

Both fail the frozen >=20% saving on each case requirement. Private work saves
only 1.829% and 3.691% relative to identity and cannot rescue the shared gate.
Maximum recorded table differences are 4.44e-16 and 8.88e-16; all recorded
roots equal the archived candidate roots. These are numerical consistency
checks, not evidence of speed. Same-run arm times are 0.404/0.417/0.438 and
0.833/0.846/0.898 seconds. Archived identity times were 0.391 and 0.829 seconds;
that control variation and the fixed arm order preclude a statistical speed
interpretation. All observed timing differences remain descriptive.

Independent read-only SHA-256 verification passed all 12 frozen source/artifact
pins, this result's manifest link, and the predecessor result's manifest link.
The current manifest pins the imported NW helper explicitly, addressing the
predecessor manifest's provenance omission without rewriting it. Source hashes
do not pin Python/NumPy/SciPy/BLAS execution environments or prove chronology.

No new experiment, broader coverage, literature search, or solver change is
required to close this screen. Remaining closure work is integration: record
this review and the failed gate in the cycle status/ledger, preserve historical
artifacts, and complete the authorized repository checks and publication step.
No novelty, full-grid win, population guarantee, outward root certificate or
SOTA result follows. Starting another research mechanism is a separate cycle.
