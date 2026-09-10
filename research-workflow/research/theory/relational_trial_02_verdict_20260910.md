# Trial 02 verdict: valid causal-tree baseline, no promotion

2026-09-10. User selected mathematical conditional order preservation. This
bounded cycle supplies a concrete sufficient rule and a PO investment decision.
It does not impose top-K, statistical risk, automatic fallback or a new contract.

## Result

For prefix h, the maximal bicausal equal-prefix mass is
m_h=m_parent min(p_h,q_h). The tree-cost optimum is
sum_h w_h(mu_h+nu_h-2m_h), for nonnegative edge weights. The reviewer independently
confirmed the argument and found its core construction in Beiglbock--Zona,
arXiv:2506.22106v1, Lemma 2.1. This is retained as a known baseline/corollary.

For common depth range C_t=(max_t-min_t)^p, tree weights C_t/2 dominate numeric
path cost. Thus U_tree=sum_t C_t(1-A_t) is an upper bound on D. The sum of
scalar marginal OT costs is L_marg<=D. The explicit computable condition

    U_tree(Q,A)<L_marg(Q,B)

proves D(Q,A)<D(Q,B), without needing either exact D. It can also compare two
pairs without a shared query under the same target definition. This is elementary
bound separation, not a new order theorem of demonstrated scientific significance.

## Checks and headroom

- Twelve rational comparisons of the prefix formula (six pairs, both depth-only
  and arbitrary positive node weights) match an independently formulated 2x2
  bicausal affine transport polytope.
- Twelve rational numeric-cost checks (six pairs, absolute/squared) satisfy
  L_marg<=D<=U_tree. No floating certificate or general-purpose solver claim.
- The common-tree range upper is visibly weak on the old temporal fixture:
  Q,B has absolute interval [1/16,5/8] around exact 3/16; Q,C_high has
  [1/4,3/8] around exact 1/4. Their order remains unresolved. In fact none of
  the three query-Q comparisons among B,C_low,C_high is certified by this rule
  for either cost. These hand-selected diagnostics are not statistical coverage.
- A separated-support fixture gives U_tree(Q,A)=1 < L_marg(Q,B)=3, proving
  nonvacuity only. It is terminal-only and does not satisfy the significance gate.

The scalar unit-tree score remains discontinuous with respect to small numeric
perturbations: deterministic (0,0),(epsilon,0) cost epsilon in AW_1, but 4 on
the unit prefix tree for every epsilon>0. The causal fix alone does not fix
geometry. This is specific to those weights/representation, not all tree methods.

## Work and review boundary

An explicit full-prefix traversal is linear in traversed edges. For aligned
k-window kernels and time/state/transition-dependent weights, surviving full-prefix
agreement aggregates on the compact state graph; no exponential full-path
expansion is needed for that regime. Both the prefix formula and this aggregation
were addressed in the recovered independent review. General arbitrary-prefix
weights or substituting the raw sample trie for a recombined k-window law do
not inherit that guarantee. Arithmetic operation counts omit rational bit growth.

The reviewer wrote `relational_trial_02_independent_review_20260910.md` and sent a
substantive finding before its turn failed on usage limit. Retain the written
review as received evidence, but do not report final independent sign-off on
the complete root packet or range/marginal proof-check implementation. No other
reviewer was started to work around the limit. No promoted candidate depends
on the missing sign-off.

## PO decision

Retain this as an analytical baseline. Do not register a performance hypothesis,
open grid, implement a production compact kernel, or center a paper on this
formula. The scientific-significance gate does not pass. The next bounded
decision is a geometry-aware condition that beats this baseline on a genuinely
conditional fixture, with input-only condition checks and explicit omitted work.
Detailed task and stop gates: `DECISION_ORDER_PRESERVATION_20260910.md`.

This closes root's bounded diagnostic/decision task with the final independent
review boundary disclosed; it is not a completed scientific outcome.
