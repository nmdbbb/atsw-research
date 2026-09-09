# H_D01 prior-art review — Lane B

Date: 2026-09-09. Draft reviewed: `hypotheses/H_D01_monotone_transport_reuse.json`; SHA-256 `aa53b645286396c3a563465901d592a739130bd6b361a7cd9618786f1327f724`.

**Recommendation: treat the current H_D01 as an implementation optimization and direct baseline, with novelty unestablished.** Its certificate is elementary objective-cost sensitivity. Its inverse-support propagation is a specialization of reverse dependencies for the currently selected minimizing MDP action. The present card does not yet identify a distinct transport algorithm. It may nevertheless be practically worthwhile: applying a known stability test before an expensive OT call is a legitimate optimization to measure.

A potentially distinct contribution would need an additional, explicit multi-parent grouping or update mechanism, with an amortized work result and measured savings over the generic reverse-dependency baseline. Neither an inverted support map nor a high skip rate on designed miss events establishes that contribution.

Only this report was written. No grid, registration, solver installation or numerical experiment was run by Lane B. This bounded review used primary sources; it does not establish completeness of the literature or impossibility of a new method.

## 1. Primary sources and their exact relevance

### Minimum-cost flow optimality and reoptimization

[Bertsekas and Tseng, *The RELAX Codes for Linear Minimum Cost Network Flow Problems*, Annals of Operations Research 13 (1988), 125–190, author PDF](https://web.mit.edu/dimitrib/www/BT_Relax_1988.pdf), Section 1, Eqs. (3)–(13), especially complementary slackness (10)–(12), printed pages 126–127; Section 3 gives the relaxation method. Primal feasibility plus flow/price complementary slackness characterize optimality. Preserving that certificate after a cost modification is therefore standard LP/min-cost-flow reasoning. The paper also documents reoptimization and sensitivity capabilities. This is the relevant foundation for H_D01; no new perturbation theorem is required for nonnegative changes supported only on zero-flow coordinates.

[Bertsekas and Tseng, *RELAX-IV: A Faster Version of the RELAX Code for Solving Minimum Cost Flow Problems*, LIDS-P-2276 (1994), author PDF](https://web.mit.edu/dimitrib/www/Bertsekas_Tseng_RELAX4_!994.pdf), introduction, one-based PDF page 3. It explicitly discusses reusing good dual prices for reoptimization/sensitivity and contrasts this with difficulties in preserving primal bases when data change. Thus retaining dual information across related flow problems is established practice. H_D01's fixed-marginal, monotone-cost restriction is simpler than general changing-data reoptimization; the cited discussion does not itself give a multi-parent adapted-OT index.

### Dynamic discrete OT

[Xu and Ding, *A Novel Skip Orthogonal List for Dynamic Optimal Transport Problem*, arXiv:2310.18446v5 (2024)](https://arxiv.org/html/2310.18446v5), Section 2.1/Eq. (5), Section 3, Sections 4.1–4.2 and Appendix H. Section 4.1 reuses a solution under point-position, weight, insertion and deletion updates; cost changes trigger primal network-simplex reoptimization. Section 4.2 maintains adjusted costs for pivot selection and updates, using the Section 3 structure. Appendix H.1/Theorem H.1 gives expected linear time for `Cut`. The small number of pivots is an instance-dependent premise/empirical observation, not a universal constant bound per update.

**Boundary:** the paper's geometric position updates commonly change a full row/column of one transport matrix; H_D01 has sparse nonnegative continuation changes shared across many different parent marginals. Its data structure is not the proposed inverse-support map. This distinguishes update models, but does not make simple inverse indexing novel. It is a strong local reoptimization comparator if adapting its update interface is justified and counted; it is not an automatically compatible adapter for arbitrary Bellman costs.

### Reverse dependencies and incremental action-value updates

[Van Seijen and Sutton, *Planning by Prioritized Sweeping with Small Backups*, ICML 2013, PMLR 28(3), 361–369](https://proceedings.mlr.press/v28/vanseijen13.html); [primary PDF, titled *Efficient Planning in MDPs by Small Backups*](https://proceedings.mlr.press/v28/vanseijen13.pdf), Section 3.1/Lemma 3.1 and Theorem 3.1, Section 4 and Section 5/Algorithm 2.

Section 3 maintains action values by individual successor increments. Section 4 defines the reverse predecessor set by positive transition probability and propagates one changed successor to its predecessor state-action pairs. It also caches the greedy action to avoid unnecessary maximization. Section 5 combines these reverse backups with prioritized sweeping. Consequently, sparse successor-change propagation through positive-probability reverse dependencies is direct prior art. Their finite-action reward formulation is not H_D01's transport implementation; the generic monotone-action deduction below is the precise bridge.

[Hansen and Zilberstein, *Heuristic Search in Cyclic AND/OR Graphs*, AAAI 1998](https://cdn.aaai.org/AAAI/1998/AAAI98-058.pdf), Figure 1 and surrounding AO* discussion, one-based PDF page 3. The algorithm caches marked minimizing actions, updates affected ancestors, prefers the current marked action in a tie, and discusses limiting updates using marked connectors and changed values. This makes an intentionally exhaustive ancestor replay an ablation, not the strongest incremental-search baseline.

### Markov OT and static sparsity

[Calo et al., *Bisimulation Metrics are Optimal Transport Distances, and Can be Computed Efficiently*, arXiv:2406.04056v2](https://arxiv.org/html/2406.04056v2), Section 2.1/Eq. (3), Appendix B.1 and Appendix F.2. Couplings are already MDP actions, and the paper explicitly credits maintained coupling warm starts and describes exploiting positive transition supports. The discounted setting does not directly supply finite-horizon certificates, but neither coupling reuse nor positive-support storage is new as a general principle.

[Schmitzer, *A Sparse Multi-Scale Algorithm for Dense Optimal Transport*, arXiv:1510.05466](https://arxiv.org/html/1510.05466), Section 3/Propositions 3.2 and 3.6, Corollary 3.10, Section 4.1. Shielding gives globally valid certificates while omitting transport inequalities. It is relevant if H_D01 broadens from support-miss detection to local repair or pricing. Any geometric shortcut must apply to the full updated continuation cost. Static shielding and the current zero-support test are distinct operations; both belong in the comparison map.

## 2. What the H_D01 lemma actually contributes

The following deductions are elementary mathematical analysis of the card, not an assertion that a source contains its exact code.

For a standard-form LP `min c·x` with `Ax=b, x>=0`, let `x*` be optimal. For `d>=0` with `d·x*=0`, every feasible `x` satisfies

```
(c+d)·x >= c·x >= c·x* = (c+d)·x*.
```

Thus the optimum and selected optimizer are unchanged. If `y*` is a feasible optimal dual with `A^T y* <= c`, it remains feasible under `c+d`, certifying the unchanged objective. H_D01 is this argument with a transport LP and `d=Delta`. The result does not require a tree, OT geometry, a rank condition or a unique optimizer. It concerns the positive primal support; a degenerate basic variable can be zero, so equating “outside support” with “nonbasic” would be inaccurate.

The same omission criterion is available directly in a generic MDP. Let

```
Q_old(a) = g(a) + P_a v,
V_old = min_a Q_old(a),
a* in argmin_a Q_old(a),
v' = v + Delta, Delta>=0.
```

All action values weakly increase. If `P_(a*) Delta=0`, then

```
Q_new(a) >= Q_old(a) >= V_old = Q_new(a*)
```

for every action. The incumbent action remains minimizing. Set `P_(a*)=pi` and this is exactly H_D01. No explicit enumeration of alternative coupling actions is needed: monotonicity bounds all alternatives at once. Transport duals make the certificate auditable but do not alter this generic reason why the action can be retained.

The inverse-support map

```
I(child_pair) = {cached parents whose selected plan gives that child positive mass}
```

is therefore the reverse-dependency graph of selected actions. With a sparse nonnegative change set `D`, only parents in `union_(e in D) I(e)` require the proposed fallback. Maintaining such an inverse graph is a sensible way to implement the known operation. Calling it “inverse-support propagation” does not introduce a new data-structure principle.

This is stronger evidence of overlap than observing a vaguely similar paper title. The whole card's proposed decision can be derived without using transport marginal structure beyond having a nonnegative transition distribution for the chosen action.

## 3. Closest baseline and necessary ablations

The closest direct baseline is **incremental AO*-OT with cached selected-action reverse dependencies and monotone action-stability checks**. It should share the candidate's model, initial cache, update trace, monotonicity guarantee, exact OT kernel, witness policy, tie rule and upper/root evaluation. It propagates each child increment through the cached selected plans, keeps an unaffected minimizing action, and invokes the local solver only when that action receives a positive cost increment. With the present card, this baseline and H_D01 can be the same algorithm.

Do not manufacture a distinction by requiring the baseline to scan every parent, revisit all marginal cross-pairs, discard cached optimality information or restart every local LP. The following controls remain useful but answer narrower questions:

| Control | Question it answers |
|---|---|
| Incremental AO*-OT with forced solves on all affected parent blocks | Benefit of the known monotone stability optimization in this application |
| Cached support scan per affected parent | Benefit of inverting the support relation rather than scanning it |
| Selected-action inverse dependency baseline | Whether anything in H_D01 goes beyond the existing generic implementation principle |
| Basis/dual warm-started local min-cost flow on hit blocks | Whether cold fallback exaggerates savings or hides reoptimization opportunities |
| Dynamic OT structure, after an audited update adapter | Whether a more general local dynamic solver is competitive on the same cost-update workload |

A same-kernel ablation is sufficient for early mechanism measurement but not a final fastest-comparator claim. If a benchmarked kernel cannot accept a basis or useful dual warm start, record that limitation and keep the appropriate dynamic-solver comparison unresolved. Do not treat lack of an adapter as a win.

Freeze plan tie handling and replacement. Retaining one minimizing plan gives valid reuse; changing to another minimizing plan changes the inverse graph and future hit rates. Tests of different witness-selection strategies are additional algorithms, not free choices informed by audit optima.

## 4. What could still be distinct

There is a meaningful distinction in **workload**, not yet a demonstrated distinction in algorithm: many parent OT problems share one changing continuation table; their supports change when a fallback chooses a new plan; and changes can cascade across a time-indexed recombining DAG. This may enable a specialized implementation or instance-dependent result.

For example, let `S` be total stored support incidences, `D_q` the changed successor entries in event `q`, `L_q=sum_(e in D_q)|I_q(e)|`, `H_q` the unique hit parents and `R_q` the support insertions/deletions after their fallback solves. An ordinary inverted-list implementation already suggests event work of the form

```
O(|D_q| + L_q + R_q) + sum_(p in H_q) local_reoptimization_work(p)
```

plus indexing, deduplication, scheduling, materialization and verification costs; storage is `O(S)` with sparse maps. This is an implementation accounting bound, not a new theorem about adapted OT. It must include initial solves/index construction and every later event. A genuine additional contribution would need to beat this baseline by exploiting a proved shared structure—for example aggregating repeated dependency groups so they need not be enumerated individually, with a fully specified applicable domain and bound. A generic hash-map inversion alone does not meet that standard.

Another possible direction is handling support **hits** without a full solve by maintaining an alternative optimal-face witness or repairing a small residual subproblem. That would be more substantive than detecting misses, but has closer overlap with dynamic min-cost flow and LP sensitivity, so it needs the stronger local comparisons above. The row/column-shift certificate proposed in the H_C02 review is also elementary; a fast, shared method for finding and verifying its nonnegative remainder would be the unresolved contribution.

No such grouping, face-maintenance method or transport-specific amortized theorem is specified in H_D01 today. The conservative allowed claim is an application/evaluation of known monotone certificate reuse. A favorable fixture result may justify further development, without settling novelty.

## 5. Probe and certificate issues affecting interpretation

Lane C's metric objection is material: an inverse support index enumerates hits, not all affected parent blocks or all misses. The skip denominator must come from a defined all-dependency controller or a separately labelled audit trace. Its construction and queries are charged whenever used by the candidate. Reporting only touched index lists cannot establish a fraction of omitted eligible solves.

Use separate event groups for support misses, support hits, mixed events, one-successor controls and degeneracy. Positive performance thresholds cannot reasonably be imposed on every correctness control: a used-arc update intentionally defeats the test, and a deterministic parent with one available successor has no support-miss opportunity within its feasible rectangle. Declare which groups bear the 50%/25% predictions and what primitive operations define the denominator. A scalar index visit and a skipped constraint entry are different cost units; their ratio is a diagnostic, not a time reduction.

Charge witness replay proportionately and explicitly. With truly certified old witnesses, known fixed marginals and a certified globally nonnegative update, the old dual remains feasible without rechecking every old inequality. Conversely, if every reuse replays the entire dense primal/dual block, the projected index advantage may vanish. Both choices are valid engineering designs; neither cost may disappear from accounting.

The float64 cache needs an honest statement. Feasible primal/dual witnesses with an existing nonzero gap preserve an interval under disjoint updates; they do not become exact because a fresh float64 solve agrees within `1e-9`. Primal repair can introduce support that must be included in the index. Tiny positive masses cannot be discarded without an error budget. These issues were also confirmed by Lane A.

The index/version state must remain complete across skipped events. If a parent skips several misses and is later hit, its fallback must use **all** accumulated child-cost changes, including changes previously absent from its cached plan support. Updating only entries ever sent to that parent creates a stale cost matrix. Define one authoritative continuation table or an auditable versioned change log and include the cost of materializing the current local matrix. Also test support replacement, stale inverse entries, duplicate changed children, zero-mass successors and a hidden negative update that must reject the monotone rule.

A reused optimizer need not be the only optimizer. A support hit does not prove that the optimal value changed or that no other zero-increment optimal plan exists. For example, with a zero `2x2` cost and uniform marginals, a cached diagonal plan is hit by positive diagonal increments while the anti-diagonal remains a zero-cost optimizer. This limits a single cached plan's hit rate; it does not invalidate safe fallback or establish a general obstruction.

## 6. Decision and edits before registration

1. Add the explicit LP/min-cost-flow certificate and the generic MDP stability reduction to `nearest_prior_art`, with the reverse-backup source. Declare the present lemma and inverse-list operation as known ingredients.
2. Add the selected-action reverse-dependency baseline. Retain forced-resolve and scan-versus-index versions as performance ablations, not as substitutes for the closest method.
3. Define eligible events, cost units, chronological update trace, tie policy, cache support/repair, versioning, fallback materialization and candidate-versus-audit work before the probe.
4. Limit any initial conclusion to correctness and applicability of monotone reuse on the declared fixtures. A failed skip/work threshold stops only that performance prediction; a passing threshold does not demonstrate a new transport mechanism or a full-domain algorithm advantage.
5. If novelty remains a project requirement for the next card, specify an additional grouping/repair operation and a comparison that cannot be reduced to the same generic reverse-dependency routine. Otherwise it is appropriate to keep H_D01 as an engineering baseline optimization and move research effort to a genuinely different unanswered mechanism.

The audit supports strong prior-art overlap and a precise direct baseline. It leaves practical performance and any broader contribution unestablished.
