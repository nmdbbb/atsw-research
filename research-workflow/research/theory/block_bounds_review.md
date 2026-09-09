# H-B independent review: successor-block bounds

Prepared 2026-09-09. This is a mathematical review and proposed preregistration, not an implementation, registered experiment, benchmark, or SOTA result. Only this file was written. Read `objective.json`, `WORKFLOW.md`, `adapters/common_model.py`, the H-B theory card, SOTA notes, and the H-A result for context. H-A's failed broad compression prediction is not evidence for or against H-B. Critical objections below were sent to the orchestrator before implementation.

**Verdict:** the pushforward lower bound and conditional-proportion lift are correct. A concrete finite terminating interval algorithm exists. Its useful performance is unproved: computing exact block minima, evaluating product lifts, or refining almost everything can erase all proposed savings. Permit a tiny falsification probe only after registration and independent review. Do not implement a full benchmark on the strength of this lemma.

## 1. Exact common-model target

Write the left/right state spaces as X_t,Y_t, kernels P_t,Q_t, scalar representatives r_t,s_t, and initial laws a_0,b_0. A state is the complete stored k-window. Let p=1 for absolute cost and p=2 for squared cost. The adapter uses

    V_T(x,y) = 0,
    V_t(x,y) = OT(P_t(x,.), Q_t(y,.), c_(t+1) + V_(t+1)),
    c_t(i,j) = |r_t(i)-s_t(j)|^p,
    R = OT(a_0,b_0,V_0).

No time-zero stage cost is added. Every bound below concerns R=AW_p^p on this finite model. It is neither a full-history empirical target nor a population certificate. A dummy root with transition laws a_0,b_0 and zero incoming cost makes the last formula another instance of the same construction.

## 2. Local lower and upper lemma

Fix a parent pair (t,x,y). Let a_i=P_t(x,i), b_j=Q_t(y,j). Partition its positive successor supports into disjoint A blocks and B blocks. Retain all positive mass, however small. Put a_A=sum_(i in A)a_i and b_B=sum_(j in B)b_j.

Assume certified pointwise continuation lower bounds L_(t+1)<=V_(t+1). If

    m_AB <= c_(t+1)(i,j)+L_(t+1)(i,j)  for every (i,j) in A x B,

then OT(a_blocks,b_blocks,m) is a lower bound on V_t(x,y). For any fine coupling pi, its block sums gamma_AB=sum_(A x B)pi_ij have the required coarse marginals, and sum gamma*m <= sum pi*(c+L) <= sum pi*(c+V). Minimize to obtain the claim. The minimum on each rectangle need not be attained at one common transport-feasible collection of pairs; this only makes the relaxation weaker.

For ANY feasible coarse gamma, define

    pi_ij = gamma_AB * (a_i/a_A) * (b_j/b_B),  i in A, j in B.

Then sum_j pi_ij=(a_i/a_A)sum_B gamma_AB=a_i; similarly sum_i pi_ij=b_j. Omit zero-mass blocks, so there is no division by zero. These proportions are specific to the original parent rows. Block population frequencies or a representative parent's proportions are not interchangeable with them.

Suppose a feasible continuation policy at every successor pair has cost J_(t+1)(i,j)<=U_(t+1)(i,j), and

    u_AB >= c_(t+1)(i,j)+U_(t+1)(i,j)  throughout A x B.

The lifted policy has cost at most sum gamma_AB*u_AB. Therefore an optimal coarse plan for u supplies an upper bound and an implicit feasible policy. The lower and upper coarse plans may differ. A block maximum is an upper estimate of a policy's cost, not an assertion that its exact cost was evaluated. Using the lower coarse objective as the lifted policy's cost is invalid.

Repeat the argument backward and at the initial-law root to get L_root<=R<=U_root. Keep max of previously valid lower scalars and min of previously valid upper scalars; retain the upper witness corresponding to the winning bound. Any collection of local conditional couplings defines an admissible bicausal policy on this finite model. Policies may be defined implicitly on coarse rectangles; all required conditional marginal constraints still apply.

