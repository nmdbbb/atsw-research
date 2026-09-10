# Geometry condition screen 01: common regeneration blocks

Status: diagnostic complete, independent review pending. Task `geometry_condition_screen_01`, 2026-09-10.
One construction reserved; no numerical benchmark or hypothesis preregistration.

## Decision and target

Can a cheaply verified common deterministic reset of the complete k-window state
remove the artificial persistent penalty of prefix disagreement, and is the
remaining contribution substantive enough for a probe? Target stays finite-model
bicausal value D=AW_p^p, p=1 or 2, same time/cost/grid convention per comparison.

Construction: partition all compared laws at common, fixed deterministic reset
states of the full Markov window. Restart prefix agreement at these times and
use the retained range-weighted tree bound independently per block. This changes
one irreversible prefix tree into a common forest of blocks. Equality of just the
current coordinate is insufficient for k>1; small probability of another state
does not certify an exact reset. Detect resets from model state marginals, not
population generator coefficients. The forest and depth ranges are common to
the declared database/query collection.

Planned discriminator: two unequal early information patterns, two deterministic
zero steps (full k=2 reset), then a common large random excursion returning near
the other process. A third law shifts the excursion by a small constant. Compare
reset bound versus the already retained non-reset prefix/range bound, and exact
analytically attainable adapted values. Nonzero conditional penalty in the first
block prevents this from being a terminal-only fixture.

Provisional reasoning: deterministic full-state resets remove dependence of each
law's future on its own past in the declared Markov representation. Concatenating
blockwise feasible bicausal couplings therefore gives a globally feasible coupling.
Within each block the established maximal-prefix-agreement policy bounds additive
numeric cost by the range at each depth times disagreement probability. This is
expected to be a compositional baseline, not a novel theorem.

## Precise condition and bound

Finite time-inhomogeneous Markov laws on aligned k-window states, fixed common
initial state, nonnegative additive numeric stage cost |x_t-y_t|^p. All positive
mass states/edges are retained. A common deterministic time tau is admissible
when every law's entire state distribution at tau is the same Dirac mass.
These times and the coordinate ranges C_t=(max x_t-min x_t)^p are computed over
one declared collection. No exact OT values or unobserved generator parameters
enter the test. State-marginal propagation and equality tests must be exact or
rigorously certified; a floating tolerance cannot manufacture a reset.

