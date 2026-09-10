# Conditional-offset comparison 01

Started 2026-09-10; completed construction 2026-09-11, final delta review pending.
The separate verdict will supersede this status without editing reviewed bytes.
One construction, one exact location-mixture family and assumption controls,
one justified repair, one independent reviewer. No preregistered probe yet.
Restricted target: finite-law AW_2^2, natural filtrations, deterministic time zero.
Supplied reconstructed k-window law must actually satisfy the conditions below;
latent generator descriptions alone do not establish applicability.

## Proposed factorization, before optimizing the initial coupling

At time 1 each process reveals its mixture component: Q_1=q_i with distinct q_i
and positive weights alpha_i; candidate X_1=x_j with distinct x_j and weights
beta_j. Conditional on this component, future paths have laws

    Q_(2:T) | i = a_i + Z,
    X_(2:T) | j = b_j + W.

The deterministic vectors a_i,b_j are the conditional mean paths. Z and W
are centered at each time, have finite support, and do not depend in law on
their own component. Their temporal dependencies are arbitrary and need not
be Gaussian, independent over time, equal to each other, or monotone. For a
query's comparisons with candidates A and B, the candidate centered residual
law W is the SAME for both. The query residual Z may differ arbitrarily from W.

Claim, subject to review:

    D(Q,X)=C(Z,W)+OT(alpha,beta; M),
    M_ij=(q_i-x_j)^2 + sum_(t=2)^T (a_i,t-b_j,t)^2,
    C(Z,W)=AW_2^2(Z,W).

Proof: the first component pair is chosen before either future is revealed.
Bicausality fixes the conditional future marginals to the corresponding
component laws. Deterministic translation and its inverse preserve their
conditional natural filtrations. For any conditional bicausal coupling,
expanding the square gives E||Z-W||^2+||a_i-b_j||^2 because both means are zero.
The infimum is therefore C plus that deterministic cost, for EVERY pair (i,j).
Any root component coupling can be extended with an optimal residual coupling
in each pair, so the lower bound is attained. Since root masses sum to one,
the constant C appears once outside the root OT.

For A and B with the same residual W, C cancels in D(Q,B)-D(Q,A). Thus their
ordering is EXACTLY that of two small OTs between their conditional mean paths
and the query's. No residual cross-process transport is needed for ranking.
This is not raw signed minimization: the conditional infima have been retained
before cancelling their common value. Equal time marginals A/B no longer force
the comparison to abstain. Ties of the small OTs imply ties of the target.

## Conditions and computational charges

The finite supplied laws must demonstrate initial component observability and
equality of the FULL centered conditional residual laws, including filtration,
not merely equal covariance or one-time marginals. The proof concerns natural
full histories; use on a reconstructed k-window model requires checking those
actual model laws, not substituting an unreconstructed path law. Atoms and
overlapping later supports are allowed if the declared model's filtration and
conditional laws are correct; unknown latent labels at time 1 are not allowed.

The initial diagnostic groups explicit paths by first value, calculates means,
subtracts them and compares exact residual path dictionaries. This can require
exponentially many paths for a compact reconstructed model. It is retained as
an independent structural reference, not used inside the model recognizer below.

The mechanism avoids solving C and all repeated residual node-pair transports;
mean-path construction and K_Q by K_X root matrices/OTs remain. Symbolically
cancelling C is a possible comparator design, not an identified implemented or
published eligible competitor. We cannot grant the comparator this mechanism
for free and then treat hypothetical parity as negative evidence. Actual
matched-guarantee early-stopping performance has not been measured; comparison
against full exact-value DPs alone does not settle it.

## Scientific question to decide in this cycle

Successful limited theorem: exact order within a declared common-residual
location-mixture class, including nonmonotone finite noise and arbitrary unknown
residual transport, with a finite-data applicability check. The ingredients
(squared-cost centering, conditional DP) are standard. Independent review must
decide whether this is only their elementary combination or has enough new
structural/computational content to fund a probe. No absence-of-search-result
novelty claim. Next append exact reversal, unequal-residual and assumption-break
checks, then make that investment decision rather than stopping at the question.

## Implemented recognition on finite k-window models

The diagnostic now includes `centered_model(masses,kernels)` and
`compare_models(models)`, which consume the actual finite model, not its path
enumeration. Preconditions are a valid time-layered k-window model with exact
rational positive reachable probabilities, compatible shifting windows and a
common deterministic zero time zero. Input model validity is a precondition;
this helper is not a validator for arbitrary malformed external dictionaries.

For each observed state i at time 1:

1. Propagate conditional state probabilities forward from that state using the
   supplied kernels. This yields every conditional mean m_i,t.
2. At time t, subtract the corresponding segment of the mean path from each
   reachable k-window. This translation is one-to-one within each component
   and time; no approximate state merging is performed.
3. Canonically sort each translated state and its translated probability row.
   Compare the entire sequence of normalized layers across components. The
   initial centered window is deterministic zero. Matching signatures therefore
   imply identical centered residual path laws by induction on the kernels.
4. Compare the candidate signatures across A and B; Q may have a different
   common signature. Build root mean-path costs and solve the component OTs.

