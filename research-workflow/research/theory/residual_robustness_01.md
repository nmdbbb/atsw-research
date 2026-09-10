# Residual robustness 01

2026-09-11. Construction complete, final review pending. One finite analytic family, one repair if justified,
one independent review. No empirical prediction, sweep or performance probe.
Target: finite natural-filtration AW_2^2 on a declared scalar Markov subclass.

## Retrospective that changes this investment

The preceding cycle produced a correct exact-subclass certificate and a model
recognizer. It did not establish a central contribution or real-data advantage.
The nuisance cost 40000 can be increased by rescaling the residuals, so its
size is not scientific weight or performance evidence. Exact residual equality
may fail under reconstruction. Checking k=2 on the same Markov fixture does not
test genuinely second-order history dependence. No new workflow framework is
needed; test this mathematical fragility before broadening implementation.

## Concrete family and claims to check

For independent fair signs J,L,N, let sigma>2 and 0<=e<sigma/2. Let

    Q=(J/2, J+sigma L, 4J+4sigma L+4sigma N),
    A=(J, J+sigma L, 4J-4sigma L+4sigma N),
    B_e=(-J, J+(sigma-e)L, 4J-4sigma L+4sigma N).

All have fresh conditional randomness. Initial components are observed; each
conditional centered future law is component-independent. Candidate residuals
are W_0=(sigma L,-4sigma L+4sigma N) and
W_e=((sigma-e)L,-4sigma L+4sigma N); query residual Z has +4sigma L.
The component mean-path scores stay S_A=1/4, S_B=9/4 for all e. Pairwise
location factorization still holds, but the common offsets need not agree.

Exact identities, derived below and checked by the rational diagnostic:

    AW_2^2(W_0,W_e)=e^2,
    AW_2^2(Z,W_e)=(2sigma-e)^2,
    D(Q,B_e)-D(Q,A)=2-4sigma e+e^2.

Reason: the first residual coordinate reveals L in each law. The last-stage
conditional transport is between translations of the same fair-sign noise,
so it attains squared mean difference. For Z/W_e the first-stage residual
coupling should pair opposite signs; for W_0/W_e identical signs. Verify both
extrema rather than assuming the old optimal coupling persists.

If these identities hold, any positive fixed residual tolerance admits a
scale sigma for which the old score ranks incorrectly despite a margin of 2.
This would refute scale-free tolerance replacement in this construction, not
all robust conditional-order algorithms. A scale-aware stability bound or a
verified optimizer-dependent comparison may remain useful.

## Analytical result and a usable conservative certificate

The two exact residual conditional costs for Z/W_e are e^2+64sigma^2 when
the revealed signs match, and (2sigma-e)^2 when opposite. Balanced binary
transport chooses the opposite signs, for the entire stated parameter range.
For W_0/W_e the equal-sign and opposite-sign costs are e^2 and
(2sigma-e)^2+64sigma^2 respectively. Hence all displayed identities hold.
The restrictions sigma>2 and e<sigma/2 keep the middle-state labels distinct
across (J,L), making the full laws Markov; they avoid silently changing the
target when reconstructing k=1. Fresh final signs remain conditionally random.

The exact first reversal occurs at

    e_star = 2sigma-sqrt(4sigma^2-2)
           = 2 / (2sigma+sqrt(4sigma^2-2)).

The rationalized expression avoids cancellation. It is asymptotic to
1/(2sigma), not a fixed absolute tolerance. For any tolerance eta>0, pick
0<e<=min(eta,1/10) and sigma sufficiently large (and >2); then the residual
AW distance is at most eta but the mean score margin 2 has the wrong sign.
This construction proves failure of a SCALE-FREE positive matching tolerance
for this score. It does not preclude margin-and-noise-dependent certificates.

Let m=S_B-S_A be the exact component-score gap, delta a verified upper bound
on AW_2(W_A,W_B), and R an upper bound on AW_2(Z,W_A). Metric triangle and
reverse triangle give, with d(r,s)=AW_2(r,s),

    m + max(0,R-delta)^2 - R^2 <= D_B-D_A
                               <= m + 2R delta + delta^2.

For the lower inequality the function max(0,r-delta)^2-r^2 is decreasing in
r>=0, so replacing the unknown r=d(Z,W_A) by R is safe. The right inequality
uses d(Z,W_B)<=r+delta. Both preserve squared-cost units. This is a standard
metric-stability baseline, not a novel optimizer-aware theorem.

One free-of-OT choice is R^2=E||Z||^2+E||W_A||^2: independent coupling is
bicausal and the centered cross term vanishes. Obtaining delta is NOT free:
the diagnostic verifies an adapted invertible residual-path map and computes
its exact squared coupling cost. A general routine finding such a witness is
not implemented. Exact common residuals inside each process still need the
previous model check; only equality BETWEEN the two candidates is relaxed.

