# Independent H-A quotient review, 2026-09-09

**Verdict: ACCEPT the narrow recorded result `development_performance_prediction_falsified`.** The registered requirement was at least 25% median logical Bellman-request reduction in **every** k=2 process/delta cell, across the two declared seeds. Four of six medians fail. The exact quotient lemma survives, and the recorded tiny analytic checks support the implementation on their stated cases. This result does not establish that all exact future-equivalence methods fail, that quotienting cannot improve runtime, or that the broader adapted-OT objective is unattainable.

Reviewed: `objective.json`; H-A in `research/theory/notes.md`; `adapters/common_model.py`; `tests/test_common_model.py`; the hypothesis and immutable preregistration for `H_A01_future_classes`; `probes/future_classes.py`; and `runs/cycle_1/H_A01_future_classes.json`. This reviewer did not rerun the experiment, run a benchmark, or change the implementation, preregistration, or result. The only computation during result review parsed the existing JSON and checked its arithmetic and file hashes. No novelty judgment is made.

## Recorded result and integrity audit

The six stored medians, independently recomputed from the two seed rows in each cell, are:

| Process | delta | Median reduction | Required | Result |
| --- | ---: | ---: | ---: | --- |
| AR(1) | 0.5 | 14.843815% | 25% | Fail |
| AR(1) | 0.3 | 22.931426% | 25% | Fail |
| AR(1) | 0.18 | 27.219390% | 25% | Pass |
| Nonmonotone second order | 0.5 | 14.810642% | 25% | Fail |
| Nonmonotone second order | 0.3 | 23.171560% | 25% | Fail |
| Nonmonotone second order | 0.18 | 27.934222% | 25% | Pass |

All 24 process/seed/k/delta rows are distinct and present. Every time series has 50 entries. Every stored fine and quotient total equals the sum of its entries; every reduction equals `1 - quotient_pairs / fine_pairs`; every quotient layer count is at most its fine count; and every total satisfies `quotient_pairs <= atom_only_pairs <= fine_pairs`. Every median and pass flag is correct. The current implementation, preregistration, and objective SHA256 values match the three hashes stored in the run.

The implementation takes `all(passed)` over exactly these six k=2 medians. Thus its failure status follows from the registered conjunction without cross-cell compensation. The k=1 rows, whose reductions range from approximately 0.533% to 3.506%, are reported but correctly have no minimum in this development gate.

The precise supported conclusion is: **the preregistered normalized-binary quotient implementation failed its chosen small-sample structural continuation criterion.** It is reasonable to decline promotion of this implementation as the sole broad performance mechanism on this evidence. A universal claim that exact quotients cannot be useful would exceed the experiment.

## Exact model and quotient construction

The adapter fixes a finite, time-indexed k-window Markov model with output `r_t(x)` equal to the current scalar cell representative. It charges times 1 through T, excludes time zero, and optimizes the initial coupling:

```text
V_T(x,y) = 0
V_t(x,y) = OT(P_t(x), Q_t(y), c_(t+1) + V_(t+1))
root = OT(mu, nu, V_0).
```

The state is the full available k-window. The theorem concerns this specified finite-memory model, not equality to the full-history empirical process or a population distance.

Two class maps are needed on each side. `F_t` identifies reusable **future values**, while `A_t` identifies successor atoms safe for evaluating the incoming cost plus future value. Construct them independently on each side, backwards, with interning confined to a time layer:

```text
F_T(x) = one common terminal future class
A_T(x) = (r_T(x), F_T(x))                  when T > 0

for t = T-1, ..., 0:
    signature_t(x) = exact distribution of P_t(x) over A_(t+1)
    F_t(x) = intern(signature_t(x))
    A_t(x) = intern((r_t(x), F_t(x)))       if t >= 1
    A_0(x) = F_0(x)
```

For T=0 there are no charged costs and all future/root classes may be merged. For T>0, terminal outputs must be retained even though all terminal future values are zero. At intermediate times, different current outputs may share `F_t` and therefore `V_t`, but they must remain distinct successor atoms when their incoming costs differ. At time zero, the output may be omitted because it is uncharged.

Equal output labels suffice for both squared and absolute scalar costs. This construction is conservative: it is not a claim to find every pair-specific or cost-specific coincidence of optimal values. Equality of a flattened future distribution, equality of a single scalar continuation value, and equality of recursively conditional futures are different conditions; the row-signature construction uses the last of these.

Let `p_t^f` be the common aggregate row for future class f. Define:

```text
U_T = 0
M_(t+1)(A,B) = c_(t+1)(r(A), r(B))
                 + U_(t+1)(F(A), F(B))
U_t(f,g) = OT(p_t^f, q_t^g, M_(t+1)).
```

The fine value equals `U_t(F_t(x),F_t(y))`. Aggregate the original initial marginals onto `F_0` and solve their root transport problem against `U_0`. A modal initial state is not a substitute.

