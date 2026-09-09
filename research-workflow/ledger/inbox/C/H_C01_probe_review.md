# H_C01 numerical-verifier and work-design review — Lane C

Date: 2026-09-09. Recommendation: **revise before registration**. The valid-h active-subsolution formulation passes the inspected small correctness tests. The proposed oracle screen still lacks the activation rule, upper-bound source, complete cost ledger and decisive comparator needed to interpret its performance claim. This is a v2 review of root-gap tightness versus explicit work, not a full-domain result or an impossibility claim.

## Scope and evidence

Read all files required by `panel_prompts/H_C01_REVIEW.md`, including the v2 contract/bridge, frozen design/amendment, adapters/tests, H_C01 draft, theory/SOTA notes and both cycle-2 verdicts. Archived results remain known development evidence. The model router's `benchmark_design` route is Sol baseline -> Astra/high; no downgrade was used.

Executed only the existing five-test module and nine hand-built diagnostic configurations. All five tests passed in the reported 0.076 seconds; this is test execution time, not a solver performance result. All nine additional configurations matched an independently written clamped backward recurrence. No proposed 16-group grid was run. `probes/global_subsolution_oracle.py` does not yet exist. No implementation, hypothesis, frozen design, registration, run or root-owned state was changed.

Source SHA-256 at review:

| File | SHA-256 |
|---|---|
| `adapters/global_subsolution.py` | `0ea8e024c69061852bc677f7ce389aed89b152e806893970bbb52d14a62c3f31` |
| `adapters/common_model.py` | `4e4b3971c6fda889bda46583606f200b9dc13cac2f7f177fc705cfca0d96ef74` |
| `tests/test_global_subsolution.py` | `ea04a50b5079ed1518da4fc7617e9897741240864fe351ab91a2849bf567045a` |
| H_C01 draft | `a93ffce2d0ddf34e970107077b28dc994a021bcc6838c2e48fbe6af84e329111` |
| `objective.json` | `72f92ab104f9489ee97be10845f0f35f2216197698077581aacd432e2133f7fe` |

## What the implementation actually solves

Let `A_t` be active nonterminal pair nodes, `v_T=h_T=0`, and fix `v_t=h_t` outside `A_t`. At each active `z=(i,j)`, introduce `v_z>=h_z`, unrestricted potentials `alpha_z(x), beta_z(y)` on the positive marginal supports, and impose

```
v_z - sum_x P_t(i,x) alpha_z(x) - sum_y Q_t(j,y) beta_z(y) <= 0
alpha_z(x) + beta_z(y) - v_(t+1)(x,y) <= c_(t+1)(x,y).
```

When a successor is inactive or terminal, its fixed h value moves to the right-hand side. The dummy root has its own value and potentials, initial marginals, zero immediate cost, and every positive initial-support cross pair. The objective maximizes only the dummy-root value. Time zero is not charged; costs are times 1 through T. This matches `common_model.py` and the declared optimized initial coupling.

Every active parent retains all required successor inequalities (`global_subsolution.py:142–179`). Omitting a child's own Bellman block does **not** remove an incoming inequality at an active parent. No policy-support assumption is used to delete such inequalities.

Lane A confirmed the induction under the h assumptions and the stronger computational fact:

```
w_T = h_T
w_t(z) = h_t(z)                         if z is inactive
w_t(z) = OT(P_t(i), Q_t(j), c_(t+1)+w_(t+1))  if z is active
L_A = OT(initial_left, initial_right, w_0).
```

This **clamped backward DP has exactly the same root optimum as the global LP for the same A and h**. The global LP may return other optimal tables because its objective weights only the root. Full activation guarantees root-optimum equality to exact DP; it does not force every returned table entry to equal the exact value table. The clamped recurrence is the mandatory first ablation. “With versus without time coupling” is otherwise underspecified and can falsely attribute a bound improvement to the global formulation.

The current module is a float64 formulation probe, not a usable independently checkable certificate API:

- `solve_active_subsolution` assumes h is valid. It checks h shape/finiteness but does not enforce `h_T=0` or prove the Bellman inequalities. A cheap terminal guard should be required. Lane A's identical deterministic T=1 example with terminal h=1 returns L=1 although the true value is 0; this violates the documented input precondition, not the theorem.
- The solver returns only L, tables, counts and one aggregate inequality residual. It does not export local potentials, variable-bound residuals, primal flows, or a feasible upper-policy witness.
- The residual check at lines 188–190 is a float64 `A_ub x-b_ub` maximum with threshold 1e-7. It is not outward certification. Missing bound-residual checking weakens the promised `v>=h` subsolution invariant; it need not by itself invalidate direct backward domination when inactive h is independently known below V.
- Lane A supplies the relevant correction lemma: for each active block, let b be its positive value-inequality residual and d its maximum positive successor-inequality residual. Under normalized marginals and valid inactive h, subtract `epsilon_root + sum_t max_(z in A_t)(b_z+d_z)` from the reported root value. Applying this as certification requires exported witnesses, outward arithmetic bounds, and verified h; the current scalar floating residual does not meet those conditions.
- `_transport_value` validates and renormalizes marginal roundoff, while the global LP uses supplied marginals directly. Model validation and a shared declared normalization convention belong in the numerical audit. Negative/unnormalized custom kernels are outside the intended model assumptions; zero marginal entries should be excluded exactly, while small positive entries should not silently disappear.

