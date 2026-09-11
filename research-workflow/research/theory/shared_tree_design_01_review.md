# Independent review of shared conditional-state trees, design 01

2026-09-11. Bounded reviewer; no PO decision authority. **Final exact-version
review completed.** Only this review file is reviewer-owned. The final sign-off
below supersedes the provisional v1 investment recommendation while preserving
the earlier analysis as construction history.

**Verdict:** admit the specified finite-window AW1 certificate construction and
its exact sparse tree-transport primitive as an executable research candidate.
Both observed mathematical/geometry defects were repaired within the same tree
architecture. No blocking proof or implementation defect was found in the frozen
version. Recommend bounded design of a frozen cost/decision probe;
do not admit novelty, runtime superiority, general coverage, or scientific
completion from these adaptive diagnostics.

## Review scope and version

Initial design reviewed: `shared_tree_design_01.md`, SHA256
`A8B5B8813D3D8862A6A807E7C8FE2496C0FF919DCF3F6C9A767060989FCBA0F1`.
The target is finite k-window AW1, scalar absolute output cost on times 1..T,
with the declared full window observed. No population claim, squared-cost claim,
novelty certification, or performance claim is reviewed here.

## Mathematics: no blocking defect in the two certificate inductions

On the disjoint union of tagged layer states, terminal absolute output distance
is a pseudometric. Assuming d[t+1] is a pseudometric, its Wasserstein lift on
probability rows is a pseudometric, including rows from different models. Adding
the current-output pseudometric gives d[t]. Finite-horizon conditional Bellman
optimization identifies the initial lift with the declared target. The full
window qualification matters: this is not a theorem for a hidden-state model
with only the current numerical emission observed.

For the upper bound, suppose rho[t+1] dominates d[t+1] pointwise. Monotonicity
of transport in its ground cost gives each selected edge length

    g(s,r) + W_rho(P_s,P_r) >= g(s,r) + W_d(P_s,P_r) = d[t](s,r).

Summing along the unique tree path and applying the triangle inequality for the
true d[t] gives rho[t] >= d[t] on every pair, even though only tree edges were
weighted. A final initial-distribution transport preserves the inequality.
Zero edge lengths cause no problem. This proves a numerical upper certificate
without claiming that an ordinary full-path tree coupling is bicausal.

For the lower bound, every admitted next-layer probe f obeys

    |E_P f - E_Q f| <= W_d(P,Q).

The maximum over a nonempty finite bank is a pseudometric of rows. Adding g
gives ell[t] <= d[t]. For any anchor a, reverse triangle gives

    |ell[t](s,a)-ell[t](r,a)| <= ell[t](s,r) <= d[t](s,r).

Thus these anchor probes are admissible for the next backward step, and the
initial expectation maximum is a valid lower bound. The terminal bank must
actually consist of probes Lipschitz for absolute output distance. Strict
interval separation admits an order; zero lower bounds do not admit equality.

## What the architecture changes

The proof does not require equality of aggregate kernel rows. Every tagged
conditional state and its supplied transition row remains represented. It also
does not use a global TV-times-range replacement: each selected edge uses the
geometry of the recursively constructed next-layer tree. This is a substantive
representation change from exact quotient/lumpability or one global envelope.
Its new liabilities are tree stretch, limited probe expressiveness, and the cost
of reading/traversing rows and trees. They need their own diagnostic accounting.

An arbitrary feature-selected spanning tree has no proved distortion bound.
In particular, a path can detour through positive-length edges between states
whose true conditional distance is zero. Tiny fixtures cannot settle horizon
stability or batch-insertion sensitivity. No general stretch claim is admitted.

## A concrete lower-bank limitation and repair within this architecture

With J next-layer probes, any sufficiently large terminal support admits
distinct probability rows agreeing on those J expectations: take a nonzero
mass-zero vector in the nullspace of the feature matrix and perturb an interior
probability vector in both directions. For equal current outputs the two rows
then have ell=0; every distance-to-anchor probe made from that ell remains blind.

