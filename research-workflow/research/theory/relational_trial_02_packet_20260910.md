# Trial 02: causal prefix overlap and an order-preservation condition

2026-09-10. User has selected **mathematical conditional order preservation** and
authorized continued PO decisions. Query-triplet comparisons are a minimal
diagnostic unit, not an imposed top-K product. No statistical-guarantee pivot,
mandatory full ordering, or fallback requirement. This is a bounded mathematical
baseline/proof check, not a registered performance experiment or claimed novelty.

## Question and investment gate

Can a common tree cheaply respect bicausality and support a checkable sufficient
ordering condition for the original numeric cost? Review correctness, nearest
prior art and representation cost BEFORE building a candidate solver. A known
formula plus elementary bounds can be retained as a baseline but cannot pass the
scientific-significance gate alone.

## Statement A: bicausal transport with a common prefix-tree ground cost

Finite equal-length paths, common fixed time zero, own natural prefix filtrations.
Union prefix tree, nonnegative edge weights w_h. Let mu_h,nu_h be prefix masses
and p_h=mu_h/mu_parent, q_h=nu_h/nu_parent at positive parent masses. Set

    m_empty=1; m_h=m_parent*min(p_h,q_h).
    S_bc(mu,nu)=sum_{h nonempty} w_h*(mu_h+nu_h-2*m_h).

If a parent has zero mass on either side, m_h=0 for every descendant regardless
of the arbitrary conditional version there. Duplicated observed paths are first
aggregated into leaf probabilities. This is a formula for the tree PATH ground
cost, not ordinary tree OT and not automatically the numeric reference cost.

Proof candidate: for every bicausal coupling, the probability of both prefixes
equal to h is at most m_parent*min(p_h,q_h), hence at most m_h inductively.
At each equal-prefix state, choose a maximal diagonal coupling of its conditional
rows. Set diagonal mass min(p_h,q_h) on every shared child and couple leftover
mass arbitrarily (residual positive supports are disjoint). At unequal-prefix
states any conditional coupling is allowed, since prefixes cannot reunite.
This feasible bicausal policy attains all m_h simultaneously. The cost of crossing
edge h is mu_h+nu_h-2*pi(both prefixes h). Nonnegative weights yield the formula.

Ordinary tree-Wasserstein replaces m_h by min(mu_h,nu_h); that substitution can
be strictly optimistic. Trial 01's U,V fixture has S_ordinary=2, S_bc=5/2.

Independent reviewer has already identified direct overlap with Beiglbock--Zona,
*Pinsker's inequality for adapted total variation*, arXiv:2506.22106, Lemma 2.1.
The overlap/closed-form construction is not proposed as a novel theorem. Full
review will specify conventions and depth/node-weight corollaries.

## Statement B: useful order only after bridging the numeric geometry

Let c(x,y)=sum_t |x_t-y_t|^p for a fixed p in {1,2}, the original finite-model
cost. If a verified, cheaply obtained E(mu,nu) satisfies |c-d_tree|<=E uniformly
on the two supports, then |D_c-S_bc|<=E (same feasible bicausal couplings).
Consequently S_bc(Q,A)+E(Q,A)<S_bc(Q,B)-E(Q,B) preserves the strict order.
This is standard perturbation plus interval separation, NOT new contribution.
Computing E by enumerating all path pairs is not an acceptable free oracle.

A concrete conservative bridge avoids that enumeration. For each time t, obtain
global coordinate extrema over the ONE fixture/database collection, including
the declared query regime. Set C_t=(max_t-min_t)^p and all tree edges at depth t
to w_t=C_t/2. Since c's stage cost is zero before first unequal prefix and is
at most C_t afterward, pointwise c<=d_tree. Therefore

    D_c(mu,nu) <= U_tree(mu,nu)=sum_t C_t*(1-A_t),
    A_t=sum_{h at depth t} m_h.

L_marg(mu,nu)=sum_t W_p^p(mu_t,nu_t) <= D_c(mu,nu), since every joint process
coupling induces a coupling of each pair of one-time marginals. Scalar W_p^p is
computed by sorted quantile matching. Thus

    U_tree(Q,A) < L_marg(Q,B)  =>  D_c(Q,A) < D_c(Q,B).

The condition is sufficient only; failure means unresolved, not reversed.
Zero weights give a pseudometric, which is adequate for the nonnegative-cost
argument. The bounds need rigorous arithmetic for asserted decisions; rational
toy checks below do not turn arbitrary floating inputs into certificates.

This common geometry range bound may be too loose. Adaptive per-pair ranges are
also valid bounds but cease to be a single shared metric; do not silently claim
one common representation when weights depend on the compared pair.

## Statement C: representation and cost are part of the claim

For an explicit prefix trie, prefix overlaps cost linear work in traversed nodes
and intersected child supports. Full expansion of an empirical k-window Markov
law may generate exponentially many recombined paths; its raw input-path trie
generally represents a DIFFERENT law. It is not a legitimate cheap replacement.

For depth-only weights, avoid expansion using a common alphabet of cell labels
and compatible k-window states. Let m_0 be the matched initial-state mass and

    m_{t+1}(s')=sum_s m_t(s)*min(P_t(s,s'),Q_t(s,s')),
    A_t=sum_s m_t(s).

Here state s is the same window in both laws and m_t aggregates ONLY histories
that have agreed at every preceding time; it is not arbitrary probability of
equal current states. This distinction matters when diverged paths return to
the same k-window. Missing states/edges have zero overlap. Kernels and labels
must use the same grid/state encoding. Ordinary one-sided marginal forward
passes provide mu_t,nu_t for L_marg. No cross-process continuation table is
needed. Preprocess label alignment once; charge kernel reads, alignment, sorting,
prefix representation construction if used, and all marginal computation.

General arbitrary-prefix weights may defeat this compact aggregation. The
complexity assertion is restricted to weights representable from depth/state or
transition information along the still-agreed histories.

## Planned proof checks, not held-out performance evidence

Use exact Fractions on two small families, then no grid:

1. Reproduce Trial 01 same-tree ordinary=2 versus bicausal=5/2 and compare the
   new prefix formula with its independent affine-coupling reference.
2. Check all ordered pairs in Trial 01's Q,B,C_low,C_high collection under a
   single tree: formula equals exact bicausal tree-cost LP; L_marg<=D_c<=U_tree
   for absolute/squared cost. Count nothing as statistical coverage.
3. A separated-support sanity fixture demonstrating nonvacuity: Q has terminal
   values {0,1}; A has probabilities {3/4,1/4} on those same terminal values;
   B has terminal values {3,4}, with common zero first coordinate. Under common
   C_2=4 (absolute), U_tree(Q,A)=1 < L_marg(Q,B)=3. This proves the rule can
   fire; it is a one-stage embedding, not a hard temporal contribution.
4. Demonstrate the numeric-distortion limit: two deterministic trajectories
   (0,0) and (epsilon,0) have D=epsilon yet a unit-edge prefix score of 4.
   No uniform multiplicative bridge for that fixed trie as epsilon decreases.

Stop/promotion policy: if A/B/C are correct but elementary prior-art consequences,
retain a baseline and do NOT promote a new algorithm or claim SOTA. A new
geometry/conditional mechanism requires a separate claim and discriminator.
Useful next decision is whether to fund such a mechanism, not whether another
page of closed-form algebra can be produced.
