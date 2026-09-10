# Theory round: compressing the interaction part of the continuation

Date: 2026-09-10. Lane: theorist. This file delivers **Đầu ra 1** (candidate
mathematical statement) and **Đầu ra 3** (work table) of
[`research/theory/direction_revision_20260910.md`](research/theory/direction_revision_20260910.md).
**Đầu ra 2** (adversarial counterexamples) belongs to the independent skeptic and is
*not* delivered here; §7 is my list of what to attack.

**Headline outcome: the open lemma target FAILS on this model class.** The
Dobrushin-type route does not control the interaction part of the continuation for the
project's regime, and the failure is structural rather than statistical: the total
variation Dobrushin coefficient of the repo's `k`-window kernels is **exactly 1 by
construction** for `k >= 2`. A repaired Wasserstein-metric version is *proved* here as a
conditional theorem, but its hypothesis is refuted by the project's own frozen
generators, and even if the hypothesis were granted, the resulting bound is too wide for
the 0.5% root target. All three no-deployment conditions of the task card are triggered.
No novelty is claimed anywhere in this document.

Everything numeric quoted below is either (i) read from a bundle file, with its path
given, or (ii) computed by the toy sanity checks of Appendix A, which are labelled as
such and are **not** benchmark evidence. Nothing in `runs/` was read as an input to a
new measurement, nothing in `runs/` was written, and no grid was opened.

---

## 1. Setup and notation

Notation follows `adapters/common_model.py` exactly. The relevant functions are
`build_window_model`, `stage_cost`, `_transport_value` and `exact_dp`.

**State spaces.** `build_window_model(paths, k, delta, shift)` quantizes each scalar
observation to the cell index `floor((x - shift)/delta)` (int64) and defines the state at
time `t` as the *tuple of the last `min(k, t+1)` cell indices*. Write `X_t` for the set of
distinct left-side states at time `t` (`states[t]`) and `Y_t` for the right side. Both
sides carry their own `k`; the code permits different `k` per side and requires equal
`horizon`. `T = horizon = len(kernels)`, so paths have shape `(samples, T+1)`.

**Output map.** `representatives[t][i] = (last_cell + 0.5) * delta + shift`. Write
`r_t : X_t -> R` and `s_t : Y_t -> R`. Only the **current** coordinate of the window
reaches the cost; the older coordinates affect the transitions only. This is the property
that the H-A probe design exploits (`research/theory/notes.md`, H-A "Decisive probes":
two `k=2` windows with identical current coordinate and opposite next-state laws).

**Kernels and initial law.** `kernels[t]` is the row-normalized empirical count matrix
from `X_t` to `X_{t+1}`, for `t = 0, ..., T-1`; write `P_t(x, .)` for its rows and
`Q_t(y, .)` for the right side. `initial` is the empirical law on `X_0`, normalized by
`sample_count`; write `a_0` and `b_0`. The builder raises if a listed state has no
outgoing sample, so every row is a genuine probability vector.

**Stage cost.** `stage_cost(left, right, kind)` returns
`c_t(i, j) = |r_t(i) - s_t(j)|^p` with `p = 2` for `kind='squared'` and `p = 1` for
`kind='absolute'`. Per `objective.json:target.solver_track` the reported value is
`AW_p^p` on this finite model.

**Local transport problem.** For a probability vector `a` on a finite set, `b` on
another, and a cost matrix `M`, write

```
    T(a, b)[M] = min { <pi, M> : pi >= 0, pi 1 = a, pi^T 1 = b }.
```

`_transport_value(a, b, M)` computes this: it restricts to the strictly positive support,
renormalizes the two restricted vectors (`pa /= pa.sum()`), returns `pa @ M @ pb`
directly when either restricted support is a singleton (the "forced" case), and otherwise
solves the transportation LP with HiGHS. "Local transport problem at node `(t, x, y)`"
below always means `T(P_t(x, .), Q_t(y, .))[c_{t+1} + V_{t+1}]`.

**Backward recurrence and root.** `exact_dp` implements, with the stage cost charged at
the *successor* time and no time-zero cost:

```
    V_T(x, y) = 0                                     on X_T x Y_T
    V_t(x, y) = T(P_t(x, .), Q_t(y, .))[c_{t+1} + V_{t+1}]     t = T-1, ..., 0
    ROOT      = T(a_0, b_0)[V_0].
```

