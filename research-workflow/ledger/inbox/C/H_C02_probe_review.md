# H_C02 cheapest-fixture probe review — Lane C

Date: 2026-09-09. Recommendation: **revise into a deterministic fixture probe before any registration or grid**. First-inactive lower-policy expansion repairs the known delayed alternative. Root improvement need not occur at every expansion, and a small final active set can still require more cumulative work than full DP. The next claim must distinguish correctness/progress, activation choice, and total certification cost.

Reviewed draft SHA-256: `a292ff5489e2742cd11234bed24b0ec30fed3f230fe4c8f36af509736df571e8`. Scope is `tree-adapted-ot-sota-v2`, objective hash `72f92ab104f9489ee97be10845f0f35f2216197698077581aacd432e2133f7fe`. Read the H_C02 draft, H_C01 panel/theorem/probe reviews, current common-model/active-LP adapters and policy-pool policy routines. Existing development evidence is known, not blind confirmation.

Only this report was written. Ten small deterministic configurations were evaluated in an in-memory diagnostic: five fixtures under both absolute and squared costs. No implementation file, registry, grid, large run or root-owned state was modified. The deterministic design below is a proposed specification, not a claim that the H_C02 draft already defines it.

## 1. Specify one operational rule

Freeze the following before writing a runner:

1. Use the normalized common finite k-window model, costs at times 1..T, optimized zero-cost dummy-root initial coupling, and target units `V=AW_p^p`. Keep h fixed during an activation run; separate H=0,1,2 runs and count each run's construction. The fixture core uses H=0 and H=2 rather than an unexplained best-of-three choice.
2. Start with `A_0=empty` and permanently accumulate activations. The dummy root is always solved. Replacing A by the latest policy support can cycle; a shrinking mask is a different algorithm.
3. At round q, compute the exact clamped recurrence in the represented arithmetic and save every active local minimizing plan and the root plan. Recovering the same plans in an additional OT solve would be duplicate work and must be counted. Never solve an inactive local OT merely to estimate its residual for selection.
4. Propagate root-plan mass forward through **active nodes only**. Stop a path at its first inactive nonterminal pair node and accumulate its hitting mass there. Coalesce repeated arrivals at the same time-indexed pair node before ranking. Terminal arrivals are closed mass. The resulting set `F_q` is the lower-policy frontier. Full-policy occupation beyond the first inactive node is a different object and cannot justify the stated progress lemma.
5. Unless the stopping rule succeeds, activate exactly one frontier node, maximizing its hitting mass; break equal-mass ties by increasing `(time, left_state_index, right_state_index)`. State order is the stable lexicographic order of the model's state keys, never hash-map iteration order. No residual weighting, empirical gap weighting, value-of-information scoring, or hidden backup of all frontier nodes is permitted in this first rule.
6. Use permanent union `A_(q+1)=A_q union {selected}`. Expand even when the selected node's eventual Bellman residual is zero. A strict-positive-residual requirement can stall before later costs become visible. For a separate batch ablation, freeze the top-b frontier nodes from the same pre-expansion frontier; do not secretly recalculate scores during the batch and call it the same rule.
7. Stop on the declared root interval test or resource limit. Absence of strict root improvement is logged as a plateau, not immediate mechanism failure. A nonempty frontier plus no new selected node is an implementation error. A closed lower-optimal stopped policy should yield an equal-cost feasible full policy in exact arithmetic; a material gap with an empty frontier is an audit failure.

Lane A confirms finite expansion under this rule on a finite graph: every nonclosed round adds a node, so there are at most N nonterminal activations. This is a termination bound, not a useful complexity bound or strict-ascent guarantee. If a first-inactive node has hitting mass d>0 and backup residual r>0, the old stopped policy improves by at least dr after expansion; reoptimization may switch to a tied alternative and leave the root value unchanged. A full-trajectory reached descendant below an inactive ancestor does not have this guarantee.

## 2. Deterministic transport ties without an arbitrary perturbation

The cheapest fixtures need only positive support shapes 1-by-m, n-by-1 and 2-by-2. Use the same analytic transport kernel for candidate, clamped baseline and full DP:

