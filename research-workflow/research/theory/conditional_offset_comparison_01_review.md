# Conditional-offset comparison 01 — independent review

2026-09-10. Bounded theory/prior-art reviewer assignment, not PO. Only this
review file is owned by the reviewer. No implementation or performance probe.

## Preliminary review, before final fixture

Draft `conditional_offset_comparison_01.md`, SHA256
`b9b9de99786997c81f2ce7a63b132f05d7fa85bb142f969fa9bae35d4994791c`.
Final fixture, checker, output and later packet bytes have not yet been reviewed.

**Preliminary investment recommendation: KEEP as a useful exact subclass
baseline; KILL a standalone coverage/performance probe justified only by this
factorization.** The mathematics is correct on the stated domain and retains
conditional mean information. However the successful result is an immediate
centering specialization of established bicausal DP. A new component recognition
or approximation mechanism is not supplied by this packet; benchmark speed
cannot create such a contribution retroactively. This is a significance
assessment under the project's stated priority, not a mathematical rejection.

### Independent proof and filtration checks

Let `I` and `J` denote the components observed at time 1. In a bicausal coupling,
the law of the query future conditional on `(I=i,J=j)` equals its law given
`I=i`, and the analogous assertion holds for the candidate. This follows from
causality at time 1 in the two directions. In particular, the centered residual
means are zero conditional on the *pair* `(i,j)`, not merely on each marginal's
own component. Subsequent conditional coupling kernels are bicausal for these
two conditional future laws.

For a fixed pair `(i,j)`, subtracting `a_i` and `b_j` coordinatewise is an
invertible adapted deterministic transformation of the respective conditional
natural filtrations. Thus the conditional feasible set is exactly
`Pi_bc(Z,W)`. For every coupling in this set,

    E sum_t (a_i,t+Z_t-b_j,t-W_t)^2
      = sum_t (a_i,t-b_j,t)^2 + E sum_t (Z_t-W_t)^2.

The cross term vanishes by the fixed zero marginal means. No Gaussian,
monotonicity, independence-across-time or equality of Z and W is used.
The residual minimum is the same number `C` at every component pair.
The bicausal first-stage decomposition therefore gives

    D(Q,X) = min_gamma sum_ij gamma_ij [M_ij+C]
           = OT(alpha,beta;M)+C.

Attainment is elementary on finite supports: choose an optimal root coupling
and attach an optimal residual coupling at every positive-mass root pair. The
conditional kernels have the prescribed marginals, and concatenate to a
bicausal full coupling. This proves both inequalities, not only an upper bound.
With the same candidate residual law W, subtracting two such identities gives
the claimed exact order and tie equivalence without determining C.

Initial observability is substantive. An unobserved latent component cannot
be treated as an initial state or added to the filtration without changing the
target. Repeated observed first values are harmless only if one groups by the
actual observed value and verifies the required conditional law after grouping.
Later overlaps of supports do not break the full-history result: the initial
tag remains in the natural filtration. A k-window reconstruction may erase
this dependence; the formula must then be checked for that reconstructed
process, as the packet correctly requires.

For canonical finite processes with natural filtration, equality of full
ordered residual path laws already determines equality of those natural
filtered laws. There is no extra hidden-filtration equality to infer from
identical one-time marginals. If external latent information is present, the
declared natural-filtration statement does not cover it.

### Closest primary sources and overlap

