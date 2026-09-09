# H_D02 independent correctness and compatibility gate

Date: 2026-09-09. Decision: **pass as an exact local reference fixture; revise before controller promotion**. This is an unregistered development audit, not confirmation evidence, a root certificate, or a performance claim. The historical `adapters/monotone_reuse.py` remains invalid for exact acceptance; it has not been overwritten.

## What question this step resolves

Objective v2 prioritizes the cost of a valid certificate for the original root target. It is wasteful to time an optimization that falsely accepts local values. The bounded task was to establish a trustworthy local reference and determine whether it can receive the controller's existing witnesses. It was not to build a production rational OT solver or launch a grid.

## Mathematical statement and independent proof

Fix finite nonnegative marginals with the same total mass, a finite cost matrix M, and a nonnegative update D. Let v be the old optimum and P its feasible transport polytope. For every p in P,

`<M+D,p> - v = (<M,p> - v) + <D,p>`.

Both terms on the right are nonnegative. The updated optimum equals v iff some old-optimal p has zero update cost. Because p and D are nonnegative, zero update cost means p only uses edges with D=0. For any exactly optimal old dual, complementary slackness implies every old-optimal plan uses only its exactly tight edges. Therefore feasibility on the zero-update, old-dual-tight graph exactly characterizes value preservation under these mathematical assumptions. Basis degeneracy alone does not ensure more than one optimal plan, nor that a second plan avoids all updates.

For an accepted numerical witness, exact primal feasibility, dual feasibility and primal-dual equality are sufficient for the local conclusion. A solver's success status or agreement with a fresh solve using the same tolerances is not sufficient. Failure to obtain a verified witness is not proof of mathematical infeasibility.

## Reviewed implementation contract

Reviewed `adapters/monotone_reuse_reviewed.py` interprets the binary64 representation of every input as an exact rational. It checks nonnegative finite inputs, exactly matching marginal totals, every row/column of the old plan, exact dual inequalities and old primal-dual equality. Allowed repair edges have exactly zero update and exactly zero old reduced cost. HiGHS proposes a repaired plan; a second exact witness replay decides acceptance. The authoritative returned value is a Fraction. Failed numerical witnesses return a fallback decision, without claiming non-reusability.

Code inspection found no acceptance path bypassing these checks. Zero total mass also passes the old witness gate before returning. The independent oracle below checks candidate plans using separate Fraction computations. This supports the stated local soundness argument; it is not a formal proof of Python execution or a claim of completeness for all solver outputs.

The new counters include dense witness/classification scans, rational conversion counts and feasibility LP variables/nonzeros. They prevent reporting kept edges alone as total tested work. They are diagnostic counts, not interchangeable cost units or evidence that the new LP is cheaper than dynamic weighted OT reoptimization. A support-miss check currently replays the witness twice; that is acceptable for a reference fixture, not an optimized production claim.

## Reproducible independent findings

Run `python research-workflow/probes/hd02_independent_audit.py`. The resulting `runs/cycle_2/hd02_review/verification.json` records the reviewed module SHA-256 and the results.

- Positive update 5e-11 on every edge: both historical gates accept unchanged zero incorrectly. Both reviewed gates reject.
- Dyadic tiny-mass case: a=(2^-27,1-2^-27), b=(1/2,1/2), M=0, and D=1 on the first row. The exact updated optimum is 2^-27. Historical face reuse accepts zero; reviewed reuse rejects the solver candidate for exact marginal infeasibility. Dyadic values deliberately isolate LP tolerance from a mismatch in exact marginal totals.
- 64 seeded 3x3 dyadic-marginal additive-cost fixtures: an independent oracle enumerates all rational capacitated Hall inequalities on the permitted graph. There are 10 feasible cases accepted and 54 infeasible cases rejected, with every accepted plan independently replayed for exact feasibility and objective. This is a small correctness screen, not an estimated real-workload reuse rate.
- A unique diagonal optimum with unavoidable positive diagonal updates is correctly rejected.

## Safety does not establish usable integration

Two distinct compatibility problems are decisive:

1. Among 64 seeded pairs of ordinary 3-entry Dirichlet float marginals, 61 have unequal total mass when binary64 entries are interpreted exactly; only 3 match. This screen does not estimate all project datasets. It establishes that ordinary independent floating normalization is incompatible with the new exact-input contract often enough that silent direct integration is unacceptable. The historical decimal 1e-8 counterexample also needs this qualification; the dyadic example above removes it entirely.
2. Even with exactly feasible dyadic marginals, the current `policy_pool_candidate.transport_plan_and_dual` unconditionally shifts beta downward using `_make_feasible`. On a zero-cost, zero-update example, the supplied old primal-dual gap is exactly 1/140737488355328. The reviewed checker rejects solely because old optimality is not established exactly. This rejection is safe and intentional. It would occur before any possible face repair on that witness.

Neither finding warrants loosening tolerance or silently renormalizing the target. Neither implies face reuse is mathematically impossible. The current production-style upstream witness and this strict exact reference serve different numerical contracts. A local exact fixture is not an original-target root certificate, and none of this supplies a population guarantee.

## Decision and next-step filter

Preserve the historical implementation as invalid evidence and keep the reviewed file as a reference fixture only. Do not wire it into the current controller, promote H_D02, register a performance probe, or open a large grid on the basis of this audit.

Before further engineering, a small real controller trace must show whether H_D01 support hits leave enough alternative-face opportunity to matter under an explicitly compatible witness contract. Report opportunity separately from numerical witness rejection. If that signal is absent or resolving the witness contract dominates potential savings, stop this direction without calling it an impossibility theorem. Do not build a general rational production transport solver merely to rescue H_D02.

Only a favorable, scoped opportunity result would justify assessing a numerical bridge and fully charged comparison against dynamic reoptimization on the identical trace. Root propagation and the original finite target must then be reviewed separately. Current audit evidence does not authorize a SOTA, speed, or full-domain completion claim.
