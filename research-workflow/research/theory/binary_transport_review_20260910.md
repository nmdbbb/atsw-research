# Binary-support transport review — 2026-09-10

**Verdict:** mathematically exact local specialization; shared ordering is an engineering hypothesis, with no established novelty.

For finite costs, normalized nonnegative marginals, and active rows r0,r1 with masses (p,1−p), put d_j=C[r0,j]−C[r1,j]. Every feasible coupling is π[r0,j]=x_j, π[r1,j]=b_j−x_j, where 0≤x_j≤b_j and Σx_j=p. Therefore

V=Σb_j C[r1,j]+min Σd_j x_j.

Fill ascending d. Choose λ satisfying Σ_{d<λ}b≤p≤Σ_{d≤λ}b; fill strictly cheaper columns completely and distribute the residual among equal-cost columns. Exchange of mass from a higher d to a lower d proves optimality. The dual certificate is

u[r0]=λ, u[r1]=0, v_j=min(C[r0,j]−λ,C[r1,j]),

with value λp+Σb_jv_j=V. For p=0 choose λ≤min d; for p=1 choose λ≥max d. Singleton support has its unique product coupling. Transpose for binary right support.

These potentials initially cover active supports. To extend across zero-mass columns, set v_j=min_active_i(C[i,j]−u_i); then extend zero-mass rows by u_i=min_all_j(C[i,j]−v_j). Feasibility and objective are preserved. Charge this extension if a global certificate is requested.

Cache by ordered row pair and immutable continuation-matrix version. Restricting a full sorted permutation preserves order for every right support and every marginal; shared order does not imply shared optimizer or value. Row reversal reverses differences. Matrix updates can reverse order: d=(0,1) becoming (1,0) invalidates the cached optimizer. Exact ties permit arbitrary deterministic splitting; approximate tie merging does not. Retain every strictly positive mass: arbitrarily small mass times sufficiently large finite cost has non-negligible value. Validate residuals and finite arithmetic; direct primal evaluation avoids the baseline formula’s avoidable cancellation.

Full sorting costs O(N log N), versus O(m log m) for each supported pair. Global-permutation scanning costs O(N) per query; cached-rank sorting still costs O(m log m). Count construction, restriction, sorting, allocation, cache memory, and fallback. Compare identical implementations with/without order reuse, plus the existing LP reference.

Exact DP propagation follows backward induction using identical stage-plus-continuation matrices and exact fallback for all remaining local/root problems. Numerical error is bounded by the sum of layerwise maximum local errors, plus root-solve error, since OT is 1-Lipschitz in the cost sup norm. Floating-point agreement is not an outward-rounded certificate.

