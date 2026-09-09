# H-B verdict (Lane C, independent adversarial review)

Prepared 2026-09-09 by Lane C. Read before writing: `hypotheses/H_B01_temporal_block_bounds.json`,
`research/theory/block_bounds_review.md`, `research/theory/notes.md` (section H-B),
`adapters/common_model.py`, `objective.json`. Only this file and `ledger/inbox/C/H_B01_decision.json`
were written.

**This document contains no registered experiment, no benchmark and no SOTA claim.** The numbers in
sections 4 and 5 are a *reviewer-side audit* run for adjudication only: they were not preregistered,
they were produced by my own reconstruction of the generator seeding convention, and they run at
T=4 on the development grid, not on the required T=50 domain. Treat every number here as
**provisional evidence about the mechanism**, never as a result about the objective.

**Verdict: `revise`.** The lemmas are correct and the recursion is propagated to the root correctly
— I verified both symbolically and numerically. What fails is the quantitative premise. On the
registered development grid the one-sided reachability envelope is between one and two orders of
magnitude too loose to leave any positive-mass successor rectangle unexpanded at the required
0.5% root tolerance, except at the layer adjacent to the terminal time, which is exactly the
contribution the hypothesis's own ablation is designed to attribute to static terminal-cost pruning.
Where the envelope does buy room (k=2, fine delta) it correlates 0.79 with the empirical model
degenerating into deterministic single-successor paths. H-B should not be implemented as a full
hierarchy before a cheap headroom audit (section 7) is registered and passed.

---

## 1. Exact target, restated from the adapter

From `adapters/common_model.py` (`exact_dp`), with p=2 for `squared` and p=1 for `absolute`:

    V_T(x,y) = 0
    V_t(x,y) = OT( P_t(x,.), Q_t(y,.), c_{t+1} + V_{t+1} ),   t = T-1..0
    c_s(i,j) = |r_s(i) - s_s(j)|^p                            (current cell centres)
    R        = OT( a_0, b_0, V_0 )                            (no time-zero stage cost)

`V_t(x,y)` is therefore the value of the remaining problem *excluding* the stage cost at time t:
`V_t(x,y) = min over admissible bicausal continuations of E[ sum_{s=t+1..T} c_s(X_s,Y_s) | X_t=x, Y_t=y ]`.
All statements below are about this finite model. They are not population statements.

## 2. Proof sketch: the three lemmas are valid

Write the exact Bellman map as `(T W)_t(x,y) = OT(P_t(x,.), Q_t(y,.), c_{t+1} + W)`.

**L1 (block relaxation is a lower bound).** Fix a parent (t,x,y), `a_i = P_t(x,i)`, `b_j = Q_t(y,j)`.
Partition the positive successor supports into blocks A, B; `a_A = sum_{i in A} a_i`, `b_B` likewise.
Let `Lnext <= V_{t+1}` pointwise on the *whole* positive support, and `m_AB <= c_{t+1}(i,j) + Lnext(i,j)`
for every `(i,j) in A x B`. For any fine coupling `pi` with marginals a,b, the block sums
`gamma_AB = sum_{A x B} pi_ij` are coarse-feasible and `sum gamma m <= sum pi (c+Lnext) <= sum pi (c+V_{t+1})`.
Taking `pi` optimal for `c+V_{t+1}` and minimising the left side over coarse-feasible gamma gives
`OT_coarse(m) <= V_t(x,y)`.

**L2 (proportional lift is an upper bound).** For any coarse-feasible gamma, `pi_ij = gamma_AB (a_i/a_A)(b_j/b_B)`
on `A x B` has marginals a and b (omit zero-mass blocks). If `Unext >= V_{t+1}` pointwise is the cost of
*some* admissible continuation at each successor pair and `u_AB >= c_{t+1}(i,j) + Unext(i,j)` on `A x B`,
then `V_t(x,y) <= sum pi (c+V_{t+1}) <= sum pi (c+Unext) <= sum gamma u`. Because bicausal policies are
defined node-locally, mixing witnesses across distinct successor pairs is admissible: the retained
pointwise minimum of previously valid uppers is still realised by one admissible policy.

**L3 (one-sided reachability envelope is valid).** Let `ell^X_{t,s}(i)`, `h^X_{t,s}(i)` be the min/max
representative reachable at time s from state i at time t over positive kernel edges, and let
`I^X_s(A)` be the union interval over `i in A`. Under *any* admissible policy, `X_s in I^X_s(A)` and
`Y_s in I^Y_s(B)` almost surely, so `|X_s - Y_s|` lies in `[d_min, d_max]` of the two intervals pointwise.
Summing `s = t+1..T` and taking expectations,

    E_lo(A,B) = sum_s d_min(I^X_s(A), I^Y_s(B))^p  <=  c+V  <=  sum_s d_max(...)^p = E_hi(A,B)