## 3. Four counterexamples and failure modes

1. **Continuation destroys scalar ordering, for both costs.** At time 1, left and right outputs are (0,1), with equal masses. Terminal outputs at time 2 are deterministically (0,H) on the left and (H,0) on the right, H>1. Consequently c_1+V_1=[[H^p,1],[1,H^p]]. Scalar-monotone diagonal transport costs H^p; off-diagonal transport costs 1. This is a common-model example: use two equally weighted paths (0,0,0),(0,1,H) versus (0,0,H),(0,1,0), with delta=1 and shift=0.5 to represent integer outputs exactly. In the k=2 variant use random initial values (-1,1), current value 0 on both histories, and opposite deterministic future laws. Equal current outputs then coexist with arbitrarily different continuation costs. Current-coordinate diameter zero does not justify a zero continuation envelope.

2. **A valid product lift can be very poor and expensive.** With a=b=(1/2,1/2), one block, and M=[[0,D],[D,0]], the exact coarse minimum is 0, true OT is 0, and the product lift costs D/2. A tiny positive constant added to all entries makes the relative certificate arbitrarily bad while the optimum is positive. In a larger block, explicitly evaluating sum pi_ij*M_ij accesses every positive fine entry even when the coarse plan has only one arc. A small coarse LP alone does not demonstrate omitted work.

3. **Uniform or shared-parent lifting is infeasible.** For one block, a=(0.9,0.1), b=(0.2,0.8), gamma=1, the correct product lift is [[0.18,0.72],[0.02,0.08]]. Uniform 1/4 entries give both marginals (1/2,1/2). Any reuse must preserve the original conditional proportions or prove a different valid lift.

4. **Unqueried entries and incumbent support.** A black-box block containing an unqueried M_ij can hide a lower value consistent with every queried entry. Without an independent envelope, sampling entries cannot certify its minimum. Similarly the incumbent diagonal policy in counterexample 1 assigns zero mass to the improving off-diagonal alternatives. Incumbent occupation can prioritize refinement but cannot bound the mass that another admissible policy may send there. Locally gamma_AB<=min(a_A,b_B) is universal; incumbent gamma_AB is not.

## 4. An honest envelope oracle without a dense M scan

The most conservative concrete construction uses each process separately. For every state i at time t and future time s>=t, compute the minimum and maximum scalar output reachable with positive probability, denoted ell^X_(t,s)(i), h^X_(t,s)(i). Initialize at s=t with the representative and propagate extrema backward over positive kernel edges. Compute the right-side arrays likewise. Optionally also propagate conditional means mu^X_(t,s)(i)=E[X_s|state_t=i] and mu^Y.

These arrays cost O(T * sum_t nnz(P_t)) and O(T * sum_t nnz(Q_t)) scalar edge operations in a sparse representation, bounded by O(T^2 times the largest layer edge count); storage is O(sum_t (T-t+1)(|X_t|+|Y_t|)). This is real preprocessing, not free. The existing adapter stores dense kernels: conversion/zero scanning costs must also be counted. This construction does not inspect cross-process continuation entries.

Build a deterministic binary hierarchy on each layer's states, sorting by current representative then full history as a tie breaker and splitting by cardinality. Store each node's extrema of the precomputed arrays. This hierarchy groups states for bounds; it does not merge their transition laws. For intervals I,J define d_min(I,J)=max(0,ell_I-h_J,ell_J-h_I), and d_max(I,J)=max(|ell_I-h_J|,|h_I-ell_J|).

For a rectangle A x B at successor time t+1, let I^X_s(A) and I^Y_s(B) be the unions' enclosing reachability intervals at future time s. Then

    m_reach(A,B) = sum_(s=t+1)^T d_min(I^X_s(A),I^Y_s(B))^p,
    u_reach(A,B) = sum_(s=t+1)^T d_max(I^X_s(A),I^Y_s(B))^p.

