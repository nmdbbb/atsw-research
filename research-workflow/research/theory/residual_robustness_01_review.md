# Residual robustness 01 - independent review

2026-09-11. Bounded reviewer assignment, not PO. Reviewer owns only this file.
No new family, random sweep, performance probe, or blanket sign-off on prior work.

## Preliminary independent mathematical review

Reviewed the initial analytic claims in `residual_robustness_01.md`; final
checker, output, model controls and certificate implementation remain pending.
This partial result is saved before those artifacts are available.
Initial packet SHA256:
`e10554fbab4e7b6705e1d879f5e3068e30509359e56d8d1ba16ed7e6bbee6929`.

**Mathematical verdict:** all three proposed analytic identities hold for the
declared natural full-history laws when sigma > 0 and 0 <= e < sigma.
The scale-free positive tolerance replacement fails. The metric stability
repair is standard and its sharp reverse-triangle form is attained by this
very family; the example cannot support an optimizer-aware improvement over
that form.

### Independent two-stage calculation

The first residual coordinates of Z, W_0 and W_e reveal their respective fair
signs because sigma and sigma-e are strictly positive. Conditional on signs
L=i and K=j, the terminal laws are translations of the same fair-sign noise
4 sigma N. Jensen gives a squared conditional-mean-difference lower bound;
coupling the fresh noises identically attains it, with admissible conditional
marginals. Therefore the exact residual first-stage cost matrices are:

| Residual pair | i=j | i=-j |
|---|---:|---:|
| W_0, W_e | e^2 | (2 sigma-e)^2 + 64 sigma^2 |
| Z, W_e | e^2 + 64 sigma^2 | (2 sigma-e)^2 |

Every coupling of two fair signs is a convex combination of their equal-sign
and opposite-sign assignments. The equal-sign assignment strictly minimizes
the first row. In the second row, equal minus opposite cost is
60 sigma^2 + 4 sigma e > 0, so opposite signs strictly minimize it. This
checks both extrema and does not assume an earlier optimizer remains valid.
Consequently AW_2(W_0,W_e)^2=e^2 and AW_2(Z,W_e)^2=(2 sigma-e)^2.
At e=0 the latter also gives AW_2(Z,W_0)^2=4 sigma^2.

For root signs J and K, the conditional mean-path root cost is
(J/2-bK)^2 + 17(J-K)^2, where b=1 for A and b=-1 for B_e.
Its equal/opposite-sign costs are 1/4 and 281/4 for A; 9/4 and 273/4 for B_e.
Thus the optimized mean scores are 1/4 and 9/4. Independent component centering
and conditional bicausal decomposition yield the exact target gap
2-4 sigma e+e^2. The roots and residual optimizations have both been checked.

For any positive unsquared AW tolerance tau, choose 0<e<tau and then
sigma > max(e,(2+e^2)/(4e)), avoiding any reconstruction collision if k=1 is
required. Residual distance is below tau but the gap is strictly negative,
whereas the mean-only comparison gives +2. For a squared-distance tolerance,
choose e^2 below that tolerance instead. No conclusion is obtained for a
bounded residual scale, or for algorithms using scale-aware uncertainty.

### Filtration and representation boundary

The analytic identity is valid for the natural path filtration. A k=1 model
reconstructed from these path laws may differ when the second coordinate
does not identify the root/sign history and those histories have different
terminal conditional laws. For B_e this issue can occur at sigma-e=1;
for Q and A the possible corresponding collision is sigma=1. The full
history retains the observed first component, so these collisions do not
invalidate the full-history calculation. They do forbid transferring it to
a reconstructed first-order Markov law without checking that law. The e=sigma
endpoint is excluded for a separate reason: the first residual coordinate
then fails to reveal its sign. Quantization can create either loss of
information and is not controlled merely by a coordinate perturbation norm.

### Scale-aware certificate and nearest known result

