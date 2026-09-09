# H_C02 theorem review — Lane A

Date: 2026-09-09. Reviewed draft: `hypotheses/H_C02_lower_policy_frontier.json`, under `tree-adapted-ot-sota-v2`. Recommendation: **revise the lemma and freeze the stopping/frontier/tie contract before registration**. Lower-bound validity and monotonicity survive. The strict-improvement assertion is true for positive first-inactive hitting mass, with fixed old policy decisions; it is false if “reaches” includes descendants behind an earlier inactive node. Strict increase of one old policy's stopped value does not imply strict increase of the reoptimized root lower bound.

Only this Lane A inbox file was written for H_C02. No grid, registration, candidate implementation, or exact-reference-driven activation was run. The proof uses the clamped-DP and baseline results in `H_C01_theorem_review.md`; bounded diagnostic calls below use the existing adapters. Prior-art conclusions remain Lane B's responsibility. None of these results establishes a work advantage, novelty, or full-domain completion.

## 1. Define a stopped lower policy before defining its frontier

Use the finite-model Bellman operator B_t, terminal value zero, costs at times 1 through T, and optimized dummy-root initial coupling established in the H_C01 review. Fix a Bellman subsolution h, and let

    w_T^A=0,
    w_t^A(z)=h_t(z)                    if z is inactive,
    w_t^A(z)=B_t w_{t+1}^A(z)          if z is active,
    L_A=OT(mu,nu,w_0^A).

At the dummy root choose an optimal initial coupling. At each active state pair choose a minimizing conditional coupling for c+w_next. Propagate mass only through active nodes. **Stop at the first inactive nonterminal node on each trajectory, charge h there, and propagate no lower-policy mass beyond that stop.** A path that reaches time T stops with terminal value zero. This is the stopped lower problem, whose optimum is L_A.

Write d_A^pi(z) for first-inactive hitting mass at an inactive node z under a selected policy pi. Its frontier is

    F_A(pi)={z inactive and nonterminal : d_A^pi(z)>0}.

In a recombining k-window DAG, paths may merge and have different stopping depths. Stopped mass is propagated and accumulated through the active graph; ordinary full-horizon occupation computed after arbitrary completions below inactive nodes is not the same quantity. A time-indexed node behind a stop may have positive full occupation but zero first-inactive hitting mass.

A stopped policy is not yet a complete original-target upper policy when its frontier is nonempty. A feasible completion, such as product conditional couplings at inactive nodes, gives a complete policy, but its original cost must be evaluated and charged separately. Its cost generally exceeds the stopped cost.

## 2. Correct strict-improvement theorem and proof

For a fixed completed feasible policy pi, let J_A(pi) be its stopped cost using h at first inactive nodes. The completed policy specifies an initial coupling and a feasible conditional coupling at every nonterminal pair, although J_A ignores decisions after its first stop. This common policy domain lets us compare different active sets unambiguously. The set of all such policies is a finite product of compact transport polytopes.

Let A' contain A. Since h is a Bellman subsolution, h_t(z)<=E_q[c+w] whenever w>=h and q has the prescribed marginals. Backward induction with pi fixed therefore gives

    J_A'(pi)>=J_A(pi) for every feasible pi,
    w^A'>=w^A, and L_A'>=L_A.

Every w^A remains a global Bellman subsolution, hence L_A<=V_root. These claims require no exact reference value and no occupation oracle.

Define the inactive local residual relative to the old clamped table by

    r_A(z)=B_t w_{t+1}^A(z)-h_t(z)>=0.

Suppose pi is lower-optimal for A, z belongs to F_A(pi), r_A(z)>0, and z is added to A'. Keep pi's old active decisions fixed, and use any feasible continuation after its former stop. Then

    J_A'(pi)-J_A(pi) >= d_A^pi(z) r_A(z)>0.