Within a block starting at a reset, initialize r at that common state with mass
one, then propagate r_{t+1}(s')=sum_s r_t(s) min(P_t(s,s'),Q_t(s,s')). Let A_t
be its total mass. At each next reset, after charging that time's (zero) stage
cost, replace r with mass one at the common state. Define

    U_reset(P,Q) = sum_t C_t (1-A_t).
    L_marg(P,Q) = sum_t W_p^p(P_t,Q_t).
    L_marg <= D <= U_reset <= U_unbroken_prefix.
    U_reset(Q,A) < L_marg(Q,B) implies D(Q,A) < D(Q,B).

Proof of the upper: in each block use a sequential coupling that maximizes each
shared-child diagonal mass as long as the block prefixes agree; after divergence
choose any feasible conditional coupling. It attains the stated agreement
recursion. Numeric cost is zero on equal block prefixes and at most C_t
otherwise. At the reset, the full states agree surely, and each law's subsequent
kernels depend only on the state and time, so concatenating these block policies
has the required conditional marginals at every paired history: it is bicausal.
Its expected cost is at most U_reset, which bounds the infimum D. The marginal
lower bound follows because every feasible process coupling induces each
one-time coupling. Resetting adds nonnegative mass to r relative to the unbroken
recursion; monotonicity of its nonnegative transition operator gives the final
inequality. Interval separation is sufficient; failure remains unresolved.

This proof asserts a feasible upper, not optimality of maximal numeric agreement
or a general additive decomposition theorem. Blocks form a common forest rather
than one unchanged full-prefix metric; disclose that representation change.
Deterministic full-state reset is sufficient, not necessary. Merely close states,
random meetings or equal current coordinates are outside this argument.

## Exact discriminator and independent reference route

Let J,H be independent fair bits in each law. Include deterministic time zero.
The six following coordinates are:

    Q = (0,   J/4, 0, 0, 4H,       -4H)
    A = (J/8, J/4, 0, 0, 4H,       -4H)
    B = (0,   J/4, 0, 0, 4H+1/4,   -4H+1/4).

Four equally weighted paths per law. The first block of A reveals J at time 1;
Q reveals it at time 2. Bicausality forces these early Q/A bits to be independent,
giving D(Q,A)=3/16 (p=1) and 5/128 (p=2). Identical later blocks can be coupled
at zero cost independently of the early choices. For Q/B, the marginal lower
bound 2*(1/4)^p is attained by identical early bits and a translated common tail
bit, so D(Q,B)=1/2 and 1/8 respectively. Thus the near pair has a genuine causal
penalty beyond its marginal bound (1/16 and 1/128); this is not terminal-only.

All coordinates are multiples of 1/8. Under the repo's grid delta=1/8,
shift=-1/16, cell centers equal these coordinates. For k=1 and k=2 the fitted
finite-window transition law equals the displayed full-path law: the early
conditional laws fit these windows, two zero steps erase the whole k=2 window,
and H is independent of the early bit. The exact checker reconstructs these
laws from weighted window counts and checks equality. No claim about arbitrary
path data, other grids, population processes or T50 follows.

The checker computes adapted reference values by full-prefix backward recursion
using exact endpoints of each 2x2 transport polytope, with no reset shortcut.
The candidate uses forward window-state agreement propagation. These are two
different calculation routes, plus the analytic attaining couplings above.

| Cost | Exact near | Old near upper | Reset near upper | Far marginal lower = exact far |
|---|---:|---:|---:|---:|
| absolute | 3/16 | 53/8 | 1/4 | 1/2 |
| squared | 5/128 | 3475/128 | 7/128 | 1/8 |

Both k values give this table. For k=1, times 3 and 4 are admissible; for k=2,
only time 4 is detected. Time 3's common coordinate does not certify a full
window reset. All four deterministic checks resolve the comparison where the
unbroken bound fails. These four checks are not independent data samples or a
coverage estimate. The intentionally large tail inflates the old bound; this
does not establish superiority to an eligible adapted-OT competitor.

## Charged work and scientific-weight gate

| Work | Candidate requirement / what remains unmeasured |
|---|---|
| Build model, align labels | Must be charged from paths; k-window fitting and sparse indices are not free |
| Detect common resets and ranges | One-sided marginal propagation and support scan, O(sum E_i + sum S_i) arithmetic with existing sparse kernels |
| Pair upper | O(E_P+E_Q) upper estimate with aligned sparse rows, no full-history expansion or cross-state continuation table; same order as retained agreement baseline |
| Pair lower | Sorted one-dimensional marginal transport, charge sorting/matching unless cached |
| Exact arithmetic | Operation counts omit numerator/denominator bit growth; no float production certificate implemented |
| Toy count | Both old and reset routines visit 8 matched edges; no measured runtime advantage. Both bounds use zero local OT solves |
| Reference | Full-prefix enumeration and small exact OT belong solely to this diagnostic evaluator, not the proposed input test |

The newly resolved decision can avoid asking an exact reference in this fixture,
but no production fallback workload or end-to-end speedup was measured. Existing
exact-future reuse or elementary common-tail elimination is an obvious comparator.
The improvement over the deliberately coarse retained bound is not enough for
the scientific-significance gate.

## Source check and provisional PO conclusion

[Beiglbock--Zona, arXiv:2506.22106v1, equation (2.1) and Lemma 2.1](https://arxiv.org/html/2506.22106v1)
give the sequential conditional-coupling characterization and iterated maximal
agreement used here. Reopened the relevant full-text sections this turn.
[Moulos, Markovian Couplings and Theorem 1](https://arxiv.org/html/2010.06831)
provides explicit prior art for the Markov coupling/DP viewpoint; its stationary
setting is not cited as a theorem covering our finite inhomogeneous reset bound.
The reset concatenation and range inequality above are our elementary derivation,
not a claim that either source states this exact combined formula. This targeted
overlap check is not an exhaustive novelty survey.

Provisional decision: keep a scoped reset-block baseline and stop investment in
this construction as a central contribution. It passes a nontrivial conditional
fixture but supplies no demonstrated new principle beyond known feasible coupling
and a strong exact-regeneration assumption. No grid, production kernel or registered
probe is warranted. The next architectural question, if user continues, is whether
cheap input-verifiable *approximate* future alignment can replace exact resets
without losing a useful bound or requiring dense OT. That question is not answered
by this screen; no budget for an implementation is implied.

Artifacts: [checker](../../tools/check_geometry_condition_screen_01.py),
[exact output](geometry_condition_screen_01_checks.json). Review and final verdict
will be linked here; no final independent sign-off is claimed yet.
