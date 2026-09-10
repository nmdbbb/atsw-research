# Signed-prefix comparison 01 — independent skeptical review

2026-09-10. Assigned reviewer only; no PO/checkpoint decision. This file separates
preliminary mathematical/prior-art assessment from the final artifact-bound
assessment to be appended after the root supplies its fixture. No benchmark run.

## Preliminary assessment

Reviewed draft: `signed_prefix_comparison_01.md`, SHA256
`086584178fa730c6db8b030d61cc6df84a6e321b4fc0c36e2665c7b6efe86dc4`.
This hash covers the initial mechanism and questions, not later fixture/results.

**Investment recommendation: keep as an auxiliary exact comparison baseline;
kill promotion of this theorem alone as a substantive v3 contribution.** The
statement is correct on its declared finite domain. Its proof combines a
filtration-preserving change of variables, elementary optimization inequalities,
and established bicausal dynamic programming. A successful illustrative fixture
can establish non-vacuity; it cannot by itself change this contribution assessment.

### Correctness, derived independently from conditional independence

Let `A`, `B`, `Q` be finite laws on a common horizon, with natural filtrations,
and let `F` and `G=F^{-1}` be adapted on their positive-mass supports, with
`F#A=B`. Thus `sigma(F(Y)_{1:t})=sigma(Y_{1:t})`, for every `t`.
For any bicausal `(X,Y)` with laws `(Q,A)`, replacing `Y` by `F(Y)` preserves
both conditional-independence definitions of causality, since the relevant past
and full sigma-fields of that coordinate are unchanged. The inverse argument
gives a bijection of the complete bicausal feasible sets. A marginal-preserving
map with information loss would not justify this equality of feasible sets.

Put `K=Pi_bc(Q,A)`, `a(pi)=E_pi C_A`, `d(pi)=E_pi Delta`,
`L=min_K d`, `U=max_K d`. The finite polytopes are nonempty and compact.
For every `pi`, `a(pi)+d(pi)>=min_K a+L`, which proves the lower bound after
minimizing. At an `a` minimizer, `a+d<=min_K a+U`, which proves the upper bound.
This does not assume that the optimizers of the two original distances agree.
The bounds need not be equalities. A signed maximum below zero certifies the
reverse ordering; zero endpoints alone do not certify a strict order.

For additive coordinate costs and `F(Y)_t=Y_t` after `s`, `Delta` is measurable
on `(X_{1:s},Y_{1:s})`. A full bicausal law restricts to a prefix bicausal law.
Conversely, append at each later time the product
`Q(dx_t | x_{1:t-1}) A(dy_t | y_{1:t-1})` to any feasible prefix law. The two
conditional marginals remain the prescribed one-process kernels, so the result
is a full bicausal law. Consequently minimizing/maximizing Delta on the prefix
gives exactly the full-horizon signed extrema. Signed stage costs cause no
problem on finite supports. These are extrema of the difference cost, not the
difference of two independently truncated distance values.

Qualification: a general adapted `F_t` may depend on the complete candidate
history. Then horizon `s` truncation remains valid, but a k-window state DP is
not justified without sufficient state augmentation. Layerwise state bijections
for genuinely k=1 Markov laws do suffice, provided the initial probabilities and
every reachable transition row are transported exactly. For k>1 the analogous
check must use the declared window states and their history consistency.

The suffix cancels from the signed optimization, **not from applicability
verification**. A supplied deterministic map must still be checked against the
full finite laws, including transition rows crossing `s` and later rows. Charging
zero future DP is justified; charging zero suffix read/check work is not.

### Targeted primary prior art and exact overlap