- If one side has support size one, the coupling is unique: `pi=a outer b`.
- For 2-by-2 normalized marginals, write `x=pi_00`, `lo=max(0,a_0+b_0-1)`, `hi=min(a_0,b_0)`. Its objective slope in x is `s=C_00-C_01-C_10+C_11`. Select x=hi if s<=0 and x=lo otherwise. The s=0 choice maximizes the first row-major coupling coordinate and fixes a canonical diagonal preference for uniform marginals.
- The fixture probabilities, locations and costs are dyadic, so this tie comparison is exact in their represented arithmetic. Pin shape/order and record the chosen plans. Do not add a small cost perturbation that changes the actual primary optimization target.

For later general-support LPs, “deterministic” requires a written tie contract. Pinned single-thread solver/version, canonical input ordering and saved plans provide reproducibility within that stack; they do not prove a mathematically unique optimizer across versions. If lexicographic optimization of the true optimal face is used, every secondary solve and its tolerance/face validation belongs in the work ledger. A chain of secondary LPs is not free selection. The fixture kernel avoids this expense entirely and should not be presented as a general transport implementation win.

## 3. A reference-independent upper bound and stopping rule

At each round, complete the saved lower policy to a feasible full dynamic policy: use its saved root and active-node plans; at every encountered inactive node use a fixed north-west coupling in canonical state order, and continue to time T. Evaluate original stage costs by forward mass propagation. This gives a concrete feasible U without V*, without additional optimization at inactive nodes, and without a full SVD-policy sweep. Define `U_best` as the minimum of all evaluated feasible upper-policy values so far and retain the associated witness. A policy from an earlier round remains a valid upper bound.

Sparse north-west construction can use at most a+b-1 positive arcs per local support, but actual allocation, scans, zero handling, plan caching and full-policy flow must be charged. The existing `nw_plan` implementation constructs a dense matrix; using it unchanged requires counting those entries. The current policy-pool `evaluate_policy` is a full dense backward evaluation, so importing its U cannot be described as a free or sparse upper.

For this finite float64 fixture probe, freeze the diagnostic success test as `U_best-L<=1e-10` OR `L>0 and (U_best-L)/L<=0.005`, with explicit feasibility checks and both raw endpoints reported. All scales in the proposed fixtures are fixed and their arithmetic is simple. Label this a numerical development enclosure, not an outward certificate. A production certificate requires safe endpoints, outward witness arithmetic and a preregistered absolute criterion in target units. Do not replace the denominator by V* or `max(V*,tiny)`.

Exact DP is run only after the candidate trace is closed and recorded. Containment checks, all-active references and the H_C01 global-LP check belong to a separate oracle/audit phase. An exact-optimal-occupation mask is an explicitly oracle ablation executed afterwards, not a permitted candidate input. Exact values/tables must not seed h, choose H, select batches or stop the candidate.

## 4. Cumulative, complete work accounting

Maintain an append-only event log for the standalone run. Every event has a round, phase, operation, support dimensions, scalar/entry count, elapsed time and cache hit/miss status. Report the cumulative prefix at every returned `(L,U_best)`; final active size alone is not a cost metric.

Let `d_z=a_z b_z` be the full positive successor product at nonroot pair node z; root product is `d_root=r s`. For a repeated full clamped sweep with saved plans, round q incurs

```
K_lower(q) = 1 + |A_q|                 transport evaluations
E_lower(q) = d_root + sum_(z in A_q) d_z  positive cost-entry visits
K_lower_cumulative(Q) = sum_(q=0..Q) K_lower(q)
E_lower_cumulative(Q) = sum_(q=0..Q) E_lower(q).
```

For one new activation per round, `A_0=empty`, and Q activations, this is `(Q+1)(Q+2)/2` transport evaluations, including the final solved round. The final unique parent-context product count is only `d_root+sum_(z in A_Q)d_z`; neither that number nor the final node fraction can replace the cumulative sum. Full DP is `N+1` evaluations and `d_root+sum_z d_z` entry visits. Separate root, analytic one-sided, analytic 2-by-2 and general LP evaluations. In the executed fixtures, no general transport LP is required by the matched analytic kernel.

