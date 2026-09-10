# Root-gap decomposition review, 2026-09-10

**Proceed as a bounded numerical diagnostic.** This reviews the proposed algebra and gate, not an executed implementation or outward certificate.

For each occupied pair node let M=c+L_child, q=OT(M), e=q-L_node, and r=<pi,M>-q. Include the dummy root with occupancy one, zero stage cost, M=L_0, and its actual improved-policy coupling. Feasible pi gives r>=0. A subsolution L_node<=OT(c+L_child) gives e>=0. Forward masses from exactly this policy yield

    U_pi-L_root = sum_node mu_pi(node)*(e_node+r_node).

Recombining-parent masses add; terminal lower values are zero. No optimal-policy occupancy is involved.

The actual `lower_sweep` preserves the required subsolution in exact arithmetic. Free bounds and forced values lie below their local OT. Maxima preserve this property. With fixed old-policy upper tables, the preceding sweep's floors are already below those uppers, so the final minimum preserves sweep-to-sweep monotonicity. Consequently each old floor remains a subsolution after child values increase. Taking the minimum with an upper only decreases a candidate. Zero is valid here because costs and continuations are nonnegative. Arbitrary external floors would require a separate check.

Numerical checks must retain signed e/r, report every negative and tolerance, and reject material violations. Audit local primal-dual widths, marginal residuals, and dual feasibility. A returned primal objective only approximates q. Telescoping alone cannot validate these solves: q cancels identically in e+r. Forced nodes should contribute essentially zero policy regret and only guard-scale subsolution slack.

Report root separately, layer sums, forced/nonforced sums, and 50%/90% counts for total residual and its two components. Include the denominator of occupied eligible nodes and local matrix sizes.

A small actionable concentration metric is the fraction of nonforced pair residual captured by the largest 16 contributions per layer, matching the existing selection budget. Freeze 90% capture as a heuristic gate for considering one targeted probe; record component capture to identify its target. Root-dominated residual requires a root-specific probe. Failure closes only this concentration heuristic on these cases. Neither component equals true lower/upper error, and captured residual is not predicted repair savings: subsequent policies and occupancies change.

## Implementation review and follow-on design

Read-only inspection of `probes/root_gap_decomposition.py` and its frozen manifest/results found no blocking attribution or policy-occupation bookkeeping defect. All twelve manifest source/artifact pins match. No experiment was rerun or frozen artifact altered. The actual frozen gate is **global top16 nonforced contributions >=80% of total gap**; the earlier 90%-per-layer suggestion above is not that experiment's gate and must not replace it retrospectively.

Recorded coverage is 37.23% coarse and 89.40% fine; their 90% counts are 114/312 and 17/118 occupied nonforced nodes. Dummy-root contributions are about 2e-14; the substantial t=0 contribution is a real nonforced pair node. Forced totals are below 1.2e-13 and telescoping errors below 4e-16. Signed negative regret entries remain recorded at floating-point scale. However, `_transport_value` checks primal residuals without auditing a dual gap. Therefore e/r remain provisional numerical attributions. The total and concentration depend on their sum, which cancels q algebraically, and support the scoped frozen gate independently of that split.

The proposed controlled scorer comparison addresses a real ranking uncertainty cheaply. For the same fixed feasible policy,

    U_node-L_node = [pi(c+L_child)-L_node] + pi(U_child-L_child).

Thus local scoring removes inherited continuation width. It still contains policy regret that lower-only backups cannot necessarily remove. Both arms must share the improved B16 policy/occupation, forced rule, B4/B16 schedule, floors and tie rules; this is a new control, not archived reproduction. Cache occupied-plan expectations once per layer because M and pi remain fixed during its selected backups. Charge plan-edge scans, score passes, selected solves and actual LP work.

Suggested pre-execution quality gate: at B16, the local scorer removes at least 5% of the new control's root gap on fine, with no added selected-solve budget or diagnostic OT. Report coarse descriptively and any regression. This threshold is heuristic; passing permits considering further work, not a speed or novelty claim. Negligible gain closes this scorer direction. Total timing and operation counts remain necessary context.

## Final residual-priority implementation check

Read-only review of `residual_priority_screen.py` and frozen artifacts supports rejecting this scorer without escalation. All 15 source/artifact pins and the result-to-manifest hash match. No rerun or frozen edit occurred.

Both arms share reconstructed improved-policy tables and occupation, forced/free bounds, B4/B16 floors, shared-dual updates, upper clamps and tie handling. Only the scoring bound changes. Local plan expectations are cached once per layer per sweep; their 2,866 occupied-plan evaluations and 5,080 edge scans are recorded. Signed occupied residuals are checked before clipping. Neither diagnostic OT nor the numerical reference enters ranking; the reference is only a post-sweep lower-endpoint check. These remain numerical original-target bounds, not outward certificates.

Both arms use 82 selections and 77 LP calls. Independent unmodified `lower_sweep` reproduces the control endpoint exactly. B16 lower decreases from 2.9235888017 to 2.9224597810, widening relative width from 24.16199% to 24.20996%; root-gap reduction is -0.15983%, failing the frozen +5% gate. Retain the improved-policy control only as a numerical baseline. Recorded times and narrow operation counters support no speed claim. Coarse was excluded by the frozen fine-only design.