Why the check suffices: conditional on i, translated windows are a deterministic
adapted bijection of original windows with an adapted inverse. Conditional
probability propagation visits exactly the states reachable under i. Given
valid shift-consistent windows, the normalized row system describes the
centered residual k-window process with its natural filtration. Equal reachable
row systems starting at zero generate equal path laws, even where histories
merge. Thus accepting the model proves the factorization's conditions without
substituting a generator or assuming the observed path law equals reconstruction.

Complexity is polynomial in the supplied model, not claimed linear in total
input size: for each model with K initial states and E edges, propagation and
signature extraction make at most O(K E) edge visits, with O(k) work per key
and sorting costs (conservatively O(K E k log(E+1))). Conditional means add
state-visitation work; exact rational operand lengths also count. Root matrices
cost O(T K_Q K_X) each, followed by their OT cost. Current root dispatch handles
exactly two positive components; larger root transports are a theoretical
extension requiring another solver, not implemented here. Stored signatures
and one-component propagation require up to O(E k) structural storage per
component, plus mean vectors/signatures retained for the three compared models.
No residual Q-by-X state-pair transport is computed. If K is large or signatures
fail late, applicability checking may consume the intended savings.

## Exact result and adversarial checks

Let J,L,N be independent fair signs and d in {-1,+1}. The main finite family is

    Q_d=(J/2, dJ+100L, 4dJ+400L+400N),
    A=(J, J+100L, 4J-400L+400N),
    B=(-J, J+100L, 4J-400L+400N).

Each law has fresh randomness at all three times, eight paths and nonzero
residual transport. Query residual Z=(100L,400L+400N); candidate residual
W=(100L,-400L+400N). The theorem is not using Gaussianity or Z=W.
All A/B time marginals match, so the previous unconditioned signed interval
cannot certify either strict comparison.

| Query | component scores A,B | true adapted values A,B | ordinary path OT A,B |
|---|---|---|---|
| d=+1 | 1/4,9/4 | 160001/4,160009/4 | 80001/4,80009/4 |
| d=-1 | 9/4,1/4 | 160009/4,160001/4 | 80009/4,80001/4 |

The common residual value is 40000, checked only by the diagnostic oracle.
The candidate compares scores without requesting that value. It asserts the
correct strict order and reverses it when query conditional shifts reverse,
unlike a prefix-only or equal-marginal comparison. Ordinary and adapted OT
differ by 20000 in every main row.

On both k=1 and k=2, independent reconstruction confirms the fixture path laws
equal the declared model laws. The model recognizer then receives only models,
visits 72 edges across propagation and signature passes for Q/A/B, and its two
root transports reproduce the exact gap (+2 or -2). Full Markov references use
21+21 binary transport dispatches; full-history references agree. The 72 supplied
path coordinates are INPUT SIZE, not a count of all accesses: the path checker
rereads values. Neither count is wall-clock speed or a lower bound for competitors.
Sorting, state visits, model construction and exact arithmetic costs remain.

Controls, all included in the reproducible checker:

- Replace B's residual by Z. Every time marginal stays the same but the common
  offset condition fails; ignoring it would reverse the correct order because
  the replacement has D=9/4. Both path and k=1/2 model checks reject it.
- Make a candidate's residual transition depend on its initial component.
  Both path and k=1/2 model checks reject it.
- Use initial query component masses 1/4 and 3/4 instead of equal weights.
  Model-recognized comparison still equals the exact full reference gap.
- The initial last-noise width 100 had equal ordinary and adapted values.
  That failed the intended adapted-specific fixture gate; the single reserved
  repair changed it to 400. The width-100 control remains reproducible in code
  and output. This is constructed diagnostic development, never blind validation.

[Checker](../../tools/check_conditional_offset_comparison_01.py) and
[saved exact output](conditional_offset_comparison_01_checks.json). Reproduce
with `python research-workflow/tools/check_conditional_offset_comparison_01.py`.
Source and imported reference hashes are included. Imported reference helpers
are diagnostic oracles, not uncharged information available to the candidate.
The independent reviewer uses separate analytical and exhaustive-assignment
arguments; agreement between two callers of one helper is not independence.

## Source boundary and PO decision to finalize after review

Nearest ingredients identified in the independent review: Peyre--Cuturi,
*Computational Optimal Transport*, Remark 2.19 (quadratic centering), and
Backhoff et al., *Causal transport in discrete time*, Props. 5.1-5.2 (conditional
bicausal DP). Component-weight OT is established in mixture transport, but an
unobserved latent-mixture theorem is not a substitute for our observed-component
proof. See [review](conditional_offset_comparison_01_review.md) for precise
primary links and the distinction between overlap and literal theorem identity.

The explicit finite-model recognizer removes the specific need to enumerate
all reconstructed paths. It does not establish prevalence of exact residual
equality, robustness to reconstruction noise, a novel recognition theorem or
empirical advantage. The combined proof remains short and uses known centering
and DP; no exact matching paper found is not evidence of novelty.

PO disposition to be ratified with the final delta review: retain this as an
implemented exact conditional-order baseline on a declared subclass, including
its input-checkable structural mechanism and the noise-cancellation example.
Do not fund a performance grid to manufacture scientific weight. This is a
concrete positive result beyond the preceding failed construction, while the
project's central-significance and empirical advantage gates remain unmet.
The current two-construction cycle ends after review/integration and a recorded
investment decision, not merely after writing a new list of missing evidence.