Even adding every available single-state anchor need not make the final bank
measure-separating. On the four corners of the unit square with L1 distance,
the uniform measures on the two opposite-corner pairs each have expected
distance 1 to every corner. The true Wasserstein distance is 1, but the anchor
expectation lower bound is 0. This metric is realizable by conditional states
with deterministic two-time output sequences; full observed windows can retain
the branch identifier. The example is a mathematical expressiveness diagnostic,
not an additional empirical family or an instruction to expand this cycle.

A specific repair, if the fixed fixtures locate lower-bank blindness, is to add
distance-to-anchor-set probes

    f_S(s) = min_{a in S} ell(s,a).

The minimum of finitely many 1-Lipschitz functions is 1-Lipschitz, so the same
induction remains valid. The diagonal anchor set separates the square example
exactly. Retain old probes and charge all set construction/evaluation work; a
predeclared O(J) selection of sets is bounded, while enumerating all subsets is
not. This is a concrete optional same-architecture repair, not a completeness or
novelty claim. Raw tree-cut indicators are not automatically valid lower probes.

## Cost gate and provisional investment recommendation

The dense implementation's sum N[t]*N[t+1] traversal term can erase the stated
mechanism. Replacing quadratically many general OT solves by linearly many tree
edge evaluations may still reduce expensive optimization, but is not a linear
total-work claim. Strong sparse/deterministic exact references may be cheap.
For a single small batch, transductive rebuild and lower-feature costs can
dominate any saved pair solves.

If upper construction is the diagnosed blocker, prefer one sparse tree-transport
repair: aggregate signed support mass on its visited ancestor union, with actual
support reads, visited edges, depth, preprocessing and root queries charged.
A chain-shaped terminal tree can still have long ancestor paths; a compressed
path/LCA implementation or sorted sparse 1D terminal computation would need its
own accounted work. Merely naming sparsity does not establish improved cost.
If lower blindness is the blocker, use the set-anchor repair above instead.
If geometric upper stretch is the blocker, the design's bounded candidate-edge
MST repair is appropriate. Spend the one-repair budget on the measured blocker,
not all three. Final choice awaits the exact diagnostic artifacts.

## Established ingredients versus potential algorithmic contribution

