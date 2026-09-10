# Signed-prefix comparison 01

2026-09-10. Construction complete; final version review pending. Not a registered
probe or accepted novelty. The separate verdict supersedes this status after review.
Target D(Q,X)=AW_p^p on finite supplied laws with natural filtrations; initially
p=2, declared restricted claim. One construction, one finite rational family,
one justified repair and one independent review. No coverage/speed experiment.

## Concrete proposed mechanism

Suppose A and B have a supplied, checked deterministic adapted bijection F,
with adapted inverse, pushing A to B. In a k=1 implementation this can be
layerwise state bijections f_t preserving initial probabilities and every
transition row. In addition f_t(y)=y for all reachable states at t>s. No
generator-only access or guessed topology is allowed; check the finite models.

Pull every QB bicausal coupling back by F inverse to obtain a QA coupling,
and conversely. On this common feasible set define C_A and C_B as their
pathwise total costs and Delta=C_B-C_A. Then

    min_pi E Delta <= D(Q,B)-D(Q,A) <= max_pi E Delta.

Indeed, C_B=C_A+Delta; take infima for the lower inequality and evaluate C_B
at an A optimizer for the upper. F being invertible AND filtration preserving
in both directions is essential, not merely having the correct marginals.

Since the stage difference vanishes after s, optimizing Delta requires only
the truncated Q/A bicausal problem up to s. Any truncated coupling extends
to the full laws by independent conditional continuation; any full coupling
projects to a truncated one. Thus no future continuation costs enter the
signed problem. A strictly positive signed minimum certifies A closer than B.
The general min-difference inequality is elementary optimization sensitivity;
possible scientific value would have to come from useful temporal truncation,
verifiable applicability and decision work on a meaningful domain.

## Questions to settle by actual construction

- Exact fresh-randomness example with ordinary versus adapted distance gap,
  positive signed bound and unresolved separate retained baseline intervals.
- Include all topology/bijection checks and signed DP work; compare a solver
  allowed to stop as soon as ordering is known, not just two exact-value solves.
- Does this mechanism differ substantively from known causal stability,
  common-feasible-set perturbation bounds, or standard prefix lower bounds?
- When F loses information or the models merely look similar, do not apply the
  theorem. Matching exact topology in empirical reconstruction may be restrictive.

## Results: exact finite family, not a performance experiment

Let J,L,N be independent fair signs. The law notation below defines separate
copies; it does not impose a reference coupling. Let

    A=(J, J+L, 4(J+L)+N),
    B=(b J, J+L, 4(J+L)+N),
    Q=(J/2, d J+L, 4(d J+L)+N).

Time zero is a common deterministic zero. Each law has eight equally weighted
paths and fresh randomness at all three stages. These are scalar Markov laws;
the checker verifies conditional rows agree across histories ending at the
same current value. F scales only A's first coordinate by nonzero b, so both
directions are adapted and the suffix is literally unchanged.

| d,b | D(Q,A) | D(Q,B) | ordinary QA,QB | signed interval |
|---|---:|---:|---|---|
| 0,3/2 | 69/4 | 18 | 35/4,39/4 | [3/4,7/4] |
| 1,-1 | 1/4 | 9/4 | 1/4,5/4 | [-2,2] |
| -1,-1 | 9/4 | 1/4 | 5/4,1/4 | [-2,2] |

The positive row proves the sufficient comparison is not vacuous, even with
an adapted/ordinary gap. The marginal lower bounds are 33/4 and 9; even the
EXACT near value 69/4 as upper cannot separate from the far marginal lower 9.
However its signed problem is only one time step and adds no conditional
information by itself. This is not evidence of a new conditional mechanism.

Independent analytic oracle: conditional stage-three optimum is 16(x-y)^2.
At stage two, conditional quantile transport of translated fair signs attains
17(d j-k)^2. Hence

    D(Q,B_b)=1/4+b^2+17(d^2+1)-abs(b+34d).

The checker instead performs rational binary transport at every full-history
node and every merged Markov node, with exact equality between both references.
Ordinary OT is independently computed by uniform assignment subset DP, not by
reusing the bicausal recursion. All three rows belong to one chosen family;
there is no random-sample coverage claim.

Artifacts: [checker](../../tools/check_signed_prefix_comparison_01.py),
[exact output](signed_prefix_comparison_01_checks.json).

## A class-wide obstruction to this particular certificate

Under the independent bicausal coupling Q tensor A, X is independent of both
Y and F(Y). For p=2 its expected signed cost is

    sum_t {E B_t^2-E A_t^2 - 2 E Q_t (E B_t-E A_t)}.

If A and B have equal first and second moments at every time, this is zero.
Consequently the EXACT signed interval always contains zero, for every Q.
The unconditioned signed-min/max certificate can never assert a strict order
on that class. This holds at any horizon and is not inferred from failed
experiments. For p=1, identical A/B time marginals likewise make the independent
expectations equal. These claims require the common-feasible-set construction
to be valid; they are not impossibility results for other order certificates.

The last two exact rows exhibit the obstruction with genuinely different
distances. A/B have identical entire time marginals. Reversing only Q's
conditional future reverses the target order while leaving all prefix laws
unchanged. A rule observing only those prefixes (and the fixed A/B pair)
cannot distinguish these two queries. An algorithm reading Q's conditional
future can; this is not a lower bound against all input-reading algorithms.
More accurate signed DP or a larger grid cannot repair this zero-in-interval
obstruction. The independent coupling being potentially very suboptimal is
precisely the lost information: the certificate optimizes over every coupling.

## Work, closest source and investment result

The one-sided signed calculation uses one binary transport call, versus 11+11
full Markov calls in the positive row and 14+14 in the other rows. Computing
both signed endpoints takes two calls. These are NOT generic LP calls: the
binary reference needs zero generic LPs. Nor are these end-to-end timings or
a comparison against the strongest early-stopping solver.

The fixture checker verifies the full-path pushforward. A layerwise production
checker is not implemented: 12 distinct A edges is the counted traversal size,
and checking all mapped probabilities/labels on both models, suffix included,
must be charged. Q input construction also costs work. The count does not
demonstrate a material total saving or prevalence on independently reconstructed
empirical models. Exact probability-preserving isomorphism is a strong condition.

The independent reviewer located Backhoff, Beiglbock, Lin and Zalashko,
*Causal transport in discrete time and applications* (2017), Propositions
5.1-5.2: bicausal kernel characterization and DP already cover finite signed
costs. Biadapted maps are established objects; the construction uses no density
theorem for atomic laws. See the review for primary links and source coverage.
The elementary min-difference inequality and cancellation of zero suffix cost
therefore do not constitute a central new theorem.

PO decision: close UNCONDITIONED signed-prefix bounds as a central v3 candidate,
retain the correct auxiliary tool and the scoped obstruction. No probe/grid.
This decision follows a constructed success, an exact conditional failure and
a proof for the whole moment-matched class, not another restatement of a gap.

The decision-changing follow-through is to test a different placement of the
cancellation: factor a common unknown continuation offset BEFORE optimizing
over the initial component coupling, instead of minimizing raw cost differences
over all couplings. A finite location-mixture construction can potentially do
this while retaining the query's conditional shifts. It must be checked on the
moment-matched reversal above and against prior art before any promotion.