For incremental implementations replace `A_q` by the set of actual backed-up nodes `B_q`, retaining each re-solve/version. An unchanged cached value/plan may avoid an OT call but still incur a dependency query, certificate check, entry scan or flow traversal. The log must reflect the actual operation, not infer work solely from masks.

The complete ledger must include all of these categories:

| Phase | Required counts and boundary |
|---|---|
| Model/input | Paths scanned, quantization/history construction, dense kernel cells allocated/read, support extraction, index/dependency construction, model hash work. Charge once from paths; report solver-only separately. |
| h | `sum_t min(H,T-t)n_t m_t` one-time scalar-OT calls for the direct construction, each support product, propagation multiplications/additions, support coalescing/sorting, allocated/read h entries and validation. Keep scalar OT separate from general continuation OT. |
| Lower solve | Every actual local/root backup including repeated versions; support discovery/caching; stage-cost and continuation reads, distinct entries and repeated visits; sparse/dense matrices and LP variables/rows/nonzeros; solver iterations, presolve, analytic shortcuts and tie solves. |
| Lower witness | All dual/primal construction, residual checks, support/normalization checks, outward correction if supplied, and retained witness bytes. A whole-model oracle check is not a candidate certificate routine. |
| Frontier | Root-plan entries read; active graph nodes visited; actual positive plan arcs traversed; stopped mass accumulation/coalescing; all scanned dense zeros if dense arrays are used; score comparisons, sort/heap operations, mask/list updates. |
| Upper | Every reached node and positive/full plan entry visited, north-west plan construction or cache retrieval, original scalar cost access, forward flow, marginal checks, policy repair, witness copying and retained best-policy memory. |
| Reuse/control | Cache construction/lookups/invalidations, changed-support dependency queries, array copies/clears, stopping tests, every failed or abandoned attempt, fallback, and cumulative wall time. |
| Resources | Peak live memory and allocation volume by candidate/h/cache/witness phase; process peak and complete elapsed time. Report additional audit resources separately. |

Count **three different entry notions** explicitly: unique parent-context successors `(t,i,j,x,y)`; unique time-state continuation entries `(t+1,x,y)`; actual accesses to either, including repeated scans and solves. These have different denominators. A shared continuation entry may appear under many parents. The draft's “fewer continuation-cost entries and local OT work” must choose its metric before running.

The in-memory diagnostic instrumented lower calls/positive entries, h scalar-OT calls/positive entries, frontier positive-arc traversals and upper positive-arc/fallback counts. It did **not** instrument every dense allocation, propagation arithmetic or copy. Its table below is a transparent partial work audit, not an invented complete runtime score. The complete event ledger is a required next implementation deliverable. Larger counted lower work already defeats a claim of fewer lower-entry visits for that schedule; it does not alone establish a machine-time ranking.

## 5. Executed fixtures and expected traces

All paths have equal empirical weights within a side. Unless stated otherwise use k=1, delta=1, shift=0.5, which preserves the listed integers. Both cost families were run. A is empty initially. Selection and ties use Sections 1–2. U_best=1 throughout every listed run. Exact values are all 1. Candidate execution completed before independent `exact_dp` and per-round `solve_active_subsolution` checks; every comparison agreed within 1e-9.

| Fixture | Lower sequence, including round zero | Final active nodes | Cumulative lower calls / positive entry visits | Full DP calls / visits | Extra h calls / entries |
|---|---|---:|---:|---:|---:|
| Delayed singleton, H=0 | 0, 0, 0, 1 | 3/3 | 10 / 10 | 4 / 4 | 0 / 0 |
| Same singleton, H=2 | 0, 1 | 1/3 | 3 / 3 | 4 / 4 | 5 / 5 |
| Tied positive one-step costs, H=0 | 0, 0, 0.5, 0.5, 1 | 4/4 | 15 / 30 | 5 / 8 | 0 / 0 |
| Inactive alternatives, H=0 | 0, 0, 0.5, 1 | 3/4 | 10 / 22 | 5 / 8 | 0 / 0 |
| H=2 delayed alternative, absolute | 0, 0.25, 0.5, 1 | 3/12 | 10 / 22 | 13 / 16 | 20 / 20 |
| H=2 delayed alternative, squared | 0, 0.03125, 0.5, 1 | 3/12 | 10 / 22 | 13 / 16 | 20 / 20 |

