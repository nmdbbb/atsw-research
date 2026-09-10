# Bounded upper-policy improvement screen — 2026-09-10

Decision: few local policy replacements can repair the fixed-upper obstruction on the selected coarse case, but do not repair it on the selected fine second-order case. Do not promote a lower-only cache solver or a broad-domain performance claim from this screen. There is a useful upper-improvement signal; there is no evidence yet that the combined method reaches the root certification target economically across the operating domain.

## Frozen exploratory scope

The two cases were selected posthoc using known historical upper errors. This is development evidence, not preregistered confirmation. Both use the original smoke generation: T=5, 128 paths per side, seed1000, shift0. There are two independent budgets, B=4 and B=16 local pairs per layer, starting from the same initial SVD policy. A single backward pass and one extra root OT are allowed per budget. No hypothesis was registered and no grid was enlarged.

- Script: `probes/upper_policy_improvement_screen.py`.
- Manifest, frozen before execution: `runs/cycle_2/upper_policy_screen/manifest.json`.
- Results: `runs/cycle_2/upper_policy_screen/results.json`.
- Manifest SHA256: `6c628f4bf709f785cf9ff0984a62963bacb37795fb60119ea6682190dab35c96`.

The complete screen took19.95s inside its60s cooperative budget. The timer starts after import and provenance verification; it is not cold-start or end-to-end benchmark time. It includes path/model construction, initial policy construction, occupation, both independent improvements, score scans and full policy reevaluation.

## Method and mathematical checks

The initial policy is constructed using the unchanged `_orders` / `_ordered_policy` kernel, with both feasible NW orientations compared at each local problem. Plans are stored as nonzero edges to avoid replicating dense next-state matrices for every parent pair. Initial occupation is computed from precisely those stored plans.

At layer t, the cost matrix is the original stage cost plus the current improved child-policy upper table. Every retained old plan is reevaluated on this same matrix. Ranking uses initial occupation multiplied by the difference between its old-plan value and `free_lower` on this matrix. This lower value is a bound on the local OT with fixed upper continuation, used only to rank candidates; it is not a lower certificate for the true recursive continuation.

The selected pairs use the existing local OT kernel. A new plan is accepted only if its original-matrix objective is smaller than that of the retained old plan. The root is also optimized against the final improved table, retaining the initial root plan if cheaper. In exact arithmetic, feasible replacement and backward induction give pointwise nonincrease in policy value and therefore a feasible upper at the original root. Initial occupation influences selection only; it is never substituted for the final policy objective.

The executed numerical gates verify local marginals and nonnegativity to1e-8, pointwise upper nonincrease, complete backward replay, and forward occupation replay of stage costs1..T with no time-zero cost. Both completed cases passed. Largest recorded marginal/negativity residual was4.03e-16; largest forward/backward root discrepancy was4.45e-16. These are float64 checks, not outward-rounded certificates. `pack` retains nonzero values, including any negative entries tolerated by the numerical gate; no silent clipping or exact-feasibility claim is made.

## Observed results

The excess columns are `(policy_upper - archived_DP_reference) / archived_DP_reference`. They are conditional numerical obstructions to a relative root-width target, not achieved certificates.

| Case | Initial excess | B4 excess | B16 excess | B16 initial excess removed |
|---|---:|---:|---:|---:|
| ar1, k1, delta0.5, squared |1.08745%|0.38730%|0.07968%|92.67%|
| second_order_nonmonotone, k2, delta0.18, absolute |18.23584%|6.95811%|5.17839%|71.60%|

Both budgets move the coarse case's upper excess below the0.5% target. A valid sufficiently tight lower would still be needed; this result alone does not establish a certificate. The fine case remains above target by a factor of10.36 at B16 even if its lower were perfect.

| Case | Initial policy construction | B4 improvement | B16 improvement | Stored nonzero plan edges | Parent pairs scanned/replayed per pass |
|---|---:|---:|---:|---:|---:|
| coarse |0.100s|0.045s|0.125s|6,526|747|
| fine |18.713s|0.424s|0.509s|50,215|35,006|

B4 invokes17 local solves plus1 root solve; B16 invokes65 local solves plus1 root solve in each case. Some marginals are singleton, so these are not all LP calls: actual LP counts are14/59 for coarse B4/B16 and7/23 for fine B4/B16. Fine B16 uses0.143s in local solves,0.174s in policy scans,0.004s in score calculation, and0.187s in full backward/forward reevaluation. Thus few solve calls are not equivalent to little total work, and the fine initial policy construction dominates this implementation's measured time.

The recorded `dense_plan_entries_constructed` field is a proxy: it counts one dense matrix footprint per parent, whereas `_ordered_policy` constructs two orientations, and it omits root/internal arrays. It must not be represented as complete primitive work or allocation accounting. The scan and solve counters have the narrower meanings recorded in results; no dynamic-OT comparator was run, so these timings imply no speed advantage.

## Reference provenance and remaining decision

The archived numerical DP references are reused only for audit reporting. The original smoke result's manifest SHA matches its actual frozen manifest, and current generator, common model, original probe and policy candidate source SHA values match that original manifest. Inputs are generated directly by the hash-validated original `paths` function; its fixed grid, seed and params are preserved. Reproduced initial policy roots match the archived identical-input roots within1e-8. New model hashes are retained in results. The archived exact DP is an independent code path but still float64 HiGHS, not exact arithmetic; no fresh oracle time is hidden in candidate timing and no reference information enters selection.

The next justified decision is to identify whether the remaining fine-case upper error is addressable with a bounded, targeted policy change before building lower-cache machinery. This screen does not justify an escalating budget loop or large grid. A coarse-only certificate exploration would require an explicitly limited claim and would not satisfy the original broad-domain algorithmic objective. Root coordination should choose one of these bounded directions from the complete evidence, rather than treating any monotone improvement as permission to keep expanding experiments.
