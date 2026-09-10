# Gaussian population oracle: bounded diagnostic

Date: 2026-09-10. Imported domain knowledge: main `790b555`.
Decision: retain the finite-model solver estimand and add a separate population diagnostic.
No new hypothesis, large grid, smoothing implementation or SOTA claim.

Gunasingam--Wong Theorem 1.1 gives, for scalar Gaussian paths with their natural
filtrations and positive lower Cholesky factors L and M,

`AW2^2 = ||mean_left-mean_right||^2 + tr(LL^T)+tr(MM^T) - 2 sum_j |(L^T M)_jj|`.

We evaluate the equivalent nonnegative sum `||mean_difference||^2 + ||L-M S||_F^2`,
where S has the signs of those column products on its diagonal. The sequential
KR coupling has gap `4 sum_j max(0,-(L^T M)_jj)`.
[Primary theorem and Corollary 4.4](https://arxiv.org/html/2404.06625v4).

The generator starts at deterministic X0=0, not its stationary distribution.
We omit that shared coordinate and use X1..XT; its omitted cost is zero and the
remaining covariance is nondegenerate. The innovation factor is
`L_ij = sigma*a^(i-j)` for i>=j. Costs sum squared differences over all T stages.
This does not cover absolute cost, the nonlinear family, or arbitrary filtrations.

For the existing AR1 pair `(a,sigma)=(0.7,1.0),(0.55,1.15)`, all column products
are positive: population KR is optimal, with zero gap. This does not imply zero
gap for quantized empirical/window models, or for the candidate's SVD/NW policy.

| Horizon | Population AW2 squared |
|---|---:|
| 5 | 0.25551969317665985 |
| 8 | 0.5762261306857269 |
| 50 | 5.485216920503423 |

The following posthoc comparisons reuse archived numerical DP results. All use
T=5, 128 paths per side, seed 1000 and shift 0. No OT solve was rerun.

| k | delta | Finite model value | Finite/population |
|---|---|---:|---:|
| 1 | 0.5 | 3.836142672 | 15.0131 |
| 2 | 0.5 | 6.961485719 | 27.2444 |
| 1 | 0.18 | 5.057082043 | 19.7914 |
| 2 | 0.18 | 6.947079954 | 27.1880 |

These are realized total pipeline discrepancies, not estimates of expected bias.
They do not isolate sampling, quantization or finite-window approximation, do not
extrapolate to 4000--8000 paths/T50, and do not invalidate the finite solver target.
Population parameters are privileged audit inputs and must not enter the candidate.
The oracle and archived DP are float64 evaluations, not outward-rounded certificates.

Validation: five focused tests include an independent variance/covariance recursion
at T50, a negative-column-product Gaussian case with nonzero KR gap, deterministic
initialization, means, identity, and invalid inputs. An independent agent reviewed
the column orientation, theorem scope and generator match against primary text.
Review found no issue in the bounded AR1 scope; very large factors outside this
scope can overflow column-product metadata, so arbitrary-scale numerical robustness
is not claimed.

Reproduce from the repo root:
`python research-workflow/probes/gaussian_population_audit.py`.
The script verifies archived source pins and refuses to overwrite different results.
Full provenance and values: `runs/cycle_2/gaussian_population_audit_20260910.json`.

Read [the rate audit](../sota/DOMAIN_RATE_AUDIT_20260910.md) before interpreting the
imported convergence/smoothing claims. Neither the cited exponent nor this small
sample discrepancy establishes nonidentifiability or justifies changing estimand.
Next solver work must still identify a valid route to a narrower root interval and
measure omitted/shared work. Gaussian closed forms are an audit baseline, not a new
mechanism on the original paths-only domain.