Write r=AW_2(Z,W_0), s=AW_2(Z,W_e), and delta=AW_2(W_0,W_e).
Metric triangle and reverse triangle give |s-r|<=delta. In particular,

    max(0,r-delta)^2-r^2 <= s^2-r^2 <= 2 r delta+delta^2.

If delta<=r the lower endpoint is -2 r delta+delta^2. Here r=2 sigma,
delta=e, and s=r-delta, so the lower endpoint equals the true offset change
exactly. A symmetric bound |s^2-r^2|<=delta(2r+delta) is valid but looser.
Any usable certificate must obtain and charge for certified information on
r or a suitable moment/coupling upper bound; an exact diagnostic residual
oracle is not a free input to a candidate claiming to avoid that solve.

Backhoff-Veraguas, Beiglbock, Eder and Pichler, *Fundamental Properties of
Process Distances*, equation (3.1) and the following metric statement, define
the same sum-of-coordinate-costs nested distance on natural filtrations;
section 3.1 gives its backward recursion. Its p=2 specialization supplies
the metric property used above. The square expansion is the reviewer's
elementary consequence, not a claim that the source states this ranking
certificate verbatim. [Primary manuscript](https://arxiv.org/html/1701.03955).
The similarly named finance stability distance is defined differently, so it
is not needed as a substitute source. No broad novelty search is claimed.

The signs here solve a two-by-two transport problem and terminal translations
admit a monotone noise coupling. The exact optimizer therefore follows from
elementary assignment/conditional transport. Calling this optimizer-aware
does not establish a new improvement: the strongest metric lower bound is
already attained. This assessment does not rule out useful optimizer
information in another, separately authorized setting.

**Preliminary investment recommendation:** KEEP the analytic counterexample
and a correctly charged scale-aware safeguard as a baseline/limitation result;
STOP a standalone performance or central-contribution expansion on this
family. It resolves a real fragility in exact residual cancellation but does
not establish a new robust ordering mechanism or empirical benefit.

## Final version-bound review

Completed 2026-09-11. Accepted artifact versions:

| Artifact | SHA256 |
|---|---|
| `residual_robustness_01.md` | `203999fd7b8988bda6e50bd71867d833527bb33f82e82b5ac167870b59a5761a` |
| `../../tools/check_residual_robustness_01.py` | `336425800d2f6ec0825ec9350e293b66855ca1a0bb7303639719b46120af7706` |
| `residual_robustness_01_checks.json` | `2020c47b31e8f08bdd3072f7213d2a13158dd7c8d5deb58e711f8da37fbd509c` |
| Imported `check_signed_prefix_comparison_01.py` | `23181ec7c2bf701f9bed89cb4630f92393a42bf2a37b12cc77f146d3cfc74020` |
| Imported `check_geometry_condition_screen_01.py` | `b6bed1f47a70fe63ae37e6c6d147442be4e055ba0cb18894bc3bc590730cbd46` |
| Imported `check_conditional_offset_comparison_01.py` | `7c9fd87dcab12dbf465a9a280390bc6146c8ab260573bda8a682c9fd7ab61acf` |

The dependencies are pinned for the specific functions used by this diagnostic;
this is not blanket review of unrelated historical claims. The reviewer read
the final packet and checker, checked the relevant centered-law helper code,
reran the checker successfully, and compared its parsed output with the saved
JSON for exact structural equality. Mathematical independence comes from the
explicit sign-cost and root-cost derivations above, not from rerunning the
same reference oracle.

**Accepted:** the exact identities and scale-free tolerance failure; the
scale-aware sufficient certificate for component-independent residual laws;
both supplied adapted-bijection witnesses and their computed costs; all six
reported rational cases and reconstructed k=1/k=2 law-equality checks. The
packet correctly distinguishes the certificate's inputs from diagnostic exact
OT outputs and accurately limits the witness implementation to path laws.

### Final domain and reconstructed-model check

The final domain sigma>2 and 0<=e<sigma/2 is narrower than the preliminary
full-history analytic domain. It gives sigma-e>1 and sigma>1. For any c>1,
the four values J+cL are distinct for the four sign pairs (J,L). Therefore
each second observed state identifies its root and residual sign; the terminal
transition depends only on that state. This independently explains why k=1
reconstruction preserves the full law in this domain. The explicit checker
also compares every reconstructed k=1 and k=2 path dictionary to its declared
law and invokes `centered_model`, whose component-signature equality check
rejects component-dependent residual models. These checks resolve the actual
representation objection for this domain. They establish neither resilience
to arbitrary quantization nor genuinely second-order dependence.

### Witness soundness and cost admission

For Z to W_0, the supplied map T(z_1,z_2)=(-z_1,z_2) is adapted and has an
adapted inverse. Setting K=-L carries the query terminal value to
-4 sigma K+4 sigma N, exactly the candidate residual law. Its pushforward
is verified by the checker using full residual path dictionaries. The
coupling cost is 4 E[Z_1^2]=4 sigma^2 and is calculated from those inputs.
Thus it is a valid upper bound on r^2 without proving or querying optimality.

For W_0 to W_e, the supplied map rescales the first coordinate by the strictly
positive factor (sigma-e)/sigma and leaves the second coordinate fixed. This
also has an adapted inverse, exact checked pushforward, and computed cost
e^2. A deterministic adapted bijection with adapted inverse induces a bicausal
coupling: either coordinate history determines the other history, which
verifies causality in both directions. Consequently both witness costs are
legitimate certificate inputs. The dictionary comprehensions do not merge
atoms for these injective maps. This code is not a generic validator for an
arbitrary supplied map or malformed probability input.

To justify upper bounds rather than exact radii, put r=d(Z,W_A),
d_0=d(W_A,W_B), r<=R and d_0<=delta. Reverse triangle implies
d(Z,W_B)>=max(r-delta,0). The function
max(r-delta,0)^2-r^2 decreases with r>=0, giving the final packet's lower
bound at R; triangle gives the upper bound 2R delta+delta^2. When delta<=R,
the lower target gap is m-2R delta+delta^2. Strict positivity is equivalent
to m+delta^2>0 and (m+delta^2)^2>4 R^2 delta^2. The checker enforces
delta^2<=R^2 and performs this rational comparison, so no square-root rounding
or uncharged exact residual value affects its answers.

The independent centered product coupling gives R^2=66 sigma^2, while the
query witness gives R^2=4 sigma^2. The latter is the source of the additional
certifications at e=1/500 and e=1/200. At sigma=100, direct gap substitution
gives 300001/250000 and 1/40000 respectively. At e=1/100 the gap is
-19999/10000 and both strict certificates abstain. At sigma=201/40,
e=1/10, the gap and witness lower bound are exactly zero; strict inequality
properly abstains. The e=0 and e=1/1000 cases likewise agree with the table.

These witnesses close a real missing-input objection: the improved radius
is obtained as a verified feasible-coupling cost, not supplied for free from
the exact OT oracle. Their optimality follows separately from this family's
binary conditional costs. Supplying these two maps therefore improves this
implemented certificate over the moment-only version, but remains standard
feasible-coupling bounds plus metric stability. The packet does not discover
witnesses from arbitrary kernels, and path-dictionary verification can be
expensive when the source representation is compact. No measured performance
or matched-comparator advantage has been established.

**Final investment recommendation:** ratify KEEP of the sharp tolerance
counterexample and actionable, correctly charged scale-aware certificate as
supporting results. STOP a standalone central robustness/performance expansion
of this family and further variants of its triangle-bound algebra. The
supplied-witness delta is a positive implementation result, but the mathematical
bound is already standard and exactly saturated here. A scalable witness
construction mechanism would be a separately specified algorithmic investment,
not a completion requirement or automatic continuation of this cycle. No
central scientific or broad impossibility claim is admitted. Later artifact
versions do not inherit this sign-off.