throughout `A x B`, for both p=1 and p=2, with no cross-process information used. The upper side
additionally bounds *every* admissible policy, so the independent-transition policy is an immediate
witness.

**Numerical check.** On all 48 development cells (2 seeds x 2 process families x 2 costs x k in {1,2}
x delta in {0.5,0.3,0.18}, T=4, 24 paths per side) I computed the exact `V_t` tables and the singleton
envelopes and checked enclosure at every state pair of every layer. Maximum violation:
`1.4e-14` on the lower side, `7.1e-15` on the upper side — floating-point noise. **The lemmas hold.**

## 3. Does H-B certify at the root, or only at a perturbed node? (mandatory check)

The concern is real and general: a bound computed at a node against an *approximate* future value
certifies a perturbed problem, not the original one. H-B avoids this, but for a reason its card does
not state.

The correct argument is **monotone-operator induction, not local bounding**. Define the relaxed maps
`T_L` (block-min costs) and `T_U` (block-max costs with the proportional lift). L1/L2 say
`T_L W <= T W <= T_U W'` whenever `W <= V <= W'` pointwise; L3 provides the base envelopes; and
`T`, `T_L`, `T_U` are monotone in their cost argument (OT is monotone in the cost matrix, and
`OT(M + const) = OT(M) + const`). Starting from `L_T = U_T = V_T = 0` and applying the maps backward,
`L_t <= V_t <= U_t` at every layer and hence `L_root <= R <= U_root`. Validity is inherited from the
terminal layer upward — it is never asserted at an isolated node.

This works only under three invariants, and **H-B's `lemma_or_invariant` field states none of them**.
They must be added to the preregistration and made assertable in the verifier:

- **I1 (total pointwise validity).** At every refinement step, the continuation bound used at a parent
  must be valid at *every* positive-probability successor pair in the rectangle, including pairs never
  visited. In the top-down algorithm this holds because unvisited pairs carry the L3 envelope; an
  implementation that defaults an unvisited pair to a cached sibling value, a sampled entry, or zero
  breaks the induction silently and certifies a perturbed problem. Assert: no rectangle is priced
  without an envelope covering its whole support.
- **I2 (do not mix bound targets).** The L3 envelope and the conditional-mean refinement bound both
  bound `c+V` directly. The recursive block bound bounds `c + Lnext` for one specific `Lnext`. Their
  pointwise **maximum is valid** (both bound `c+V`); substituting one for the other inside a rectangle
  minimum is not. `research/theory/block_bounds_review.md` §4 flags this; the hypothesis card does not.
- **I3 (monotone retention).** Keeping the max of previously valid lowers and the min of previously
  valid uppers is safe even when ancestors are stale, because a stale bound is still a valid bound.
  Staleness therefore cannot break correctness — but it does inflate the reported width, so the
  ancestor re-solve after each refinement is a *cost* item, not a correctness item (see §5).

**Conclusion of the mandatory check: H-B does the right thing at the right place, structurally.** The
root propagation is sound. The exposure is implementational, and I1-I3 are the exact assertions that
close it.

## 4. The counterexample: it is quantitative, and it is against the performance claim

I have no counterexample to the lemmas. I have a measured counterexample to the premise that
rectangles can stay unexpanded. Three independent measurements, all on the registered development
grid, all reproducible from the scripts in §8.

**New lemma (frontier accumulation), which is what makes this decisive.** Let `w*` be the occupation
measure of the exact optimal bicausal coupling and `F` a cut of the pair tree at which the algorithm
stops recursing and uses envelopes. Since `V_t - L_t >= E_{pi*}[V_{t+1} - L_{t+1}]` (take `pi*` optimal
for `V`; it is feasible for the `L` problem), unrolling from the root gives

    R - L_root      >=  sum_{node in F} w*(node) * (V - E_lo)(node)
    U_root - R      >=  sum_{node in F} w^U(node) * (E_hi - V)(node)

Local slacks therefore **add up under the occupation measure**; they do not average out and they are
not discounted by depth. A root certificate of width `eps*R` forces the occupation-weighted sum of
retained local slacks below `eps*R` across the entire frontier. Checked numerically at every cut of 16
cells: **64/64 checks satisfied, 0 violations.**

