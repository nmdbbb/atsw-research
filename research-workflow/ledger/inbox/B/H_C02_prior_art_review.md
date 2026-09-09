# H_C02 prior-art review — Lane B

Date: 2026-09-09. Draft reviewed: `hypotheses/H_C02_lower_policy_frontier.json`, SHA-256 `a292ff5489e2742cd11234bed24b0ec30fed3f230fe4c8f36af509736df571e8`.

**Recommendation: retain as a named AO*-OT adaptation/baseline; revise before any claim of a new mechanism.** The proposed lower-policy frontier is almost exactly AO*'s best-partial-solution expansion on the time-expanded coupling MDP. Correcting H_C01's occupation heuristic is valuable, but is not itself a contribution beyond heuristic MDP search. A cheap development screen can be justified to learn whether that known architecture helps this application. It cannot establish novelty by beating full DP or an exact-occupation mask.

Only this report was written. No grid, registration, candidate implementation, or benchmark was run. This is a bounded primary-source review; absence from the sources inspected is not evidence of novelty.

## 1. Direct primary-source overlap

### AO*/LAO*: the same expansion loop

[Hansen and Zilberstein, *Heuristic Search in Cyclic AND/OR Graphs*, AAAI 1998](https://cdn.aaai.org/AAAI/1998/AAAI98-058.pdf), AO* recurrence on one-based PDF page 2, Figure 1 on page 3, LAO* Figure 2 on page 4, Theorems 1–2 on pages 5–6, and Forward search on page 6.

Figure 1 follows the current marked minimizing policy from the start until an unexpanded tip, expands that tip, and backs up affected ancestors. New tips receive `h`. It prefers the existing marked action when optimal actions tie. The discussion permits batching and prioritizing high probability of reaching a tip. Theorems 1–2 preserve admissible estimates. Thus lower-greedy expansion, stable tie preference, occupation priority, batching, and incremental ancestor updates all have direct precedent. Finite-horizon time expansion is acyclic, so AO* is the closest version; the loop handling in LAO* is unnecessary here.

### BRTDP: lower-greedy exploration and a root interval

[McMahan, Likhachev and Gordon, *Bounded Real-Time Dynamic Programming: RTDP with monotone upper bounds and performance guarantees*, ICML 2005, author PDF](https://www.cs.cmu.edu/~ggordon/mcmahan-likhachev-gordon.brtdp.pdf), Section 2/Theorems 1–2, Section 4/Algorithm 2, one-based PDF pages 2 and 4–5.

Algorithm 2 selects actions greedily against the lower values, explores outcomes weighted by transition probability times the successor upper/lower gap, updates values forward and backward, and stops using the gap at the start state. It returns a policy guided by the upper values. Theorem 2 and its following example distinguish a guaranteed upper-policy value from an optimistic lower-greedy policy, which can perform poorly. Consequently, adding gap-weighted exploration, upper/lower tables, or a root-gap stopping rule would not by itself distinguish H_C02. BRTDP uses sampled trials rather than H_C02's deterministic frontier batches; that implementation difference needs a measured mechanism, not a new label.

### Markov OT: coupling-valued actions already treated explicitly

[Moulos, *Bicausal Optimal Transport for Markov Chains via Dynamic Programming*, arXiv:2010.06831](https://arxiv.org/html/2010.06831), Section 3 and Theorem 1. The action set at a pair state consists of distributions with the prescribed transition marginals; the chosen distribution determines the next pair state. Theorem 1 establishes Bellman characterization, value iteration and existence of an optimal Markovian coupling. The paper considers both discounted and undiscounted infinite-horizon cases under its stated assumptions. Continuous coupling actions therefore do not create an unexplored connection to MDP search.

[Calo et al., *Bisimulation Metrics are Optimal Transport Distances, and Can be Computed Efficiently*, arXiv:2406.04056v2](https://arxiv.org/html/2406.04056v2), Section 2.1/Eq. (3), Section 3/Lemma 1 and Theorem 1, Section 4, Appendix D and Appendix F.2. These cover coupling-valued Bellman optimization, an occupancy LP, and SVI/SPI. Appendix F.2 explicitly credits retaining/warm-starting couplings and discusses positive-support sparsity. Theorems 2 and 6 concern discounted accuracy under their evaluation conditions; they do not directly give H_C02's finite-horizon numerical certificate. Warm starts and sparse transition supports are required fair-baseline features, not novelty credits.

### Sparse OT: a later pricing addition also needs differentiation

[Schmitzer, *A Sparse Multi-Scale Algorithm for Dense Optimal Transport*, arXiv:1510.05466](https://arxiv.org/html/1510.05466), Section 3/Propositions 3.2 and 3.6, Corollary 3.10, Section 4.1/Algorithm 4.1 and Proposition 4.2. These certify omitted dual constraints using shielding and recover global optimality from a sparse restricted solve. Section 5 uses properties of the actual cost to construct the certificate. H_C02's current full-successor backups do not implement this mechanism. A future transport pricing proposal must justify its advantage over applying a valid static certificate to each changed Bellman cost; scalar cost geometry alone does not control the continuation matrix.

## 2. Exact interpretation of H_C02

This mapping is the reviewer's deduction from the draft, using the independently audited H_C01 clamped-DP equivalence.

Let the MDP state be `(t,x,y)`. Its action is a coupling of `P_t(x)` and `Q_t(y)`; its expected one-step cost uses the scalar successor cost. Include an active dummy root whose action couples the two initial laws and incurs no time-zero cost. For a fixed active set, an inactive pair is a terminal tip of the relaxed problem with terminal cost `h_t(x,y)`. An active pair chooses an optimal OT plan against `c_(t+1)+w_(t+1)`.

H_C02's recovered minimizing policy is therefore a **stopped partial policy**. Its frontier consists of the first inactive node on each positive-mass path from the dummy root. Expanding that frontier and reoptimizing is the direct AO* application. No conditional transport plan below an inactive tip is needed to define this lower problem. An arbitrary completion below the tip is a different object and must not determine the lower frontier.

The draft's switch from exact-optimal occupation to lower-policy occupation targets the actual optimistic escape routes. This is a correction from an unsuitable oracle heuristic to established optimistic search. Success on the delayed-alternative fixture demonstrates that correction; it does not distinguish the proposed method from AO*-OT.

Incremental activation makes the root lower bound nondecreasing. It need not strictly rise after every expansion: ties may preserve a different minimizing route, or a zero immediate backup residual may hide a deeper unresolved cost. Requiring a strict positive local residual before any expansion would need a separate termination argument and can prevent revealing delayed costs. Lane A confirmed the first-inactive interpretation and the absence of unconditional strict root ascent.

A stopped lower policy does not itself supply a feasible full-model upper value. A completion needs valid conditional couplings below its tips and evaluation under the original costs; alternatively use a separate feasible upper policy or a proved upper subroutine. If the minimizing partial policy is fully closed at the terminal horizon, its original evaluation equals its lower value and certifies optimality. These are correctness conditions, not novelty claims.

## 3. Direct baseline required before mechanism attribution

Use **incremental AO*-OT on the same common model**, implemented as follows:

1. Use exactly the candidate's baseline `h`, local unregularized OT kernel, support representation, numerical witness checks, deterministic tie rule and upper-policy source. Charge their construction and maintenance to both.
2. Start with the dummy root. Cache exact minimizing local plans and clamped values at expanded nodes. Follow the marked lower policy to its first inactive tips, accumulating first-hit probability when paths merge in the DAG.
3. Expand a fixed batch of those tips. A deterministic one-tip baseline can choose largest first-hit mass, then a lexicographic tie; use the same batch/priority when isolating another proposed primitive.
4. Update affected expanded ancestors in reverse topological order and cache unchanged results. Include all relevant alternatives in each OT backup. Prefer the previous plan when it remains minimizing under the declared tie rule. Do not force the baseline to resolve every previously expanded node on every round.
5. Stop at the same validated root interval or cumulative work budget. Every plan recovery, tie computation, graph/flow traversal and upper-policy update counts.

With those choices, the current H_C02 core and this baseline can be the same algorithm. Identical lower values and expansion traces are then expected; there is no meaningful head-to-head novelty test until a concrete additional primitive is specified.

Keep full exact DP as the practical reference and same-kernel control. Keep exact-occupation, upper-policy and random masks as informative ablations. None replaces AO*-OT as the closest direct baseline. A BRTDP-style OT adaptation using lower-greedy transitions and gap-weighted exploration is the next comparison if the contribution shifts toward gap-based selection; establish its finite-horizon implementation rather than transplanting a theorem mechanically.

Report cumulative OT solves and successor entries visited, including repeats, plus preprocessing, certificates and upper-policy work. Final active-set size alone hides repeated optimization. Compare the candidate's new primitive with that primitive disabled in the same incremental AO*-OT implementation.

## 4. Minimum additional transport mechanism

The minimum is **one concrete, proved transport-specific operation that certifies omission or reuse of work which the incremental AO*-OT baseline still performs**, together with a cost model and evidence that detecting the opportunity costs less than the omitted work. A new search priority is insufficient unless it exploits transport structure in a way that has an independently established effect on root certification and a direct baseline comparison.

A narrow candidate worth formulating is **shared certification of changed continuation costs across multiple parent transports**. All pair parents at a layer use restrictions of the same continuation-cost table but have different marginal rows. Temporal activation changes that table repeatedly. The extra mechanism would reuse this shared change description to certify a batch of existing parent plans and values without solving each OT again or scanning every parent support product.

One exact certificate specification is:

```
old optimal plan: pi in Pi(a,b)
old optimal dual: alpha_i + beta_j <= C_ij
new cost: C'_ij = C_ij + r_i + s_j + R_ij
verified on every positive-marginal cross pair: R_ij >= 0
verified on the incumbent plan: <pi,R> = 0.
```

Then `alpha+r, beta+s` are feasible for the new cost. The incumbent plan's new cost is its old optimal cost plus `a·r+b·s`. The shifted dual has exactly that objective, so the old plan remains optimal and the new value is known without an OT solve. Lane A independently checked this implication. Parent marginal supports and normalized masses must remain unchanged; otherwise plan feasibility needs an additional argument.

This elementary certificate is **not being claimed as a new theorem**. Additive row/column changes and primal-dual complementarity are basic OT/LP structure. The research content would have to be an implementable representation/index or grouping theorem that recognizes many such opportunities from temporal updates, shares the verification, and bounds its cumulative cost. Constructing `r,s,R` or verifying `R>=0` by visiting every entry for every parent erases the proposed mechanism.

Two useful limiting cases set the baseline strength. If a nonnegative update is zero on the cached plan's support, that plan still minimizes at unchanged value; this is ordinary monotone action stability and can already support generic incremental search. If the update is exactly a row-plus-column matrix, the value shift is fixed by the marginals; its identity alone is elementary. A transport contribution requires more than rediscovering either case—for example verified shared processing of structured remainders over many different parent supports, with a declared domain where those remainders occur and a savings argument beyond ordinary dependency caching or warm starts.

Do not weaken the exact claim silently. If only `<pi,R> <= eta` is verified, the shifted dual and incumbent plan give a local gap of at most `eta`; the plan is no longer known to be exactly lower-optimal. Using it to define the frontier then needs a revised selection/stopping proof and root propagation of local error. The cheapest clean test of this additional mechanism should first use the exact certificate, including a negative remainder hidden at an uninspected cross pair and a positive remainder on a used arc as rejection fixtures.

An alternative new mechanism could be a rigorously bounded grouped transport separation procedure or a marginal-based upper completion whose total cost is demonstrably smaller. Those remain proposals. They must face static shielding, warm-started OT, and ordinary partial-state search as appropriate; this review has not established any of them as novel or useful on the required domain.

## 5. Edits and decision boundary

- Add the AO*-OT identity and BRTDP overlap to the card, including the direct baseline. Describe a no-oracle lower-policy frontier as a baseline adaptation until an additional primitive is defined.
- Freeze first-inactive stopping of the lower policy, plan ties, batch rule, cached ancestor updates, upper completion, near-zero convention and cumulative work budget. The exact-oracle mask is a separately labelled comparator and cannot supply candidate stopping information.
- Separate implementation validity, delayed-fixture repair, and quantitative work advantage. Failure to outperform a comparator is not a proof that all transport-aware search cannot improve it.
- Replace the ambiguous phrase “no work advantage ... on any preregistered group” by an explicit per-group quantifier and material-improvement rule. Differentiate a scoped useful group from full required-domain success, under scope v2.
- If the next step remains the literal H_C02 loop, run only a bounded, preregistered evaluation of **AO*-OT applicability**, without a novelty claim. If a transport-specific contribution is sought, revise the card around one explicit omitted-work primitive and its same-implementation ablation before registration.

The sources support a strong overlap verdict. They do not imply an impossibility result or decide whether a carefully implemented AO*-OT adaptation will be practically useful on these finite k-window models.