The root is a genuine transport problem on the two initial laws, not a modal-root
selection (`common_model.py` docstring: "Initial distributions are coupled by a root OT
problem; no modal root is selected").

**Exact versus floating-point.** Exact in the pipeline: the cell indices; the integer
counts behind each kernel row; the window-membership relation. Floating-point: the
representatives, every kernel entry (counts divided in float64), every stage-cost matrix,
every `V_t` table, and every value returned by `_transport_value` — including the
"forced" product formula. The renormalization inside `_transport_value` means the LP is
solved for *perturbed* marginals, by design ("Normalization corrects summation roundoff,
not missing probability mass"). The only exact-arithmetic components anywhere in the
bundle are `adapters/support_monge.py:monge_predicate` (`Fraction` on the represented
float entries) and H-A's `aggregate_exact`
(`research/theory/quotient_review_v1.md`, "Implementation audit and exactness limits").
Consequently: **no object in this pipeline is an outward-rounded certificate**, exactly as
`common_model.py` declares ("not exact arithmetic or an outward-rounded mathematical
certificate"). Every statement in §2 that says "certified" is therefore conditional on
work that does not yet exist in the repo; §2.3 says precisely what it requires.

**Interaction notation.** For a real matrix `A` on `X x Y`:

```
    (f (+) g)(x, y) = f(x) + g(y)                       additive / one-sided part
    D_A(x, x'; y, y') = A(x,y) + A(x',y') - A(x,y') - A(x',y)      second difference
    osc2(A)  = sup |D_A(x, x'; y, y')|                  interaction oscillation
    iota(A)  = inf_{f, g} ||A - f (+) g||_inf           interaction seminorm
    Lam_X(A) = max_{x, x'} max_y (A(x,y) - A(x',y)) = max_y span_x A(., y)
    Lam_Y(A) = Lam_X(A^T).
```

`osc2` and `iota` are seminorms that annihilate additive matrices; `Lam_X` annihilates
column-additive matrices `1 (+) g` but **not** `f (+) 1`, which matters in §4.1.

---

## 2. Elementary facts — declared NOT novel

Every statement in this section is textbook or already in the bundle. They are recorded
with proofs because §4 uses their exact constants.

### 2.1 Additive-split invariance

**Lemma 2.1.** Let `p, q` be probability vectors on the two supports, `f, g` arbitrary
real vectors, `M` a cost matrix. Then

```
    T(p, q)[M + f (+) g] = T(p, q)[M] + <p, f> + <q, g>,
```

and the set of optimal couplings is unchanged.

*Proof.* For any `pi` in `Pi(p, q)`, `<pi, f (+) g> = sum_{x,y} pi(x,y) (f(x) + g(y))
= <p, f> + <q, g>`, using only the two marginal constraints. Hence the objective
`pi -> <pi, M + f (+) g>` equals `pi -> <pi, M>` plus a constant that does not depend on
`pi`. Adding a constant to an objective changes neither its minimum's argmin set nor the
minimum by more than that constant. []

Consequence for the split `V_t = f_t (+) g_t + R_t`: with the marginals fixed by the two
kernels, the additive part shifts the local value by the coupling-independent amount
`<P_t(x), f_{t+1}> + <Q_t(y), g_{t+1}>` and **only** `R_{t+1}` selects the optimizer.
Verified numerically to 5.0e-16 (Appendix A, check 1). This is the invariance already
stated in the task card and is the degeneracy direction of Kantorovich duality; it is not
new.

### 2.2 Error propagation

**Lemma 2.2 (local 1-Lipschitz, monotone).** At fixed marginals,
`|T(p,q)[M] - T(p,q)[M']| <= ||M - M'||_inf`, and `M <= M'` pointwise implies
`T(p,q)[M] <= T(p,q)[M']`.

*Proof.* For any `pi` in `Pi(p,q)`, `<pi, M> <= <pi, M'> + ||M - M'||_inf` because `pi` is
a probability measure; minimize both sides over the (marginal-determined, hence common)
feasible set and symmetrize. Monotonicity is immediate from `<pi, M> <= <pi, M'>` for
every feasible `pi`. []

**Lemma 2.3 (Bellman nonexpansiveness and additive root propagation).** Define
`(B_t W)(x, y) = T(P_t(x,.), Q_t(y,.))[c_{t+1} + W]`. Then
`||B_t W - B_t W'||_inf <= ||W - W'||_inf`. Consequently, if a scheme replaces the true
`V_{t+1}` by a representation `~V_{t+1}` and, at each layer, commits a further local
representation error `eps_t := ||B_t ~V_{t+1} - ~V_t||_inf`, then
`e_t := ||V_t - ~V_t||_inf` satisfies

```
    e_T <= eps_T,      e_t <= eps_t + e_{t+1},      |ROOT - ~ROOT| <= e_0.
```

*Proof.* Nonexpansiveness is Lemma 2.2 applied pointwise at each `(x,y)`, since the
marginals do not depend on `W`. Then
`||V_t - ~V_t|| <= ||B_t V_{t+1} - B_t ~V_{t+1}|| + ||B_t ~V_{t+1} - ~V_t||
<= e_{t+1} + eps_t`. The root inequality is Lemma 2.2 at the fixed marginals `(a_0, b_0)`,
whose cost matrix is `V_0` with no additional stage cost. []

Three properties of this recurrence must be kept in view. It is **nonexpansive, not
contractive**: the factor on `e_{t+1}` is exactly 1, so layer errors accumulate over the
horizon with no decay. It is the **same envelope shape** as H-A's approximate recurrence
(`research/theory/notes.md`, H-A "Approximate version to verify"; corrected indexing in
`research/theory/quotient_review_v1.md`, "Approximate TV envelope"), differing only in
that no marginal is perturbed here, so H-A's `R_{t+1} * min(1, a_t + b_t)` term is
absent. And by Lemma 2.1 it may be applied to `R` alone: if `~V_{t+1} = f (+) g + ~R` and
the additive part is carried exactly, then `eps_t = || R_{t+1} - ~R ||_inf`.

**Per-layer budget.** With `epsilon = 0.005` and `required_T = 50` from `objective.json`
and the fine-case lower value `2.923588801715` from
`research/theory/root_gap_priority_decision_20260910.md`, uniform allocation of the
relative root budget over the horizon gives a per-layer interaction-error budget of
**2.9235888e-4** (Appendix A, check 8). Errors cancelling in practice would relax this;
the bound does not.

### 2.3 What "certified" requires (and what the repo does not have)

The word "certified" in the sentences above is a promissory note. To turn Lemma 2.3 into
a root certificate one needs, at minimum:

1. **Outward-rounded local values.** Each local LP value must be replaced by an interval
   `[lo, hi]` containing the exact optimum of the exact problem. The standard route is
   post-processing an approximate dual with directed rounding: Neumaier–Shcherbina
   `doi:10.1007/s10107-003-0433-3` and Jansson `doi:10.1137/S1052623402416839`, both
   recorded in `research/sota/EXTERNAL_KNOWLEDGE_20260910.md` §2, which also records that
   both are **closed access and unread**, so they may not be implemented from memory.
   The local problems here are transportation LPs with `0 <= pi <= 1`, i.e. the
   finite-simple-bounds class those results address.
2. **Exact normalized marginals.** `_transport_value` renormalizes in float64. A
   certificate must either carry the counts as exact rationals or charge the
   renormalization perturbation explicitly. `research/theory/quotient_review_v1.md`
   documents that the `Fraction.from_float`-then-normalize convention is *not*
   interchangeable with the exact integer-count convention.
3. **Feasible plan arithmetic.** Any upper bound must come from a plan whose marginal
   residuals are corrected outward, not merely small. The repo's own record is explicit
   that this is missing: `research/theory/structured_local_ot_decision_20260910.md` states
   the exact Monge predicate "does not turn the recurrence into an outward certificate",
   and flags that the NW helper's cumulative floating sums can lose an interior tiny mass
   while the residual tolerance still passes.

**Therefore every "certified" claim below is conditional on item 1–3 being built.** This
is not a formality: the project has *no* outward-rounded certificate at any scale today.

### 2.4 The range constant and its indexing

The constant that the §4 estimates need is `Lam_X` / `Lam_Y` of the **reduced local cost
including the stage cost at the successor time**:

```
    N_{t+1} := c_{t+1} + R_{t+1}      (R_T = 0),
```

and the two facts used are:

**(i) Dual span is bounded by `Lam`.** Any optimal dual pair may be taken in
`c`-transform form `u(i) = min_j (N(i,j) - v(j))`. For such `u`, choosing `j*` optimal for
`i'`, `u(i) - u(i') <= N(i,j*) - N(i',j*) <= Lam_X(N)`, hence `span(u) <= Lam_X(N)`.
Attained: for `N = [[0,a],[a,0]]` the `c`-transform span equals `Lam_X(N) = a` (Appendix A,
check 3).

**(ii) `Lam_X` of an anchored interaction is bounded by `osc2`.** Fix anchors
`x_0, y_0` and set `R(x,y) := D_V(x, x_0; y, y_0)`; then
`V = f (+) g + R` with `f(x) = V(x,y_0)`, `g(y) = V(x_0,y) - V(x_0,y_0)`. For this `R`,
`R(x,y) - R(x',y) = D_V(x, x'; y, y_0)`, so

```
    Lam_X(R) <= osc2(V),      Lam_Y(R) <= osc2(V),      ||R||_inf <= osc2(V),
```

and conversely `osc2(V) <= 4 iota(V)`, so `osc2/4 <= iota <= osc2`: the two seminorms are
equivalent within a factor 4. All §4 statements are made in `osc2`, whose recursion is
clean; converting to `iota` (which is what a *representation* error is measured in) costs
that factor 4 and is stated where used.

**Indexing check — the stage cost must be inside `Lam`.** At `t = T-1`, `R_T = 0` but
`Lam_X(c_T) != 0`, and indeed `osc2(V_{T-1})` is generally nonzero. In the Appendix A
check-5 toy, `osc2(V_3) = 0` while `Lam_X(c_3) = 4.0` and `osc2(V_2) = 8.0`, i.e. exactly
`2 * Lam_X(c_3)`. Using a range constant that omits the incoming stage cost would predict
zero interaction at the last transition and is wrong for this adapter — the same indexing
error that `research/theory/quotient_review_v1.md` corrects in H-A's recurrence
("Using only `osc(coarse_V_(t+1))` is wrong for this adapter").

---

## 3. The ONE frozen structural quantity

**Chosen (frozen before any measurement): (a) the numerical rank of the interaction part
`R_t` on the actual positive support.**

**Definition.** Let `S_t` be the set of pairs `(x, y)` in `X_t x Y_t` that are reachable
with positive probability, and let `R_t` be the anchored interaction of §2.4(ii). For
tolerance `eta > 0`,

```
    rho_t(eta) = min { rho : exist A in R^{X_t x rho}, B in R^{Y_t x rho}
                              with  iota( (R_t - A B^T)|_{S_t} ) <= eta }.
```

`rho_t(0)` is the exact rank of the interaction modulo additive matrices; `rho_t(eta)` is
its `eta`-numerical rank. The seminorm `iota`, not a norm, is the right measure because
Lemma 2.1 makes additive discrepancies free for the optimizer and exactly accountable for
the value.

**Why (a) and not (b).** Alternative (b), the `tau`-step truncation error
`||R_t - R_t^{(tau)}||_inf`, is **dead by definition**: `R_t` is the true interaction part
of the true continuation, so measuring (b) requires computing the object the mechanism
exists to avoid. Its only escape is an *a priori* bound on the truncation error as a
function of `tau` — which is exactly the lemma target of §4. §4 reports that lemma as
failed; therefore (b) has no checkable form on this model class, and choosing it would
have triggered the task card's second no-deployment condition ("checking the structural
condition requires knowing the whole continuation") immediately and with nothing learned.
(a) is chosen because it has at least one regime with an exact one-sided check, described
next, and because for `p = 2` the stage interaction is exactly rank one, so rank is the
natural currency of the recursion.

**How (a) could be computed or bounded from the input data.**

*Exactly and one-sidedly at the terminal transition, both cost families.* Both stage
costs are submodular in the scalar order: `(r-s)^2` and `|r-s|` are convex functions of
`r - s`, so `D_c((u,u'); (v,v')) <= 0` for `r_u <= r_u'`, `s_v <= s_v'`. Hence at
`t = T-1`, where `V_T = 0` and the local cost is `c_T` alone, the comonotone (north-west)
coupling of the two conditional laws is optimal — Hoffman 1963 and Bein–Brucker–Park–Pathak
`doi:10.1016/0166-218X(93)E0121-E`, both already pinned in
`research/sota/EXTERNAL_KNOWLEDGE_20260910.md` §4 — and therefore

```
    V_{T-1}(x, y) = integral_0^1 | F_x^{-1}(w) - G_y^{-1}(w) |^p dw,
```

where `F_x` is the law of `r_T` under `P_{T-1}(x, .)` and `G_y` that of `s_T` under
`Q_{T-1}(y, .)`. For `p = 2` this expands to

```
    V_{T-1}(x, y) = phi(x) + psi(y) - 2 <F_x^{-1}, G_y^{-1}>_{L^2(0,1)},
    phi(x) = E[ r_T^2 | x ],   psi(y) = E[ s_T^2 | y ],
```

so `R_{T-1}(x,y) = -2 <F_x^{-1}, G_y^{-1}>_{L^2(0,1)}` is (minus twice) a **Gram matrix of
one-sided quantile functions**, and

```
    rho_{T-1}(eta) <= min( numerical rank of {F_x^{-1}}_x , numerical rank of {G_y^{-1}}_y ),
```

both computable by an SVD of a one-sided quantile matrix at cost
`O((|X_{T-1}| + |Y_{T-1}|) G)` for a common grid of size `G`, never touching a joint
table. A crude a priori bound needing no SVD: `rho_{T-1}(0) <= min(#distinct rows of
P_{T-1}, #distinct rows of Q_{T-1})`, i.e. exactly H-A's row-signature count. The
identity was verified to 8.9e-16 on a toy (Appendix A, check 7).

**Does checking (a) require knowledge you would not otherwise compute?**

**Yes, for every layer except the last — so the mechanism is dead in the form that would
have made it useful. Say it plainly.** For `t < T-1` the map `R_{t+1} -> R_t` passes
through a minimum over the coupling polytope (§4), so it is not bilinear and rank does not
propagate; `rho_t(eta)` can only be measured on a materialized `R_t`, whose construction
is the whole per-node cost the mechanism was supposed to omit. The one-sided route above
survives only where the *reduced* local cost `N_{t+1} = c_{t+1} + R_{t+1}` remains
submodular in the two scalar orders, since only then is the optimizer known without
solving. The repo has already measured the closest available proxy for that condition —
the strict support-Monge predicate on the actual continuation matrices — at
**60.10% of nodes on the coarse case (247 of 411) and 3.25% on the fine case (10 of 308)**
(`research/theory/structured_local_ot_decision_20260910.md`), and the near-Monge rescue at
**0 of 164 coarse and 12 of 298 fine (4.03%)** defect sums in `(0, 1e-10]`. So the layer
where the structural quantity is checkable one-sided is, on the fine cell, a 3.25%
minority. `structural_quantity_checkable_without_full_continuation = false`.

---

## 4. The open lemma target

**Question.** Does a Dobrushin-type condition on the two transition kernels control
`osc2(V_t)` (equivalently, up to the factor 4 of §2.4, `iota(V_t)`) for the project's
regime: finite horizon, no discounting, time-inhomogeneous kernels, and a coupling that
is optimized at each node?

**Answer: NO on this model class. Outcome = FAILED.** §4.1–§4.3 derive the correct
one-step estimate and the resulting sufficient condition; §4.4 shows that condition is
violated by construction, not by accident; §4.5–§4.6 prove a repaired Wasserstein version
and show the repo's own frozen generators refute its hypothesis; §4.7 shows that even
granting the hypothesis the bound is unusable at 0.5%; §4.8 states exactly what breaks
and what nevertheless survives.

### 4.1 The reduced (interaction-only) recursion

Fix `t`. Apply §2.4(ii) at `t+1`: `V_{t+1} = f_{t+1} (+) g_{t+1} + R_{t+1}` with
`Lam_X(R_{t+1}), Lam_Y(R_{t+1}), ||R_{t+1}||_inf <= osc2(V_{t+1})`. By Lemma 2.1,

```
    V_t(x, y) = <P_t(x), f_{t+1}> + <Q_t(y), g_{t+1}>
                + T(P_t(x, .), Q_t(y, .))[ N_{t+1} ],        N_{t+1} = c_{t+1} + R_{t+1}.   (4.1)
```

The first two terms are additive in `(x, y)`, so they are annihilated by `D` and by
`osc2`. **This is the load-bearing structural point of the whole round:** the additive
part propagates through two *independent one-sided linear recursions* whose total cost is
`O(sum_t nnz(P_t))` and `O(sum_t nnz(Q_t))` scalar operations — no joint object at all —
and the second difference of `V_t` depends only on the reduced cost `N_{t+1}`, in which
the previous layer enters solely through its interaction `R_{t+1}`.

It also fixes the correct range constant: `Lam_X(f (+) g) = span(f) != 0`, so had we not
absorbed the additive part first, the one-sided value (which grows like the remaining
horizon) would have entered every estimate. After absorption,

```
    Lam_X(N_{t+1}) <= Lam_X(c_{t+1}) + osc2(V_{t+1}),                                   (4.2)
```

and symmetrically for `Lam_Y`. For `p = 2` the reduction is sharper still: writing
`c_{t+1} = r_{t+1}^2 (+) s_{t+1}^2 - 2 r_{t+1} (x) s_{t+1}`, the squared stage cost
contributes an exactly rank-one interaction, so the whole problem is equivalent to
maximizing the bicausal covariance `sum_s E[X_s Y_s]` — the finite-horizon analogue of the
structure behind the Gaussian closed form in
`research/theory/GAUSSIAN_ORACLE_20260910.md`. That reduction is classical
(Hoeffding–Fréchet) and is not claimed as new.

### 4.2 The one-step second-difference estimate

**Proposition 4.1.** Let `N` be a fixed cost matrix on the successor supports and let
`p, p'` be probability vectors on the left successor support and `q, q'` on the right. Put
`G(a, b) = T(a, b)[N]`. Then

```
  | G(p,q) + G(p',q') - G(p,q') - G(p',q) |
        <=  2 * min ( TV(p, p') * Lam_X(N) ,  TV(q, q') * Lam_Y(N) ),
```

where `TV` is half the `l1` distance. Moreover the constant 2 cannot be improved.

*Proof.* Write `Delta` for the bracketed second difference. The dual of `T(a,b)[N]` is
`max { <a, u> + <b, v> : u(i) + v(j) <= N(i,j) }`; crucially, **the dual feasible set does
not depend on the marginals**. Let `(u, v)` be optimal for `(p, q)` and `(u', v')` optimal
for `(p, q')`, both in `c`-transform form, so `span(u), span(u') <= Lam_X(N)` by
§2.4(i). Then

* `G(p,q) - G(p',q) <= <p - p', u>` : the pair `(u,v)` is dual-feasible at `(p', q)`, so
  `G(p', q) >= <p', u> + <q, v>`, while `G(p, q) = <p, u> + <q, v>`.
* `G(p,q') - G(p',q') >= <p - p', u'>` : the pair `(u',v')` is dual-feasible at
  `(p', q')`, so `G(p', q') <= <p', u'> + <q', v'>`, while `G(p, q') = <p, u'> + <q', v'>`.

Subtracting, `Delta <= <p - p', u - u'>`. Since `p, p'` are probability vectors,
`<p - p', w> = <p - p', w - c1>` for any constant, hence
`<p - p', w> <= ||p - p'||_1 * span(w) / 2 = TV(p,p') * span(w)`, and
`span(u - u') <= span(u) + span(u') <= 2 Lam_X(N)`. This gives
`Delta <= 2 TV(p,p') Lam_X(N)`; swapping the roles of `(p, p')` bounds `-Delta` the same
way, and the whole argument with the two sides exchanged gives the `Lam_Y` branch. Take
the minimum.

*Tightness.* Take `N = [[0, a], [a, 0]]`, `p = q = (1/2 + e, 1/2 - e)`,
`p' = q' = (1/2 - e, 1/2 + e)`. On two-point spaces with this 0/`a` cost,
`G(a_1, b_1) = a |a_1(1) - b_1(1)|`, so
`Delta = 2a|e - e| - 2a(e + e) = -4ae`, while `TV(p,p') = 2e` and `Lam_X(N) = a`,
so the bound equals `4ae` exactly. Appendix A check 3 reproduces ratio `1.000000`;
a random search over 4000 tiny instances (supports 2–3 on each side, random costs and
random skewed marginals) found a worst ratio of `0.999605` and no violation
(Appendix A, check 2). []

Three remarks tie this to the task card's three named obstructions.

* **Obstruction (ii) — the minimum over the coupling polytope.** It is handled, not
  avoided: the proof works entirely through dual feasibility, which is marginal-free, so
  the `min` costs nothing structurally. But the `min` *is* what creates the factor 2:
  optimal potentials are discontinuous in the marginals. In the tightness example the
  `c`-transform potentials at `(p,q)` and at `(p,q')` are `(0, a)` and `(a, 0)` however
  small `e` is, so `span(u - u') = 2 Lam_X(N)` is attained at arbitrarily small marginal
  perturbation. Span contraction through a `min` is therefore **not** automatic, and the
  factor-2 loss is exactly the price of that discontinuity.
* **Obstruction (iii) — per-marginal mixing is not enough.** Proposition 4.1 makes the
  precise sense in which this is true: mixing controls only the *first* factor. The second
  factor `Lam(N)` is a property of the joint reduced cost, and by (4.2) it is where the
  previous layer's interaction re-enters **with coefficient 1** — and §2.4(ii) shows that
  coefficient is attained. So no amount of marginal mixing bounds `osc2(V_t)` without a
  simultaneous bound on the accumulated interaction; the two must be closed into a
  recursion, which is §4.3, and the recursion is what fails.
* **Obstruction (i) — Moulos Lemma 3 does not transfer for free.** Confirmed. Lemma 3 of
  `arXiv:2010.06831` bounds `||W_bc||_inf <= 1/(1 - delta(P))` for a *stationary* kernel,
  *infinite* horizon, via a *fixed* Wasserstein coupling and a hitting-time domination
  (`research/sota/MOULOS_BACKHOFF_AUDIT_20260910.md` §1). Proposition 4.1 is the analogous
  "Dobrushin implies bound" mechanism, transplanted to the second-difference seminorm at
  finite horizon with an optimized coupling; the transplant costs the factor 2, and the
  finite-horizon version bounds an oscillation rather than a level.

### 4.3 The resulting recursion and its sufficient condition

Let `delta_t^X = max_{x, x'} TV(P_t(x,.), P_t(x',.))` and `delta_t^Y` likewise be the
one-step Dobrushin coefficients of the two empirical kernels. Combining (4.1), (4.2) and
Proposition 4.1:

**Theorem 4.2 (conditional).** For `t = T-1, ..., 0`, with `osc2(V_T) = 0`,

```
  osc2(V_t) <= min_{Z in {X, Y}}  2 delta_t^Z ( Lam_Z(c_{t+1}) + osc2(V_{t+1}) ).      (4.3)
```

If moreover `2 delta_t^Z <= kappa < 1` for one side `Z` and all `t`, then

```
  osc2(V_t) <= kappa / (1 - kappa) * max_s Lam_Z(c_s)                                  (4.4)
```

uniformly in `T` — i.e. the interaction part is bounded independently of the horizon, and
a `tau`-step truncation error decays as `kappa^tau`.

*Proof.* (4.3) is Proposition 4.1 applied at every quadruple with `N = N_{t+1}`, plus
(4.2). For (4.4), iterate `z_t <= kappa(L + z_{t+1})` from `z_T = 0` to get
`z_t <= kappa L (1 - kappa^{T-t}) / (1 - kappa) <= kappa L / (1 - kappa)`. []

The bound (4.3) is attained at the terminal transition in the Appendix A check-5 toy:
`delta_2^X = 1`, `Lam_X(c_3) = 4.0`, `osc2(V_3) = 0`, bound `8.0`, actual `osc2(V_2) =
8.0`. One layer further back it is loose (bound `24.0`, actual `8.0`), and — the point of
the check — `osc2` does **not** decay backwards: `8.0` at `t = 2` and `8.0` at `t = 1`.

So the mathematics does produce a Dobrushin-type theorem. The question is whether its
hypothesis can hold here.

### 4.4 The hypothesis fails by construction: `delta_t = 1` on the `k`-window model

**Proposition 4.3.** In a model produced by `build_window_model` with `k >= 2`, for every
`t` at which two states of `X_t` differ in their **last** cell index,
`delta_t^X = 1` exactly. The same holds for `Y`.

*Proof.* For `k >= 2` the state at time `t+1` is the tuple of the last `min(k, t+2) >= 2`
cell indices, whose **first** retained component is the cell index at time `t`. That
component is a deterministic function of the state at time `t`. Hence if `x, x'` in `X_t`
have different last cell indices, every state reachable from `x` disagrees with every
state reachable from `x'` in that component, so `P_t(x, .)` and `P_t(x', .)` have disjoint
supports and `TV = 1`. []

This is not a statistical accident that more data would cure: it is a property of the
state encoding, and it is the *same* property that makes `k = 2` carry information that
`k = 1` destroys (`research/theory/quotient_review_v1.md`: the second-order fixture
"retains squared value 4 for `k = 2` and returns 0 for `k = 1`"). For `k = 1` the
coefficient is 1 as soon as two states have disjoint observed successor cell sets, which
is the generic situation for an empirical kernel with singly-observed tail states (a state
observed once has a Dirac row, hence `TV = 1` against any row not supported on that same
cell). On the toy of Appendix A check 4, `delta_t = 1.0` at every layer with more than one
state, for both `k = 1` and `k = 2`. I have **not** measured `delta_t` on the frozen
`T = 50` grid — doing so would mean opening it — so the `k = 1` statement is a generic
argument plus a toy demonstration, whereas the `k >= 2` statement is unconditional.

Since `2 delta_t = 2`, (4.3) degenerates to `osc2(V_t) <= 2 Lam(c_{t+1}) + 2 osc2(V_{t+1})`,
which is *worse* than no information: the trivial a priori bound `osc2(V_t) <= 2 ||V_t||_inf
<= 2 sum_{s>t} max c_s` is tighter. **The TV-Dobrushin route contributes nothing on this
model class.**

### 4.5 The repair: a Wasserstein-metric Dobrushin condition

TV is the wrong metric precisely because the `k`-window encoding forces disjoint supports
while the *outputs* remain close. Replace it. Equip `X_t` with a metric `d_t` and define

```
    alpha_t^X = sup_{x != x'} W_1^{d_{t+1}}( P_t(x,.), P_t(x',.) ) / d_t(x, x'),
    lambda_t  = sup_{x != x'} sup_{y, y'} | D_{V_t}(x,x'; y,y') | / d_t(x, x').
```

**Theorem 4.4 (conditional; proved).** Assume the cost is `d`-Lipschitz in each argument
with constant `Lc` (true with `Lc = 1` for `p = 1` and `Lc = 2 max|r - s|` for `p = 2`
when `d` is the current-coordinate distance). Then for all `t`

```
    lambda_t <= 2 alpha_t^X ( Lc + lambda_{t+1} ),                                     (4.5)
```

and if `2 alpha_t^X <= kappa < 1` for all `t` then `lambda_t <= kappa Lc / (1 - kappa)`
uniformly in `T`, whence `osc2(V_t) <= lambda_t * diam(X_t)` and a `tau`-step additive
truncation error decays as `kappa^tau`.

*Proof.* Repeat the proof of Proposition 4.1, replacing the pairing bound
`<p - p', w> <= TV(p,p') span(w)` by Kantorovich duality
`<p - p', w> <= Lip_d(w) W_1^d(p, p')`. The `c`-transform `u(i) = min_j (N(i,j) - v(j))` is
an infimum of functions each `Lip_d`-bounded by the first-argument modulus of `N`, so
`Lip_d(u) <= Lip_d(N)` in the first argument, and by §2.4(ii)
`N(i,j) - N(i',j) = c(i,j) - c(i',j) + D_{V_{t+1}}(i,i'; j, j_0)`, giving
`Lip_d(N_{t+1}) <= Lc + lambda_{t+1}`. Then
`|D_{V_t}(x,x'; y,y')| <= 2 Lip_d(u) W_1(P_t(x), P_t(x')) <= 2 (Lc + lambda_{t+1})
alpha_t^X d_t(x,x')`. Iterate as in Theorem 4.2. []

Verified numerically: over 4000 random tiny instances with random scalar support
positions, the worst ratio of `|Delta|` to the right-hand side of the one-step
`W_1` estimate was `0.993525`, with no violation (Appendix A, check 6). The constant 2 is
again attained, by the same 0/1-metric instance as in Proposition 4.1.

**The hypothesis is `2 alpha < 1`, i.e. `alpha < 1/2` — not `alpha < 1`.** This threshold
is the single most consequential number in this document, and §7 lists it as the first
thing to attack.

### 4.6 The repo's two frozen process families refute the hypothesis

The frozen generator laws are recorded in `research/theory/block_bounds_review.md` §7
("Reuse exactly the H-A registered laws"): AR(1) coefficients **0.7 versus 0.55** with
noise scales 1 versus 1.15; second-order coefficients **0.25 versus 0.15** on the latest
value and **0.7 versus 0.6** on `sin(2 * older value)`, same noise scales, zero start,
missing older value zero. The AR(1) pair `(a, sigma) = (0.7, 1.0), (0.55, 1.15)` is
confirmed in `research/theory/GAUSSIAN_ORACLE_20260910.md`.

For a kernel with additive noise, `X_{t+1} = m(x) + sigma xi`, the two conditional laws
share the noise, so `W_1(P(x,.), P(x',.)) = |m(x) - m(x')|` exactly and
`alpha = Lip(m)` before quantization (quantization perturbs each conditional law by at
most `delta/2` in `W_1`).

* **AR(1) family.** `m(x) = a x`, so `alpha = a`. `2 alpha = 1.4` for `a = 0.7` and
  `1.1` for `a = 0.55`. **Both exceed 1.** The hypothesis of Theorem 4.4 fails for both
  AR(1) generators, and it fails for the *more* contractive one too.
* **Second-order family, `k = 2`.** `m(x_{old}, x_{now}) = A x_{now} + B sin(2 x_{old})`
  with `(A, B) = (0.25, 0.7)` and `(0.15, 0.6)`. With the current-coordinate metric
  `d(x, x') = |x_{now} - x'_{now}|` used by the cost, `alpha = +infinity`: two windows
  with identical current coordinate and different older coordinate are at distance zero
  and have different successor laws. This is the H-A probe configuration verbatim. The
  only repair is a weighted window metric `d_w = |Dx_{now}| + w |Dx_{old}|`; the successor
  window is `(x_{now}, x_{next})`, so a contraction factor `alpha` requires
  `2B <= alpha w` and `A + w <= alpha` for some `w > 0`, i.e.
  `alpha^2 - A alpha - 2B >= 0`. Minimizing over `w`, the best achievable factor is
  **1.3148** for `(0.25, 0.7)` and **1.17301** for `(0.15, 0.6)` (Appendix A, check 5b).
  **No weighted window metric of this form makes the second-order family a `W_1`
  contraction at all**, let alone `alpha < 1/2`.

So the only regime in which any version of the hypothesis could plausibly be approached is
the AR(1)/Gaussian family — which already has a closed-form population solution
(`research/theory/GAUSSIAN_ORACLE_20260910.md`, Gunasingam–Wong Theorem 1.1; population
`AW_2^2 = 5.485216920503423` at `T = 50`). That is the task card's **first no-deployment
condition** verbatim.

### 4.7 Even granting the hypothesis, the bound is too wide for 0.5%

Suppose, counterfactually, `2 alpha_t <= kappa < 1`. Then a `tau`-step truncation commits
an interaction error `~ kappa^tau lambda diam` at each layer, and by Lemma 2.3 the layer
errors **add** with coefficient 1 to the root. Against the per-layer budget
`0.005 * 2.923588801715 / 50 = 2.9235888e-4` of §2.2, the required lookahead is
(Appendix A, check 8):

| `kappa` | `lambda * diam = 1` | `= 5` | `= 20` |
|---|---:|---:|---:|
| 0.5 | `tau = 12` | 15 | 17 |
| 0.7 | 23 | 28 | 32 |
| 0.9 | 78 | 93 | 106 |
| `>= 1.0` | no finite `tau` | — | — |

At the repo's actual coefficients (`kappa >= 1.1`) the table has no entry. And even at the
fictitious `kappa = 0.5`, a `tau ~ 12`-step lookahead per node at `T = 50` means expanding
a depth-12 subtree per node instead of reusing one shared table per layer. That is
obligation 3 of Đầu ra 2 realized as arithmetic rather than as a probe: *shorter lookahead
is not automatically less work, because the existing DP already shares one table per time
layer*. This is the task card's **third no-deployment condition**.

### 4.8 Verdict

**FAILED.**

**The precise step that breaks.** The chain
`osc2(V_t) <= 2 delta_t (Lam(c_{t+1}) + osc2(V_{t+1}))` requires
`2 * (mixing coefficient) < 1` to contract, because (i) the factor 2 is the tight price of
the discontinuity of optimal dual potentials in the marginals (attained in Proposition
4.1's example), and (ii) the previous layer's interaction enters `Lam(N_{t+1})` with
coefficient exactly 1 (attained in §2.4(ii)). Both mixing coefficients available on this
model class violate that threshold: `delta_t = 1` identically for `k >= 2` by Proposition
4.3, and `2 alpha_t >= 1.1` for every frozen generator by §4.6. The break is therefore in
the *hypothesis-satisfaction* step, and it is forced twice over — once by the state
encoding and once by the generator constants.

**Smallest concrete configurations that exhibit the failure.**

1. *Constant is unimprovable (2 x 2, one stage).* `N = [[0,a],[a,0]]`,
   `p = q = (1/2 + e, 1/2 - e)`, `p' = q' = (1/2 - e, 1/2 + e)`: second difference
   `-4ae`, bound `4ae`, ratio 1 for every `e > 0`. Optimal potentials jump by the full
   `Lam(N)` under an `O(e)` marginal change.
2. *Dobrushin coefficient is 1 (3 paths, `k = 2`, `T = 2`).* Two paths whose time-1 cells
   differ, e.g. `(0, 0, .)` and `(0, 1, .)` with `delta = 0.5`: the time-2 windows
   `(0, ., )` and `(1, ., )` retain the time-1 cell, so the two rows of `kernels[1]` have
   disjoint support and `TV = 1`. Appendix A check 4 exhibits `delta_t = 1.0` at every
   layer of a 6-path toy for both `k = 1` and `k = 2`.
3. *No backward decay (`k = 1`, `T = 3`, 4 paths per side).* Appendix A check 5:
   `osc2(V_3) = 0`, `osc2(V_2) = 8.0 = 2 Lam_X(c_3)` (bound attained), `osc2(V_1) = 8.0`
   (no decay).
4. *Second-order family admits no contracting window metric.* `A = 0.25, B = 0.7` gives
   best `alpha = 1.3148 > 1`; `A = 0.15, B = 0.6` gives `1.17301 > 1`.

**What nevertheless survives, stated honestly.** Theorem 4.2 and Theorem 4.4 are proved,
with all constants and their (absent) `T`-dependence explicit; they are the correct
finite-horizon, time-inhomogeneous, optimized-coupling analogues of Moulos's Lemma 3
mechanism, and they say that *if* a mixing coefficient below 1/2 were available in some
metric, the interaction part would be horizon-uniformly bounded and `tau`-truncatable.
That is a real conditional theorem and worth recording. It is not a PARTIAL outcome for
this project, because its hypothesis is not merely unverified — it is **refuted** by the
repo's frozen generator constants and by the state encoding, and §4.7 shows the
conclusion would be unusable at `epsilon = 0.005` even if it held. Reporting this as
PARTIAL would misrepresent a refuted hypothesis as an open one.

Also surviving, and independent of §4: the exact one-sided reduction (4.1), and the
terminal-transition quantile identity of §3. Neither is novel (Lemma 2.1 is Kantorovich
degeneracy; the quantile identity is Hoffman 1963 / Bein et al. 1995 plus
Hoeffding–Fréchet), and neither by itself omits a single local solve — see §6.

---

## 5. Distinction table

"What mine adds" is assessed against the *delivered* content of this round, i.e. including
the §4 failure. Rows are not graded on intention.

| Route | What it already gives | What this round's statement adds beyond it |
|---|---|---|
| **H-A** certified quotient by equivalent futures (`research/theory/notes.md`; `runs/cycle_1/H_A01_verdict.md`; `quotient_review_v1.md`) | Exact merging of states with identical recursive conditional-future signatures, with pushforward/lift proof; approximate TV envelope `e_t <= eta_{t+1} + e_{t+1} + R_{t+1} min(1, a_t+b_t)`. Development gate failed in 4 of 6 `k=2` cells (14.844 / 22.931 / 27.219% AR(1); 14.811 / 23.172 / 27.934% second-order, threshold 25%). | **Concrete difference:** no state is merged and no marginal is perturbed, so the `a_t + b_t` term is absent and the additive part is carried with *zero* error at one-sided cost regardless of whether any two states coincide. H-A can represent a continuation only where signatures agree (or agree in TV); (4.1) always applies. Shared, not added: the propagation envelope shape (Lemma 2.3 is H-A's envelope restricted to the interaction) and the `osc`-indexing correction. |
| **H-B** successor-block bounds / hierarchical refinement (`notes.md`; `block_bounds_review.md`; `runs/cycle_2/H_B01C1_verdict.md`) | Pushforward lower bound and conditional-proportion lift on successor rectangles, one-sided reachability-interval envelopes, refine-on-demand with a terminating interval algorithm. Occupation-headroom prediction falsified in all 12 groups (best group/layer median 2.917% against a 10% requirement); distinct-entry prediction still `inconclusive_metric_mismatch`. | **Concrete difference:** H-B's one-sided arrays are interval *envelopes* over reachable outputs used to enclose blocks; (4.1) uses exact one-sided *expectations* and removes them from the joint problem entirely rather than bounding them. Saving unit differs: H-B omits fine continuation entries inside rectangles; §3/§6 omit local solves at layers whose reduced cost stays submodular. Adjacent, and both are one-sided-propagation ideas. |
| **H-C** occupancy flow with certified sparse pricing (`notes.md`) | Single global finite-horizon flow LP, dual pricing, feasible-policy recovery, warm starts; dense variable count `sum_t |X_t||Y_t| degX_t degY_t`. | **Concrete difference:** stays inside the backward recurrence and changes the *representation of the value*, not the optimization formulation; no dual pricing and no global LP. Orthogonal rather than competing. |
| **Moulos 2020**, `arXiv:2010.06831` (`MOULOS_BACKHOFF_AUDIT_20260910.md`) | bicausal OT = MDP with Bellman fixed point; monotone value iteration from below at `beta = 1` (each iterate a valid lower bound); Lemma 3: `delta(P) < 1` implies `||W_bc||_inf <= 1/(1-delta(P))`, via a fixed Wasserstein coupling, stationary kernels, infinite horizon. | **No clear distinction.** §4 is exactly the transfer of Lemma 3's mechanism to the second-difference seminorm at finite horizon with an optimized coupling, and that transfer **fails** on this model class. What remains after the failure is either textbook (Lemma 2.1, Lemma 2.2) or Moulos's (Dobrushin implies bound). The change of setting — finite horizon, non-stationary, optimized coupling — is a difference in hypotheses, not in delivered content, once the conclusion does not hold. This row is a finding, not an omission. |
| **Schmitzer shielding**, `arXiv:1510.05466` (`EXTERNAL_KNOWLEDGE_20260910.md` §3; `block_bounds_review.md` §6) | Def 3.3 shielding condition; Prop 3.4/3.6 short-cuts; **Cor 3.10** local optimality on a shielding neighbourhood implies global optimality; Alg 4.1/4.6 sparse + multiscale. Author-declared limits: efficient shield maps need the cost's geometric structure, and overall complexity is open. | **Concrete difference:** no sparse restriction and no shield map; §3 uses submodularity of the *whole* reduced matrix to know the optimizer in closed form and to factorize a whole layer through one-sided quantile functions. Schmitzer certifies one static OT with sparse work; this is a statement about which part of `c + V` retains structure across time. Enabling fact is Hoffman 1963 / Bein et al. 1995, not this round; and the repo's own measurement (60.10% coarse, 3.25% fine) is the evidence that continuation destroys the structure — precisely Schmitzer's declared limitation. |
| **Calo et al. 2024**, bisimulation metrics as OT distances (`notes.md`) | Bisimulation/state-aggregation to OT correspondence, occupancy formulation, coupled iterations, maintained-coupling warm starts — in a **discounted stationary** setting whose guarantees do not transfer by setting `gamma = 1`. | **Concrete difference:** asks whether *mixing* can substitute for the discount factor as the source of contraction in the undiscounted finite-horizon problem, and answers **no** for this model class (§4.4, §4.6). Different question, negative answer. No algorithmic addition, and no aggregation or occupancy claim is made here. |
| **Demoted joint refinement** (`direction_proposal_20260910.md`, demoted by `direction_revision_20260910.md`; MDP line in `EXTERNAL_KNOWLEDGE_20260910.md` §1) | Anytime two-sided bounds with gap-guided selective refinement, transferred from BRTDP 2005 / Focused RTDP 2006 / LAO* 2001 / interval iteration 2017 / bounded-parameter MDP 2000 / prioritized sweeping 1993; retained as execution tool and comparison base. | **Concrete difference:** a value-*representation* claim rather than a bound-refinement *schedule*; the two compose rather than compete, since refinement would consume an a priori interaction bound to skip layers. Because §4 fails, the operational addition is **nil**; what is added is a negative delimitation of which a priori bound that schedule may not assume. |

Rows with no clear distinction: **Moulos 2020**.

---

## 6. Work table (Đầu ra 3)

Comparator, per the task card and
`research/theory/structured_local_ot_cycle_close_20260910.md`: the **strengthened dispatch
baseline** (direct binary-support formula + strict support-Monge dispatch), **not** an
all-LP Python implementation. Measured baseline behaviour, from
`research/theory/structured_local_ot_decision_20260910.md`:

| Baseline quantity | Coarse (AR1, `k=1`, `delta=0.5`, squared) | Fine (nonlinear, `k=2`, `delta=0.18`, absolute) |
|---|---:|---:|
| general LP calls, all-LP -> binary-direct | 543 -> 411 | 1,067 -> 308 |
| general LP calls, after support-Monge dispatch | 411 -> 164 | 308 -> 298 |
| nodes passing the strict support-Monge check | 247 (60.10%) | 10 (3.25%) |
| rejections with defect sum in `(0, 1e-10]` | 0 of 164 | 12 of 298 (4.03%) |
| binary fraction among nonforced, `T=50`, frozen `n` | 10.23% | 27.62% |
| forced fraction of all transition pairs, `T=50` | 15.10% | 39.19% |

### 6.1 Units

* **U1** general LP calls (the repo's `dispatch.rejected`; note `counts.LP_calls` counts
  *entries* into the general hook, not solves).
* **U2** closed-form local solves: forced/singleton products, binary-direct knapsack,
  NW after a passed Monge check.
* **U3** materialized continuation entries, `sum_{t<T} |X_t| |Y_t|` — the H-A metric.
* **U4** successor-support entries read per node (`nnz(P_t(x)) * nnz(Q_t(y))`).
* **U5** one-sided scalar edge operations, `sum_t nnz(P_t)` and `sum_t nnz(Q_t)`.

### 6.2 What the prospective algorithm omits or shares

* **The additive/interaction split alone omits nothing in U1–U4.** It moves
  `sum_t nnz(P_t) + sum_t nnz(Q_t)` of work into U5 (two independent one-sided
  recursions), and every node still faces a local transport problem of the *same
  dimensions* with cost `N_{t+1}` instead of `c_{t+1} + V_{t+1}`. Smaller entries, same
  LP. This must be said plainly: the split is a re-parameterization, not a saving.
* **Savings appear only where the structural quantity is small.** At a layer where
  `N_{t+1}` is submodular on the two scalar orders, the optimizer is the quantile coupling
  for *every* node of that layer, so U1 and U2 drop to **zero** at that layer and are
  replaced by `|X_t| + |Y_t|` one-sided quantile constructions plus one evaluation per
  pair; if additionally `rho_{t+1}(eta) = rho` is small, the layer's value table becomes
  `additive + A B^T` with `A, B` of width `rho G`, so U3 drops from `|X_t| |Y_t|` to
  `(|X_t| + |Y_t|) rho G` and U4 disappears at that layer.
* **Sharing across time.** The one-sided recursions are shared by all pairs by
  construction, which is the only unambiguous sharing gain, and it is small: U5 is
  linear in the model's edge count whereas U1+U2 is quadratic in layer size.
* **What is *not* omitted.** Nothing at layers where the reduced cost is not submodular;
  the repo's measured proxy says that is 39.90% of dispatch-eligible nodes on the coarse
  case and **96.75% on the fine case**.

### 6.3 Cost to detect and maintain the structure

* **Detecting submodularity** costs the repo's `monge_predicate`, i.e.
  `(|supp_x| - 1)(|supp_y| - 1)` exact `Fraction` adjacent checks per node — proportional
  to reading the node's whole matrix, and therefore to the cost of forming it. On the fine
  case, 96.75% of nodes pay the check *and* the LP.
* **Detecting `rho_t(eta)`** requires `R_t` for `t < T-1` (§3), i.e. the materialized
  joint table. There is no one-sided route past the terminal transition, and §4 failed to
  supply an a priori substitute. **Detection cost = computation cost.**
* **Maintaining** a factorized representation requires re-deciding at every layer, since
  submodularity is destroyed by the continuation and is not inherited backwards — the
  mechanism cannot commit once and amortize.

### 6.4 Cost to certify

Per §2.3: outward rounding for every local value (Jansson-style `O(n^2)` per node on top
of the solve), exact or explicitly-charged marginal normalization, and outward-corrected
plan arithmetic for any upper bound. For the quantile route specifically, the integral
`int_0^1 |F_x^{-1} - G_y^{-1}|^p dw` must itself be outward-rounded over merged
breakpoints, and the exact-Monge predicate certifies only the *represented* float matrix,
not the marginal arithmetic. None of this exists in the repo today.

### 6.5 Does certification eat the saving? Yes — and the arithmetic is not close

Upper bound on the reachable saving on the fine cell: 3.25% of dispatch-eligible local
solves, against a certification cost added to **100%** of them. Meanwhile the target is a
0.5% relative root interval, and the fine case's current fixed upper is **5.178% above
the numerical reference even with a perfect lower bound**
(`research/theory/root_gap_priority_decision_20260910.md`), with the current control
interval at 24.161993% relative width. A mechanism that removes at most 3.25% of local
solves and adds certification everywhere does not close a 5.178% one-sided obstruction.

### 6.6 Check against the three frozen no-deployment conditions

All three are triggered.

1. **"Only the Gaussian case is provable."** Triggered. The only family where any
   version of the §4 hypothesis is even approachable is AR(1) (`alpha = 0.7 / 0.55`,
   still failing `2 alpha < 1`), which has a closed-form population solution
   (`GAUSSIAN_ORACLE_20260910.md`); the second-order family admits no contracting window
   metric (`alpha >= 1.17301`).
2. **"Checking the structural condition requires the whole continuation."** Triggered.
   `rho_t(eta)` is one-sided-checkable only at `t = T-1`; elsewhere its check is the
   computation. §3 states this as a plain finding.
3. **"The bound is too wide to use at the 0.5% target."** Triggered. §4.7: no finite
   `tau` exists at the repo's coefficients, and even at a fictitious `kappa = 0.5` the
   required lookahead is `tau = 12` to `17`, which destroys the per-layer table sharing
   the current DP already has.

**Recommendation to the root lane: do not fund an implementation cycle on this
mechanism.** The bounded theory round has done its job by closing the route on paper
before any grid was opened. The retained by-products are (i) Theorem 4.2 / Theorem 4.4 as
recorded conditional statements with tight constants, (ii) Proposition 4.3 as a structural
fact about the `k`-window encoding that any future mixing-based argument must confront,
and (iii) the terminal-transition quantile identity of §3 as a possible engineering
micro-optimization for the last transition only, which must be measured against the
existing dispatch and not against all-LP.

---

## 7. Questions for the independent skeptic

Ordered by how much they would change the verdict, most dangerous first. The first is the
one I most fear.

1. **Is the factor 2 in Proposition 4.1 and Theorem 4.4 really unimprovable inside the
   recursion?** This is decisive. If the true threshold is `alpha < 1` rather than
   `alpha < 1/2`, then the AR(1) family (`alpha = 0.7`, `0.55`) **satisfies** it and the
   lemma becomes live for `k = 1` AR(1) cells, changing the verdict from FAILED to
   PARTIAL. I show the *one-step* inequality is tight (ratio 1 attained), and that
   `span(u - u') = 2 Lam(N)` is attained by two `c`-transforms of the same cost. I do
   **not** show that the tight one-step configuration can be realized at every layer of a
   consistent finite model simultaneously, which is what the recursion needs. Attack:
   bound `Lip_d(u_{pq} - u_{pq'})` jointly (they are `c`-transforms of the *same* `N`)
   instead of splitting the span; or find a primal exchange/gluing argument for the mixed
   second difference; or exhibit a model realizing the factor 2 at every layer.
2. **Is `osc2` (a supremum over all quadruples) the right object?** The root certificate
   needs an occupation-weighted quantity, not a sup: `delta_t = 1` is produced by state
   pairs that may carry negligible occupation. The dual-weighted-residual literature
   (Becker–Rannacher `doi:10.1017/s0962492901000010`, pinned in
   `CROSS_DOMAIN_MAP_20260910.md`) is the right frame, and the repo's own attribution
   identity `U_pi(root) - L_root = sum_n mu_n (<pi_n, c_n + L_child> - L_n)` is already an
   adjoint-weighted residual. Counter-evidence I am relying on:
   `runs/cycle_2/H_B01C1_verdict.md` found no layer able to retain 10% of optimal
   occupation inside the 0.5% budget (best group/layer median 2.917%). Attack: build the
   occupation-weighted interaction seminorm and check whether the `delta = 1` pairs are
   actually charged.
3. **Proposition 4.3 may be attacking a straw encoding.** `delta = 1` for `k >= 2` is a
   fact about the *window* chain. The natural object might be the current-cell marginal
   chain (which is not Markov in the window model) or a lumped chain in H-A's
   future-signature quotient. Attack: is there a valid Dobrushin coefficient on a lumping
   that both (i) is below 1/2 and (ii) supports Proposition 4.1's dual argument?
4. **The `W_1` coefficients are generator quantities, not empirical ones.** I compute
   `alpha = Lip(m)` for the *population* mean maps and add a `delta/2` quantization
   remark. The actual `alpha_t` of `build_window_model`'s empirical kernels at the frozen
   sample sizes is unmeasured — I did not open the grid. It could be smaller (pooling and
   quantization smooth the rows) or larger (sparse tail rows). Attack: measure `alpha_t`
   on a small held-out configuration; note that a *smaller* empirical `alpha` would not
   rescue the second-order family, whose obstruction (`alpha >= 1.17301`) is metric-level,
   not sampling-level.
5. **`Lam_X(c_{t+1})` is a crude constant.** It is the maximum column span of the stage
   cost, i.e. essentially the state range, and I use it unmodified. A support-restricted or
   occupation-restricted version could be far smaller, which would not change the
   contraction threshold but would change §4.7's table. Attack: does a sharper range
   constant make any `kappa` regime usable?
6. **Anchored versus best-additive decomposition.** I work with the anchored `R` and
   convert to `iota` via `osc2/4 <= iota <= osc2`. Constants could shift by up to 4x in
   either direction, and the anchor choice is arbitrary. Attack: does a Diliberto–Straus
   style centering change any threshold, and is `Lam_X(R) <= osc2(V)` still attained after
   optimal centering?
7. **The rank claim is thin.** `rho_t` is characterized exactly only at `t = T-1` and only
   for `p = 2` (Gram of quantile functions); for `p = 1` the terminal layer is a `W_1`
   table, which is a per-pair quantile integral but not bilinear, so the rank statement
   does not apply. Attack: is there any layer beyond the last where a one-sided rank
   certificate exists?
8. **Additive accumulation may be pessimistic.** Lemma 2.3 is worst-case; interaction
   representation errors at different layers could cancel systematically, which would
   relax the `2.9235888e-4` per-layer budget. Attack: is there a variance-style or signed
   accounting that beats the triangle inequality here? (Note the corresponding warning in
   `CROSS_DOMAIN_MAP_20260910.md` about cancellation between signed residuals, and the
   effectivity-index concept, which cuts both ways.)
9. **Did I mislabel a PARTIAL as a FAILED?** Theorem 4.4 *is* a proved conditional
   theorem. I argue FAILED because the hypothesis is refuted rather than unverified and
   because §4.7 makes the conclusion unusable anyway. A reviewer may reasonably want the
   label PARTIAL with the assumption `2 alpha_t <= kappa < 1` stated and its refutation
   recorded separately. The difference is presentational, not mathematical, and I would
   accept the change if the round's ledger prefers it.
10. **Everything I did not check.** No prior-art sweep was run this session; `osc2`-type
    interaction bounds for bicausal OT may exist in literature I did not query, in which
    case Theorem 4.2/4.4 are prior art and not merely non-novel by declaration. The
    Kršek–Pammer duality background, Pichler–Weinhardt nested Sinkhorn
    (`doi:10.1007/s10287-021-00415-7`) and the KR near-optimality candidates
    (`arXiv:2312.16515`, `arXiv:2209.03243`) were **not** read.

---

## Appendix A. Toy sanity checks

These are **sanity checks on toy configurations**, run in a scratch workspace with
`numpy`/`scipy`. They are not benchmark evidence, not registered experiments, and were not
written into `runs/`. Their purpose was to test the candidate inequalities of §4 and to
hunt for counterexamples to my own claims. Toy support sizes are 2–5 per side, horizons
3–4, and 4–6 synthetic paths per side.

| # | What was checked | Result |
|---|---|---:|
| 1 | Lemma 2.1 additive-shift invariance on a random 4x5 instance | max abs error `5.0e-16` |
| 2 | Proposition 4.1 (TV form) over 4,000 random tiny instances | worst ratio to bound `0.999605`; **no violation** |
| 3 | Proposition 4.1 tightness instance; `c`-transform span vs `Lam_X` | ratio `1.000000`; span `1.0000000000000002` vs `Lam_X = 1.0` |
| 4 | Dobrushin coefficient of `build_window_model` on a 6-path toy, `k = 1` and `k = 2`, `delta = 0.5` | `delta_t = 1.0` at every layer with >1 state, both `k` |
| 5 | Backward behaviour of `osc2(V_t)` on a `k = 1`, `T = 3`, 4-paths-per-side toy, squared cost | `osc2(V_3) = 0`, `osc2(V_2) = 8.0` (bound `2 Lam_X(c_3) = 8.0` attained), `osc2(V_1) = 8.0` (no decay) |
| 5b | Best `alpha` over weighted window metrics for the frozen second-order laws | `1.3148` for `(A,B) = (0.25, 0.7)`; `1.17301` for `(0.15, 0.6)` — both `> 1` |
| 6 | Theorem 4.4 one-step `W_1` estimate over 4,000 random tiny instances with random scalar supports | worst ratio to bound `0.993525`; **no violation** |
| 7 | Terminal-transition quantile identity `V_{T-1} = phi (+) psi - 2 Gram`, `p = 2`, `G = 2e5` | max abs error `8.9e-16` |
| 8 | Budget arithmetic from `objective.json` (`epsilon = 0.005`, `T = 50`) and the fine lower value `2.923588801715` | per-layer budget `2.9235888e-4`; `tau` table of §4.7 |

Checks 2 and 6 are the important ones: they are attempts to *falsify* Proposition 4.1 and
Theorem 4.4 by random search, and both inequalities held while being nearly attained,
which is why I assert the constants are tight rather than merely sufficient.

## Appendix B. Bundle files used

`adapters/common_model.py`, `adapters/support_monge.py`, `adapters/binary_transport.py`,
`objective.json`, `SCOPE_REVISION_2.md`,
`research/theory/direction_revision_20260910.md`,
`research/theory/notes.md`,
`research/theory/structured_local_ot_decision_20260910.md`,
`research/theory/structured_local_ot_cycle_close_20260910.md`,
`research/theory/root_gap_priority_decision_20260910.md`,
`research/theory/block_bounds_review.md`,
`research/theory/quotient_review_v1.md`,
`research/theory/GAUSSIAN_ORACLE_20260910.md`,
`research/sota/MOULOS_BACKHOFF_AUDIT_20260910.md`,
`research/sota/EXTERNAL_KNOWLEDGE_20260910.md`,
`research/sota/CROSS_DOMAIN_MAP_20260910.md`,
`runs/cycle_1/H_A01_verdict.md`, `runs/cycle_2/H_B01C1_verdict.md`.

`research/sota/notes.md` was read only by targeted string search, for the second-family
description and for the two identifiers quoted in §7 item 10
(`doi:10.1007/s10287-021-00415-7`); its comparator map was not reviewed here.

Not read this session, and therefore not relied on: `WORKFLOW.md`,
`research/sota/DOMAIN_KNOWLEDGE.md`, `research/sota/DOMAIN_RATE_AUDIT_20260910.md`,
`research/theory/direction_proposal_20260910.md` beyond its demotion,
`research/theory/binary_transport_review_20260910.md`,
`adapters/global_subsolution.py`, `adapters/policy_pool_candidate.py`,
`adapters/forced_transport_lower.py`, `probes/gaussian_population_audit.py`.


---

## Root integration note (orchestrator, 2026-09-10)

This document was produced by an independent theorist lane and is integrated unedited
above. Two corrections and one confirmation from the integrating root:

**Correction 1 — second-order generator law (material).** The lane's declared deviation is
accurate: `generators.py` was omitted from its context bundle (packing error by the root),
so it took the second family from prose and got it wrong. The frozen law in
`research-workflow/generators.py` is

    X_{t+1} = b X_t + c sin(w X_t) + d (X_t - X_{t-1}) + sigma eps_t,
    b = 0.55, c = 0.95, w = 1.7, d = -0.45, sigma = 0.7

not "0.25/0.15 on the latest value, 0.7/0.6 on sin(2 * older)". Recomputing the
W_1-Dobrushin coefficient from the correct law: the window mean map is
`m(x_now, x_old) = (b+d) x_now + c sin(w x_now) - d x_old`, so
`sup |dm/dx_now| = |b+d| + c w = 1.715` (attained at `cos(w x) = 1`, verified numerically
on a 4e5-point grid) and `|dm/dx_old| = 0.45`. In the weighted window metric
`|dnow| + w_m |dold|`, `alpha(w_m) = max(1.715 + w_m, 0.45/w_m)`, minimized at
`w_m* = 0.2312` giving

    alpha_SON = 1.9462   (2 alpha = 3.8924)

against the lane's reported 1.3148/1.17301. **The refutation is therefore stronger than
the document states, not weaker.** The AR(1) figures (alpha = 0.7 and 0.55, from the
frozen pair `(a,sigma) = (0.7,1.0)` and `(0.55,1.15)`) are confirmed correct.

**Correction 2 — scope of the AR(1) claim.** As the lane declares, these coefficients come
from the generator mean maps, not from `build_window_model`'s empirical quantized kernels
at the frozen sample sizes. They are statements about the generating laws; the empirical
`alpha_t` at `T = 50` remains unmeasured.

**Confirmation — the load-bearing result does not depend on either correction.**
Proposition 4.3 (`delta_t = 1` exactly for `k >= 2`) is a property of the state encoding,
proved unconditionally and independently of any generator parameter. The factor-2 tightness
of Proposition 4.1 and the coefficient-1 additive propagation of Lemma 2.3 are likewise
parameter-free. The verdict FAILED therefore stands on the corrected numbers.

**Still open for the skeptic lane** (beyond the document's own §7): whether Proposition 4.3
is being over-generalized — it kills the TV route on this encoding, but an encoding-level
obstruction invites the question of whether a different but equivalent state representation
evades it while preserving the same finite-model target.