They enclose c_(t+1)(i,j)+V_(t+1)(i,j) throughout the rectangle. The upper bound in fact covers the cost of EVERY admissible continuation policy, so the independent-transition policy is an immediate witness where no better policy has been constructed. Query cost is O(T-t) scalar interval operations, not |A||B| fine evaluations. Bounds can be very loose and do not imply a useful algorithm yet.

Optional stronger lower oracle: enclose conditional means at each s in block intervals J^X_s(A),J^Y_s(B), and sum d_min(J^X_s(A),J^Y_s(B))^p. Jensen's inequality under each pair's fixed marginal future laws proves validity for p=1,2. This ignores cross-time compatibility and need not become exact even at singleton states. It is a direct bound on c+V; it must NOT be mislabeled a bound on c+L for an arbitrary previously chosen L. One can take the maximum of this independent direct bound and the recursive lower bound, since both bound c+V.

For the recursive construction, a child rectangle table with certified lower ell_AB gives m=c_min+ell_AB. If it was obtained by scanning all fine continuation entries, count that scan. Hierarchical aggregation of already computed fine values saves later repeated accesses but does not retroactively eliminate their construction. Store unresolved rectangles with their reachability envelopes and refined children with improved envelopes. A parent envelope can be updated from child extrema without scanning descendant fine pairs. Singleton bounds can be improved by solving that pair's own successor problem recursively.

## 5. Concrete tiny recursive algorithm

Start from the dummy initial-law root; all unvisited pair rectangles have the envelopes above and an independent-policy witness. Maintain successor partitions as cuts of the two fixed binary hierarchies.

1. At a queried pair, push its own original kernel rows to the current cuts, obtain certified block lower/upper costs, and solve the two coarse transport problems. Store the interval and the coarse upper plan with the proportional lift rule.
2. If the root interval fails the requested tolerance, refine a block contributing to its uncertainty. A deterministic local priority is min(a_A,b_B)*(u_AB-m_AB); tie-break by time and block IDs. This is a refinement heuristic, not a proof of root error allocation. Recompute valid ancestor intervals after each change.
3. Refine a nonsingleton block by splitting a constituent hierarchy node, maintaining genuine marginal partitions. For a singleton successor pair, improve its continuation recursively. At terminal time V_T=0 exactly. Cache all pair results and count every cache miss, hit, scan, and envelope query.
4. For guaranteed termination, after every fixed number of priority steps, refine the first unresolved positive-mass dependency in deterministic depth-first order. The finite singleton expansion plus exact local LP solves recovers full DP. Its worst case is dense DP plus hierarchy/refinement overhead.

Stop certified runs only from L_root>0 and (U_root-L_root)/L_root<=0.005. For zero/near-zero synthetic fixtures request an explicitly registered absolute gap; exact zero can require full refinement. Exact and relative-certified results remain separate. No reference value is available to candidate selection or stopping.

The upper policy can stay factorized. Expanding it solely to verify marginals is unnecessary when the algebraic lift is checked; numerical coarse feasibility still requires correction. For the tiny rational fixtures, exact rational primal/dual witnesses are preferable. The common SciPy LP reference is numerical and its residual checks alone are not an outward-rounded certificate. A floating probe may test enclosure to tolerance, but must label that as numerical validation until witness correction/rounding is audited independently.

## 6. Closest primary prior art and claim limits

