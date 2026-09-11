# Shared conditional-state trees: design 01

2026-09-11. Active construction, not a novelty or performance claim.

## PO decision and authority

The user explicitly redirects work to designing/upgrading the shared tree and
its algorithm instead of continuing unrelated elimination/auxiliary lemmas.
Keep objective v3 and the selection in DECISION_ORDER_PRESERVATION_20260910.md.
Invest this cycle in one executable tree architecture. Earlier constructions
remain historical evidence, not an instruction to enumerate all possible failures.
The prior robustness task is closed. Its witness-discovery suggestion is not a
mandatory successor requirement. This document records the newer PO decision.

Budget: one design, three fixed adversarial families, at most one substantive
repair, one independent investment review. Rational finite diagnostics only;
no empirical coverage/runtime prediction, random sweep, or registered probe yet.
Root owns implementation and integration; reviewer owns only its review file.

## Intended complete algorithm and paper-level question

Build a shared representation once per batch of finite models, obtain both lower
and upper adapted-OT bounds from that representation, and assert a strict order
only on interval separation. The proposed saving is replacing all state-pair
Bellman OT solves with a linear number of tree-edge constructions at each time,
plus cheap lower features. The actual build/feature/tree traversal costs count.

The first executable version is **AW_1, absolute scalar cost**, times 1..T, on
the declared finite k-window model. It does not cover squared cost or population
AW. A meaningful restricted development claim is allowed by v3; no objective
bytes change. Candidate input is the model's states, probabilities and outputs,
never exact OT labels or generator parameters. The union includes queries:
this version is transductive batch construction, not free online insertion.

## The tree represents conditional states, not full paths

At time t pool tagged states (model ID, full k-window). Distinct model states
stay distinct even if current numeric outputs coincide. Their conditional kernels
can differ. The data structure is a shared family of trees, one per time layer;
it is not a prefix trie and does not enumerate all reconstructed full paths.
The hierarchy is by conditional geometry, while the supplied model DAG retains
temporal transitions. Tree edges describe comparison routes, not time steps or
edits. This is a deliberate upgrade of the original common support-tree idea.

For analysis define the true conditional pseudometric on the pooled layer:

    d_T(s,r) = |x_s-x_r|
    d_t(s,r) = g_t(s,r) + W_{d_{t+1}}(P_s,P_r)
    g_t = |x_s-x_r| for t>=1; g_0 = 0.

Each kernel stays inside its model's next layer. Wasserstein lifting plus the
sum of pseudometrics makes d_t a pseudometric. The root target is
W_{d_0}(initial_A,initial_B). This is exactly the finite-state Bellman target;
using full k-state observations matters. No claim about an arbitrary empirical
full-history law is substituted for the reconstructed model.

## Upper certificate: recursive tree construction

Start with a terminal chain sorted by numeric output and edge lengths equal to
absolute numeric differences. Its path metric is exactly d_T, allowing zero
length edges between duplicate outputs.

At each preceding layer choose a spanning-tree topology using current output
and conditional feature vectors described below. The initial topology uses
recursive median splitting along the feature of greatest spread; a real state
is the hub, and hub-to-child-hub links form the spanning tree. No all-pairs OT
is used to choose it. For every selected edge (s,r), set

    length_t(s,r) = g_t(s,r) + W_tree[t+1](P_s,P_r).

W_tree is computed by the subtree-mass closed form. By induction each edge
length dominates d_t(s,r). By the triangle inequality, every path distance in
the constructed tree dominates d_t. Thus

    U(A,B) = W_tree[0](initial_A,initial_B) >= D(A,B).

This does not claim a full-path ordinary tree coupling is bicausal. Tree OT is
used at one transition at a time to upper-bound the Bellman transport, and the
triangle inequality joins conditional comparisons. A numerical policy need not
be expanded to certify this inequality. Root equality on identical objects can
also use the exact identity D(A,A)=0; the raw upper need not be tight there.

## Lower certificate: a small shared bank of conditional probes

Tree lengths give upper bounds only. A lower bank is part of the algorithm,
not an optional future fix. If all f_j at t+1 are 1-Lipschitz for d_{t+1}, define

    z_s,j = E_{P_s} f_j
    ell_t(s,r) = g_t(s,r) + max_j |z_s,j-z_r,j|.

At T, ell_T is absolute numeric distance. At all earlier layers ell_t is a
pseudometric and ell_t <= d_t by the Kantorovich inequality. For each chosen
anchor a, f_a(s)=ell_t(s,a) is 1-Lipschitz for d_t: the reverse triangle
inequality for ell_t proves this. Choose a fixed small number of anchors from
the input tree hubs; no OT labels are used. Then

    L(A,B) = max_a |E_initial_A f_a - E_initial_B f_a| <= D(A,B).