**(a) The envelope alone is vacuous.** With one block per side, the reachable ranges of the two
processes overlap at every future time, so `d_min = 0` and `L_root = 0` in 48/48 cells — the relative
criterion is undefined and the stopping rule cannot even be evaluated. `U_root/R` ranged from 6.2x
(absolute cost) to 25.6x (squared cost) on the 16 cells spot-checked.

**(b) Truncating the recursion anywhere breaks the tolerance.** Replacing exact recursion by the
singleton envelope at only the *terminal-adjacent* layer already leaves root relative width at median
0.53 and up to 3.44, against the required 0.005; only **2/48** cells pass. Truncating two layers deep:
**0/48** pass, relative width 0.031 to 26.7. Full exact recursion: 48/48, by construction. Note this is
the *best case* for the mechanism — singleton blocks and the true `V` below the cut; any real hierarchy
with non-singleton blocks is strictly looser.

**(c) How much occupation mass can the envelope actually serve?** For each layer I spent the *entire*
root budget `eps*R` on that layer alone and greedily admitted the smallest-gap nodes first. The fraction
of optimal-coupling mass that may remain coarse (median over 24 cells per k, layers 1/2/3):

| | layer 1 | layer 2 | layer 3 (terminal-adjacent) |
|---|---|---|---|
| **k = 1** | 0.000 (max 0.125) | 0.049 (max 0.149) | 0.215 (max 0.434) |
| **k = 2** | 0.167 | 0.713 | 0.868 |

The occupation-weighted lower gap in units of the whole budget is 140-186x at layer 1 for k=1
(median 168), 77-142x at layer 2, 31-69x at layer 3. **At k=1 — which `objective.json` requires — there
is no headroom above the terminal-adjacent layer.** Since these per-layer figures each consume the full
budget, any joint frontier gets strictly less than the single best entry.

**(d) The k=2 headroom is confounded by sample degeneracy.** The layer-1 servable mass correlates
**r = 0.788** with the fraction of empirical states having out-degree 1. Mean out-degree-1 fraction is
0.39 at k=1 and 0.60 at k=2; in the cells where the envelope works best (k=2, delta in {0.3, 0.18}) the
kernels at layers 2-3 have out-degree exactly 1.00 — the "model" is 24 deterministic paths. For a
deterministic-future pair the reachability intervals are single points, so `d_min = d_max` and the
envelope is *exactly* the pathwise cost, for free. That is a property of 24 sample paths at a fine
grid, not of a temporal mechanism, and it will get **more** extreme at T=50 with a fixed path count.
The hypothesis's ablation list separates static terminal-cost pruning and permuted hierarchies but has
**no degeneracy control**, so as written the probe cannot tell the mechanism from sample sparsity.

Taken together: on this grid, the registered prediction "in EACH of 24 groups the two-seed median
omits at least 10% of distinct nonterminal fine continuation entries while reaching root relative
width <= 0.5%" is very likely to fail at k=1 on structural grounds, and where it passes at k=2 it is
likely to be attributable to out-degree-1 degeneracy rather than to temporal envelopes.

## 5. Does the envelope hide dense work? (mandatory cost question)

**Answer in two parts, and the second part is the one that matters.**

**(i) Constructing the envelope does NOT require rescanning all state pairs.** The reachability arrays
are one-sided. Backward propagation over positive kernel edges costs

    sum_t nnz(P_t)*(T-t)  +  sum_t nnz(Q_t)*(T-t)   =   O( T * sum_t nnz(P_t) + T * sum_t nnz(Q_t) )

which for an empirical model built from N paths is `O(T^2 N)` per side; storage is
`O( sum_t (T-t+1)(|X_t|+|Y_t|) ) = O(T^2 N)`; each rectangle query is `O(T-t)` interval operations.
The cross product `X_t x Y_t` is never touched. This is a genuine asymptotic separation from the
exhaustive DP, which needs `sum_t |X_t||Y_t|` transport subproblems and `sum_t nnz(P_t) nnz(Q_t)`
arc variables. **But it is not free, and against the current adapter it is not even small:**
`common_model.py` stores dense kernel tables, so merely locating positive entries costs
`Theta( sum_t |X_t||X_{t+1}| + |Y_t||Y_{t+1}| )`. Measured per cell (median over 48):
sparse edge operations **377**; dense positive-entry scan **1888**; exhaustive-DP arc variables
**1788**; exhaustive-DP pair solves **854**. Against the adapter as it stands the preprocessing scan
is ~1.06x the entire DP arc count. The card's `cost_accounting` field lists reachability edge
operations but not this dense-to-sparse conversion scan; the review text notes it, the card must too.

