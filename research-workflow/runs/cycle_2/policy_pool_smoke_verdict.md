# Common-model policy-pool smoke verdict

This is a development correctness and scope smoke, not a certificate or SOTA
benchmark. The manifest was frozen before execution.

All 16 cases completed across both process families, both costs, k in {1,2}
and delta in {0.5,0.18}. Every float64 lower/upper interval contained the
independent common-model exact-DP value. The largest root dual feasibility
violation was -7.11e-15, hence all recorded duals passed the represented-matrix
feasibility gate.

The port fixes the scope defects of the archive: arbitrary initial laws,
correct k-window models, both registered costs, and all grid shifts can pass
through one interface with an outer from-paths timer. It remains a numerical
development implementation because arithmetic is not outward rounded.

The mechanism is not competitive at the tested budgets. At B=16 witnesses
per layer, relative root width ranged from 9.59% to 551.85%, with median 63.29%;
zero of 16 cases reached 0.5%. B=4 was wider. Therefore the old shared local
dual pool is retained as a correctness baseline and ablation, not promoted as
the macro algorithm sought by the project.

Raw evidence: `runs/cycle_2/policy_pool_common_smoke.json`.
Implementation: `adapters/policy_pool_candidate.py`.