Proof: condition on where the old stopped process first stops. At a newly expanded z, its new continuation cost under the fixed completed policy is at least B_t w_next^A(z): any policy continuation under A' is at least the minimum stopped continuation under A, since A' contains A. Thus replacing h(z) increases the conditional cost by at least r_A(z). Old inactive nodes that remain inactive retain h; all other changes are nonnegative. Averaging with the old first-hit probabilities gives the stated inequality. The same proof allows multiple expanded old-frontier nodes and yields

    J_A'(pi)-J_A(pi)
        >= sum_{z in (A'\A)} d_A^pi(z) r_A(z),

where d is zero for nodes that were not first-inactive stops. More exactly, the difference equals the sum over old frontier nodes of first-hit mass times their new fixed-policy continuation minus h; nodes that remain inactive contribute zero.

This is a strict increase of the old policy's **stopped lower-model cost**. It is not a strict change of that completed policy's original-model cost, which is independent of A. It is also not a theorem about a new policy obtained by reoptimizing old ancestors.

The draft should replace “a lower-optimal policy reaches an inactive node” by “a stopped lower-optimal policy puts positive first-inactive hitting mass on that node.” Without this qualifier, the stated implication fails; see the two-transition singleton fixture below.

## 3. Exact condition for strict increase after root reoptimization

Let

    M_A={pi : J_A(pi)=L_A},
    Delta(pi)=J_A'(pi)-J_A(pi)>=0.

Both stopped objectives are continuous on the compact common completed-policy domain. The following condition is necessary and sufficient:

    L_A'>L_A  iff  Delta(pi)>0 for every pi in M_A
              iff  min_{pi in M_A} Delta(pi)>0.

Proof: if any old-optimal policy has Delta=0, it still attains L_A after expansion, so the new minimum stays L_A. Conversely, if the new minimum equals L_A, a new minimizing policy pi' satisfies L_A<=J_A(pi')<=J_A'(pi')=L_A; it is old-optimal and has Delta=0. Compactness and continuity turn pointwise positivity on M_A into a strictly positive minimum.