Unlike only time-marginal means, these probes apply nonlinear anchor distances
to conditional expectations recursively. They can distinguish timing and
conditional laws, but a small bank can still be blind. Zero lower bounds must
remain unresolved, not be interpreted as equality. Certified decisions require
U(Q,A)<L(Q,B), retaining ties/unresolved cases honestly.

## Upgrade/refinement path within this design

The initial tree may stretch distances badly. Its edge cost is computable
without fine DP, so a local topology repair may add candidate comparison edges,
form an MST of the O(N) candidate graph, and preserve the same upper proof.
The candidate graph and number of added edges must be fixed/charged; a dense
all-pairs graph would forfeit the mechanism. A second tree can be built and
valid upper bounds minimized. Old lower features can be retained and additional
anchors maximized; blindly replacing a bank need not monotonically improve it.
These are specified successors, not yet implemented or automatically funded.
Adaptive selection based on a failed bound is allowed for deterministic
correctness, but empirical confirmation would require a frozen protocol.

## Costs and admission checks

Let N_t be the total pooled state count and E_t the total transition support.
There are N_t-1 weighted tree edges, not N_t squared local OT solves. However
one dense tree-Wasserstein traversal costs O(N_{t+1}); this first diagnostic
implementation therefore costs O(sum N_t*N_{t+1}) in this step. Merely counting
OT calls is insufficient! A sparse ancestor-aggregation implementation can
reduce a traversal to the visited ancestor union, but is not claimed as already
implemented. High-degree tree hubs can repeatedly read the same transition row.
Feature work is O(J E_t + N_t J^2) for J anchors as implemented directly.
Topology sorting, pooled model construction, exact rational bit growth, root
traversals and rebuilding after query insertion all count. No runtime advantage
is inferred from tiny fixtures or zero general LP calls.

The three fixed diagnostic families are: divergence then reconvergence; identical
time marginals with different information-release timing; genuine second-order
dependence with equal current output and opposite future kernels. Check each
interval against an independent exact finite reference, disclose unresolved
orders, inspect work and compare the information-free ablation. A failure must
locate a tree/probe/refinement issue in this architecture before considering a
different research direction. The one-repair budget prevents infinite tuning.

## Nearest work and remaining uncertainty

- Tree-Wasserstein closed form: Le et al., NeurIPS 2019, Proposition 1,
  https://papers.nips.cc/paper_files/paper/2019/file/2d36b5821f8affc6868b59dfc9af6c9f-Paper.pdf .
- Flowtree: Backurs et al., ICML 2020,
  https://proceedings.mlr.press/v119/backurs20a.html . Tree-guided ordinary OT
  is prior art; it does not itself certify the bicausal root target.
- Moulos, Bicausal Optimal Transport for Markov Chains via Dynamic Programming,
  https://arxiv.org/abs/2010.06831 . Bellman/Wasserstein lifting is prior art.
- Calo et al., Bisimulation Metrics are Optimal Transport Distances,
  https://arxiv.org/html/2406.04056 . Recursive transport metrics and their
  computation are a necessary nearest comparison, not a novelty claim here.
- Internal research/theory/notes.md H-A/H-B already proposed quotient and block
  envelopes. This construction does not require equal aggregate kernel rows or
  a global TV-times-range envelope: all states remain, O(N) conditional comparison
  edges replace their pair table. That distinction needs an investment review.

The proof ingredients are known. Scientific weight would require a useful
conditional representation/refinement mechanism with honest cost and coverage,
not a claim that this elementary induction is new. Novelty, geometric stretch,
probe blindness, long-horizon stability, and break-even against strong solvers
are open. This cycle should produce a working inspectable construction and a
specific upgrade decision, not repeat the generic statement that a gap exists.

## Version 0 observation and the one authorized repair

The fixed diagnostic at `shared_tree_design_01_checks_v0.json` used four
single-state anchors. All intervals were valid, but no query order separated.
On the genuine k=2 case, D(Q,A)=2 and D(Q,B)=1, U(Q,B)=1, yet L(Q,A)=0.
Thus this particular decision is blocked by the lower representation, not by
an exact solve or an insufficient upper witness.

There is a structural reason: on a four-corner L1 square, the uniform measures
on opposite diagonals have equal expected distance to every single corner,
although their W1 distance is positive. Adding every single-state anchor would
not fix that example. The independent reviewer identified the same mechanism.

**Repair 1, same algorithm:** retain the four anchor functions and add the
pointwise minimum for every pair of anchors (at most six more probes). A minimum
of finitely many 1-Lipschitz functions is 1-Lipschitz, so the lower certificate
is preserved. These distance-to-two-anchor-set probes can detect support patterns
that singleton distances miss. The implementation already contains this option;
the initial result used only `--bank anchors`. Activate `--bank pair_min` only
after recording this repair. No held-out or blind-confirmation claim.