**(ii) A block bound tight enough to be useful DOES require the dense scan.** This is the real
dichotomy and it is not resolved anywhere in the H-B material:

- Price a rectangle from the L3 envelope: cost `O(T-t)`, no cross scan — and, by §4, slack 31x to 186x
  the entire root budget at k=1, so the rectangle must be refined anyway.
- Price it by the true rectangle minimum of `c + Lnext`: tight — and computing that minimum reads every
  fine entry of the rectangle, which is precisely the work the hypothesis claims to omit.

The only regime in which both hold is a rectangle whose members have structurally identical (or
interval-identical) futures — duplicated deterministic futures, or the out-degree-1 states of §4(d).
**So the honest formulation of H-B's mechanism is not "temporal envelopes avoid cross-time work"; it is
"exact duplication of conditional futures avoids cross-time work".** That is a much narrower claim,
it is testable directly, and it should be the registered claim.

**Cost of detection and certification, in subproblems.**

- Exhaustive DP: `sum_t |X_t||Y_t|` pair OT solves + 1 root solve (median 854+1 per cell here);
  `sum_t nnz(P_t) nnz(Q_t)` arc variables (median 1788).
- H-B: **two** coarse OT solves (lower and upper) per visited node **per refinement round**, plus one
  recursive descent per singleton pair it must resolve, plus hierarchy construction
  `O(sum_t (|X_t| log|X_t| + |Y_t| log|Y_t|))`. Given §4(c), at k=1 essentially every positive-mass pair
  is visited, so H-B pays **>= 2x the DP's subproblem count** before any saving.
- **Refinement-schedule term, unregistered and potentially fatal to the arc criterion.** Refining a node
  with degrees n x n by doubling both cuts each round costs `1 + 4 + ... + n^2 ~ (4/3) n^2` arc
  variables — a 33% overhead over the DP's `n^2`. Refining **one block at a time** and re-solving, which
  is what §5 step 2 of the review describes, costs up to `Theta(n^3)` arc variables at that node. The
  registered criterion "total candidate transport arc variables do not exceed memoized exhaustive DP"
  is therefore schedule-dependent, and the schedule is not registered.
- **Ancestor re-solve term, not in the cost accounting at all.** Step 2 recomputes valid ancestor
  intervals after each refinement: `O(depth)` coarse re-solves per refinement, so `O(R_refinements * T)`
  extra transport solves. At T=50 this term alone can dominate.

## 6. What this review establishes and what it does not

**Established.** The block lower bound (L1), the conditional-proportion lift (L2) and the one-sided
reachability envelope (L3) are correct, and enclosure holds numerically to 1e-14 on all 48 development
cells. Root propagation is sound as monotone-operator induction; invariants I1-I3 are the assertions
that make it auditable. The frontier accumulation lemma is proved and verified 64/64. Envelope
construction is one-sided and needs no cross-process rescan.

**Not established (and, on this grid, contradicted).** That the envelope is tight enough for any
positive-mass rectangle above the terminal-adjacent layer to stay unexpanded at eps=0.005. That the
k=2 headroom is a temporal effect rather than out-degree-1 degeneracy. That the total arc-variable
count can stay under exhaustive DP under any registered refinement schedule. Nothing here concerns
T=50, population targets, novelty, or speed; the reviewer-side audit is post-hoc and cannot be
promoted to registered evidence.

## 7. Decision and the cheapest probe that settles it

**`revise`.** Required before any hierarchy implementation is registered:

1. Add invariants I1-I3 to `lemma_or_invariant` and to the verifier's assertion list.
2. Add the frontier-budget gate as an explicit falsifier: the occupation-weighted retained slack must
   be below `eps*R`, reported per layer.
3. Add a **degeneracy control** to the ablation list: report the out-degree distribution and the
   fraction of state pairs with zero envelope slack, and recompute every omission statistic with
   out-degree-1 states excluded. No omission percentage may be credited without it.
4. Register the refinement schedule and add ancestor re-solves and the dense-to-sparse conversion scan
   to `cost_accounting`.
5. Restate the mechanism as duplication-of-conditional-futures (see §5(ii)) if it is to survive at all.

**Cheapest arbitrating probe (Probe C1, "envelope headroom audit").** It settles the question without
implementing the hierarchy, the coarse LPs, the priority queue or the fallback, because it computes an
*upper bound on the tightness any block scheme can achieve*: singleton blocks with the true `V` below the
cut dominate every coarser partition. Per group (24 groups x 2 seeds, T=4, the registered development
grid):