Moulos establishes a dynamic-programming treatment of bicausal transport for
Markov chains: [primary paper](https://arxiv.org/abs/2010.06831).
Calo et al. explicitly formulate the Bellman transition-coupling recursion and
develop occupancy-coupling/Sinkhorn value iteration machinery:
[primary paper, sections 2--4](https://arxiv.org/html/2406.04056).
These sources were inspected for this concrete overlap, not as a novelty search.

Bellman lifting, metric domination, the tree transport formula, and the
Kantorovich/reverse-triangle lower proof are established mathematical ingredients.
Their being elementary does not invalidate an algorithmic research direction.
The candidate contribution to assess is the batch-shared conditional tree,
its recursive feature bank, and a charged refinement mechanism that yields
useful certified order decisions. Neither inspected source establishes novelty
of this complete proposed combination, and this review does not certify it.

## Historical v1 implementation and fixed-result review

Inspected `tools/check_shared_tree_design_01.py`, its imported binary transport
and finite-window model routines in `check_geometry_condition_screen_01.py`, and
both v0/v1 JSON result files. The provisional code hash recorded by these first
results is `807d5f42c6800d0dd01cd8c42ac05a36d56462f5e452a11f72c4088f27a33862`.
The candidate computes trees/probes before calling the evaluator reference; no
exact pair labels feed its feature or topology selection. The exact reference
enumerates the endpoints of each 2x2 transport polytope and uses independent
Bellman recursion. This is appropriate for the checked binary rows, not a
general large-support reference. The layer audit checks both tree domination
and every stored probe's Lipschitz property on every pooled state pair.

The one repair uses four singleton anchors plus their six pairwise minima when
four distinct anchors exist. Each added function passes the min-Lipschitz proof
above. Rebuilding anchors and recursive geometry means v1 does not literally
retain the complete v0 bank; no global monotone-improvement claim follows.

The diagnostic findings are specific:

| Family, window | Exact query distances (A, B) | v1 query intervals (A, B) | Interpretation |
| --- | --- | --- | --- |
| Reconvergence, k1 | 3/16, 1/2 | [3/16,27/16], [1/2,15/4] | Strict order exists; upper stretch blocks it. |
| Reconvergence, k2 | 3/16, 1/2 | [3/16,35/16], [1/2,21/4] | Same blocker after retaining memory. |
| Information timing, k1 | 1, 2 | [1,5/2], [2,7/2] | Upper stretch blocks the reconstructed-model order. |
| Information timing, k2 | 2, 2 | [2,5], [2,9] | True tie; no strict-order recovery is required. |
| Genuine k2, k1 | 0, 0 | [0,0], [0,0] | Reconstruction has removed the dependence. |
| Genuine k2, k2 | 2, 1 | [2,4], [1,1] | Correctly certifies B closer. |

All listed v1 pairwise lower bounds equal their binary-reference distances.
This is a property of these fixtures only. On genuine_k2/k2, v0 had lower bound
zero for both query pairs while already having U(Q,B)=1. Thus the repaired
lower bound L(Q,A)=2 is enough to explain the new strict order even with that
old upper held fixed. All supplied one-time marginals are identical in this
family; the k1 reconstruction collapses all distances to zero. These checks
support an actual conditional-information mechanism on this fixture. They do
not estimate general order coverage, and k1 is a changed-model ablation rather
than a bound on the original k2 target.

The upper geometry can regress after bank/topology reconstruction: on the
information_timing/k2 BQ pair its upper rises from 4 in v0 to 9 in v1. The final
algorithm must not claim retained upper quality unless it explicitly retains
and charges an older valid upper representation. A frozen-old-upper comparison
can isolate a repair mathematically but is not free deployment work.

For genuine_k2/k2, both versions visit 81 tree nodes over 15 tree OT calls and
build 17 edges on 21 pooled states. Feature-edge reads rise from 80 to 200.
This is measured additional candidate work to obtain the certificate. Counters
do not constitute a full runtime model: feature-coordinate operations inside
distance evaluations, pair-min generation, sorting, root feature expectations,
pool construction, memory, and rational arithmetic costs also matter. No
runtime or asymptotic saving is admitted.

## Historical v1 investment recommendation, superseded below

Continue this conditional-tree architecture for one bounded topology/stretch
construction, not an unrelated lower-bound lemma or a sparse-kernel optimization
before recovering useful decisions. The repair has made the lower side exact
on all current fixtures, so the measured blocker for the remaining strict
orders is specifically the upper tree, not lack of another lower probe.

A concrete next construction is the current median tree plus adjacent-state
edges from each existing feature-coordinate sort, including current output.
For fixed J this supplies O(J*N[t]) candidate edges. Compute the recursive tree
transport weight only on that union and take its MST. Do not use the exact
reference table in choosing edges. Retain the old valid root upper by a minimum
if preservation of existing decisions is promised, and charge the complete
extra builds/traversals. Freeze the edge rule and count before execution.

The bounded gate is recovery of at least one presently unresolved strict order
while preserving the genuine_k2 certificate. Reused diagnostic families can
guide construction; passing them is not a new coverage/performance experiment.
If this candidate graph still fails, record which layer's conditional detour
dominates before funding further refinements. This is an actionable investment
proposal for the PO, not a new mandatory completion condition or authorization
to exceed the current one-repair budget.

That recommendation was accepted as repair 2 after the PO explicitly extended
the budget to two repairs. It has now been executed and assessed below. It is
not an outstanding instruction to perform another topology construction.

## Final exact-version coverage and attestation

The following SHA256 values were independently read from disk after the final
freeze. Paths are relative to `research-workflow/`.

| Artifact | SHA256 |
| --- | --- |
| `research/theory/shared_tree_design_01.md` | `8f5f8161a7e12338e0ec70b565a078e396a639f7a829699058141f8df1000483` |
| `adapters/shared_conditional_tree.py` | `e222239de4e4b4918deb37995ffc05e22c343069a4af8939b2b9c9ca5f4cd75a` |
| `tools/check_shared_tree_design_01.py` | `e5d498d3efee7e52051e583aedb1c8026346a8675e220d1d3808c0fbbeea036b` |
| `research/theory/shared_tree_design_01_checks_final.json` | `373e96eb16f1bbaca48a3906452002fda75e5c91583be27672745473d6c0fbb8` |
| `tests/test_shared_tree_transport.py` | `e66e6848839402088995edf1a3bd860d8210a8a86aa7a37eeeaff2d2367a084d` |
| `tools/check_geometry_condition_screen_01.py` | `b6bed1f47a70fe63ae37e6c6d147442be4e055ba0cb18894bc3bc590730cbd46` |

Reviewed the final candidate/evaluator separation and changed defaults. The
candidate imports only Fraction and combinations; it contains no diagnostic
path enumeration or exact Bellman/ordinary reference. `SharedTrees(models)`
selects pair-min probes, feature-MST topology, and virtual transport, with dense
audits disabled. The diagnostic explicitly enables dense audits and records
candidate, checker and reference-dependency hashes. Its legacy CLI defaults
require the documented explicit flags to reproduce the final version. This is
consistent with the final design. Valid normalized rational finite rows are a
precondition; arbitrary float-array integration is not supplied or admitted.

The reviewer independently reran
`run('pair_min', 'feature_mst', 'virtual')` after this separation and compared the
entire resulting object against the saved final JSON (read as UTF-8 with BOM).
They match exactly. All 18 root-pair intervals and 372 conditional state-pair
audits pass; all 231 selected-edge/root virtual transports equal the dense
formula. The new test file was inspected: it covers singleton cancellation,
zero-length edges, interior mass, branching LCAs, all Dirac pairs on a branching
tree, dense rational masses, and disabling evaluator audits. The PO reports 96
suite tests passing; the reviewer did not repeat the full unrelated suite.

## Repair 2 and final diagnostic conclusion

The O(FN) feature-neighbor graph plus MST matches the proposed bounded repair.
Weights are computed on the candidate graph before the evaluator reference;
MST selection preserves the original upper-domination proof. All candidate
weights, including discarded edges, are charged. Some small layers become
complete graphs, so these fixtures do not demonstrate asymptotic sparsity.

The final intervals are:

| Family, window | Final query intervals (A, B) | Final decision |
| --- | --- | --- |
| Reconvergence, k1 | [3/16,5/16], [1/2,3/4] | A closer |
| Reconvergence, k2 | [3/16,5/16], [1/2,3/4] | A closer |
| Information timing, k1 | [1,5/2], [2,7/2] | Unresolved despite true 1 < 2 |
| Information timing, k2 | [2,3], [2,4] | Unresolved; true tie |
| Genuine k2, k1 | [0,0], [0,0] | No strict order; reconstructed target is zero |
| Genuine k2, k2 | [2,2], [1,1] | B closer |

Repair 2 therefore passes its own construction gate: it recovers the previously
unresolved reconvergence strict orders and preserves the genuine-k2 certificate.
This conclusion uses the final single candidate; it does not require a free
unaccounted ensemble of historical trees. MST optimality concerns total tree
weight, so no pairwise monotonicity guarantee is inferred beyond these results.

The independently inspected ordinary-path reference uses rational uniform
expansion and exact assignment DP on the reconstructed law, entirely in the
evaluator. On reconvergence, L(Q,A)=3/16 exceeds ordinary path OT=1/16. Thus the
conditional bank demonstrably exceeds an ordinary-path lower certificate on
this control. The genuine-k2 successful order alone would not show that: its
ordinary and adapted distances coincide. Equal marginals and the k1 ablation
show a conditional dependence mechanism but must retain that distinction.

## Virtual transport: proof and actual complexity gate

The sparse primitive is an exact implementation change. Add LCAs of consecutive
Euler-sorted nonzero signed-support vertices, add the global root, deduplicate
and sort again, and connect each virtual vertex to its nearest virtual ancestor.
An omitted off-Steiner branch has zero imbalance. Along any compressed path the
subtree imbalance is constant, so its contribution is exactly the absolute
imbalance times the difference of endpoint root distances. Summing these values
equals the dense subtree formula. Ancestry uses Euler intervals, so duplicate
root distances caused by zero edge lengths do not corrupt the construction.
The inspected implementation follows this argument and accumulates exact
Fraction mass in reverse virtual order, asserting zero total mass.

Let m be the number of entries read from the two input distributions and s the
nonzero signed-support size after cancellation. Index preprocessing costs
O(N log N) space/work. A query costs O(m+s log s+s log N), without a tree-depth
factor, including terminal chains. Empty signed support is handled immediately.

For F feature coordinates, each median-tree vertex has degree at most 3 and
each sorted coordinate contributes at most 2 incident edges. The candidate
graph degree is therefore at most 3+2F. Consequently the summed input support
read over a layer's candidate-edge queries is O(F E_t), and their virtual
transport work is O(F E_t log N_next), using log(2+N) to include singleton
layers. This removes the earlier dense N_t*N_next traversal term under fixed F.
It does not remove the input-size dependence if transition rows are dense.

Include all per-tree O(N log N) indexes, root queries, feature generation,
candidate graph/MST sorting, and rebuilding for a new batch. The implemented
median recursion re-sorts subproblems: its upper bound is
O(F N log N + N log-squared N), not O(N log N). These are operation bounds with
rational arithmetic/key operations treated abstractly; bit growth and actual
wall time remain separate. Thus the structural savings mechanism now survives
review, while practical break-even remains unestablished. The reported virtual
visits, index entries and LCA lookups are different work units and cannot be
subtracted or turned into a speedup ratio.

## Final admission and next bounded investment

Admit the two certificate inductions, pair-min probe extension, feature-MST
upper construction, exact virtual transport, the support-sensitive operation
bound with the stated additional costs, and the listed adaptive diagnostic
outcomes for the frozen versions above. The construction really avoids an
exact-lumpability premise and a global TV-times-range envelope; no such
assumption has been hidden in the implementation. This is a concrete upgrade of
the shared conditional tree and its algorithm, not merely an auxiliary lemma.

Do not admit universal probe separation, uniform tree distortion, long-horizon
usefulness, population AW or squared-cost guarantees, fast online insertion,
production float integration, measured coverage/speed superiority, SOTA,
publication novelty, or completion of the scientific objective. Established
proof ingredients do not invalidate the algorithmic investment, but this review
has not conducted a general overlap search for the full algorithm.

Recommend stopping construction tuning on these six controls and making the
next bounded investment the design of one frozen small cost/decision probe of
this exact candidate against eligible early-stopping baselines. Fix
anchors/feature width, graph rule, input representation and batch
accounting before sampling or scaling. Charge construction and indexes as well
as queries; keep the unresolved information-timing case visible and distinguish
true ties from abstentions on strict orders. The next decision should be whether
the complete algorithm earns useful certified decisions for its total cost on
the admitted finite AW1 target. This review admits bounded protocol design;
it does not authorize a broad performance run, further tree retuning, or bypass
the workflow's probe-admission gate. Publication novelty is a separate open
question. This recommendation adds no completion condition to the interrupted
construction cycle the user asked to finish.

No sign-off extends to future artifact edits or empirical claims.