A usable sufficient condition, though potentially expensive to check, is

    eta = min_{pi in M_A}
              sum_{z in (A'\A)} d_A^pi(z) r_A(z) > 0.

The minimum uses the **whole old optimal stopped occupation face**. The objective is linear in its terminal hitting masses. This condition guarantees strict root ascent, but is not necessary: zero old residual at one expanded node can become positive after other descendants are also expanded. It also does not imply L_A'-L_A>=eta. A previously nonoptimal policy can become the new optimum with a smaller increase.

For a quantitative elementary bound, enumerate the finite family of policies selecting an extreme point of each local coupling polytope, including the root. This finite family contains minimizers of both stopped problems. Let m be the least Delta over its old-optimal members, and g the positive gap between L_A and its old-nonoptimal members' old values, using g=+infinity if none exist. Then L_A'-L_A>=min(m,g). This is a theoretical margin statement, not a proposed enumeration algorithm. There is no positive gap to all nonoptimal randomized policies: mixtures can approach an optimal policy arbitrarily closely.

In particular:

* Positive r and hitting mass under one chosen optimum are insufficient for root ascent.
* A unique relevant old optimal stopped occupation, with positive mass on an expanded positive-residual node, is sufficient. Uniqueness of the root coupling alone need not settle choices deeper in the active graph.
* Choosing a relative-interior point of the optimal face exposes the union of possible supports, but positive mass there does not mean every optimum must visit that node. It is not a substitute for the universal condition.
* The safe algorithm does not need to enforce strict ascent each round or compute this face minimum. Structural progress is enough for finite completion.

## 4. Deterministic handling of multiple optimum couplings and faces

For a minimal reproducible baseline, order states by time and their full window keys, and successors lexicographically by their full keys. At every active OT and the root:

1. Minimize the original primary linear cost exactly at the mathematical level.
2. On that primary optimal face, choose the lexicographically largest flattened coupling in the fixed successor order. Equivalently, maximize its first coordinate, fix it, maximize the next coordinate, and continue while retaining the primary objective equality and all earlier coordinate equalities.
3. Recover and propagate this selected coupling. At unreachable active nodes a local minimizing plan can be stored consistently, but it does not add root mass. At inactive nodes do not solve an OT merely to complete the lower policy.

This defines a unique plan even on a high-dimensional face, preserves primary optimality, and requires no exact V_root. A practical lexicographic optimizer or provably equivalent deterministic pivot scheme can implement it; all extra work must be counted. Unspecified solver basis selection, fixed random seeds alone, and “whichever solution HiGHS returns” are not this mathematical tie rule. Adding an arbitrary finite epsilon times a secondary objective is also not equivalent unless a valid primary-gap argument protects the primary optimum.

A more expensive optional tie rule can prefer a closed optimal policy: minimize total nonterminal stopped mass on the primary optimal stopped occupation face, then apply a fixed lexicographic rule. If this secondary minimum is zero, the selected policy is already complete and certifies L=U. This may avoid expanding tips belonging only to other tied optima, but its additional LP work is not free and is not required for correctness or finite progress.

Do not conflate deterministic policy selection with an optimal-face guarantee. To certify that all old optima incur positive residual-weighted expansion cost requires the face minimum in Section 3. To discover the union of optimal frontier supports, one can maximize each frontier coordinate over that face and average the resulting witnesses; this is another potentially dense computation. Neither operation is needed by the simple cumulative expansion rule.

In float64 the active primary optimum and its optimal face are only approximate until residuals are audited. Freeze the numerical feasibility/tie tolerances and record their effects. A tolerance-based secondary selection may be a practical priority heuristic, but does not inherit the exact strict-improvement theorem merely by being reproducible.

## 5. Smallest stall and cycle counterexamples

All examples below are valid common-model fixtures for both absolute and squared costs. They are deterministic diagnostics, not draws from the preregistered process families. Unless specified otherwise, use k=1, delta=1, shift=1/2 and uniform mass over the listed paths.

### A. Shadowed reach falsifies the unqualified draft implication

    T=2, X=[(0,0,0)], Y=[(0,0,1)], h=0, A empty.

There is one state pair at each time and one feasible completed policy. Its full occupation at the time-one pair is 1, and that inactive pair has residual r_1=1. Activating only time one leaves the time-zero pair inactive, so both the stopped policy cost and root lower remain 0. The old stopped policy never reached time one: it stopped at time zero. This needs two nonterminal depths to place an inactive ancestor before an expanded descendant, so a singleton two-transition chain is the smallest configuration for this defect.

### B. A positive first-frontier residual need not raise the root minimum

    T=1,
    X=[(0,0),(2,2)], Y=[(1,1),(3,3)], h=0, A empty.

All root couplings are initially lower-optimal with L=0. The lexicographically largest coupling is diagonal, with mass 1/2 at each diagonal pair. The pair (0,0) has residual 1. Activating it raises the old diagonal stopped value from 0 to 1/2. The root nevertheless switches to the still-zero anti-diagonal and L remains 0. The true original value is 1. There must be at least two feasible initial couplings to obtain this tie-switch phenomenon; a 2-by-2 positive marginal support and one transition is the smallest nontrivial transport configuration.

### C. Replacing activity by the current-policy support creates a two-cycle

Use fixture B. With A equal to the diagonal, its values are 1 while inactive anti-diagonal values are zero, so the lower policy is uniquely anti-diagonal. If the next active set replaces A by that policy's anti-diagonal support, the diagonal becomes inactive and the next lower policy is uniquely diagonal. This repeats forever:

    diagonal active -> anti-diagonal policy -> anti-diagonal active
                    -> diagonal policy -> diagonal active -> ...

Every root lower is 0, while V=1. The phenomenon does not depend on tie-breaking after these active sets are formed. It violates cumulative activation. For genuine A_{n+1} containing A_n with at least one new pair each round, such an active-set cycle is impossible; there are only finitely many pairs. Selected policy patterns can recur during strict growth of A, which is harmless unless incorrectly treated as a convergence test.

### D. Requiring a positive current residual can stall before delayed cost

Use fixture A, but inspect the actual first-inactive frontier: it consists only of time zero, whose residual B_0 h_1-h_0 is 0. A rule that expands only positive-residual tips has nothing to do, although V=1 and the root gap remains open. Expanding time zero with zero immediate increase exposes time one; expanding time one next gives L=1. Root values are 0,0,1. Stopping when L does not change would fail after the first valid expansion.

The same defect survives the proposed strongest H=2 baseline. Take

    T=4, X=[(0,0,0,0,0)], Y=[(0,0,0,0,1)],
    h^2=[0,0,1,1,0] across times 0,1,2,3,4.

This h^2 is a verified Bellman subsolution. At time zero, r=0. The successive active sets empty, {time zero}, {time zero,time one} yield L=0,0,1, with V=1. Generally fixed H can hide a terminal cost at time H+2 behind a zero first-frontier residual. The zero-residual plateau is structural, not a floating-point issue.

An H=2 baseline may also already certify a short fixture without any activation, or exact DP may itself require only a few forced transports. Therefore a universal demand for strictly less work than full DP on every deterministic correctness fixture is not supportable. Correctness fixtures and an explicitly scoped efficiency prediction must have distinct gates.

## 6. Safe cumulative expansion and finite completion without a reference

The following mathematical baseline is sufficient:

1. Keep A permanently cumulative and compute the current clamped lower solution with a fixed deterministic OT tie rule.
2. Recover its stopped policy and first-inactive hitting masses by traversing only its active support from the dummy root.
3. If the nonterminal frontier is nonempty and the declared budget/interval gate allows another round, choose one frontier node with maximum hitting mass, breaking ties by earliest time and then lexicographic full-window pair key. Set A to A union {that node}. Do not test its residual first. Fixed-size batches chosen by the same ranking are also safe.
4. Back up the expanded node and affected active predecessors through full positive successor supports, preserving all alternate couplings. Recompute or safely update the root lower witness. Preserve the best valid lower and upper bounds seen.

Each nonclosed round adds a previously inactive node, so at most N-|A_initial| such rounds are possible, where N is the total number of nonterminal pairs. This is a bound on distinct activations and iterations, **not** a sub-DP work bound: repeated backups, plan recovery, tie resolution, and upper-policy evaluation may make cumulative work much larger than one dense sweep.

If a selected lower-optimal stopped policy has empty nonterminal frontier, all of its positive-mass trajectories reach time T through active pairs. Extend it arbitrarily at unreachable nodes. It is then an original-model feasible policy with cost exactly L_A. Consequently

    L_A <= V_root <= U_selected=L_A.

This proves exact termination without knowing V_root. It is enough that one selected lower-optimal policy is closed; other tied lower policies may still have nonempty frontiers. Selecting or searching for all of them is unnecessary for this certificate. When the frontier remains nonempty, a valid original-cost upper policy and the root interval, not lack of lower progress, determine whether to stop at the desired accuracy. Exhausting the budget returns the valid interval with a budget-exhausted status.

For the proposed relative gate, (U-L)/L<=0.005 is sufficient when L>0. Freeze a separate near-zero convention, including exact U=L=0, instead of dividing by zero or consulting V_root. Product-completing the lower policy can supply an upper without any exact optimal-reference call, but evaluating its original costs and all completion/propagation work must be charged. An existing independently feasible upper policy can also be retained.

Lower validity is robust to using an approximate policy merely as the frontier priority: the active mask may be arbitrary, so a poor policy only affects efficiency. The exact strict-ascent and closed-policy-equality arguments require the stated exact optimizing/evaluation premises, or a corresponding residual-aware version. In particular, a numerical primal OT objective alone is not a certified lower value: a feasible primal plan bounds a local minimum from above. Export and validate local/root dual witnesses, preserve h provenance, and use outward residual correction before asserting a mathematical lower certificate. The H_C01 review supplies a conditional sum-of-layer-residual correction.

At an algorithmic level, safe asynchronous backups are also possible. If the current table is a Bellman subsolution, increasing one node to a validated dual lower value for its current successor table, while retaining the old node value when larger, keeps the table a subsolution. The node stays below its Bellman backup; predecessors only see larger successor bounds. Revalidating the root dual preserves a root lower bound during partial ancestor updates. This can avoid demanding a complete new sweep merely for validity, but proving and measuring efficient transport reuse is a separate mechanism question.

## 7. Executed diagnostics and reproducibility

An inline `python -B -` diagnostic imported the current `common_model` and `global_subsolution` adapters. For both costs it evaluated the empty/singleton/diagonal/anti-diagonal active masks in fixture B, the four masks of fixture A, and the first three activation states in the H=2 delayed singleton. Results were:

| Fixture | Lower values | Independent common-model exact value |
|---|---|---:|
| T=1 tie / replacement cycle | empty 0; one diagonal node 0; diagonal 0; anti-diagonal 0 | 1 |
| T=2 shadowed / zero-residual stall | empty 0; descendant only 0; first only 0; both 1 | 1 |
| T=4 H=2 plateau | empty 0; first only 0; first two 1 | 1 |

The reported first/second frontier residuals for the T=2 chain were 0 and 1. Both H=2 baseline checks passed with maximum residual zero. These were post-hoc mathematical diagnostics, not a performance screen. Exact values were used to check the fixtures and did not choose an adaptive candidate sequence.

Minimal reproduction for the false shadowed-reach implication and plateau:

```python
import sys
import numpy as np
sys.path.insert(0, 'adapters')
from common_model import build_window_model, exact_dp
from global_subsolution import zero_subsolution, solve_active_subsolution

def model(paths):
    return build_window_model(paths, k=1, delta=1, shift=0.5)

left, right = model([[0,0,0]]), model([[0,0,1]])
no = np.zeros((1,1), dtype=bool)
yes = np.ones((1,1), dtype=bool)
for cost in ['absolute', 'squared']:
    h = zero_subsolution(left, right)
    results = [solve_active_subsolution(left, right, cost, h, masks).lower
               for masks in [[no,no], [no,yes], [yes,no], [yes,yes]]]
    assert np.allclose(results, [0,0,0,1], atol=1e-10)
    assert abs(exact_dp(left, right, cost)-1) < 1e-10
    print(cost, results)
```

## 8. Required draft edits and scope conclusion

Freeze first-inactive stopping, positive hitting mass, cumulative activity, and deterministic primary-optimal coupling selection. Replace the current strict-improvement sentence by Section 2 and explicitly retain the optimal-face qualification in Section 3. Permit zero-gain activation rounds. Treat a repeated policy or unchanged L as a diagnostic, not a stopping certificate. Charge all tie/face queries and repeated backups, and keep original-cost upper-policy construction independent of the exact reference.

Separate invalid-certificate failures from a valid but inefficient rule, and define per-fixture correctness versus per-group work gates before results. In particular, the current phrase “fewer ... than full exact DP and exact-optimal-occupation activation” cannot be a universal strict inequality on every easy deterministic model. Completing the delayed fixture demonstrates correct handling of alternate lower policies; it does not by itself demonstrate a transport-specific algorithmic contribution.

The safe stopped-frontier expansion theorem is valid and implementable without reference access. It supplies finite completion, not a prediction of small cumulative work. A scoped probe can assess whether this defined rule earns its cost; its failure would not establish an impossibility result for tree OT, broader heuristic search, or root certification. Main objections, exact conditions, and diagnostic fixtures were communicated to root and Lane C during review; the transport-update lemma proposed by Lane B was also checked independently.