### Pushforward and lift proof

Assume the equality at time t+1. Then the fine successor matrix `c_(t+1)+V_(t+1)` is constant on each `A_(t+1)`-by-`B_(t+1)` block. Every fine transition coupling pushes forward to a feasible coupling of the aggregate rows, preserving its objective.

Conversely, for a coarse coupling gamma and an original current pair (x,y), write `p_A = P_t(A|x)` and `q_B = Q_t(B|y)`. For u in A and v in B set

```text
pi(u,v) = gamma(A,B) * P_t(u|x)/p_A * Q_t(v|y)/q_B,
```

on blocks with positive p_A and q_B. Zero-mass blocks have zero gamma mass and contribute nothing. Summing over v gives `P_t(u|x)`; summing over u gives `Q_t(v|y)`. The lifted objective is unchanged because the matrix is block constant. Both infima are therefore equal. Backward induction proves the value claim; the same argument proves root equality after pushing forward and lifting the initial coupling.

Applying the lift conditionally at every original state pair gives transition couplings with the original marginal kernels, hence a feasible bicausal policy for the finite model. A quotient state need not itself be a literal k-window for this equality proof.

## Implementation audit and exactness limits

`aggregate_exact` converts each nonzero input probability using `Fraction.from_float`, sums those Fractions, divides by their exact total, and aggregates exactly over successor atom labels. It does not normalize in floating point before forming these exact signatures. `construct_classes` retains current output through `output.hex()` at charged times and implements the two class maps above. `quotient_value` uses successor atoms for the cost matrix and future classes for the continuation table, then performs the initial-law transport. No structural error was found in these functions.

The mathematical probability convention actually implemented is

```text
p_i^* = Fraction.from_float(raw_p_i)
        / sum_j Fraction.from_float(raw_p_j).
```

The theorem applies exactly to these normalized binary-rational rows. Float conversion and the shared numerical LP routine are separate approximation steps. `common_model.exact_dp` explicitly disclaims exact arithmetic and outward certification, so agreement with it cannot create such a certificate. The run correctly records `exact_arithmetic_certificate: false`.

There is a material limit on interpreting the negative development result: exact normalized binary rows can distinguish distributions that would agree when computed from the original integer empirical counts as rational fractions. Small floating conversion differences can destroy an exact equality and propagate class splits backwards. The registered convention is explicit and the recorded verdict is valid under it. It does not rule out more compression under an exact-count representation. Such a different representation would need a separate declared experiment and target/roundoff accounting; it must not be substituted into this frozen run after seeing the result.

## What the work counts establish

At source lines 217-219, the definitions are:

```text
N_fine = sum_(t=0)^(T-1) |X_t| |Y_t|
N_F    = sum_(t=0)^(T-1) |F_t^X| |F_t^Y|
N_A    = sum_(t=0)^(T-1) |A_t^X| |A_t^Y|.
```

These are coherent counts of Bellman transport-value requests for a complete backward sweep. They exclude the terminal layer, which requires no Bellman solve, and exclude the one final root request from both totals. They do not count actual numerical LP iterations or necessarily actual calls to a general LP solver: `_transport_value` handles singleton marginals directly. They also give equal weight to problems of different support sizes, omit changes to root problem dimension, and do not measure which computations an optimized eligible competitor would already share or avoid.

`N_A` is a useful logical ablation for output-preserving state quotienting; the development run computes that count, not a separate A-only solver execution. Likewise, the fine development count represents the disabled-merging schedule rather than an executed fine T=50 solve. The tiny fine/quotient executions do use the same transport routine.

The classes are cost independent because they retain exact current outputs. Reporting applicability to both cost families is legitimate; these are not independent replications of the work-count evidence. The source generators, k/delta/T grid, path count, shifts and seeds agree with the registered descriptions. The second process has explicit dependence on the older state through a nonmonotone sine term. Development root values and certificates are correctly marked uncomputed. Construction times are recorded, but no time-to-certificate or SOTA comparison follows from them or from the unrepeated tiny timings.

## Analytic checks and cheapest separating probe

The frozen 32-path fixture supplies the cheapest essential separation between structural equivalence and tolerance-based merging. X has paths `(z,0,b,0)` with balanced z in {-3,3}; b in {-1,1} is fair except at z=3, where its positive probability is `1/2 + epsilon`. Y uses balanced w in {-4,4} and fair c in {-2,2}, with paths `(w,0,c,0)`. The declared epsilon values are 0, 1/16 and 1/8, all realized by integer counts, with k=2, delta=1 and shift=0.5.

Only time two is charged nontrivially. Its squared cost matrix has diagonal 1 and off-diagonal 9; its absolute matrix has diagonal 1 and off-diagonal 3. Conditional transport at X's perturbed branch therefore costs `1+8*epsilon` squared or `1+2*epsilon` absolute. That branch has initial mass 1/2, so root values are exactly