[Schmitzer, arXiv:1510.05466v2](https://arxiv.org/html/1510.05466v2), Sections 3.2-3.3, 4.1-4.2 and 5.3, read during this review: short-cuts imply omitted dual constraints; shielding gives global optimality from a suitable sparse restriction; Algorithm 4.1 alternates restricted solves and shielding. Section 4.2 defines hierarchical partitions and pushed-forward measures. Its multiscale efficiency is not asserted as a general theorem. Section 5.3's displayed power-cost construction assumes p in (1,infinity), so it does not directly cover absolute cost. Our inference: applying this method inside Bellman DP requires shielding for the full c+continuation matrix. Scalar-cost shielding alone fails in counterexample 1. Hierarchy, sparse restrictions, pushed-forward marginals, and verification of omitted constraints are established ingredients. H-B's possible contribution would have to be useful conditional-future envelopes and root-directed cross-time work elimination, with their costs included; this review establishes neither novelty nor speed.

[Bontorno-Hou, Nested Optimal Transport Distances](https://arxiv.org/html/2509.06702), Sections 2-3 and the local source audit: quantized path trees and conditional backward OT are already the direct nested-OT comparator. The appropriate additional ablation is a static hierarchical/shielding method applied independently to each common-model Bellman problem. If all fine continuation values are built before static block pruning, the experiment has not established elimination across time.

## 7. Proposed preregistered decisive probe

**Not yet registered or executed.** Freeze all choices before outputs. Keep this a short-horizon work-count probe, not a performance benchmark or replacement for the required T=50 domain.

- Correctness fixtures: the four examples above; a three-stage repeated-history k=2 example; zero and tiny masses; random rational non-Monge local costs embedded in explicitly declared finite conditional models; nontrivial random initial laws. Independent verifier checks each lower envelope, coarse/fine marginals, complete root enclosure, monotone retained bounds, and singleton recovery. Arbitrary cost fixtures test the generic transport primitive; they do not replace the required scalar-cost process fixtures.
- Positive mechanism fixture: duplicated deterministic futures with large blocks and known constant block cost. It must certify without evaluating every fine continuation entry. This tests whether the implementation actually consumes rectangle bounds.
- Breadth screen: T=4, 24 observed paths per side, seeds 20260909 and 20260910, both k in {1,2}, all delta in {0.5,0.3,0.18}, shift=0, and both costs. Reuse exactly the H-A registered laws: AR(1) coefficients 0.7 versus 0.55 with noise scales 1 versus 1.15; second-order coefficients 0.25 versus 0.15 on the latest value and 0.7 versus 0.6 on sin(2*older value), same noise scales, zero start and missing older value zero. Freeze generation code/hash. The screen has 48 small solves; it does not authorize a full-horizon grid.
- Count unique fine c+V entries requested, repeated fine accesses, distinct fine Bellman pair solves, all coarse LP arc variables across every lower and upper solve and every refinement, hierarchy work, one-sided edge operations, policy-bound operations, and peak stored pair records. Root gaps and fallback are mandatory outputs. Count terminal costs too, but separately from recursive continuation evaluations.
- Suggested falsifiable advancement threshold: in EACH of the 24 process/cost/k/delta groups, the two-seed median must omit at least 10% of distinct nonterminal fine continuation entries relative to memoized full DP, and the total transport arc-variable count across all candidate solves must not exceed the exhaustive DP count. Report both seeds individually; no family/cost/cell averaging may rescue a failed group. Require successful root stopping and all correctness fixtures. The 10% threshold is an engineering screen for nontrivial elimination, not a speed implication. Count singleton fallback against the candidate. A zero denominator is ineligible for a savings percentage, not a pass.
- Ablations: identical local solver with exhaustive singleton supports; hierarchy with continuation envelopes replaced by universal zero/global-range bounds; hierarchy built after random permutation of states while preserving all model laws. Record operation changes, not just wall time. Temporal-envelope benefit must be visible beyond static terminal-cost pruning.
- Classification: any invalid certificate is `implementation_invalid` pending proof/implementation diagnosis; a correct implementation that misses the registered work-reduction threshold is `performance_prediction_falsified`; an omitted/unsupported numerical certificate or unusably tiny denominator is `inconclusive`, never a success. Surviving this probe licenses further investigation only. SOTA qualification, full T=50 breadth, held-out replication, and exact/certified arithmetic remain separate gates.

The central unresolved question is quantitative: do these inexpensive temporal envelopes stay tight enough that the certified root tolerates unexpanded successor rectangles across both process and cost families? The proposed probe can reject the concrete construction without disguising dense preprocessing as tree savings.
