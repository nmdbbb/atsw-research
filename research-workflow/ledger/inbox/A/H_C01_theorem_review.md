# H_C01 theorem and counterexample review — Lane A

Date: 2026-09-09. Recommendation: **revise before registration**. The active-subsolution theorem is sound under its stated mathematical assumptions. Fixed-depth future-marginal **cost** sums are valid subsolutions for both registered powers. The central interpretation requiring correction is that, for a fixed active set and baseline, the global LP has exactly the same root optimum as ordinary backward DP with inactive values clamped to the baseline. Time coupling alone supplies no tighter bound.

This review follows scope v2. It neither registers H_C01 nor evaluates its frozen performance grid. Existing H_B01C1 and policy-pool results are known development evidence; neither establishes impossibility of this direction. Only this Lane A inbox file was written. All listed panel readings were read, including the v2 bridge, common model, implementation, tests, and prior verdicts. The numerical diagnostics below were inline, bounded, float64 checks; they did not execute a benchmark entrypoint.

## 1. Target, random initial law, and finite-horizon LP

Let E_t and F_t be the finite time-indexed k-window state spaces, with scalar output maps r_t and s_t. Their normalized transition rows are P_t(.|x), Q_t(.|y), and initial laws are mu, nu. Put

    c_t(x,y) = |r_t(x)-s_t(y)|^p,  p in {1,2},
    (B_t u)(x,y) = min_{pi in Pi(P_t(.|x),Q_t(.|y))}
                        sum_{a,b} pi(a,b)[c_{t+1}(a,b)+u(a,b)],
    V_T = 0,  V_t = B_t V_{t+1},
    V_root = min_{gamma in Pi(mu,nu)} sum_{x,y} gamma(x,y)V_0(x,y).

This is the adapter's successor-cost convention: costs at times 1 through T, no time-zero cost, optimized initial coupling. For k=2, the state retains its window, while c uses only its current scalar output. Time-indexed k-window graphs may recombine; they need not be prefix trees. The proofs require only a finite layered DAG and the stated kernels.

The dummy root is a single pre-time-zero node with marginal successors mu and nu, stage cost zero, and continuation V_0. An arbitrary initial coupling fixed in advance would define a different problem. Selecting a modal initial pair would also define a different problem. The current root block implements the intended optimized coupling correctly.

For completeness the equivalent occupation LP has d_t(x,y)>=0 and f_t(x,y,a,b)>=0, subject to

    sum_y d_0(x,y)=mu(x),   sum_x d_0(x,y)=nu(y),
    sum_b f_t(x,y,a,b)=d_t(x,y)P_t(a|x),
    sum_a f_t(x,y,a,b)=d_t(x,y)Q_t(b|y),
    d_{t+1}(a,b)=sum_{x,y} f_t(x,y,a,b).

Its objective is sum_{t=0}^{T-1} sum_{x,y,a,b} f_t(x,y,a,b)c_{t+1}(a,b). Every feasible dynamic coupling policy induces such flows. Where d_t>0, pi_t=f_t/d_t reconstructs a coupling with the required conditional marginals. Where d_t=0, every corresponding f is zero; assign any feasible coupling, for example the product row, without division by zero. Mixing any history-dependent admissible conditional couplings over histories with the same current state pair preserves these marginals and the occupation flows. Thus Markovization preserves additive cost on this specified finite model. This does not recover the original full-history or population law after k-window truncation.

Now assume h_T=0 and h_t<=B_t h_{t+1} pointwise. For fixed A_t, the active LP maximizes a free root variable rho. Define v=h off A, introduce v_t(z)>=h_t(z) on A, and retain v_T=0. For every active z=(x,y), introduce free local potentials alpha_z on supp P_t(.|x) and beta_z on supp Q_t(.|y), with

    v_t(z) <= sum_a P_t(a|x)alpha_z(a) + sum_b Q_t(b|y)beta_z(b),
    alpha_z(a)+beta_z(b) <= c_{t+1}(a,b)+v_{t+1}(a,b)
          for every a,b in the positive marginal support cross-product.

