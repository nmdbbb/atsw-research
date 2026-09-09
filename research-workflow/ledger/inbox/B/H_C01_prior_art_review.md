# H_C01 prior-art review — Lane B

Date: 2026-09-09. Recommendation: **revise before registration**. This is a bounded primary-source audit, not an exhaustive novelty search, a benchmark, or a finding of impossibility. No grid, registration, or comparator installation was run. Only this Lane B report was written.

The current formulation is defensible as a correctness construction and a mechanism-screening baseline. It is not presently defensible as a new global optimization principle. Its strongest overlap is ordinary admissible-heuristic partial-state MDP optimization, with an OT coupling polytope as the action set. Lane A's independently derived equivalence to clamped backward DP makes this more precise than a superficial resemblance.

## 1. Scope and material inspected

Read the H_C01 panel prompt, scope revision v2, objective, contract revision and H_C01 bridge, both frozen-design files, common-model adapter, active-subsolution adapter and tests, H_C01 draft, theory/SOTA notes, H_B01C1 verdict and policy-pool smoke verdict. Historical notes were treated as evidence. Scope v2 prioritizes valid root-gap tightness against explicit work; it does not turn reformulation, certification, or an oracle screen into novelty.

Primary sources below were inspected directly. For Bhattacharya–Kharoufeh, the web reader failed; the author-hosted PDF was fetched into memory using Python with the Windows trust store and all eleven pages were text-extracted. No downloaded artifact was written. The references give paper sections and one-based PDF pages where relevant; search-engine crawl dates were not treated as publication dates.

## 2. Closest primary sources

### A. Calo et al.: occupancy coupling, transport actions, SVI/SPI