```text
squared:  1 + 4*epsilon
absolute: 1 + epsilon.
```

All six stored fine and quotient values match these formulas. At epsilon=0 each side has future counts `[1,1,1,1]` and atom counts `[1,1,2,1]`; 12 fine Bellman requests become 3 future-class requests. An A-only schedule would require 6. Every positive registered epsilon splits X's time-zero and time-one future classes, and the recorded quotient request count becomes 5. The value of exact merging is therefore demonstrated without a tolerance parameter. Incorrectly keeping those perturbed rows merged and claiming zero error would contradict the analytic values.

The terminal negative control also behaves correctly: X paths `[0,0]` and `[0,2]` against Y `[0,0]` have squared value 2, while the deliberately unsafe terminal merge returns 0. The second-order fixture retains squared value 4 for k=2 and returns 0 for k=1, demonstrating why current-coordinate-only substitution changes this target.

Coverage limits remain: the standalone quotient probe does not run the separate crossed-initial-label and unequal-initial-mass fixtures already present in `test_common_model.py`, nor their absolute-cost second-order counterpart. The perturbation fixture does exercise a nontrivial initial average. Source inspection supports the correct root construction, but the missing candidate-specific sentinels should not be represented as completed checks. None is needed to reverse the already-failed structural threshold.

## Approximate TV envelope: valid derivation, not run evidence

For arbitrary fixed coarse partitions, let coarse costs approximate the original stage costs with uniform discrepancy eta_s on each block pair. Let a_t and b_t bound the TV discrepancy, within every current class, between each original row pushed onto the next coarse partition and the chosen representative row. TV means half the l1 distance. Define the coarse recursion using the same successor-cost convention and set

```text
R_(t+1) = osc(coarse_c_(t+1) + coarse_V_(t+1))
e_T = 0
e_t <= eta_(t+1) + e_(t+1)
       + R_(t+1) * min(1, a_t + b_t).
```

This bounds `sup_(x,y) |V_t(x,y)-coarse_V_t(A_t(x),B_t(y))|`. The range must include the incoming stage cost. Using only `osc(coarse_V_(t+1))` is wrong for this adapter: at the last transition that quantity is zero even when changing the terminal distribution changes the objective. The current-cost recurrence in H-A can be valid in its own indexing convention, but it cannot be copied into the adapter without this change.

To prove the marginal perturbation term, start from a coupling of p and q. Couple p to p' maximally and q to q' maximally, and use their conditional kernels to change its two coordinates. The resulting pair has marginals p',q'; the probability that either coordinate changes is at most `min(1, TV(p,p')+TV(q,q'))`. A matrix with oscillation R changes its expected cost by at most R times this probability. Apply the construction to an optimal coupling, then reverse the roles of the two marginal pairs. This proves the symmetric transport-value bound. Sup-norm nonexpansiveness of transport in its cost matrix contributes `eta_(t+1)+e_(t+1)` and completes the recurrence.

If the original initial marginals are pushed forward exactly, the root error is at most e_0. If initial marginals themselves are approximated, add `osc(coarse_V_0) * min(1, a_root+b_root)`. There is no time-zero cost term. A valid coarse interval [L,U] transfers to [L-e_root,U+e_root], with its lower endpoint additionally clampable to zero for these nonnegative costs. Solver error and verified arithmetic error must already be included in that coarse interval and in the envelope calculations.

A representative approximate coarse plan generally has the wrong aggregate marginals for an individual original row. It cannot be lifted directly by the exact-case formula. Repair its aggregate marginals first, then lift, if a feasible original-model policy is required. A scalar value-transfer bound alone does not supply that policy.

For the tiny fixture, retaining the epsilon=0 partition and representative row gives eta=0, a_1=epsilon and all other relevant discrepancies zero. The uniform root envelope is `8*epsilon` squared or `2*epsilon` absolute, containing the exact errors `4*epsilon` and `epsilon`. This is an analytic proposal for a later explicit TV validation probe, not a result executed by the reviewed run. It establishes neither a 0.5% root certificate on the development models nor population accuracy.

## Final disposition

- **Accept:** exact two-class construction and pushforward/lift lemma for the declared normalized-binary model; recorded tiny analytical agreements; stored arithmetic and hashes; failure of the registered development count criterion.
- **Reject:** interpreting that failure as a disproof of the lemma, of every exact-count quotient, of possible runtime gains, or of the overall research objective. POT/HiGHS agreement is not a SOTA result.
- **Unresolved:** rigorous numerical certification, approximate-TV implementation and validation, population error, exact-count compression, optimized runtime, and comparison with the strongest eligible same-target methods.

Preserve the failed run and its threshold. Retain exact quotienting as a proved reusable mechanism, with this implementation failing its preregistered standalone development promotion gate.