At the dummy root introduce alpha_root, beta_root and

    rho <= mu.alpha_root + nu.beta_root,
    alpha_root(x)+beta_root(y) <= v_0(x,y)
          for every x in supp mu, y in supp nu.

No root floor is needed for validity. Potential gauge freedom can make the optimal witness nonunique, but cannot make the root objective unbounded when the assumptions hold. Finite OT strong duality on the positive supports supplies attaining dual witnesses.

## 2. Induction, feasibility, and all-active equivalence

At an active z, multiplying the successor inequalities by any feasible pi and using its marginals gives v_t(z)<=E_pi[c+v_{t+1}]. Taking the minimum gives v_t(z)<=B_t v_{t+1}(z). At an inactive z,

    v_t(z)=h_t(z)<=B_t h_{t+1}(z)<=B_t v_{t+1}(z),

because every successor value is at least its baseline. Starting with v_T=V_T=0, Bellman monotonicity gives v_t<=V_t backward. Root weak duality then gives rho<=OT(mu,nu,v_0)<=V_root. A feasible dynamic policy, evaluated with the original costs, independently yields U>=V_root. This proves the stated lemma.

The baseline makes the LP feasible: set all v=h and choose an optimal OT dual for c+h_{t+1} at each active node. Its dual objective is at least h_t. Set rho=OT(mu,nu,h_0) with an attaining root dual. A finite upper bound follows from the preceding induction.

There is a stronger structural identity that should be stated and used as an ablation. Define the **clamped backward recursion**

    w_T=0,
    w_t(z)=h_t(z)                 if z is inactive,
    w_t(z)=B_t w_{t+1}(z)         if z is active.

Backward induction gives w>=h: at active nodes, B_t w_{t+1}>=B_t h_{t+1}>=h_t. Hence w and optimal local dual witnesses form a feasible active-LP solution. Conversely every feasible LP v satisfies v<=w: inactive values agree, and at active nodes v_t<=B_t v_{t+1}<=B_t w_{t+1}=w_t. Therefore

    max active-LP rho = OT(mu,nu,w_0).

This equality holds for arbitrary, non-ancestor-closed active masks and random initial laws. Nested activation A subset A' also gives w^A<=w^{A'} and a nondecreasing optimal root lower bound. With every nonterminal pair active, w=V, so the LP's **root optimum** is exactly backward DP's root value.

The root-only objective does not force every returned table entry to equal V. For a T=1 deterministic continuation with uniform 2-by-2 initial laws and squared-cost matrix V_0=[[1,9],[1,1]], the all-ones table v_0 is feasible and root-optimal with value 1, yet v_0(0,1)=1<9. The same example uses [[1,3],[1,1]] for absolute cost. There exists an optimum with v=V; not every optimum has that property. The current test correctly compares the root scalar. Its observed solver happened to return exact tables in this example, which does not change the nonuniqueness argument.