The probe count increases from at most 4 to at most 10; feature construction
and tree topology can both change because they depend on the bank. Do not
attribute an observed improvement entirely to the lower bank without an ablation
holding the upper tree fixed. Finite min-pair closure is not a universal
completeness theorem. This consumes the one substantive repair allowance.

## Repair 1 result and evidence-based budget extension

The pair-min run is saved in `shared_tree_design_01_checks_v1.json`. All 18
pair intervals (three pairs in six family/k controls) enclose their exact
references. The genuine k2 decision now has U(Q,B)=1<L(Q,A)=2. Its k1 target
has all distances zero; its time marginals coincide. The frozen v0 upper plus
v1 lower gives the same decision, isolating the lower improvement logically.
Computing two banks is not free. This case alone does not discriminate ordinary
from adapted OT: those values coincide. The separate reconvergence and timing
controls do have ordinary/adapted gaps; see `shared_tree_design_01_audit.json`.

All listed v1 lower bounds happen to equal their reference values; this is a
finite diagnostic observation, not a completeness claim. The remaining strict
decisions are blocked by upper stretch: reconvergence U(Q,A)=27/16 (k1) or
35/16 (k2), versus L(Q,B)=1/2; timing k1 U(Q,A)=5/2 versus L(Q,B)=2.
The timing k2 target is an actual tie, so unresolved is appropriate.

PO reforecasts the repair budget from one to **two**, without resetting task
counters. Reason: the implemented lower repair changes the decision and locates
a concrete topology defect; the user requested upgrading this tree algorithm.
No additional family, sweep, reviewer or broad research direction is funded.

**Repair 2:** retain the median topology's candidate edges; add consecutive-node
edges from sorting each of the existing feature coordinates, including numeric
output. Deduplicate this O(JN) graph, compute its edge weights by the same
recursive tree-Wasserstein formula, and use a minimum spanning tree. This
introduces no exact Bellman labels and does not require all N squared distances.
Small layers may nevertheless become complete; disclose actual edge counts.
An MST minimizes total selected edge weight, not every query distance, so retain
the old valid root upper by taking the minimum when comparing versions, with
both build costs charged. Keep the fixed pair-min bank construction rule.

The adaptive design check is whether this recovers at least one currently
unresolved strict control and preserves the genuine-k2 certificate. It is not
an empirical coverage/speed threshold or held-out confirmation. The reviewer
independently suggested the same sparse feature-neighbor graph. After this
repair, stop further topology tuning within this cycle and issue an investment
verdict on the concrete algorithm. Probe admission remains a separate gate.

Counter limitations: reported arithmetic counters do not individually count
sorting, root feature expectations, scalar operations within a distance, pair-min
creation or rational bit growth. They expose work, not a complete runtime model.

## Repair 2 result and implementation gate

`shared_tree_design_01_checks_v2.json` records all exact intervals after the
feature-neighbor MST upgrade. Both reconvergence controls now assert A closer:
U(Q,A)=5/16<L(Q,B)=1/2. The genuine-k2 decision is retained with bounds exact
on its three pairs. Timing k1 still has U(Q,A)=5/2>=L(Q,B)=2, and timing k2 is
a true tie. These are chosen construction controls, not a measured coverage rate.
The v2 runtime still uses dense tree scans (213/273 visited nodes for the two
reconvergence controls and189 for genuine-k2). No speed claim is admitted.

The same reviewer admits implementing an exact **virtual-tree transport**
primitive: build Euler ancestry and binary-lifting LCA indexes once per tree;
for a transport query use vertices with nonzero signed mass plus their LCAs;
compress paths with constant imbalance and sum compressed edge length times
absolute subtree imbalance. Dropped off-Steiner branches have zero flow. Use
Euler ancestry, never distance equality, because zero-length edges are allowed.
Index cost O(N log N), query cost O(s log s+s log N) for signed-support size s,
plus reading both input distributions even when their difference cancels.
No Bellman value or exact label is needed. Dense equality checks are evaluator
work and must be switchable off for the candidate.

This is an implementation of the same exact primitive, not a third mathematical
or topology repair. It addresses the structural quadratic transport-build cost.
For F feature coordinates, the candidate graph has degree at most3+2F: a median
tree has degree at most3 and each sorted coordinate contributes at most2.
Therefore all edge queries together read O(F E_t) transition entries, with
transport work O(F E_t log N_next). Include root queries separately. Current
median construction sorts recursively, costing O(F N log N+N log-squared N)
as an upper bound for fixed feature width, plus feature generation, graph/MST
sorting and indexes; do not advertise a linear total algorithm. F and anchor
count are fixed in this version. Rational bit complexity remains additional.

Implementation check: dense and virtual values must agree on every queried
edge/root in the same six controls, zero imbalance, singleton tree, and zero
length edges. Store evaluator visits separately from candidate virtual visits.
No further tree tuning or benchmark is funded in this cycle.