[Calo, Jonsson, Neu, Schwartz and Segovia-Aguas, *Bisimulation Metrics are Optimal Transport Distances, and Can be Computed Efficiently*, arXiv:2406.04056v2 (2024)](https://arxiv.org/html/2406.04056v2).

Section 2.1, Eq. (3), and Appendix B.1 formulate coupling optimization as an MDP with coupling-valued actions. Section 3, Eqs. (6)–(8), Lemma 1 and Theorem 1 give flow/coherence constraints, policy recovery and an equivalent finite occupancy LP. Thus neither transport-valued actions nor avoiding an action-indexed infinite LP is an unaddressed conceptual gap. Section 4/Algorithm 1 and Appendix D/Algorithm 2 give SVI/SPI. Theorem 2 and Appendix D.2/Theorem 6 provide discounted accuracy guarantees under their ideal evaluation conditions. Their inverse powers of `1-gamma` cannot be transferred by setting `gamma=1`. Appendix E.2 explicitly supplies a feasible product policy when occupancy is zero. Appendix F.2 credits maintained coupling warm starts and discusses exploiting positive transition supports.

**Boundary:** this paper studies discounted stationary processes. A finite-horizon adaptation needs correct indexing, terminal conditions and initial-law treatment. Those checks are necessary; the horizon difference alone does not establish a research contribution. H_C01 currently uses neither SVI nor SPI, so equivalence of optimization target must not be described as identity of algorithms.

### B. Hansen–Zilberstein: AO*/LAO* and occupation priority

[Hansen and Zilberstein, *Heuristic Search in Cyclic AND/OR Graphs*, AAAI 1998, pp. 412–418](https://cdn.aaai.org/AAAI/1998/AAAI98-058.pdf).

The AO* discussion and recurrence on PDF page 2 assign the heuristic `h` to unexpanded nonterminal tips and Bellman-back up expanded nodes. Figure 1, PDF page 3, expands a partial solution graph and updates ancestors. The LAO* policy-iteration Theorem 1 and value-iteration Theorem 2, PDF page 5, preserve admissible value estimates. The Forward search section, PDF page 6, explicitly proposes selecting a node with highest probability of being reached from the start. Consequently, both partial-state lower evaluation and occupation-based expansion priority have direct precedent.

**Boundary:** H_C01's finite time-expanded graph is acyclic, making the AO* recurrence the sharper comparison than LAO*'s handling of loops. Arbitrary fixed masks and a single global LP are not literally the published search algorithm. They nevertheless implement the same clamped Bellman evaluation once the mask is fixed. A specialized efficient transport oracle or a new verified activation rule could matter; the presence of continuous coupling actions by itself does not establish novelty.

### C. Schmitzer: omitted OT rows require a certificate

[Schmitzer, *A Sparse Multi-Scale Algorithm for Dense Optimal Transport*, arXiv:1510.05466](https://arxiv.org/html/1510.05466).

Section 3, Proposition 3.2, shows that a short-cut implies an omitted dual inequality. Definition 3.5 and Proposition 3.6 establish shielding neighborhoods and existence of such short-cuts. Corollary 3.10 converts restricted local optimality plus shielding into global optimality. Section 4.1, Algorithm 4.1 and Proposition 4.2, give sparse solve/shield iteration and finite termination. Section 4.2 describes multiscale initialization and explicitly separates it from a proved efficiency guarantee. Section 5 constructs shielding using properties of the actual cost.

**Boundary:** H_C01 currently retains every positive-support successor inequality of each active parent. It does not implement static shielding or certify omission of individual inequalities inside an active transport. It skips complete parent blocks using the baseline value. Any later shielding rule must apply to `c + continuation`, whose geometry need not follow from scalar `c`. Successful sparse static OT is neither a proof that H_C01 works nor a novelty credit for its future pricing component.

### D. Direct finite-horizon subsolution LP

[Bhattacharya and Kharoufeh, *Linear Programming Formulation for Non-stationary, Finite-Horizon Markov Decision Process Models*, accepted September 5, 2017, Operations Research Letters 45(6), 570–574, author PDF](https://cecas.clemson.edu/~kharouf/old/Papers/Bhatta_Khar_ORL_Final.pdf); [publisher record](https://www.sciencedirect.com/science/article/pii/S0167637717301372).

Section 2 permits discount `delta` in `(0,1]` and time-varying state spaces/transitions. Section 3, Proposition 1, PDF pages 4–5, proves `J <= Lambda J => J <= V*`. Theorem 1, Eq. (10), PDF page 6, maximizes weighted values subject to all Bellman action inequalities; Eq. (12), page 7, is its flow dual. Section 4, Eq. (14), pages 8–9, restricts the value function to a finite basis and discusses the remaining constraint burden.

**Boundary:** their theorem uses positive weights at every state and countable action sets. H_C01 maximizes only the dummy-root value and has a compact coupling polytope. For a finite transport polytope, linear minimization can be reduced to finitely many vertices; local OT duality supplies the compact alternative. Root-only optimization does not imply that every returned state value equals `V*`.

### E. MDP constraint generation

[Schuurmans and Patrascu, *Direct value-approximation for factored MDPs*, NeurIPS 2001 proceedings](https://papers.neurips.cc/paper/1981-direct-value-approximation-for-factored-mdps.pdf).

Section 4 and Figure 2, PDF pages 5–7, restrict the Bellman LP to a linear approximation basis and iteratively add maximally violated constraints using factored minimization. The stopping check searches for remaining violations across actions. The authors identify constraint generation as a computational bottleneck and do not guarantee that greedy generation always remains small. Section 5 uses structured residual search to bound approximation error.

**Boundary:** their reward-maximization convention reverses the lower/upper inequality orientation relative to H_C01's cost minimization. Their factored discounted model is not the common finite OT model. The relevant overlap is the architecture: compact LP plus a structured separation operation. Merely introducing pricing later is not a new architecture; an OT/temporal pricing rule would need its own correctness and cost advantage. Randomly retaining inequalities does not inherit exact separation guarantees.

## 3. Direct reduction of the current H_C01 draft

The following is this panel's deduction from the draft's equations and code, not a claim that a source contains H_C01's exact implementation.

Write `z=(x,y)` and let an MDP action at `(t,z)` be `q in Pi(P_t(x),Q_t(y))`. The transition distribution is `q`, and the expected one-step cost is `<q,c_(t+1)>`. The dummy root has action set `Pi(mu_0,nu_0)`, no immediate cost, and successor state `(0,z)`. This gives the exact successor-cost and optimized-initial-coupling conventions of `common_model.py`.

The full value LP enforces

```
v_t(z) <= <q, c_(t+1) + v_(t+1)>    for every feasible q,
v_T = 0.
```

At an active node, H_C01 replaces that family by the equivalent finite OT-dual block. This is an extended formulation: eliminating its potentials recovers the displayed Bellman inequality.

The restriction can also be written as an affine approximation basis:

```
v = h + sum_(z in A) r_z * indicator_z,    r_z >= 0.
```

At inactive nodes the Bellman inequalities are redundant because `h_t <= T_t h_(t+1) <= T_t v_(t+1)`. Eliminating them saves representation/solve work but does not create a stronger feasible set than the corresponding restricted Bellman LP.

For a fixed baseline and masks, define

```
w_T = 0
w_t(z) = h_t(z)                      if z is inactive
w_t(z) = OT(P_t(x), Q_t(y), c+w_next) if z is active
L_A = OT(mu_0, nu_0, w_0).
```

Backward induction shows every feasible H_C01 table is at most `w`. Conversely `w >= h`, and optimal local OT duals certify its active inequalities. Hence **the global LP optimum equals `L_A` exactly**. Lane A independently derived the same equivalence. No root-gap improvement can come solely from solving the same restrictions simultaneously across time. This does not preclude a runtime advantage from a particular implementation or a different model that adds useful shared constraints; neither has been established here.

The all-active claim is therefore an equality of optimal root objectives, with an optimum attaining `v=V` available. It is not a statement that all root-optimal LP tables equal exact DP pointwise, particularly at unvisited states. The existing test checks the root value, consistent with that narrower statement.

## 4. Cross-lane objections and consequences for the probe

The strongest overlap and the mandatory clamped-DP comparison were sent to A and C before finalizing. Received objections were incorporated as follows:

- **Lane A:** the baseline formed from a fixed global depth `H` sum of one-time future-marginal OT costs is a Bellman subsolution for both registered costs. With nonnegative costs, `h_2 >= h_1 >= h_0`; choosing the strongest among these is automatically choosing `H=2` if construction cost is ignored. Keep depth as a cost/quality ablation, not a search over potentially incomparable bound strengths. This report assigns no novelty to that elementary relaxation.
- **Lane A:** exact-optimal occupation need not select the nodes required to tighten the relaxed problem. Its reproduced `T=3`, `e=1/8` fixture has uniform paths `X=[[0,0,0,0],[e,e,e,2]]`, `Y=[[0,0,0,1],[e,e,e,3]]`. Activating the exact diagonal and using valid `H=2` leaves an inactive anti-diagonal escape: exact cost is 1, whereas the lower bound is 0.25 for absolute cost and 0.03125 for squared cost. This is evidence against that activation rule's universal justification, not a claim about the unrun frozen random grid or every activation strategy.
- **Lane C:** count omitted parent blocks separately from retained successor rows. With degrees `(8,1)` on both sides, activating only the high/high parent omits 75% of parent nodes but retains `64/81` of successor rows. The current adapter additionally materializes dense stage matrices, scans/copies tables and masks, and rescans kernel supports. Its LP counters are not total work.
- **Lane C:** the draft must specify whether the upper value uses a separately constructed feasible policy or exact-oracle plans/value. Using `U=V*` is a legitimate explicitly labelled optimistic headroom screen, but it grants extra oracle access beyond occupation-based selection and is not a deployable certificate procedure.

The all-active row denominator is computable without scanning all quadruples:

```
E_all = sum_t (sum_i degP_t(i)) * (sum_j degQ_t(j))
E_A   = sum_t sum_((i,j) in A_t) degP_t(i) * degQ_t(j).
```

Root rows, degree construction, baseline work, policy work, actual matrix accesses and solver work still require separate accounting. A retained-row ratio below 75% alone cannot establish a 25% reduction in time or total work.

## 5. Claims that remain defensible and required edits

**Currently defensible:** a small implementation of a known Bellman-subsolution restriction, independently checked root conventions, and a proposed oracle headroom experiment for a declared baseline/activation family. A failed aligned screen may justify stopping this direction under scope v2; it does not prove a lower bound for all tree algorithms.

**Potential future contribution, presently unproved:** an implementable temporal activation or grouped-verification method that obtains a valid root interval with demonstrably less total work than the same-baseline partial DP and eligible competitors. A useful result could instead be a precisely scoped obstruction for a defined family of heuristics/activation rules, with information access and cost model stated. Either direction needs new evidence and an expanded novelty review. A small search's silence is not evidence of novelty.

Before registration:

1. Reframe the mechanism as active-state Bellman evaluation/LP with an admissible baseline. Explicitly acknowledge the sources above; remove any suggestion that finite horizon, global coupling, occupation priority, or root certification alone is new.
2. Add same-`A`, same-`h` clamped backward DP as a mandatory comparator. Exact root equality is the correctness prediction. Compare its active local OT work with global LP assembly/solve work using the same low-level kernels. Replace the ambiguous ablation “with versus without time coupling” by this precise comparison.
3. Declare all oracle permissions, especially the upper value, mask search and stopping. Keep the oracle screen separate from a candidate. Exact occupation is a particular informed heuristic, not a certificate that the best active set was found.
4. State that omitted rows belong to inactive parent blocks. Require an independent certificate before omitting an active parent's successor alternatives. Charge all baseline, support, selection, construction, policy and certification work.
5. Keep correctness and headroom outcomes separate. The adversarial occupation fixture belongs in correctness/limitation evidence; the unrun random-grid performance prediction remains untested. A revised cheap screen may be worth running as research, despite novelty remaining unestablished.

No source reviewed here establishes that the project outperforms the strongest comparable methods. No such claim is supported by the present audit.
