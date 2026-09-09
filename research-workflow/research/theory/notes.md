# Theory lane: three mechanism hypotheses

Status: proposed cards, not registered experiments and not discoveries. Prepared 2026-09-09. No benchmark was run for these cards. The authoritative objective is `../../objective.json`: outperform the strongest eligible SOTA frontier on time at matched certification, OR certificate quality at matched total cost; POT is only an implementation baseline/oracle. Preserve all six k/delta cells, T=50, both cost families and both process families. Finite-model certificates do not certify population estimation error.

## Prerequisite and common notation

The imported k=2 modal-root defect reported in `../sota/notes.md` blocks performance interpretation. Repair and independently verify model/root equivalence before any card is probed. Retain the deterministic counterexample whose correct root cost is 4/3, not zero. A state below means a time-indexed full k-window, never just its current scalar coordinate when k=2. The cost still uses the intended current scalar observation, not Euclidean distance of the whole history vector.

For exposition put stage cost at the current state: V_t(x,y)=g_t(x,y)+min_{pi in Pi(P_t(x),Q_t(y))} E_pi[V_{t+1}], with terminal cost specified explicitly. This is just an indexing convention; the adapter must agree exactly with the original successor-cost convention and include the first cost and initial coupling. All probabilities are normalized. Finite state spaces make cost ranges finite even when the underlying population distribution has unbounded support.

Known elementary facts, not novelty: Bellman is monotone and nonexpansive in the sup norm; a feasible policy evaluated on the original model gives an upper bound; Bellman subsolutions give lower bounds; pointwise maximum preserves valid lower bounds. Floating-point feasibility needs residual correction/outward safety, not merely agreement with another approximate solver.

## Checked primary literature and overlap