The first four rows each summarize two identical cost-family traces, making ten configurations in total.

**F1: delayed singleton.** X=`[[0,0,0,0]]`, Y=`[[0,0,0,1]]`. H=0 activates `(0,0,0)`, then `(1,0,0)`, then `(2,0,0)`; the first two expansions expose structure with no root ascent. A rule requiring strict positive residual at the first frontier would never start. H=2 reduces activations but its five h evaluations erase the apparent savings in lower-call count. A longer T=4 singleton with cost only at time four is Lane A's corresponding zero-first-residual control even for H=2. These are legitimate stall/overhead controls, not fixtures on which all methods must outperform exact DP.

**F2: optimizer ties.** X=`[[0,0],[2,0]]`, Y=`[[1,1],[3,1]]`. All true one-step pair costs are 1; h=0. Canonical expansion order is `(0,0,0)`, `(0,0,1)`, `(0,1,1)`, `(0,1,0)`. Each selected node has positive residual, but the first and third activations leave the reoptimized root unchanged. Accumulation avoids cycling; all four nodes are eventually needed under this rule. Four general-looking pair backups here are merely one-sided analytic evaluations, so reporting only “LPs avoided” would be misleading.

**F3: hidden inactive alternatives.** X=`[[0,0],[2,2]]`, Y=`[[1,1],[3,3]]`; h=0. Expansion order is `(0,0,0)`, `(0,0,1)`, `(0,1,1)`. After the first expansion, the minimizing root switches from the diagonal to the unexpanded anti-diagonal. The second expansion raises the root to 0.5, and the third closes the gap. The final 75% parent/row activation hides four root re-solves and repeated local work: 22 lower entry visits versus exact DP's 8.

**F4: the H_C01 delayed alternative.** Let e=1/8, delta=e, shift=e/2. X=`[[0,0,0,0],[e,e,e,2]]`, Y=`[[0,0,0,1],[e,e,e,3]]`; use the sum of the next two one-time conditional OT costs. Activation order is again `(0,0,0)`, `(0,0,1)`, `(0,1,1)`. At the third round, the equal hitting-mass choice includes an earlier inactive node and a later frontier node; the frozen time tie correctly selects the earlier node. Root bounds reach 1 while two later diagonal frontier nodes remain inactive with already exact h values. Thus a closed frontier is sufficient but not necessary for a closed gap. This fixes H_C01's exact-occupation mask failure, yet the final 3/12 active fraction gives no demonstrated work advantage: 22 lower entry visits versus exact DP's 16, plus 20 one-time h evaluations and propagation.

For additional transparency, the executed positive-arc counts over all rounds were:

| Fixture | Stopped-frontier propagation arcs | Upper full-policy propagation arcs | Inactive upper fallback constructions |
|---|---:|---:|---:|
| Singleton H=0 | 6 | 12 | 6 |
| Singleton H=2 | 1 | 6 | 5 |
| Tied positive costs | 4 | 10 | 6 |
| Inactive alternatives | 3 | 8 | 5 |
| Delayed H=2 | 3 | 24 | 21 |

These are per run and identical between the two costs. The prototype rebuilt inactive fallback plans on every encountered round; a cached variant can reduce construction counts but must count its cache. Root-plan scans, dense clears and stage-matrix construction are additional work, as declared above.

## 6. Minimal additional correctness controls

Before a random screen, add bounded fixtures with explicit expectations:

- **Mixed-depth masking:** retain H_C01's X=`[[0,1,2],[2,3,4]]`, Y=`[[0,0,0]]`, h=0, with `A_0=[True,False]`, `A_1=[False,True]`. The active descendant under the inactive second ancestor must receive no stopped-frontier propagation from that branch. Reuse the known lower values 0.5 versus 2/5 when activation moves to the ancestor. Test mask evaluation independently of the rule's empty-start trace.
- **Rare positive mass:** X has three paths `[0,0]` and one `[1,8]`; Y=`[[0,0]]`. With h=0 and canonical NW initial coupling, the frontier has masses 3/4 and 1/4. Expanding the high-mass zero-residual node first must not drop the remaining rare node. It then contributes exact root value 2 absolute or 16 squared. A more extreme dyadic mass can expose unsafe `mass>tolerance` pruning. No positive branch is removed solely for being numerically small.
- **Already exact zero:** identical deterministic zero paths give L=U=0 immediately, no activation and a defined absolute stop. This exercises the denominator rather than proving useful general savings.
- **Zero support / k=2 root:** keep zero marginal entries excluded, tiny positive entries retained, the historical k=2 4/3 root counterexample, arbitrary initial laws, and k=2 states with identical current scalar but different successors. The first fixture set is not required breadth coverage.
- **Full activation and validation:** equality to full DP for valid nonzero h, monotonic lower values on nested A, invalid terminal h rejection, normalized plan marginals, and a terminal/dummy-root cost check.

