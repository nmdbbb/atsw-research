# Root-gap localization and priority ablation

Date: 2026-09-10. Decision: stop the proposed local-residual priority variant.
Retain the control using the improved policy's own occupation as a numerical
baseline. No new hypothesis, grid, budget escalation or scientific completion.

## Why this step was justified

The previous forced-node baseline left numerical root widths 13.73% and 31.42%
on the two selected T5/128-path/seed1000/shift0 cases. Before further engineering,
we asked whether that residual was concentrated enough to justify one targeted
selection ablation. All historical artifacts remain immutable.

For a fixed feasible policy pi, its actual occupation mu, and a Bellman
subsolution L, the exact-arithmetic identity is

`U_pi(root)-L_root = sum_n mu_n * (<pi_n,c_n+L_child>-L_n)`.

The sum includes the initial-law root, with zero stage cost. A local numerical
OT value q splits each summand into `q-L_n` and `<pi_n,c+L_child>-q`.
The diagnostic used float64 OT values with primal checks, without independent
dual-gap validation. Therefore the component split is provisional. The total
residual cancels q and does not depend on local OT accuracy; it still requires
coherent finite-model tables and policy/occupation bookkeeping. It is not a
rigorous outward-rounded certificate.

## Frozen localization screen

The original forced B4/B16 lower and the improved B16 policy were reconstructed.
Model hashes and archived endpoints matched within 1e-8; the forward policy
objective matched its backward evaluation. The script retained signed residuals
and checked nonnegativity within 1e-8, without silently repairing failed gates.

| Quantity | Coarse AR1 k1 delta0.5 squared | Fine nonlinear k2 delta0.18 absolute |
|---|---:|---:|
| Numerical root width | 13.7330% | 31.4164% |
| Gap fraction in 16 largest nonforced pairs | 37.2279% | 89.3983% |
| Nonforced pairs for 90% of gap | 114 | 17 |
| Diagnostic local LP calls | 312 | 118 |
| Forced-node total weighted residual | 5.88e-14 | 1.15e-13 |

Both dummy-root contributions are near roundoff. The actual t=0 transition pair
has mass one and remains a nonforced pair; it contributes about 40.23% of the
fine-case gap. Thus concentration is partly early-horizon, not many independent
small repairs. The frozen top16>=80% gate passes only fine. The whole diagnostic
took 2.723 seconds; local OT calls are charged diagnostic work, not free candidate
information. Reference values do not enter the subsequent selection rule.

## One bounded selection ablation

At a fixed sweep layer, the old score `mu*(U-L)` includes downstream uncertainty.
The proposed score is `mu*(<pi,c+L_child>-L)`, computable from the stored sparse
policy without a local OT call. Policy expectations are cached once per layer;
shared-dual updates then only change L. This is an elementary Bellman-residual
priority baseline, without a novelty claim or guaranteed repair benefit.

Only the fine case was run. Both arms used the same improved B16 upper policy,
its actual occupation, automatic forced-node lower values, and the B4-then-B16
shared-dual schedule. This is a NEW control: earlier forced results used the
initial policy's occupation. The comparison changes only the ranking score.
The primary gate was `(L_new-L_control)/(U-L_control)>=0.05`.

| Metric | Current-gap control | Local-residual priority |
|---|---:|---:|
| B16 lower | 2.923588801715 | 2.922459780996 |
| Fixed upper | 3.629986121951 | 3.629986121951 |
| Relative root width | 24.161993% | 24.209960% |
| Selected local calls | 82 | 82 |
| LP calls | 77 | 77 |
| Sweep seconds | 0.432692 | 0.445653 |
| Additional policy-edge reads for score | 0 | 5,080 |

The proposed score removes -0.1598% of the control's value gap: it slightly
worsens the result and fails the 5% gate. An independent invocation of the
unmodified `lower_sweep` reproduced the control lower exactly. Setup and this
validation were charged separately; total ablation time was 2.047 seconds.
One timing per arm is not a speed comparison. Generic score-array scans, support
checks and full construction remain part of the timing even when narrow counters
do not enumerate every primitive operation.

## Result and next gate

The improved-policy control reduces the previous fine width from 31.42% to
24.16%, but cannot achieve 0.5% with its fixed upper: that upper remains 5.178%
above the numerical reference even with a perfect lower. No further lower-only
priority/cache optimization on this fixed upper is justified.

Close this local-residual ranking variant on the tested scope. Do not infer that
all occupancy strategies fail, that no structural algorithm exists, or that the
original research objective is complete. The next research cycle must address
the joint upper/lower obstruction with a distinct, testable mechanism. Merely
increasing local budgets or switching among related priority scores does not
meet the gate. The surviving numeric baselines are available for that comparison.

Artifacts: `runs/cycle_2/root_gap_decomposition/{manifest,results}.json`,
`runs/cycle_2/residual_priority_screen/{manifest,results}.json`, and their scripts.
The independent reviewer checked algebra, attribution implementation, numerical
limits and the priority proposal; see `root_gap_decomposition_review_20260910.md`.
Routing: one Astra/high reviewer with a fresh short packet; root implementation,
execution and integration. No extra agent, literature sweep or service launched.