## Exact LP dimensions and the 75% denominator

Write `n_t=|X_t|`, `m_t=|Y_t|`, `a_ti=|supp P_t(i)|`, `b_tj=|supp Q_t(j)|`, `r=|supp mu_0|`, `s=|supp nu_0|`. Define

```
N       = sum_(t<T) n_t m_t
M       = sum_(t<T) |A_t|
E_A     = sum_(t,i,j in A_t) a_ti b_tj
E_all   = sum_(t<T) (sum_i a_ti) (sum_j b_tj)
E_0     = r s
D       = r+s + sum_(t,i,j in A_t) (a_ti+b_tj)
J       = number of instantiated successor inequalities whose child is active,
          including dummy-root successor inequalities.
```

The implementation's counts, in exact integer arithmetic, are:

| Quantity | Count |
|---|---:|
| Active / inactive nonterminal pair nodes | M / N-M |
| Value variables, including dummy root | M+1 |
| Dual-potential variables | D |
| Nonroot Bellman-value rows | M |
| Nonroot successor rows | E_A |
| Root rows | 1+E_0 |
| Total inequality rows | M+E_A+1+E_0 |
| CSR nonzeros | M+1+D+2(E_A+E_0)+J |
| Additional value lower bounds | M |

The bound constraints are passed through `bounds`, not included in `inequality_nonzeros`. LP solver iterations, presolve and factorization work are also absent from these dimensions.

Thus the draft's nonroot-row criterion can be frozen as `E_A/E_all <= 0.75`; it requires no all-pair-arc enumeration. Degrees can be precomputed once from sparse supports, or by a counted scan of dense kernel arrays. The numerator visits active nodes only, and the denominator factorizes by layer. Use Python integers to avoid overflow. Handle the degenerate `E_all=0` horizon-zero case explicitly. Also report root-inclusive successor ratio `(E_A+E_0)/(E_all+E_0)`, all inequality counts, and nonzeros, because a broad initial coupling can dominate work.

This distinguishes parent-node omission from successor-row omission. It does **not** measure omitted unique continuation entries: the same `(t+1,x,y)` cost/value can occur in many parent contexts. Report distinct queried entries and actual repeated traversals separately if either becomes a claim. Neither occupation mass nor pair-node count may replace these row counts. This is precisely the metric distinction that remained unresolved after H_B01C1.

## Work hidden by the current counts

The 75% row ratio is computable cheaply, but the existing adapter has not implemented corresponding sparse total access:

1. `zero_subsolution` allocates every dense pair table, including terminal; `_check_shapes` checks every h entry. Both visit `sum_(t<=T) n_t m_t` entries. `tables=[table.copy() ...]` repeats the full-table copy in the result.
2. Both `np.argwhere(active[t])` passes scan entire layer masks. A compact active-node list would avoid that scan but must itself have a counted construction process.
3. `stage_cost` constructs every dense `n_(t+1) by m_(t+1)` matrix for every layer, even if no node in that layer is active. The root additionally allocates a full zero matrix. Consequently, fewer successor rows currently does not mean fewer scalar cost entries constructed.
4. Each active dual block discovers support again by scanning the full kernel row. These repeated scans cost `sum_A(n_(t+1)+m_(t+1))`, not merely `sum_A(a_ti+b_tj)`. Cache positive supports and count their initial construction if efficiency is claimed.
5. `verify_subsolution` deliberately solves a local transport at **every** pair node. Keep its expensive numerical audit separate from candidate work only if the candidate has another proved/validated h construction and certificate procedure. Calling it inside a deployable solver but excluding its cost would hide a dense sweep.
6. Future-marginal h is not implemented in this module. A straightforward H-depth construction performs `sum_(t<T) min(H,T-t) n_t m_t` scalar-distribution OT evaluations, plus marginal propagation, support aggregation, sorting, allocation and h validation. H=1 can already touch all pair nodes. Scalar one-dimensional OT can be cheaper than general continuation OT, but this is a distinct kernel that must be counted and measured, not assumed free. For fixed nonnegative costs, H=2 dominates H=1 and H=0 pointwise; “stronger of” does not justify free best-of-three computation.
7. The module supplies no U. Count all policy construction/evaluation/repair, occupation propagation, feasibility checks, activation scoring, sorting, repeated LP rebuilds, retained memory and cumulative work over every tried mask/H. Report oracle work separately and also report total probe resources.