1. Backhoff-Veraguas, Beiglböck, Lin and Zalashko, *Causal transport in discrete
   time and applications* (SIAM J. Optim., 2017), Props. 5.1–5.2: conditional
   coupling kernels characterize bicausal laws, and a DP evaluates a general
   bounded-below Borel cost. The paper does not require Markovianity or additive
   costs for that result. Finite signed Delta fits directly. Setting future
   costs to zero yields the proposed truncation without a new DP theorem.
   [Author manuscript, §5](https://www.mat.univie.ac.at/~mathias/Causal_arxive.pdf).

2. Beiglböck, Pammer and Schrott, *Denseness of biadapted Monge mappings*
   (Ann. Inst. H. Poincaré Probab. Statist., 2025), §3, in particular Lemma 3.1:
   biadapted bijections and their recursive structure are established tools.
   The article's density theorem concerns additional regularity/atomlessness
   assumptions; it does not establish a convenient bijection for arbitrary
   empirical finite laws. Here the relevant overlap is the language and
   filtration structure, not an assertion that the density theorem proves this
   finite comparison bound.
   [Primary preprint](https://arxiv.org/html/2210.15554).

3. Pflug and Pichler, *A Distance for Multistage Stochastic Optimization Models*
   (SIAM J. Optim., 2012): nested distance controls differences of optimal values
   of suitable multistage stochastic programs. This is the relevant older
   stability setting, but not evidence that its theorem literally states the
   candidate's signed, query-dependent interval. The candidate uses a much
   stronger exact feasible-set identification and an elementary cost comparison.
   [Publisher abstract](https://epubs.siam.org/doi/10.1137/110825054),
   [author manuscript](https://www-user.tu-chemnitz.de/~alopi/publications/082505R.pdf).

4. Bartl and Wiesel, *Sensitivity of multiperiod optimization problems with
   respect to the adapted Wasserstein distance* (SIAM J. Financial Math., 2023),
   Theorems 2.2/2.4 and Lemma 3.2: studies small model perturbations, first-order
   sensitivities, and transfer of controls through bicausal couplings. This is
   a nearby but stronger/different sensitivity problem, not a literal duplicate
   of the finite signed-prefix certificate.
   [Primary paper](https://arxiv.org/html/2208.05656).

The common-feasible-set inequality above is derived directly and needs no
specialized attribution. This targeted search did not establish publication of
the exact same three-law interval. Lack of a literal matching title/formula does
not make the elementary combination a substantive new result. That last
sentence is the reviewer's significance inference, not a bibliographic claim.

### What the fixture can and cannot settle

For squared cost, if `h_t(y)=F_t(y)-y_t`, then
`Delta_t=2(y_t-x_t)h_t(y)+h_t(y)^2`. If `h_t` is a deterministic translation,
its expected signed cost is fixed by marginal means; no conditional OT is
required. A pointwise-positive difference is likewise a direct dominance
certificate. Those examples would be valid but scientifically uninformative.

A useful example would show a positive **bicausal signed** minimum while the
ordinary signed relaxation and marginal/pointwise differences cannot certify.
It should also show why the candidate correspondence is accessible from the
declared finite models. Overlap of separate distance intervals establishes
failure only of those particular retained intervals; it does not establish
advantage over strong early-stopping adapted solvers or comparison-aware bounds.

Even a favorable fixture leaves exact topology/mass matching as a severe domain
restriction for independently reconstructed models. The current packet gives no
new method to obtain/relax that correspondence, no new general class for which
the signed optimization is cheaper than its standard DP, and no new conditional
representation theorem. These are reasons to stop standalone investment at the
construction boundary, not a claim of impossibility for all later mechanisms.

## Final version-bound assessment

Completed 2026-09-10 on these exact bytes:

| Artifact | SHA256 |
|---|---|
| `signed_prefix_comparison_01.md` | `aa42b8838ddd0b97f17fe5693d1cd41da2648c1ac9b353d70761545ec1a0eb79` |
| `../../tools/check_signed_prefix_comparison_01.py` | `23181ec7c2bf701f9bed89cb4630f92393a42bf2a37b12cc77f146d3cfc74020` |
| `signed_prefix_comparison_01_checks.json` | `eac80c8450d4d6e899e9f122d3ebc24bc81c53a1632d3b02a88b2e6803a9f131` |

**Accepted with the explicit prefix wording qualification below:** the finite
comparison guarantee, truncation proof, moment-matched obstruction, exact fixture
results, and stated limited operation counts. The checker was inspected, and its
reported mathematical values were independently verified as described below.
No later artifact bytes inherit this sign-off. The last paragraph proposing a
new continuation-offset construction is outside this assignment and is neither
approved nor rejected here.

Wording qualification: the packet's phrase "leaving all prefix laws unchanged"
is correct only for the prefixes used by this certificate, namely through
`s=1`. The two-step query law changes with `d`. The accepted statement is equality
of the observed one-step Q/A/B prefix laws and of the entire fixed A/B pair,
with a reversal induced by Q's changed future conditional law. It is not
equality of every possible longer prefix law.

### Same-assignment additional evidence

The proposed product-coupling obstruction is correct. The law `Q tensor A` is
bicausal and therefore belongs to the feasible set defining both extrema. For
squared scalar coordinate cost its signed expectation is

    sum_t [E B_t^2 - E A_t^2 - 2 E Q_t (E B_t - E A_t)].

If candidate first and second moments match at every stage, this equals zero.
Thus `L<=0<=U` for **every query**; the unconditioned signed interval cannot
certify a strict comparison on this candidate class, however accurately it is
solved. Equality of candidate stage marginals implies the same conclusion for
absolute cost, and indeed any fixed integrable additive coordinate cost. This
argument does not require a particular prefix horizon. It applies wherever the
feasible-set identification used by this construction is valid. It does not
exclude a different certificate that restricts attention to plausible optimizers
using additional original-cost information.

Independent fixture derivation for fresh independent fair signs `J,L,N`:
`Q_d=(J/2,dJ+L,4(dJ+L)+N)` and
`B_b=(bJ,J+L,4(J+L)+N)`, with `A=B_1`.
The deterministic time-zero coordinate used in code contributes no cost.
At the final stage, synchronous coupling of the fresh signs minimizes squared
cost and gives `16(x-y)^2`. At the middle stage this combines with immediate
cost to give `17(dj-k)^2`, again by synchronous fresh-sign coupling. At the first
stage, minimize over the correlation `rho=E[J K]` in `[-1,1]`:

    D(Q_d,B_b) = 1/4 + b^2 + 17(d^2+1) - |b+34d|.
    [L,U] = [b^2-1-|b-1|, b^2-1+|b-1|].

These formulas independently verify the root's adapted values and signed
intervals. A separate exhaustive enumeration of all `8!` assignments using
integer doubled coordinates verifies the ordinary OT values below; it did not
import or call the candidate's subset-DP oracle.

| `(d,b)` | `D(Q,A)` | `D(Q,B)` | ordinary `(Q,A)` | ordinary `(Q,B)` | signed interval |
|---|---:|---:|---:|---:|---|
| `(0,3/2)` | `69/4` | `18` | `35/4` | `39/4` | `[3/4,7/4]` |
| `(1,-1)` | `1/4` | `9/4` | `1/4` | `5/4` | `[-2,2]` |
| `(-1,-1)` | `9/4` | `1/4` | `5/4` | `1/4` | `[-2,2]` |

The first example proves non-vacuity and a real ordinary/adapted distance gap.
However its signed problem ends at the first random stage and is ordinary
two-point OT; it does not demonstrate a conditional signed-comparison gain.
The last two examples hold the query prefix law and candidate pair fixed while
the query's later conditional dependence reverses the correct order. Candidate
stage marginals match. This is concrete evidence that the comparison discards
information needed for these decisions, consistent with the broader obstruction.

The positive example has `1+4+6=11` transport dispatches per full Markov value
and one for the signed lower endpoint. Both signed endpoints would need two
dispatches if computed separately. There are `2+4+6=12` distinct candidate
edges to inspect. These are operation counts for the displayed algorithms, not
lower bounds on eligible comparison solvers or measured end-to-end savings.
The implementation checks the full path-law pushforward and Markov row
consistency; its edge count estimates a layerwise check, it does not implement
a general production bijection search or a standalone row-by-row checker.

**Updated investment recommendation: stop this unconditioned signed-prefix
construction as the central candidate; preserve the theorem and positive
fixture as a valid auxiliary baseline.** The moment-matched blind class and
explicit conditional-order reversal supply stronger reasons than a generic
request for more testing. No coverage/speed probe should follow from this
packet. This is a scoped obstruction for a specified certificate, not a new
impossibility theorem for all adapted-OT comparison mechanisms or a completed
v3 scientific objective.