- [Bontorno–Hou, Nested Optimal Transport Distances](https://arxiv.org/html/2509.06702): checked method/experiment sections, alongside the SOTA lane's code audit. Path quantization, prefix trees, conditional distributions and backward DP are prior art. None of the cards may claim those ingredients as new. PNOT's existing Markov collapse is an especially important comparison for A.
- [Bayraktar–Han, Fitted value iteration methods for bicausal optimal transport](https://arxiv.org/html/2306.12658): checked Algorithm 1 and surrounding discussion. Learning continuation values from selected histories already avoids evaluating every history directly. Card A must distinguish a verifiable quotient/error envelope from statistical function approximation, and include estimation/training costs when comparing methods.
- [Calo et al., Bisimulation Metrics are Optimal Transport Distances](https://arxiv.org/html/2406.04056): checked Sections 2–4 and Appendix F.2. Bisimulation/state aggregation connections, an occupancy formulation and coupled iterations are prior art. F.2 explicitly credits maintained coupling warm starts for efficiency. The paper's discounted stationary setting cannot be changed to undiscounted finite horizon simply by putting gamma=1 in its guarantees. Card C needs its own finite-horizon derivation and comparison.
- [Schmitzer, A Sparse Multi-Scale Algorithm for Dense Optimal Transport](https://arxiv.org/abs/1510.05466): primary abstract and author publication description checked. Sparse restricted transport plus global optimality verification and multiscale structure are prior art. Full theorem-level shielding audit remains REQUIRED before card B can claim a distinction or reuse its guarantee. Author code: https://github.com/bernhard-schmitzer/optimal-transport .

These are nearest checked starting points, not an exhaustive novelty search. In particular, none proves that the proposed mechanisms outperform an optimized competitor.

## H-A: certified quotient by equivalent conditional futures

**Mechanism.** Merge histories only when their continuation problems are equivalent, or when an explicit error envelope permits it. Solve once per quotient-state pair instead of once per original history pair. This is different from fitting a scalar value at sampled pairs: the quotient includes transition structure and a lifting/certification argument.

**Known lemma / proof sketch.** Choose partitions A_t and B_t of the two time-indexed state spaces. Suppose (i) stage cost is constant on each A-by-B block; (ii) every x in the same A block has the same distribution over A_{t+1} blocks, and similarly for y; (iii) terminal cost has the same property. Any fine coupling pushes to a feasible coarse coupling. Conversely, a coarse coupling q(A',B') can be lifted using each original row's conditional distributions within A' and B'. Backward induction therefore gives exact equality between the fine value and the quotient value. This is finite-horizon lumpability plus OT lifting, not a new theorem claim.

**Approximate version to verify.** Let cost variation within a block be at most eta_t. Let aggregate transition rows differ from chosen representative rows by total variation at most a_t and b_t, uniformly over their respective blocks. For coarse continuation value of range R_{t+1}, a candidate uniform transfer recurrence is

    e_T = terminal envelope;
    e_t <= eta_t + e_{t+1} + R_{t+1}(a_t+b_t).

Here TV is half the l1 distance. Derive the transport perturbation bound by moving discrepant marginal mass, and check all indexing and range constants independently. This bound can be valid but too loose to be useful. Approximate compression must preserve the SAME fine-model target through [coarse value - e, coarse value + e], or a tighter verified variant; do not redefine the target as the quotient model.

**Conjectured performance.** Conditional futures have substantially fewer certificate-relevant classes than raw k-windows, including for the nonmonotone second-order family. Raw LP count sum_t |X_t||Y_t| can become sum_t |A_t||B_t|, with additional partition construction and verification work. This is the hypothesis; observed near-rank-one costs do not support it by themselves.

**Decisive probes.** First manufacture duplicated future subgraphs with known exact equivalence and verify equality to independent fine DP. Then perturb transition rows continuously and compare the claimed envelope to exact error. Include two k=2 windows with identical current coordinate but opposite next-state laws: they MUST be split or charged nonzero certified error. Finally test whether any useful compression survives the preregistered nonmonotone family at a root gap of 0.5%.

**Falsification / savings measurement.** Any out-of-interval exact value invalidates the implementation/proof. If equivalence detection costs as much as the eliminated fine DP, or the certified partition is nearly discrete at the target gap, the performance hypothesis fails for that domain. Record quotient cardinality, fine pairs never solved, transition comparisons, total preprocessing/certification time and peak memory. Ablate by disabling merges while retaining exactly the same low-level kernels. Compare against PNOT's existing Markov compression and FVI, with their different guarantees/access labelled.

## H-B: successor-block bounds and hierarchical refinement

**Mechanism.** Avoid materializing or solving against every successor pair in c+V. Maintain a hierarchy of successor blocks with rigorous lower cost envelopes and feasible lifted couplings. Refine a block only when its unresolved cost can matter to the root certificate. The omitted unit is a whole group of cost entries/transport constraints, not merely an LP selected by a scalar heuristic.

**Known lemma / proof sketch.** For partitions of the two successor supports, let m_AB be a VERIFIED lower bound on M_ij for all i in A,j in B, where M=c+L_next. Aggregated marginals p_A,q_B define a coarse OT problem. Pushing forward any fine plan proves coarse OT(m)<=fine OT(M). A feasible coarse plan q_AB lifts to a fine feasible plan via

    pi_ij = q_AB * (p_i/p_A) * (q_j/q_B), i in A,j in B,

omitting zero-mass blocks. Evaluating that fine policy on the original costs and its own continuation yields an upper bound. Recursing the lower relaxation and evaluating the feasible upper policy gives a root interval. Taking valid maxima/minima preserves old bounds across refinements.

**Required new work.** Obtain useful block envelopes WITHOUT scanning every entry of c+L_next at every refinement. Scalar cost geometry alone is insufficient: continuation values can destroy Monge/shielding structure. Possible inputs are independently proved continuation oscillation bounds or certified interval tables from the next layer. The representation and envelope construction cost is part of the mechanism, not free preprocessing.

**Conjectured performance.** Most successor blocks can remain coarse at the required root tolerance, reducing fine cost evaluations, active constraints and LP dimensions. Occupancy of a proposed policy may prioritize blocks but cannot justify deleting all alternatives. If using mass to budget certificate error, bound mass over ALL feasible couplings consistent with the relaxation. For a single rectangular successor block, min(p_A,q_B) is a valid local upper mass; using many such bounds independently may be very loose and must not double-count a claimed savings.

**Decisive probes.** Tiny non-Monge matrices embedded in a two/three-stage tree, zero/tiny marginals, and a rare branch where the candidate policy places little mass but another feasible policy gains substantially. A hidden low-cost entry inside a coarse block must either be enclosed or trigger refinement. Check nested coarse/fine intervals against exact DP while increasing resolution. Break scalar ordering through second-order nonmonotone transitions and switch squared to absolute cost.

**Falsification / savings measurement.** Invalid block minima or missed alternative policies kill correctness. Dense scans to build envelopes, almost-full refinement, or policy lifting/evaluation that erases the savings kill the proposed performance mechanism. Count evaluated fine entries, active arcs, envelope queries, refined blocks, all lower/upper work and root gap. Ablate with exhaustive fine supports and identical solver kernels. Compare nearest static multiscale/shielding solver applied to each Bellman problem; a gain must come from the temporal envelopes/refinement, not merely rediscovering sparse static OT.

## H-C: finite-horizon occupancy flow with certified sparse pricing

**Mechanism.** Replace the schedule 'fully solve one OT at every state pair in a backward sweep' with one globally coupled optimization over finite-horizon occupation flows. Maintain a feasible global policy/flow and improve only parts exposed by dual pricing. Potentially share updates across time and many histories. This is a reformulation lane and need not fit inside the certify5 architecture.

**Finite-horizon formulation to prove independently.** Let d_t(x,y) be state-pair mass and f_t(x,y,a,b) its outgoing flow. Impose nonnegativity and

    sum_b f_t(x,y,a,b) = d_t(x,y) P_t(a|x),
    sum_a f_t(x,y,a,b) = d_t(x,y) Q_t(b|y),
    d_{t+1}(a,b) = sum_{x,y} f_t(x,y,a,b).

Use the correct fixed dummy root, or optimize the specified initial coupling if the initial law is nontrivial. Minimize the sum of original stage costs against d_t (equivalently successor costs against f_t, with indices aligned). Any feasible policy induces these flows. For d_t>0, f_t/d_t reconstructs a feasible transition coupling; zero-mass states receive any feasible coupling. Prove Markovization is valid for this finite k-window model and additive cost. This establishes equality to its nested OT objective, not to an arbitrary full-history process that has been truncated to k.

**Certificate / proof obligation.** Derive the LP dual and a computable original-target dual residual bound. Restricted primal arcs give a feasible upper only if constraints remain satisfied. They give no lower bound until ALL omitted columns are priced or bounded by verified group envelopes. Feasible global primal and dual then certify the root without requiring local optimality at every node. Entropy may drive optimization, but original-cost feasibility, bias and optimization residual must be included. Do not transfer discounted SVI rates by setting gamma=1.

**Conjectured performance.** Global pricing/update structure can reduce the number of completed local OT solves and propagate improvements without repeatedly rebuilding each layer's pool. Tree/DAG sparsity may make grouped pricing cheaper than enumerating every f variable. The dense global LP has roughly sum_t |X_t||Y_t| degX_t degY_t variables; reformulation alone can therefore be WORSE than DP. Sparse pricing and certificates are the essential unproved efficiency hypotheses.

**Decisive probes.** On small finite-horizon models compare global LP, exact backward DP and recovered-policy evaluation to identical values. Include k=2/root counterexamples and zero occupancy states. Construct an omitted low-cost arc that is invisible to current-policy occupancy: global pricing must detect it or bound it. Then compare full versus grouped pricing as branching/horizon grow under fixed certificate tolerance. Check whether solving the pricing problem secretly performs all Bellman OT solves again.

**Falsification / savings measurement.** Target mismatch or inability to recover feasible couplings invalidates the formulation. If pricing/certificate cost restores the entire avoided DP work, reject the efficiency mechanism even if optimizer iterations look cheap. Count active global variables, priced blocks, fine arcs inspected, completed local OT solves, memory and total certificate time. Ablate temporal grouping; separately ablate warm starts. Compare against a justified finite-horizon adaptation of SVI/SPI and strong nested/adapted Sinkhorn, not just cold POT DP. Occupancy LP and coupling reuse themselves are known; the distinct contribution would have to be proved/measured in finite-horizon certified sparse computation.

## Execution decision

First finish common-model/root correctness and comparator adapters. Then preregister one tiny oracle probe per card and have an independent verifier challenge each lemma. Exact duplicates, a hidden-block optimum and a missed low-occupancy arc distinguish the three mechanisms; three SVD variants do not. Freeze performance thresholds, instances and resource limits before the respective runs using the root workflow. A failed implementation is repaired without declaring the hypothesis disproved; a correct implementation that fails its structural prediction returns to the outer research loop.

No card is presently novel, empirically supported across the required domain, or an algorithm achieving the user objective. The deliverable is a falsifiable starting set that keeps the broad target fixed.