Use a work vector, not an invented universal conversion from LP row count to transport time: positive-support visits, unique and repeated cost/continuation accesses, scalar-marginal OT calls and dimensions, general transport LP calls/dimensions with degree-one shortcuts separated, global variables/rows/nonzeros, iterations, certificate work, bytes/peak memory and elapsed time. The clamped baseline uses M+1 transport evaluations, the exact DP uses N+1, and many evaluations may be analytic degree-one cases. Global and local LPs can share SciPy/HiGHS, but their dimensions alone do not equalize factorization effort.

## Executed adversarial fixtures

All path rows below have equal empirical weight within their side. Unless specified otherwise, use `build_window_model(k=1, delta=1, shift=0.5)`, which preserves the listed integer outputs. All use the uncharged initial law and successor costs. Every listed h passed `verify_subsolution`; every LP lower matched a separately implemented clamped recurrence. These are designed correctness/mechanism diagnostics, not draws from the frozen process grid.

| Fixture | Cost | Exact V | Active LP L | E_A/E_all |
|---|---|---:|---:|---:|
| Inactive alternatives, H=0 | absolute / squared | 1 / 1 | 0 / 0 | 2/4 |
| Delayed alternatives, H=2 | absolute / squared | 1 / 1 | 0.25 / 0.03125 | 6/12 |
| Mixed depth, wasted descendant | absolute / squared | 5 / 15 | 0.5 / 0.5 | 2/4 |
| Same budget, earlier nodes | absolute / squared | 5 / 15 | 2 / 5 | 2/4 |
| Node-versus-row count | squared | 0 | 0 | 64/81 |

**Inactive alternatives.** X paths `[[0,0],[2,2]]`; Y paths `[[1,1],[3,3]]`. Initial laws are uniform 2x2. Activate only the two diagonal nodes, with h=0. The true optimal initial coupling is diagonal, value 1. The relaxed root can use the inactive off-diagonal nodes, both fixed to zero, so L=0 even though 50% of nonroot rows are omitted. Work counts are M=2, values=3, duals=8, Bellman rows=2, successor rows=2, root rows=5, nonzeros=25. The current inequality preservation is correct; an invalid “delete inactive child arcs” variant would hide the defect. This fixture should assert the expected loose lower, not only `L<=V`.

**Delayed H=2 alternative.** Let e=1/8, delta=e, shift=e/2. X paths `[[0,0,0,0],[2,e,e,2]]`; Y paths `[[1,0,0,1],[3,e,e,3]]`. Activate the diagonal at all three nonterminal layers. Compute h_t as the sum of one-time conditional transport **costs** for the next `min(2,T-t)` times. The diagonal true cost is 1, while inactive off-diagonal time-zero h values are `2e^p`; hence root L=`2e^p`. With the optimistic U=1, relative width `(U-L)/L` is 300% for absolute cost and 3100% for squared cost. Nonroot rows are 6/12; root-inclusive successor rows are 10/16. The h construction in this diagnostic propagated marginal laws by matrix products and used `_transport_value` for each one-time marginal, keeping arithmetic independent of the global LP. This defeats the claim that exact-optimal occupation plus bounded lookahead is generically a sufficient active set; it does not falsify the unrun random-grid prediction.

**Mixed-depth wasted work.** X paths `[[0,1,2],[2,3,4]]`; Y path `[[0,0,0]]`; h=0. Set `A_0=[[True],[False]]`, `A_1=[[False],[True]]`. The second branch's active descendant sits below an inactive ancestor fixed at zero, so its work cannot improve the root. L=0.5 for both costs. Moving that activation to the ancestor, with `A_0=all True`, `A_1=all False`, gives L=2 absolute or L=5 squared at the same two active nodes/two successor rows. Exact values are 5 and 15. All actual branches have positive optimal occupation. A selector must respect depth/access structure rather than interpreting occupation as an additive budget certificate.

**Node-versus-row metric.** On both sides use nine one-step paths `[[0,s] for s in range(8)] + [[10,0]]`. Current-state outdegrees are (8,1); activate only parent pair (0,0). This retains 1/4 nodes but 64/81=79.012345679% successor rows, missing the draft's 75% row threshold. Counts: values=2, duals=20, Bellman rows=1, successor rows=64, root rows=5, nonzeros=159. This zero-value fixture also requires a declared absolute/zero-gap convention instead of division by zero.