1. Peyré and Cuturi, *Computational Optimal Transport*, Remark 2.19, gives the
   squared-Wasserstein decomposition into squared mean difference and the
   distance of centered measures. The same square expansion applies here
   because deterministic translations preserve the bicausal feasible set.
   [Authors' book PDF](https://optimaltransport.github.io/pdf/ComputationalOT.pdf).

2. Backhoff-Veraguas, Beiglböck, Lin and Zalashko, *Causal transport in discrete
   time and applications* (2017), Props. 5.1–5.2, supplies the conditional-kernel
   characterization and general bicausal DP. Inserting the centering identity
   into the first stage gives the entire factorization in this packet.
   [Author manuscript, §5](https://www.mat.univie.ac.at/~mathias/Causal_arxive.pdf).

3. Delon and Desolneux, *A Wasserstein-type distance in the space of Gaussian
   Mixture Models* (2020), Proposition 4 / equation (16), reduces their
   mixture-restricted transport to a discrete OT over component weights with
   component Wasserstein costs. This is a close computational architecture,
   not a theorem identifying ordinary latent-mixture OT with this target.
   Here component observability and bicausality make the decomposition exact
   for the declared adapted target. That distinction is valid but is already
   explained by the preceding DP source.
   [Primary paper](https://arxiv.org/html/1907.05254).

4. Dusson, Ehrlacher and Nouaime, *A Wasserstein-type metric for generic mixture
   models, including location-scatter and group invariant measures*, Definition
   3 / equation (9), formulates mixture transport with a general component
   metric; §4 discusses affine-generated component families. It confirms that
   non-Gaussian component OT and location-family framing are established.
   It does not state this exact finite adapted ranking formula, and its
   location-scatter formulas are not used to justify arbitrary residual AW.
   [Primary preprint](https://arxiv.org/html/2301.07963).

The targeted search did not find the literal ranking formula under this exact
name. Novelty is not inferred from that absence. The assessment is based on
the explicit short derivation from the closest DP and centering results.

### Matched decision comparator and the probe decision

One conceptual comparator design can recognize the identical residual
subproblem symbolically, keep its value C unevaluated, and cancel it before
ranking. It would perform the same root OTs with zero residual solves. However,
this review has not identified a published or implemented eligible comparator
that actually performs that recognition. Hypothetically giving a comparator
the proposed mechanism is not evidence against its scientific value or proof
of measured performance parity. The standalone no-probe recommendation rests
on the explicit elementary centering-plus-DP derivation, not on this hypothetical
comparator. Actual performance against eligible early-stopping solvers remains
unmeasured. Comparison with full value solves alone would not establish it.

Full residual path dictionaries are a valid applicability test for supplied
finite path laws. Their input is not small merely because the number of initial
components is small: exact reconstruction can have exponentially many paths.
The packet correctly disclaims a scalable k-window recognition implementation.
Residual-law equality is also a restrictive exact assumption on independently
reconstructed empirical models. Neither observation invalidates the theorem;
both prevent using cheap root OTs alone as a practical efficiency conclusion.

The final fixture can establish that unequal and temporally nontrivial residual
AW cancels, and that conditional mean scores distinguish a moment-matched
order reversal. This would make a better exact baseline. It would not alter
the established-DP derivation or measure a matched-comparator advantage.
Accordingly the bounded investment answer is to finish this
construction/review and retain it, **not fund a performance probe of this
factorization alone**. A separately specified mechanism beyond these ingredients
would require its own investment decision, not automatic continuation here.

## Final version-bound review

Completed 2026-09-11. The preliminary section above is retained as the earlier
assessment; its specific statement that model-level recognition is absent is
superseded by the reviewed delta below. Final accepted artifact versions:

| Artifact | SHA256 |
|---|---|
| `conditional_offset_comparison_01.md` | `88ba1015a4279ede37108ef3a1a1abcd6a2fbcff27d2cd88b3879d8090c67f5a` |
| `../../tools/check_conditional_offset_comparison_01.py` | `7c9fd87dcab12dbf465a9a280390bc6146c8ab260573bda8a682c9fd7ab61acf` |
| `conditional_offset_comparison_01_checks.json` | `cbad3d06f3471656dbc308b9c8036155e7550bd49cc0f76c98490ff63093200c` |
| Imported `check_signed_prefix_comparison_01.py` | `23181ec7c2bf701f9bed89cb4630f92393a42bf2a37b12cc77f146d3cfc74020` |
| Imported `check_geometry_condition_screen_01.py` | `b6bed1f47a70fe63ae37e6c6d147442be4e055ba0cb18894bc3bc590730cbd46` |

**Accepted on its declared finite-model domain:** factorization and exact-order
guarantee; sufficient centered-kernel recognition for valid supplied models;
independently verified exact example, ordinary/adapted gap, assumption controls,
and unequal-weight gap; the packet's carefully limited computational accounting.
The two dependencies are pinned for reproducibility, not granted new blanket
sign-off on unrelated functions or historical claims. The review checks the
model-builder semantics used by this delta and relies on the already completed
independent arithmetic arguments, not a repeated full historical audit.

**Final investment recommendation:** ratify retention as an implemented exact
conditional-order baseline on this subclass; no standalone central-candidate
performance/coverage probe. The positive result and checked polynomial model
recognition are real progress. The additional scientific contribution beyond
centering, conditional DP and direct kernel comparison remains insufficient for
the project's priority gate. Eligible early-stopping performance is unmeasured,
not disproved. Later versions do not inherit this sign-off.

### Completed fixture assessment and 2026-09-11 recognizer delta

The fixture uses independent fair signs and query/candidate residuals
`Z=(100L,400L+400N)` and `W=(100K,-400K+400M)`. The two residual path laws are
centered, unequal and non-Gaussian. Conditional on first residual values, the
optimal final-stage squared cost is `160000(L+K)^2`; the current residual cost
is `10000(L-K)^2`. Their sum is minimized by `K=-L`, giving `C=40000`.
This direct two-stage calculation independently checks the residual reference.

For mean paths `(J/2,dJ,4dJ)` versus `(bK,K,4K)`, the root cost is
`(J/2-bK)^2+17(dJ-K)^2`. Root optimization with fair signs gives scores `1/4`
and `9/4` for `d=1`, and the reverse for `d=-1`. Adding C gives the reported
adapted values `160001/4` and `160009/4`. A separate exhaustive enumeration of
all `8!` ordinary assignments, without importing the candidate/reference
functions, checked ordinary values `80001/4`, `80009/4` and their reversal.
It also checked the retained width-one control, where ordinary equals adapted.
These checks were completed before interruption and were not repeated on resume.

The equal-stage-marginal bad candidate changes its residual law to Z. Its
residual cost is zero, yielding target value `9/4` versus A's `160001/4`.
Ignoring common-residual equality would therefore reverse the ranking.
The full residual dictionary guard correctly rejects this input and rejects
component-dependent residuals. With query first-component probabilities `1/4`
and `3/4` and candidate probabilities `1/2,1/2`, feasible sign correlation has
extrema `-1/2,1/2`. The same root cost formula gives a score/target gap of 1,
independently confirming the unequal-weight output.

The new `centered_model` is a real improvement over the initial path dictionary
checker. It operates on supplied state windows and kernels. For each observed
initial state it propagates conditional state masses, computes conditional
coordinate means, subtracts the corresponding mean coordinates from every
reachable state window, and compares sorted normalized transition signatures.
It does not enumerate full paths internally. This closes the preliminary
objection that model-level recognition was entirely absent.

Independent soundness argument: fix an initial component. At each time,
subtracting its deterministic mean window is a bijection on that component's
reachable windows. The initial translated window consists of zeros. The
translated kernels are consequently the exact transition kernels of the
centered residual process, with deterministic leading zeros included. Two equal
signatures have the same initial centered state and equal next-state laws at
every reachable centered state. Induction on time gives equality of their
complete residual path laws and hence natural filtered laws. This proves a
sufficient applicability check, not a mere equal-moment test.

The validity precondition matters: kernels must be normalized, nonnegative and
consistent with the declared window shifts and deterministic zero start;
`masses[1]` must be the actual initial-component law. The function does not
perform a complete generic input-model validation. On valid models there is
one initial window for each observed initial value, so its `weights[tag]`
assignment cannot merge hidden components. Zero-probability extraneous edges
can cause unnecessary rejection unless removed; they do not justify accepting
invalid models. The theorem concerns arbitrary component counts, but the
current `compare_models` calls a binary-only root OT routine, so its implemented
ranking interface covers two initial components in each law.

For K initial components, E total reachable transition edges and window width
k, the recognizer costs at most `O(K E k)` arithmetic/coordinate work plus
signature sorting, mass/mean bookkeeping and root costs. It is not input-linear
in E when K or k varies. Rational bit growth is additional to this arithmetic
count. The displayed 72 edge visits count propagation and signature scans for
the small fixtures; 72 supplied path coordinates is a separate input-size
number, not total accesses. Model construction and reference reconstruction are
outside recognition and remain charged. The k=1/k=2 checks use this specific
family; k=2 execution does not itself establish a genuinely second-order
adversarial test or broad empirical coverage.

**Investment verdict after the recognizer delta: retain the exact conditional
location-mixture reduction and its model-level sufficient check as a useful
baseline; do not fund a standalone performance/coverage probe as the project's
central scientific candidate.** This verdict no longer relies on missing
model recognition. The added implementation is conditional probability
propagation followed by deterministic centering and exact kernel equality,
which closes a practical correctness gap but does not supply a nontrivial
theorem beyond the centering/DP specialization identified above. Actual
matched-solver performance remains unknown; no hypothetical comparator parity
is claimed. There is no demonstrated impossibility for a later substantive
extension, and no v3 completion claim follows from this exact subclass result.