One bounded primary-source search returned [a fixed-source bottleneck transportation algorithm](https://www.sciencedirect.com/science/article/abs/pii/S0167637798000534). Its objective differs; the accessible search abstract does not establish this min-sum specialization or order reuse. Full text was inaccessible. Fractional-knapsack equivalence is established above; directly matching prior art remains unresolved.

## Bounded implementation audit

Reviewed `adapters/binary_transport.py`, its tests, the screen probe, and frozen manifest/results. The threshold at the final filled column satisfies complementary slackness, including exact boundaries and ties. Transposition correctly swaps plan axes and dual potentials. Each layer owns a copied, read-only matrix and its own cache; changing the input matrix cannot stale that snapshot. Strictly positive supports remain present. The focused unittest run passed all three tests, including 40 random LP comparisons, tiny mass, ties, boundary, invalid ordering, transpose, differing marginals, and matrix replacement.

The probe retains the original finite-window recurrence, stage costs, initial-marginal root coupling, singleton expectations, and general LP fallback. Every recorded table matches the same-run LP within 7.11e−15; archived root error is at most 4.45e−16. Direct binary dispatch reduces LP calls 543→411 and 1067→308; recorded seconds are 1.074→0.864 and 2.206→0.847.

Identical-support reuse saves only 2/132 and 17/759 difference-order sorts (1.52%, 2.24%), fails the frozen 20%-on-each-case gate, and is slower in both observations. Retain direct binary dispatch as a numerical exact-DP baseline; reject this screened reuse mechanism. Broader cross-support reuse was not tested.

Counter caveat: permutation validation itself calls `np.sort(order)` on every solve; `sort_calls` counts difference argsorts, not all sorting. Timings include validation, matrix snapshots, costs, and support preparation; model construction and equivalence checks are separately reported. One fixed-order observation per arm cannot establish speed significance or SOTA. Extreme finite costs can overflow difference/dual arithmetic, and NaNs are not explicitly rejected after construction. The screen therefore supplies numerical evidence at tested scales, not an outward certificate or universal finite-input robustness. Frozen sources/results were unchanged.

## Support-local Monge theory check

For a finite matrix in its supplied row/column order, adjacent inequalities C[i,j]+C[i+1,j+1]≤C[i,j+1]+C[i+1,j] imply every Monge rectangle inequality: each larger rectangle deficit is the sum of its adjacent deficits. Convert each represented binary64 entry to `Fraction` before arithmetic; converting an already rounded deficit does not certify its sign.

For arbitrary nonnegative marginals with equal total mass, the northwest-corner coupling is optimal under these inequalities. Probability normalization is sufficient, integrality unnecessary. Equal costs and simultaneous row/column exhaustion are allowed; uniqueness is unnecessary. Removing zero-mass supports preserves the problem, while every tiny positive mass must remain. The source is the primary research paper [A Monge property for the d-dimensional transportation problem (1995)](https://www.sciencedirect.com/science/article/pii/0166218X93E0121E), whose publisher-indexed abstract explicitly states the classical two-dimensional theorem and attributes it to Hoffman. The targeted search recovered that abstract; opening the publisher page returned 403.

Required focused regressions: random integer Monge costs against LP, ties, unequal support sizes, simultaneous exhaustion, tiny positive mass, zero-support dispatch, and genuine violating-matrix fallback. For a rounding trap, use an all-ones 3×3 matrix with the final entry `nextafter(1,+inf)`: rounded adjacent sums can tie, but exact Fraction comparison must reject.

This certifies the current supported continuation matrix, avoiding replacement by a one-sided Monge envelope. Rechecking each numerical DP matrix permits a classical exact local solver with LP fallback; it does not certify accumulated floating-point recurrence error. Charge Fraction construction/checking and NW work. No novelty claim or approval of unseen implementation follows.

## Monge implementation verdict and conditional defect bound

Reviewed the adapter, three test definitions, screen, frozen manifest/results, and imported NW helper without rerunning. Fraction conversion precedes arithmetic; rejection routes to the original LP. Tests cover 20 integer-cost LP comparisons, exact ties, a one-ULP violation, leading tiny mass, and continuation destroying Monge structure. Recorded LP reductions are 411→164 and 308→298; table discrepancies are at most 1.43e−14 and roots agree. The two-case opportunity gate fails: acceptance is 60.10% versus 3.25%. Retain a classical numerical baseline observation, without claiming novelty or robust speed gains.

Two qualifications: the frozen manifest omits imported `adapters/policy_pool_candidate.py`, which supplies NW. Its cumulative-sum intersection implementation can numerically lose an interior tiny mass, e.g. `[.5,1e−20,.5]`, while passing the 2e−12 residual gate. The leading-tiny-mass test does not cover that case. Therefore exact structure certification does not imply exact marginal preservation. No frozen artifact was changed.

The proposed conditional relaxation is valid in exact arithmetic. Let Δ[i,j] be the positive part of M's adjacent defect and F[i,j]=Σ_{k<i,l<j}Δ[k,l]. The adjacent defect of F is Δ, so L=M−F is Monge and L≤M. For the NW plan π and normalized marginals,

OT(M) ∈ [〈π,L〉,〈π,M〉], with width 〈π,F〉≤ΣΔ.

Exact interval claims require rational plan/marginal arithmetic too. A ≤1e−10 defect-sum classification concerns current supported matrices only; root propagation, checking cost, and prevalence remain unproved. It does not overturn the previous global-envelope failure. No relaxation implementation was reviewed.

## Final defect/scale checkpoint audit

Read both audit probes and frozen manifests/results without rerunning. All 12 defect-audit and 7 scale-audit pinned hashes match current files; both result-to-manifest hashes match. Supplemental NW provenance is confirmed: current `adapters/policy_pool_candidate.py` matches historical `policy_pool_smoke_manifest.json`'s `candidate_sha256`, `fd1987a1e93e604029c4de155c8229e14f3c0ccc320bd834027db67cd5b99008`. The earlier Monge manifest remains unchanged.

The defect census uses exact rational entry arithmetic and exact threshold 1/10^10; baseline LP values remain unchanged. Fine-case tiny positive defects occur in only 12/298 rejected matrices (4.03%), failing the 20% fixture gate. No local interval fixture or root certificate was built.

The scale census matches the finite target's floor quantization, history truncation, and unique observed transitions. Positive empirical transition counts remain positive after row normalization, so support degrees require no probability approximation. With state counts nA,nB, singleton counts sA,sB, and general counts gA,gB: nonforced=(nA−sA)(nB−sB), general=gA·gB, binary=nonforced−general. These count transition-layer pairs; deterministic initial root coupling adds one forced solve if reporting full-DP totals.

Frozen T=50, N=4000/8000, seed 1000, shift zero, and amended two-law parameters are respected. Binary fractions among nonforced pairs fall from 24.31%/71.13% to 10.23%/27.62%; forced fractions are 15.10%/39.19%. The both-case 20% gate fails. Counts are cost-independent: duplicating squared/absolute costs adds no information. This is support evidence, without OT execution or benchmark-grid coverage. Retain direct binary/strict Monge as numerical engineering baselines; research promotion requires progress on general supports and a joint certificate.
