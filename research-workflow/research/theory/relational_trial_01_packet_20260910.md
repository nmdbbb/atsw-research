# Trial 01: can a common prefix tree preserve adapted-OT ordering?

Date: 2026-09-10. Base HEAD: `3a6a1c7`. This is ONE bounded trial of the v3
workflow, explicitly requested after the user corrected premature scope adoption.
V3's top-K and deterministic-guarantee choices are provisional assumptions for
review, not newly confirmed user requirements. Do not revise the contract in this
trial. No learned method, performance grid or statistical correlation claim.

## Decision and scientific-weight question

Would the literal common-trie construction already give guaranteed proximity
ordering, and what information would a stronger construction need? If it does not,
stop investment in THIS guarantee, not in shared trees or empirical/statistical
ranking. A refutation of this elementary baseline is a diagnostic, not a novel
limitation paper. A cheap proof check is justified as a scope/representation test,
not promoted to a candidate scientific contribution.

## One concrete interpretation (not every possible edit-weighted tree)

Two noninitial time points; all paths have a common deterministic time zero,
omitted from notation and from cost. Build a trie of the union of observed paths.
Equal numeric prefixes share nodes. Every append edge has unit cost; the
generalization below uses positive depth weights w1,w2. Put each process's path
probabilities on leaves, compute

    S(A,B) = sum_edges weight(e) * abs(A(subtree_e)-B(subtree_e)).

This is ordinary tree-Wasserstein, not an enforced bicausal optimization. Values
are reference units, not token categories; unit edit cost is one explicit choice
where appending a symbol costs one. A geometric, learned or conditional-law tree
is OUTSIDE the refuted construction. A tree is built once for the entire fixture
collection, not separately to fit each pair.

Claim tested on paper: for this construction, S(Q,A)<S(Q,B) implies
D(Q,A)<D(Q,B) for every finite two-step process, with D=AW_1. All processes below
have two equally weighted paths. Counterexamples were derived before execution;
the planned script is an exact arithmetic proof check, not blind preregistration.

## Fixture A: strict ranking inversion in a bounded numeric domain

    Q = 1/2 (0,0) + 1/2 (0,1/4)
    B = 1/2 (0,0) + 1/2 (1/8,1/4)
    C = 1/2 (0,0) + 1/2 (0,3/4)

Tree scores: S(Q,B)=2 and S(Q,C)=1. The proposed score ranks C closer.
For positive depth weights they are w1+w2 and w2, so reweighting only the
two depths does not change that ranking.

For Q versus B, the first marginal of Q is constant while B's first coordinate
reveals its terminal value. Bicausality forces the terminal value of Q to retain
its fair law conditional on either first-step state of B. The stage-1 cost is
1/16; stage-2 expected absolute cost is 1/8. Thus D(Q,B)=3/16.
For Q versus C, both first coordinates are constant; terminal monotone matching
has cost (3/4-1/4)/2=1/4. Thus D(Q,C)=1/4. The adapted ordering is the reverse.

With squared stage cost, D2(Q,B)=1/128+1/32=5/128, while D2(Q,C)=1/8;
the same score inversion persists. D2 denotes AW_2 squared, not AW_2.

These finite examples can be represented without quantization perturbation:
prepend common zero, delta=1/8, shift=-1/16, k=1 or k=2. All observations are
cell centers. Only two transitions are present, so pooled k-window laws here
match the displayed full-prefix laws. This is an analytic fixture, not evidence
on the frozen T50 generator grid.

## Fixture B: equality of a scalar tree score cannot recover the ordering

    C_low  = 1/2 (0,0) + 1/2 (0,3/8)
    C_high = C above.

On a single tree built from Q,B,C_low,C_high, both S(Q,C_low)=S(Q,C_high)=1,
but D(Q,C_low)=1/16 and D(Q,C_high)=1/4, straddling D(Q,B)=3/16.
Any fixed monotone calibration of this scalar S cannot repair the lost ordering;
in particular, equal S cannot distinguish C_low from C_high. A sound partial rule
may still abstain; this example does not refute every certified partial ordering.
This does NOT say
the full prefix-mass embedding loses all information: distinct coordinates and
numeric labels remain available to a richer method. It does not refute learning
new edge weights or using additional conditional features.

## Fixture C: changing to tree cost does not remove the bicausal issue

    U = 1/2 (0,0) + 1/2 (0,1)
    V = 1/2 (0,0) + 1/2 (1,1)

Use the SAME unit-edge trie metric as ground cost for both optimizations.
Ordinary tree OT is 2. Bicausality forces all four leaf pair masses to 1/4.
The tree cost matrix is [[0,4],[2,4]], so the constrained value is 5/2.
This diagnostic changes the ground cost solely to isolate the information
constraint; it is not a change to the primary absolute-cost reference D.

## Prior art and limits of novelty

- Takezawa, Sato, Yamada (ICML 2021), section 2.1 equation (1): tree mass-cut
  formula and fast fixed-tree comparison. The paper also learns task-specific
  tree distances. This rules out a novelty claim based only on closed form,
  shared representation or learned tree structure. Its implemented scheme fixes
  edge weights; it is not cited here as an implemented learned-edge-weight method.
  https://proceedings.mlr.press/v139/takezawa21a/takezawa21a.pdf
- Backhoff, Bartl, Beiglboeck, Wiesel, Definition 1.1 and the two-time recursion:
  adapted OT constrains couplings and accounts for information release.
  https://arxiv.org/pdf/2002.07261
- Tree-Sliced Wasserstein (2019) and UltraTWD (2025) are comparator candidates
  already identified in the preceding discussion. No full novelty sweep or
  universal statement about their adapted-OT ranking behavior is made here.

## Work table and stopping decision

| Operation | Cost/reuse | What is not established |
|---|---|---|
| Build union trie from N total paths of length T | O(NT) expected map insertions; sorting variant must charge sorting | No measured break-even |
| Build each process's subtree-mass vector | O(n_i T) insertions/accumulations before sparsity compression | No free labels or training |
| One pair's tree score | O(number of union nonzero prefix coordinates), at most tree size | No correctness bridge to D |
| All pairs of M processes | Pair count is quadratic absent a retrieval/index mechanism | A shared tree does not eliminate pair comparisons automatically |
| Exact diagnostic | Two-leaf affine transport polytope with rational arithmetic | No general solver or speed claim |
| Restoring a guarantee | New representation/lemma or charged fallback needed | Existing v2 bounds cannot be assumed cheap or tight enough |

Do not build a learned model or large benchmark if these claims fail. Preserve
the shared-tree idea as an unselected family. A next construction must explicitly
fix numeric geometry AND conditional information, then state the type of
guarantee; merely renaming the trie or fitting a scalar calibration is insufficient.

## Independent review requested

1. Check all exact values, the bicausal constraints and the common-model mapping.
2. Check whether this is a fair bounded interpretation, and prevent extrapolating
   to arbitrary edge weights, all trees or statistical ranking.
3. Review workflow v3 itself: does demanding deterministic top-K too early
   recreate the expensive solver objective? Is the significance gate being
   misused to block necessary cheap diagnostics, or to inflate this trivial result?
4. Return a decision on this construction and recommended workflow changes ONLY;
   do not change objective.json, lock, START_HERE or historical artifacts.