For this family R^2=66sigma^2 from input moments and delta=e. With e<=R,
strict positivity of the lower bound can be checked using only rational
arithmetic: require m+e^2>0 and (m+e^2)^2>4 R^2 e^2. Thus certification does
not need an inexact square root or knowledge of C=4sigma^2.

An essential interpretation: if the exact residual radius r=2sigma were known,
the reverse-triangle lower bound equals the TRUE change -4sigma e+e^2.
This family saturates standard metric stability; it cannot demonstrate an
optimizer-aware improvement over that bound. Exact r must not be supplied to
the candidate for free from the diagnostic formula. The difference between the
input-moment bound and the sharp boundary is a price of that cheaper information,
not experimental evidence of a new theorem.

## Following through: obtain a useful radius from a checked witness

The supplied map Z -> W_0 given by (z_1,z_2) -> (-z_1,z_2) is a biadapted
bijection. Writing the target sign as K=-L and the final fresh sign unchanged
proves the pushforward. The diagnostic independently checks exact residual
path dictionaries and computes its cost as 4 E Z_1^2 = 4sigma^2. This is a
feasible-policy UPPER bound, computed without asking the residual OT oracle.
Optimality of that witness is unnecessary for soundness of the certificate.
The W_0 -> W_e map rescales the first coordinate by (sigma-e)/sigma and leaves
the second fixed; its checked cost is e^2 and it is also biadapted.

Using these two witness costs in the same metric bound resolves cases that
the independent-moment radius leaves unresolved. This addresses an actual
missing input in the earlier argument rather than supplying the optimal radius
for free. The exact binary residual oracle subsequently verifies that this
particular witness is optimal, but is not a candidate input.

For sigma=100, the exact score margin is always 2:

| e | Exact target gap D_B-D_A | Moment-radius certificate | Two-witness certificate |
|---|---:|---|---|
| 0 | 2 | A closer | A closer |
| 0.001 | 1.600001 | A closer | A closer |
| 0.002 | 1.200004 | unresolved | A closer |
| 0.005 | 0.000025 | unresolved | A closer |
| 0.01 | -1.9999 | unresolved | unresolved |

A separate rational tie uses sigma=201/40 and e=1/10; its true gap is zero
and both strict certificates abstain. These are six deliberately chosen
algebraic controls, not sampled coverage observations. The negative-gap case
shows why abstention is needed: continuing to compare mean scores alone would
be wrong. This directional certificate does not assert B closer in that case.

Artifacts: [checker](../../tools/check_residual_robustness_01.py),
[saved output](residual_robustness_01_checks.json). Full-history and reconstructed
Markov references agree; actual reconstructed k=1 and k=2 laws equal the
fixture laws in every control. This does not turn the family into a test of
genuinely second-order dependence. Exact stored source/dependency hashes
identify the diagnostic; immutable previous artifacts are unchanged.

## Source, work and investment decision

The metric used is exactly the p-root of the sum-of-coordinate bicausal cost:
Backhoff-Veraguas et al., [Fundamental Properties of Process Distances,
equation (3.1) and the following metric statement](https://arxiv.org/html/1701.03955#S3).
The same section gives its conditional dynamic computation. Only relevant
metric/DP passages were checked; no broad novelty survey is claimed. Our
stability inequalities follow from this metric property by algebra. The
constructed family saturates the reverse-triangle inequality, so it supplies
no improvement over that nearest baseline.

The candidate computes two component OTs as before, input moments or feasible
witness costs, and an exact rational inequality. The new witness check reads
full residual path dictionaries and verifies two GIVEN maps. It is a finite
diagnostic certificate, not a general scalable algorithm discovering witnesses
on arbitrary k-window kernels. Map discovery, representation, checking,
arithmetic and conditional-model recognition must be charged. The oracle's
exact residual values are not passed to the certificate. No speed or material
work-advantage claim follows merely from avoiding an oracle call in this toy.

PO outcome to finalize after review: keep the scale-aware sufficient certificate
and sharp tolerance counterexample as supporting results. Stop the proposed
standalone robustness expansion as a central candidate: its proposed extra
optimizer information is exhausted by two feasible witnesses plus known sharp
metric stability. Do not run a grid to infer novelty or claim a general negative
paper. The exact-equality baseline can be used with this explicitly checked
conservative extension; unverified approximate matches must remain unresolved.

This cycle has quantitatively tested robustness and implemented a positive
certificate rather than only noting that robustness was missing. It also
identifies a concrete future investment boundary: scalable, inexpensive
witness construction on non-identical residual models would be a DIFFERENT
algorithmic task, requiring a specified mechanism and comparison with existing
coupling policies. Further algebraic variants of the same triangle bound are
not funded by this result. No workflow rule change is needed this cycle.