1. build the two models; run `exact_dp` while retaining all `V_t` and the optimal plans;
2. compute the one-sided reachability arrays and the singleton envelopes `E_lo`, `E_hi`;
3. **validity gate:** assert `E_lo <= V_t <= E_hi` at every pair of every layer;
4. propagate the optimal-coupling occupation `w*` from the root;
5. report, per layer, the maximum occupation mass admissible coarse within the full budget `eps*R`
   (greedy on `V - E_lo`), together with the out-degree-1 fraction and the zero-slack fraction.

**Pass condition, to be frozen before the run:** in every one of the 24 groups, at some layer
`t <= T-2`, at least 10% of the optimal-coupling occupation mass is servable by the envelope within
`eps*R`, **and** that headroom survives excluding out-degree-1 states. Failure at k=1 alone is
sufficient to classify H-B `performance_prediction_falsified` without writing the solver.
Cost: ~31 s single-core for all 48 cells, ~200 lines, no new solver, no new dependency. My own run of
exactly this audit (post-hoc, §4) fails the condition at k=1 in every group.

## 8. Reproduction

Reviewer-side scripts, saved as session artifacts, not committed to the repo:
`audit.py` (validity, uniform-truncation root intervals, per-layer occupation-weighted gaps,
degeneracy), `audit2.py` (servable-mass greedy, cost accounting), `check_frontier.py` (frontier lemma,
64 checks). They import `adapters/common_model.py` read-only with bytecode writing disabled and write
nothing into the repository. Generators were reconstructed from the H-B card text; the exact seeding
convention used by H-A was not available to me, so state counts may differ from the registered runs
while the structural findings (`d_min = 0` under overlapping ranges, out-degree-1 degeneracy) do not
depend on it.

---

## 9. Robustness under the design frozen mid-review (added after §1-§8)

`frozen_design.json` and `generators.py` were committed by the root session at 12:30, while this
review was in progress. They **supersede the generators written into the H-B card** and they differ in
the one dimension that drives my §4(d) confound:

| | H-B card screen | frozen design |
|---|---|---|
| second family | `X_t = .25X_{t-1} + .7 sin(2X_{t-2}) + eps` | `X_{t+1} = .55X_t + .95 sin(1.7X_t) - .45(X_t - X_{t-1}) + .7 eps` |
| paths per side | 24 | 4000 / 6000 / 8000 by delta |
| seeds | 20260909, 20260910 | development 1000-1004, confirmation 2000-2004 |
| T | 4 | 50 |

I re-ran the audit under the frozen laws at 4000 paths per side, T reduced to 4 so that the exact-DP
reference stays computable. **Declared assumption:** `frozen_design.json` does not state the two-sided
convention, so I took both sides as independent samples of the same frozen family under paired seeds
1000 / 1001. All k=2 cells were skipped: at the frozen path counts the exact-DP reference needs
11,440 to 637,446 state pairs even at T=4, which is beyond a review-side budget. The k=1 results
below are therefore the load-bearing ones and the k=2 behaviour is untested under the frozen laws.

**Every finding of §4 survives, and the margins widen:**

- The degeneracy that flattered the 24-path screen is gone: out-degree-1 fraction falls from 0.39-0.60
  to **0.06-0.10**, mean out-degree rises to **8.7-22.6**. This confirms §4(d) as a criticism of the
  *screen*, not of the model: the H-B card's 24 paths per side is not a scaled-down version of the
  frozen design in the dimension that matters, and it is biased in the mechanism's favour.
- Servable occupation mass within the full root budget is **0.000 at layer 1 and 0.000 at layer 2 in
  every k=1 cell** (layer 3 reaches at most 0.109). Under the frozen laws the envelope has no headroom
  anywhere above the terminal-adjacent layer.
- The occupation-weighted layer-1 gap is a uniform **190x to 196x** the entire root budget across all
  12 k=1 cells, both costs, both families.
- Replacing recursion by the envelope at only the terminal-adjacent layer gives root relative width
  **13.3 to 219**, against the required 0.005. The pure envelope again gives `L_root = 0` everywhere.

**One new question for the root, not a finding.** Under my same-family reading of the frozen design,
`R` falls to 0.23-0.63 (versus 3.1-7.2 on the card's screen with two different laws), because both
sides sample the same process. A small `R` shrinks the absolute budget `eps*R` and pushes the setup
toward the card's own declared `inconclusive` hazard, "relative width undefined because the exact
target is zero". If the intended convention is two *different* laws per cell, that should be written
into `frozen_design.json` before any relative-certificate run; if it is the same law, the absolute-gap
fallback needs registering now. This is a design-freeze gap, not evidence about H-B.