Consequently a fixed-A global LP cannot have a root-tightness advantage over the clamped recursion. Any benefit must come from other choices or implementation costs: activation, verification, reuse, or a changed relaxation. Lane B independently identifies direct AO*/LAO* and finite-horizon MDP LP overlap. Its communicated references include the partial-graph recurrence and Theorems 1–2 of [Hansen–Zilberstein](https://cdn.aaai.org/AAAI/1998/AAAI98-058.pdf), and Proposition 1 / Theorem 1 of [Bhattacharya–Kharoufeh](https://cecas.clemson.edu/~kharouf/old/Papers/Bhatta_Khar_ORL_Final.pdf). The source audit and section details belong to Lane B; the equivalence above is independently derived here.

## 3. Future-marginal subsolution: proved for p=1 and p=2

The draft names a future-marginal baseline without defining it. The following precise definition is valid. For t<s, let M^X_{t,s}(x) be the scalar-output distribution at time s obtained by propagating P_t,...,P_{s-1} from state x; define M^Y analogously. These must be marginals of the same finite model, not true generator conditionals or a different full-history empirical tree. Let

    D_{t,s}(x,y) = OT_{|u-v|^p}(M^X_{t,s}(x), M^Y_{t,s}(y)),
    h_t^H(x,y) = sum_{s=t+1}^{min(t+H,T)} D_{t,s}(x,y),
    h_T^H=0,  h^0=0,

where a single integer H>=0 is used throughout. Equivalently each summand is W_p^p, not W_p when p=2. It is permissible to compute OT on the unaggregated future state supports using the scalar-output cost: pushing forward and lifting within equal-output groups shows the same value.

Fix any first-step coupling pi in Pi(P_t(.|x),Q_t(.|y)). First,

    D_{t,t+1}(x,y) <= E_pi c_{t+1}(a,b).

For s>=t+2, choose a minimum-cost one-time coupling between M^X_{t+1,s}(a) and M^Y_{t+1,s}(b) separately for every pair (a,b). Their mixture with weights pi(a,b) has marginals M^X_{t,s}(x), M^Y_{t,s}(y), because pi has the specified marginal rows. Thus

    D_{t,s}(x,y) <= E_pi D_{t+1,s}(a,b).

Summing these inequalities through min(t+H,T) yields

    h_t^H <= E_pi[c_{t+1} + h_{t+1}^H].

The child baseline includes every required later summand and, away from the horizon, one additional nonnegative summand. Taking the minimum over pi proves h_t^H<=B_t h_{t+1}^H. The proof works for either registered p and, in fact, for arbitrary nonnegative time-dependent one-time costs. It does not require a single dynamically compatible coupling to attain all marginal minima: those minima supply lower bounds for each fixed first-step coupling.

There is no counterexample to this properly specified claim. The definition also gives h^{H+1}>=h^H pointwise. Hence the strongest of H=0,1,2 is automatically H=2 in exact arithmetic. H=0 and H=1 remain useful cost/tightness ablations. More generally the pointwise maximum of finitely many Bellman subsolutions is a subsolution by monotonicity; arbitrary node-by-node selection without taking the maximum is not covered.

The direct construction performs sum_t min(H,T-t)|E_t||F_t| one-time OT evaluations, in addition to marginal propagation and support/output handling. Already H=1 visits every nonterminal pair, including inactive ones. These are scalar-cost marginal OT problems, which can use a simpler kernel than arbitrary continuation-cost OT; the count does not prove equal runtime or an impossibility. It does prevent calling the baseline free or interpreting omitted active-LP rows as all avoided transport work.

Two nearby failed statements need explicit guardrails:

* **Wrong p=2 units.** One deterministic transition with outputs 0 and 1/2 has V=1/4. Using W_2=1/2 as h_0 exceeds B_0 h_1=1/4. This is a one-state-per-side, one-transition counterexample. Summing distances instead of squared costs is invalid for the declared squared target.
* **Unconstrained depth changes by time/state.** At T=2, take deterministic paths X=(0,0,0), Y=(0,0,1), use H_0=2 and H_1=0. Then h_0=1, h_1=0, first stage cost=0, so h_0>B_0 h_1=0 for both powers. Each quantity is an admissible value lower bound, but the chosen collection is not a Bellman subsolution. A varying-depth rule needs an additional consistency proof. A sufficient rule is that every positive-support child has depth at least the parent's depth minus one.

## 4. Zero probabilities, zero occupation, and counterexamples

An exactly zero marginal coordinate forces the corresponding row or column of every feasible local transport plan to zero. Its potential and successor inequalities may be omitted from that local OT block. The implementation correctly uses the cross-product of strictly positive marginal supports. An exactly zero initial coordinate is handled the same way at the dummy root. An inline test with initial mass (1,0) confirmed exact root equality and a root block with one cross inequality plus one value inequality.

This is different from zero **joint occupation under one optimal policy**. If P_t(a|x)>0 and Q_t(b|y)>0, some feasible coupling can put positive mass on (a,b). One policy's zero occupation cannot remove that alternative. Nor may small positive probabilities be thresholded to zero without an error correction. Active parents retain inequalities to inactive children, substituting h there; skipping a child's outgoing solve does not delete its incoming constraints.

The following tiny fixtures separate these issues. All probabilities below are exactly uniform over the listed paths. They are diagnostic finite models, not samples from the frozen process grid.

**Occupation alone fails even for T=1.** Use X paths (0,0),(2,2), Y paths (1,1),(3,3), k=1, delta=1, shift=1/2. The exact V_0 matrix is [[1,3],[1,1]] for p=1 and [[1,9],[1,1]] for p=2. The unique optimal initial coupling is diagonal, with V_root=1. Activate only those two diagonal nodes, with h=0. Their raised values are 1, but inactive anti-diagonal values remain 0, so the lower LP's root chooses the anti-diagonal and returns L=0. It uses two of four nonroot successor inequalities. This is the smallest nontrivial initial transport configuration admitting two different couplings; one marginal with a singleton support has a unique coupling.

**Delayed failure survives the proposed strongest H=2 baseline.** Let e=1/8 and use

    X = [(0,0,0,0), (e,e,e,2)],
    Y = [(0,0,0,1), (e,e,e,3)],
    T=3, k=1, delta=e, shift=e/2.

Both processes have two deterministic persistent branches. The exact unique optimal coupling is diagonal at every time, with V_root=1 for both costs. Activate precisely its diagonal pair nodes in every nonterminal layer. Every active diagonal receives its exact continuation value 1. At time zero, however, h_0^2 has diagonal entries zero and both anti-diagonal entries 2e^p, since the differing terminal cost lies beyond the two-step baseline horizon. The root lower problem chooses the inactive anti-diagonal, giving

| Cost | Exact / feasible-policy U | Verified h^2 root lower L | (U-L)/L |
|---|---:|---:|---:|
| absolute | 1 | 0.25 | 3 |
| squared | 1 | 0.03125 | 31 |

There are six active versus twelve all-active nonroot successor inequalities. Including the four root cross inequalities gives ten versus sixteen. Thus both arc interpretations pass a 75% retained threshold, while both root widths fail 0.5% severely. The h^2 Bellman check has maximum residual zero. The clamped recursion independently gives the same L. Lane C independently reproduced these numbers.

This does not falsify the draft's named finite stochastic grid, which was not run; it falsifies a universal claim that optimal-occupation support suffices to certify the optimal value with this baseline. Activating selected zero-occupation nodes may fix the example. Failure of this particular priority/support rule cannot be promoted to impossibility for all activation or pricing schemes.

**Root and terminal preconditions remain essential.** The existing non-Dirac-root fixture is correct: with next outputs 0,2, initial weights (3/4,1/4) versus (1/4,3/4), the optimized squared/absolute root values are 2 and 1. Replacing the dummy-root OT by the modal pair would instead return 4 and 2. Separately, the public solver accepts malformed h without checking h_T=0: on identical deterministic zero paths of length two, h_0=0,h_1=1 returns 1 despite exact value 0. `verify_subsolution` rejects it. This is missing enforcement of a caller precondition, not a counterexample to the conditional theorem. A cheap exact terminal-zero guard should be mandatory.

## 5. Implementation and numerical certificate boundary

The code realizes the active formulation faithfully under valid normalized model inputs and valid h. The active value floor, correct root cost, positive-support cross products, inactive substitution, and all-active root result match the derivation. The current tests cover h=0 and basic partial/full activation; future-marginal construction and its tests are not yet implemented in the adapter. There is no returned upper policy or exported collection of dual potentials. The returned maximum matrix residual is a float64 diagnostic, not an independently auditable outward bound.

A precise residual correction is available, but its premises must be checked. In real arithmetic with normalized marginals, valid inactive h<=V, and v_T=0, define for each active block z

    b_z = max(0, v_z - P.alpha_z - Q.beta_z),
    d_z = max(0, max_{a,b}(alpha_z(a)+beta_z(b)-c(a,b)-v_next(a,b))),
    epsilon_t = max_{active z at t}(b_z+d_z),   empty maximum = 0.

Use the same formula for epsilon_root, with parent rho, root marginals, and zero stage cost. Weak duality gives v_z<=B_t v_next+b_z+d_z. Backward domination, using inactive h<=V directly, proves

    rho <= V_root + epsilon_root + sum_{t=0}^{T-1} epsilon_t.

Thus subtracting that sum produces a lower bound **if** h validity and every residual upper bound include verified arithmetic errors. This domination proof does not need approximate active floors, although the advertised global-subsolution invariant does. The present max residual alone does not establish the premises: there is no outward arithmetic, independently replayable dual witness, or complete h provenance. Lane C was sent this exact conditional lemma. Any numerical correction, marginal normalization, feasible upper-policy construction and h verification cost must be included in cost to root certificate.

## 6. Executed bounded checks and minimal reproduction

Inline Python ran with `python -B -`, importing the current common-model and active-LP adapters without modifying them. Two existing tiny stochastic/k=2 fixtures, both costs, H=0,1,2,3, and three masks (empty, one chosen pair per layer, full) gave 48 global-versus-clamped comparisons. Maximum h Bellman residual was 0; maximum root difference was 0. These compare formulations using the same numerical OT primitive; the proof above supplies the independent mathematical justification. The delayed, units-error, malformed-terminal and zero-initial-mass fixtures were also executed. No full grid or stochastic confirmation was run.

The following reproduces the main delayed counterexample from the repository directory using only current adapters:

```python
import sys
import numpy as np
sys.path.insert(0, 'adapters')
from common_model import build_window_model, exact_dp, stage_cost, _transport_value
from global_subsolution import zero_subsolution, verify_subsolution, solve_active_subsolution

def future_h(left, right, cost, H):
    h = list(zero_subsolution(left, right))
    for t in range(left.horizon):
        pa = np.eye(len(left.states[t]))
        pb = np.eye(len(right.states[t]))
        for s in range(t + 1, min(left.horizon, t + H) + 1):
            pa = pa @ left.kernels[s - 1]
            pb = pb @ right.kernels[s - 1]
            c = stage_cost(left.representatives[s], right.representatives[s], cost)
            for i in range(len(pa)):
                for j in range(len(pb)):
                    h[t][i, j] += _transport_value(pa[i], pb[j], c)
    return tuple(h)

e = 1 / 8
left = build_window_model([[0,0,0,0], [e,e,e,2]], k=1, delta=e, shift=e/2)
right = build_window_model([[0,0,0,1], [e,e,e,3]], k=1, delta=e, shift=e/2)
active = [np.eye(2, dtype=bool) for _ in range(3)]
for cost, p in [('absolute', 1), ('squared', 2)]:
    h = future_h(left, right, cost, 2)
    ok, audit = verify_subsolution(left, right, cost, h)
    result = solve_active_subsolution(left, right, cost, h, active)
    assert ok, audit
    assert abs(exact_dp(left, right, cost) - 1) < 1e-10
    assert abs(result.lower - 2 * e**p) < 1e-10
    assert result.work.successor_constraints == 6
    print(cost, result.lower, audit, result.work.as_dict())
```

## 7. Required changes before the cheapest decisive probe

1. Freeze the exact h^H formula, p-power units, horizon truncation, common-model marginal propagation, and a fixed-depth or proved consistent varying-depth rule. State h^2>=h^1>=h^0 rather than treating the strongest choice as an unexplained oracle.
2. State the clamped-DP identity and qualify all-active equality as root optimum. Require same-A, same-h, same-OT-kernel clamped DP as the principal formulation ablation. Neither time coupling nor a root certificate alone establishes novelty.
3. Add the H=2 delayed alternative, malformed-terminal guard, zero initial/transition support, and mixed-depth activation fixtures. Lane C supplied an additional fixture showing that work below an inactive ancestor can have no effect on the root lower bound.
4. Freeze the actual active-set selection/tie rule, all counted support scans and baseline work, the treatment of root constraints, and the width denominator. A node fraction cannot stand in for an arc fraction; exact occupation is a heuristic screen, not a best possible active-set oracle.
5. Finish the witness/upper-policy and numerical-audit contract before any original-target certificate claim. A bounded float64 oracle probe remains permissible when labelled accordingly.

The cheapest useful next step is the stated deterministic correctness suite plus the same-A clamped-DP comparison, followed only then by a small frozen activation headroom probe if its complete work budget remains justified. The draft's mathematical mechanism survives review; its novelty and practical certification advantage remain unestablished. Main objections and counterexamples were exchanged with Lanes B and C before finalization.
