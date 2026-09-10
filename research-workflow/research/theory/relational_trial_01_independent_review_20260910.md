# Independent review of relational Trial 01

Date: 2026-09-10. Reviewed the Trial 01 packet, `objective.json`, and
`adapters/common_model.py`. This is an independent analytic review of one
construction, not a benchmark or a new scope decision. Deterministic guarantees,
top-K and fallback remain provisional choices under the user's latest correction.
No objective, contract, historical artifact or hypothesis registration was changed.

**Verdict:** the arithmetic and counterexamples are correct. Stop treating the
literal unit-edge prefix-trie score, or its positive depth-only reweighting, as a
universal strict-order surrogate for the stated adapted distance. Preserve shared
trees as an unselected research family. This is a useful elementary diagnostic;
it establishes neither global impossibility nor a new scientific contribution.

## Independent mathematical checks

The calculations below use the finite coupling constraints directly. They do not
depend on the root agent's proof-check program or on floating-point LP output.

For two equally weighted leaves, every ordinary coupling has matrix

    [[a, 1/2-a], [1/2-a, a]],  0 <= a <= 1/2.

When the first process has a constant first coordinate and the second process's
first coordinate distinguishes its two leaves, causality from the first to the
second forces the first process's terminal value to be independent of the second
process's first coordinate. Consequently a=1/4; the resulting independent leaf
coupling is bicausal. When both first coordinates are constant, every such leaf
coupling is bicausal. These facts suffice for all three fixtures. They agree with
the causality definition and two-time recursion in Definition 1.1 and equation
(1.3) of [Backhoff et al., *Estimating Processes in Adapted Wasserstein
Distance*](https://arxiv.org/pdf/2002.07261).

| Comparison | Unit trie S | Absolute adapted cost AW_1 | Squared adapted cost AW_2^2 |
|---|---:|---:|---:|
| Q versus B | 2 | 3/16 | 5/128 |
| Q versus C_low | 1 | 1/16 | 1/128 |
| Q versus C_high=C | 1 | 1/4 | 1/8 |

**Fixture A.** For Q versus B, the depth-one mass differences total 1 and
the depth-two mass differences total 1. Thus S=w1+w2. For Q versus C the
depth-one difference is zero and the depth-two total is 1, so S=w2. This
is a strict preference for C for every w1,w2>0.

The first-stage absolute cost for Q versus B is (1/2)(1/8)=1/16. In its
forced independent terminal coupling, half the mass differs by 1/4, giving
1/8 and total 3/16. For Q versus C, terminal monotone matching costs
(1/2)(3/4-1/4)=1/4 and attains the minimum. Thus the ranking is inverted.
For squared cost the two Q-versus-B terms are (1/2)(1/8)^2=1/128 and
(1/2)(1/4)^2=1/32, totaling 5/128. Q versus C costs
(1/2)(3/4-1/4)^2=1/8. Both squared-cost values in the packet are correct;
they are not the square roots defining AW_2.

**Fixture B.** Adding all fixture leaves to one tree does not change the
existing prefix paths or introduce nonzero masses at unused leaves. Hence
S(Q,C_low)=S(Q,C_high)=1 on the same tree. Monotone terminal matching gives
(1/2)(3/8-1/4)=1/16 for C_low, below 3/16, whereas C_high gives 1/4,
above 3/16. An output depending only on the scalar S cannot recover these
distinct distances or their complete ordering around B. A calibration can still
abstain or collapse comparisons into ties; the fixture does not refute every
sound partial decision rule. Nor does it refute a rule using numeric labels,
the full prefix-mass vector, additional features or newly chosen edge weights.

**Fixture C.** With rows U's leaves (0,0),(0,1) and columns V's leaves
(0,0),(1,1), the common trie gives cost matrix [[0,4],[2,4]]. Its ordinary
coupling objective is 3-2a, minimized at a=1/2 with value 2. Bicausality
requires a=1/4, giving 5/2. This is a clean demonstration that the mass-cut
formula optimizes over a larger coupling set. It uses a path-tree ground cost
and must remain explicitly separate from the primary additive numeric cost.
It is not by itself an ordering inversion under that changed cost.

**Common-model mapping.** With delta=1/8 and shift=-1/16, a coordinate
x=j/8 has cell index j and representative (j+1/2)/8-1/16=x. All fixture
coordinates, including the prepended zero and C_low's 3/8, meet this condition.
Their dyadic arithmetic is exactly representable here. With the common constant
time zero and two transitions, the information needed at time one is precisely
the first noninitial coordinate. Thus k=1 and k=2 reconstruct the displayed
laws; merging terminal states for k=1 cannot affect a later kernel because
there is none. The number of transitions alone would not justify this claim
with a varying initial state. `common_model.py` charges times 1 and 2 and uses
current-coordinate costs, consistent with the packet. This analytic equivalence
does not turn its numerical LP implementation into an exact certificate and
does not test longer-horizon memory truncation or the T50 generator grid.

## Validity limits and scientific weight

The interpretation is fair because the packet names the exact construction
before refuting it: a common equality-prefix trie, fixed positive depth weights,
and ordinary leaf-measure tree OT. Numeric closeness is not reflected in those
edge costs. Fixture A therefore refutes that score's universal ranking claim,
not every conceivable edit cost or the user's broader tree idea. Fixture C
separately shows why matching the ground metric alone is insufficient to identify
ordinary and bicausal optimization in general.
In particular, a geometric or learned common tree with nontrivial edge geometry
survives this test as an unvalidated possibility; unit append cost is one literal
baseline and is not representative of every interpretation of the user's idea.

The mass-cut formula and sparse fixed-tree mass-vector comparison are already
explicit in section 2.1, equation (1), of [Takezawa, Sato and Yamada,
*Supervised Tree-Wasserstein Distance*](https://proceedings.mlr.press/v139/takezawa21a/takezawa21a.pdf).
That work also learns tree structure for a supervised task; its implemented
parameter choice fixes edge weights, so it should not be cited alone as a
specific implemented learned-edge-weight algorithm. The source check supports
the prior-art status of the formula and learned tree representation, without
constituting a novelty survey for an adapted-OT construction.

Scientific value here is decision support: these small examples prevent an
unsupported correctness claim and identify two issues a general construction
must address. They provide no speed measurement, lower bound on all algorithms,
empirical correlation result, or substantive negative theorem for a broad class.
A next method may address the issues through a restricted domain, an explicit
bound, richer conditional information, or a different representation; these
examples do not require it to invent two separate new mechanisms.

## Review of the provisional v3 workflow

V3 usefully separates relational decisions from 0.5% value accuracy, charges
reference calls, preserves ties and unresolved cases, and allows a declared
subclass. Those protections should be retained in any selected protocol.

However, the user's wish for guaranteed correlation does not uniquely select
query-relative top-K, deterministic zero-error assertions, or solver fallback.
Other precise interpretations include a deterministic distortion/margin claim,
guaranteed partial triplet comparisons, or statistical ranking risk under
declared sampling assumptions. They have different costs and scientific content.
High sample Spearman correlation alone is still not a theorem about any of them.

The current primary top-K formulation can force difficult boundary decisions.
If complete membership is demanded and margins are tiny, interval refinement
or fallback may approach the cost of solving the underlying distances. That is
a risk, not a demonstrated lower bound. V3 already permits unresolved cases and
does not literally require fallback on every query; the problem arises if these
options become defaults favoring complete retrieval before usefulness is chosen.
Fallback should remain a charged optional component, with cost and coverage
evaluated at the selected guarantee.

The statement that cheapness alone cannot justify a probe is appropriate for
launching a research candidate, but too rigid if applied to a bounded conceptual
sanity check. This trial needs no paper-level novelty to justify a few exact
calculations. Conversely, passing a workflow gate cannot upgrade its elementary
refutation into a scientific contribution. Separate a small diagnostic budget
from the significance gate for substantial implementation and experiments.

## Recommended next decision, without changing scope

1. Accept this trial as a completed diagnostic and close only the universal
   guarantee claim for the specified unit/depth-weighted trie score. Keep its
   examples as discriminators; do not launch a grid or learned variant from them.
2. Treat the current v3 primary decision and guarantee as proposals pending
   selection. Before adopting another construction, state the concrete relation
   that matters, the quantifier/probability and domain of its guarantee, the
   allowed unresolved fraction, and whether fallback is useful at all. Do not
   require top-K merely because it appears in the provisional file.
3. Only then apply the scientific-weight gate to a candidate lemma/mechanism and
   its nearest prior art. Freeze quantitative evaluation choices when there is
   an actual empirical protocol; an elementary analytic counterexample does not
   need a sample-size, statistical-risk or coverage preregistration.

These are recommendations for review. No amended objective or new research
direction is adopted by this document.
