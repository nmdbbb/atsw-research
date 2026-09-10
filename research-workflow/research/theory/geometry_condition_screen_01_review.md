# Independent review: geometry condition screen 01

Reviewer role: bounded mathematical and investment review; no PO decision or scope amendment. Date: 2026-09-10.

## Reviewed versions

SHA256 of exact bytes reviewed:

- Packet `geometry_condition_screen_01.md`: `0e9aacc447056e3a302dc658e0970c09cd408cb930fdc021aee95fbcaebe6bb2`
- Output `geometry_condition_screen_01_checks.json`: `d269d309e3460dd72beddd20efed51acc764f276e4dc419cf3862f402392ea38`
- Checker `../../tools/check_geometry_condition_screen_01.py`: `b6bed1f47a70fe63ae37e6c6d147442be4e055ba0cb18894bc3bc590730cbd46`

One replay of this finite checker reproduced the stored JSON exactly. No grid, new fixture, candidate, runtime benchmark or external novelty search was run. Review covers these versions only; later additions do not inherit this verdict.

## Mathematical claim admitted

The bound is valid for the stated finite, time-inhomogeneous k-window Markov laws, fixed common initial state, common deterministic full-state resets, and additive coordinate costs with certified common ranges.

At an agreeing paired history, choose a conditional coupling whose shared-child diagonal masses are the minima of the two transition probabilities. The residual marginals have disjoint support, so a feasible residual transport completes this coupling. After a block-prefix disagreement, arbitrary conditional couplings remain feasible. Aggregating surviving agreement mass by window state is legitimate because the kernels depend only on that state and time; equal window states reached through different agreeing histories have the same next-step kernels.

At a reset the entire state is fixed under every law. Consequently each next marginal conditional law is independent of the pre-reset history. Restarting the agreement policy there preserves the required conditional marginals at every paired history and therefore bicausality. Cost on agreeing prefixes vanishes; elsewhere it is bounded by C_t. The reset time itself has C_t=0. Summation establishes the global feasible upper. Replacing subprobability agreement mass by unit mass at the reset and applying a nonnegative transition operator establishes U_reset <= U_unbroken_prefix. One-time transport minima establish the lower bound and strict interval separation establishes the claimed ranking.

Full-state equality matters: for k=2, time 3 retains the random coordinate at time 2, whereas time 4 has state (0,0). For k=1, both times 3 and 4 qualify. Equality of only the current coordinate does not support this argument. No optimality of the greedy agreement policy is needed or established.

## Independent toy calculation

For Q/A, A reveals its early bit at time 1. At time 2, bicausality requires Q's bit to remain fair conditional on that revealed bit and the paired history. The bits are therefore independent. Time-1 cost is (1/2)(1/8)^p and time-2 mismatch cost is (1/2)(1/4)^p. Their sum is 3/16 for p=1 and 5/128 for p=2. Identical independent tail bits attain zero additional cost. The marginal near lower bounds are 1/16 and 1/128, so a strictly positive adapted penalty is present.

For Q/B, use identical early bits and identical tail bits. Each tail coordinate differs by 1/4, attaining the one-time translation lower bounds, hence D=2(1/4)^p: 1/2 and 1/8.

For Q/A the agreement masses at times 1 and 2 are 1/2 and 1/4. Thus the reset upper is (1/2)(1/8)^p+(3/4)(1/4)^p, giving 1/4 and 7/128. The unbroken policy retains only 1/4 agreement through the common tail. Across Q,A,B each tail range is 17/4, adding (3/2)(17/4)^p, hence 53/8 and 3475/128. The table and strict ranking certificate follow for both k values. Full-prefix backward transport and model reconstruction in the checker are appropriate distinct verification routes for this fixture.

## Costs, attribution and verdict

The sparse arithmetic counts are plausible with existing aligned kernels and bounded-cost state lookup; bit complexity, label construction, support storage and sorting remain separately chargeable. Eight matched-edge visits do not establish equal total runtime or a speedup. No measured fallback workload is available.

The packet appropriately attributes sequential coupling and agreement ingredients to prior work and identifies reset concatenation as an elementary derivation. I did not independently reopen the cited sources; this review admits the mathematical derivation, not bibliographic completeness or novelty. The stationary Markov reference must not be represented as directly proving this finite inhomogeneous formula.

Verdict: accept as a scoped reset-block baseline and finite diagnostic; do not advance this construction to a registered probe or central contribution on this evidence. Exact deterministic regeneration is a strong input condition, the chosen tail magnifies a known coarse-bound defect, and no advantage over elementary common-tail elimination or eligible adapted-OT competitors is demonstrated. No material mathematical objection remains within the stated scope. Population validity, other grids or horizons, approximate resets, useful prevalence, production arithmetic and scientific novelty remain unreviewed and unestablished.