Treat these as expected-behavior tests. The literal draft performance promise of fewer entries/work on all adversarial fixtures is too broad: deterministic chains and tied costs are designed to expose overhead and stall. Separate correctness gates from a subsequently frozen performance domain. “Fails to repair delayed alternative” also needs a resource budget: it cannot silently mean any single plateau is failure.

## 7. Same-kernel baselines and the cheapest next decision

Use four direct baselines, with the same h, exact transport primitive and state/tie conventions wherever applicable:

1. **Replay of the identical A sequence with clamped DP.** Must return identical root values at every round. Candidate frontier logic does not create a stronger bound for fixed A,h. The H_C01 global LP is a small correctness cross-check only; its runtime is not the principal efficiency target.
2. **Repeated-sweep frontier implementation.** The fully specified rule above supplies the simplest reproducible reference and the exact cumulative formulas. Any engineering speedup must identify what work it removes from this schedule.
3. **Incremental cached AO*/transport DP.** Keep values, plans and dependencies; after activating a node, update affected active predecessors in reverse time until the exact clamped solution is restored. Charge dependency-index construction and every visited predecessor/entry. A conservative dependency includes all positive-support alternatives, not only current marked-policy arcs. Reusing an unchanged optimal plan can be justified using its feasible dual and unchanged objective, but checking that condition is itself work. Separate conservative incremental propagation from any proposed stronger transport-specific certificate that skips changed backups. Lane B identifies this cached affected-ancestor implementation as essential prior-art comparison; repeated full sweeps alone are a weak comparator.
4. **One-pass full exact DP.** Use the same analytic/LP kernel and normalization. For the formulation/activation comparison, show work with the same prebuilt h on both sides. For standalone cost, exact DP does not need h: its baseline must not be forced to build an unnecessary H=2 table merely to mask candidate preprocessing. Report both boundaries plainly.

Upper-policy occupation priority, deterministic random masks and exact-optimal-occupation masks are secondary selection ablations. Match cumulative cost budgets, not final node counts; equal-node masks are unequal work when degrees differ. Freeze all tie and no-certificate outcomes. An oracle mask that never reaches the target is a visible failed oracle ablation, not an infinite-ratio candidate speed claim.

The cheapest decisive next task is to implement only the fixture runner and complete event ledger, together with the conservative incremental cached baseline. It should reproduce the traces above, account for saved-plan upper evaluation and all repeated work, and show the cumulative gap/work curves. There is no need for 16 groups/32 random instances to learn that lower-frontier correctness is distinct from work savings. Only a concrete measured advantage or a proved transport-specific omission mechanism would justify a later cross-family screen. Root should define any scoped performance claim and resource threshold before those new data are generated.

## 8. Cross-lane synthesis and limits

Sent Lane A the first-inactive definition and proposed max-hitting-mass rule; incorporated its finite-expansion, zero-residual stall and fixed-policy-versus-reoptimized-root distinctions. Sent Lane B cumulative count formulas, executed overhead examples and the required cached AO* baseline. Lane B confirms direct AO*/LAO* overlap and notes that gap-weighted lower-greedy exploration also has BRTDP prior art; adding such a score is not automatically a contribution.

The H_C02 idea passes the useful conceptual repair: it follows the alternatives depressing the current lower bound. These fixture results do not establish novelty or a total-cost improvement. Failure of this particular schedule, baseline or declared domain can justify stopping that direction under v2; it does not imply impossibility for active sets, tree algorithms or certification, and cannot mark the full-domain scientific objective complete.