Additional fixtures required before any larger run: the historical k=2 root example with squared value 4/3; non-Dirac initial laws; empty active sets; nested masks proving root monotonicity; all-active equality for nonzero valid h; zero marginal support versus tiny positive support; deliberately invalid terminal h; negative/nonfinite marginals rejected at model boundary; non-Monge continuation costs for both cost families; and bounded-precision witness perturbations checked with the declared correction rule. Zero-cost fixtures and rare high-cost branches should exercise the stopping denominator and positive-mass cutoff.

## Oracle separation and a fully specified small probe

The current draft's phrase “exact occupation selects the active set only” is not sufficient to implement the experiment unambiguously:

- Freeze whether A is every mathematically positive optimal-occupation node, a sorted prefix, or a budgeted selection. Specify tie-breaking, numerical support cutoff, per-layer/global budget, and whether ancestors must be included. An exact optimal policy is not a best oracle over all possible active sets; failure of its support mask cannot rule out another mask.
- There are 16 process/cost/k/delta groups and **32 instances** with two seeds, before the three H choices and mask ablations. Reconcile “every case” with “any grid group”: no unspecified median/aggregation may replace an instance-level pass rule after seeing results. Keep delta=0.3, T=50 and full path counts explicitly out of this screen's scope.
- Specify U. If U is the exact optimal policy/value, that is **additional optimistic oracle use** and must be labelled `oracle_upper`. It is a useful necessary headroom screen for a fixed A,h: any feasible U is at least V*, so failing even with U=V* cannot be repaired by a better deployable upper. It is not a deployable interval or a numerical outward certificate. Otherwise construct a reference-independent feasible policy, charge its full cost, and audit it independently.
- Compute deployable relative width as `(U_safe-L_safe)/L_safe` for positive L_safe. Freeze the zero/near-zero absolute criterion. `(V*-L)/V*` is a different oracle diagnostic and must not silently replace the root-certificate denominator. Never stop a candidate against V*.
- Keep exact tables, plans, value, occupation and tie outcomes in an oracle record. Pass only the explicitly allowed oracle-derived A to the lower solver. Build h from the observed common kernels. Do not use V* to initialize h, repair tables, tune depth/mask outside the declared oracle rule, or seed later candidate runs. If exact plans also supply U, list that extra access explicitly.
- The existing reusable-looking C1 oracle helper is horizon-specific: `probes/envelope_headroom_c1.py:75` uses module constant T=4 and does not return the plans in its public result. A T=5 H_C01 runner must not import it unmodified and assume horizon independence. Its current local-LP count also treats analytic degree-one cases as local evaluations, so labels must be precise.
- Random equal-node-count masks are not matched work when degrees vary. Preserve that selection ablation but add an equal-successor-row or equal-total-work control with a frozen overshoot rule. Match cold-start work and cumulative activation history, not only final LP dimensions.

The cheapest decisive next step is a fixture-scale runner for the exact same A,h under (i) global LP and (ii) clamped backward DP, with the corrected work vector and a declared oracle U. Add the nonzero-H/mixed-depth/degree fixtures above before drawing any grid samples. Their root gaps must coincide. A larger global LP cannot earn a mechanism claim merely by being compared to all-active global LP; it must also survive the clamped and exact backward baselines. Only after these gates and the review edits should root register and run the 32-instance screen. No current evidence justifies a full benchmark.

## Cross-lane exchange and outcome limits

Sent Lane A the correctness/API qualifications and mixed-depth diagnostic. Received confirmation of the active/clamped equivalence, H-step marginal-cost subsolution, delayed counterexample and residual-correction lemma. Sent Lane B the exact factorized row denominator, hidden scans, node/arc mismatch, mandatory clamped ablation and oracle-U ambiguity.

Lane B independently identifies the partial-state recurrence as the central overlap with AO*/LAO*, and supplies an even more direct finite-horizon Bellman-subsolution LP comparison. Its primary-source references and theorem locations belong in `ledger/inbox/B/H_C01_prior_art_review.md`; this lane does not infer novelty from the numerical formulation. In particular, whole-parent block omission here supplies no new verified pricing rule for omitted rows within an active transport.

Required draft edits are the clamped-DP comparator, operational work counts, a fixed A-selection/tie rule, explicit 32-instance quantifier, h construction/validation, U/oracle access contract, root-gap convention and witness audit boundary. Passing a revised oracle screen licenses an implementable activation/pricing probe only. Failure can stop this stated occupation/lookahead active-set direction on declared-domain cost evidence; it cannot establish impossibility for global dual methods, certification or tree algorithms, and cannot mark the original full-domain objective achieved.
