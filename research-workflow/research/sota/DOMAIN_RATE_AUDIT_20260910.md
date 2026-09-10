# Domain-rate audit before choosing an estimand

Date: 2026-09-10. Independent source audit of the domain update at `790b555`.
Decision: **retain the existing finite-model solver target; no estimand switch is required by these results.**
This note corrects interpretation, preserves the imported knowledge file, and introduces no hypothesis or performance claim.

## Verified theorem boundaries

**Mirmominov–Wiesel, arXiv:2512.18838v1.** Definition 3.3 uses additive **AW1**.
Section 3.2, equations (5)–(6), defines a quantized empirical path law, retaining full-prefix conditioning.
Theorem 4.2, equations (15)–(16), assumes compact support and Lipschitz kernels:

`E AW1(mu, muhat_N) <= C sqrt(1 + 2 sum eta(s)) rate_inf(N)`.

For `d=1`, `rate_inf(N)=N^(-1/(T+1))`; `C` depends on `L,d,T,support`.
The unbounded-support result is **different**: Theorem 4.6, equations (17)–(18), under Assumption 4.5, uses
`rate_p(N)=N^(-(p-1)/(pT)) + N^(-1/((d+1)T))` for `d=1,2`.
Here `p` controls moments; it does not turn the target into AW2 squared.
Section 3.3 and Proposition 3.8 concern dependence **across observed paths/blocks**; independence makes these mixing coefficients zero.
[Primary full text, Sections 3–4](https://arxiv.org/html/2512.18838v1).

**Larsson–Park–Wiesel, arXiv:2503.10827v2.** Section 1.4, Theorem 4 gives expected smooth AWp error `C/sqrt(n)` for iid paths, fixed `sigma>0`, and `1<p<infinity`, assuming
`integral exp(q |x|^2/(2 sigma^2)) mu(dx) < infinity`, with `q>8p(2p-1)(T+9)`.
This is an **exponential-moment** condition, not merely a finite qth moment.
Remark 5 says the prefactor may grow exponentially with dimension and deteriorate for small sigma; the p=1 discussion cites separate results.
Section 1.3, equation (11), reports smoothing bias controlled by kernel regularity moduli, becoming `O(sigma)` for Lipschitz kernels.
The bound concerns AWp, not directly its pth power; smoothing changes both path laws by Gaussian convolution.
[Primary full text, Sections 1.2–1.4](https://arxiv.org/html/2503.10827v2).

## Corrections when applying this to the repository

These are audit deductions, not additional claims attributed to the papers.

1. **0.84 is a rate factor, not an error estimate.** Direct arithmetic gives
   `4000^(-1/51)=0.84991`, `6000^(-1/51)=0.84318`, `8000^(-1/51)=0.83843`.
   An upper bound with unknown constants cannot establish a positive noise floor,
   nonidentifiability, failure to converge, or deterioration of the measured contrast/noise ratio with T.
   Even a worst-case sharp rate would not identify the error on this particular parametric family.
   Thus “literature predicts 1.31–1.51x” and “nearly unidentifiable at T=50” are unsupported inferences.

2. **The objects do not yet match.** `adapters/common_model.py:build_window_model`
   pools transitions by the last `min(k,t+1)` quantized states; the solver then evaluates this reconstructed law.
   This differs from the full-prefix quantized empirical path measure in the cited theorem.
   Even an originally Markov process need not remain Markov after quantization.
   A fixed-k approximation can trade estimation variance against window bias; neither paper provides its rate here.

3. **The generators are unbounded and independent across rows.** `generators.py` uses fresh Gaussian
   innovations for each path, with deterministic time zero. Temporal dependence within each row is not
   dependence between observed paths. The compact-support result cannot simply be applied to these laws;
   observed sample extrema do not make the population compactly supported.
   Rescaling by sample extrema also does not justify comparing delta with the theorem's prescribed grid width.

4. **“Gaussian” does not automatically satisfy the fast-rate theorem for a chosen small sigma.**
   For a centered Gaussian with covariance A, direct diagonalization of its Gaussian density shows
   `E exp(q |X|^2/(2 sigma^2)) < infinity` iff `sigma^2 > q lambda_max(A)`.
   At `p=2,T=50`, the stated theorem requires `q>2832`.
   This is a sufficient-theorem applicability check, not a necessary condition for the true fast rate:
   failure to meet it does not prove smoothing fails. It does block an unqualified small-sigma guarantee.

5. **A distance bound needs conversion to the reported value.** The contract reports `V=AW_p^p`.
   For `p=2`, an absolute distance discrepancy `e` yields
   `|d_hat^2-d^2| <= e(2d+e)`; an expected first-moment distance bound alone does not bound its squared moment.
   A relative population certificate additionally needs scale/lower-bound information and all pipeline errors.

## Consequence for the next decision

`objective.json` already distinguishes finite-model certification from population estimation.
Keep that distinction and the original solver target. A Gaussian population oracle on the matching
quadratic AR1 task is a cheap diagnostic of total pipeline discrepancy; its true parameters remain
outside the candidate's paths-only information set. Finite-minus-population error from one sample is
a realization of discrepancy, not a measured expectation/bias or a population certificate.

Do not launch a smoothing implementation or a large grid based on these exponents.
Only open a separately labelled smoothing study if a specified population objective, admissible sigma,
usable constants/bias control, and a feasible same-information computation justify the cost.
This audit leaves the root-certificate tightness problem active and makes no impossibility or SOTA claim.
