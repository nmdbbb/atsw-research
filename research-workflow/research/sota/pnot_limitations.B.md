# What the tiny PNOT audit establishes, and what it does not (Lane B)

Adversarial/qualitative review of the pinned original NestedOT ("PNOT") implementation as a
comparator, written 2026-09-09 by Lane B. Sources read: `runs/cycle_1/pnot_build.json`,
`runs/cycle_1/pnot_cases.json`, `runs/cycle_1/pnot_result.json`,
`research/sota/pnot_result_review.md`, the PNOT section of `research/sota/notes.md`, and the
algorithm itself in `third_party/nestedot/src/{solver.cpp,utils.cpp,wrapper.cpp,include/header_dist.h}`
plus `third_party/nestedot/pnot/{solver.py,py_solver.py}`. Nothing was executed and nothing was
rebuilt by this review; all numbers below are quoted from the recorded artifacts or read off the
source. **No SOTA reproduction is claimed here, and none follows from these artifacts.**

Verdict in one sentence: the audit establishes **backend identity plus exact k=1 numerical
agreement on five hand-made deterministic-root micro-instances under the `V=AW_p^p` convention**,
and it establishes nothing about k=2, random initial laws, certificates, scale, or speed.

## 1. Does it cover k=2? No — the implementation has no k parameter at all

The conditioning rule is selected by a **boolean**, and only two branches exist:

- `third_party/nestedot/src/utils.cpp:95` — `qpath2mu_x(Eigen::MatrixXi& qpath, const bool& markovian)`.
- `utils.cpp:103-104` — `if (markovian) { pre_path.push_back(qpath(i, t)); }` — the conditioning key
  is the **single current state**, i.e. exactly k=1.
- `utils.cpp:105-109` — `else { for (int k = 0; k <= t; ++k) pre_path.push_back(qpath(i, k)); }` — the
  key is the **entire prefix** `x_0..x_t`, i.e. full history.

There is no third branch and no integer memory argument anywhere up the stack:
`solver.cpp:111-117` (`double Nested(..., const bool& markovian, int num_threads, const int power, const bool verbose)`),
`wrapper.cpp:11,14` (same signature exposed to pybind11), `pnot/solver.py:4-6`
(`nested_ot(X, Y, grid_size, markovian, parallel=True, num_threads=8, power=2, verbose=False)`), and
the Python fallback `pnot/py_solver.py:15` (`def __init__(self, qX, markovian=True)`).

k=2 also cannot be smuggled in by pre-augmenting the state under `markovian=true`, because the
Markov continuation lookup is keyed by a **scalar** state:

- `include/header_dist.h:20` — `std::map<int,int> v2idx; // Only use this for markovian`.
- `utils.cpp:155` — `kernel_x[t].v2idx[condition.back()] = idx;` — the index map is built from
  `condition.back()` only, so two distinct conditions ending in the same value collide.
- `utils.cpp:160-168` then builds `next_idx` from that scalar map, and `solver.cpp:219-222`
  (`AddDppValueMarkovian(cost, V[t+1], x_next_idx, y_next_idx)`) is the only Markov continuation path.
  A k=2 state is a pair; it is not addressable by this map. The full-history branch instead uses
  prefix-tree offsets (`solver.cpp:223-227`, `int& i0 = kernel_x[t].nv_cums[ix]`), which enumerate the
  whole prefix tree rather than a 2-window.

The recorded numbers give a clean **two-sided separation**, i.e. neither native mode is k=2:

| Fixture (`pnot_cases.json`) | declared k=2 reference (abs/sq) | `native_markov_value` | `native_full_history_value` |
|---|---|---|---|
| `second_order_matters` | 2 / 4 | 0.0 / 0.0 | 2.0 / 4.0 |
| `full_history_is_not_k2` | 0 / 0 | 0.0 / 0.0 | 2.0 / 4.0 |

So Markov mode under-reports true second-order structure (`second_order_matters`), and full-history
mode over-reports where k=2 sees nothing (`full_history_is_not_k2`). **No k=2 value of stock PNOT was
computed, because stock PNOT cannot express the k=2 model.** `objective.json` requires
`required_k: [1, 2]` and lists `"k=1 only"` under `restrictions_not_allowed`.

## 2. Does it cover a random (non-deterministic) initial law? No — it reads one root cell

- `solver.cpp:238` — `double nested_ot_value = V[0][0][0];`. The t=0 value table is allocated over all
  root conditions (`solver.cpp:183-186`, `V[t] = ...(kernel_x[t].nc, ...(kernel_y[t].nc, 0.0f))`), but
  only entry `[0][0]` is returned. There is **no transport problem solved at time 0** over the two
  initial marginals, and no weighting by the initial law.
- Index `0` is the lexicographically smallest root state, because conditions are enumerated in
  `std::map` key order at `utils.cpp:128` (`for (auto pair : mu_x_t)`) over
  `std::map<std::vector<int>, std::map<int,int>>` (`utils.cpp:95-98`).
- The design assumption is visible in the author's own generator: `utils.cpp:31-33`,
  `X_extended.row(0).setZero();` — every simulated path starts at 0, so the root is a Dirac by
  construction.

Recorded consequence, fixture `random_initial_law_is_rejected` (two root states, mass 1/2 each):
`native_markov_value` is `0.0` for both cost families, against a coupled-initial-law target of
`1` (absolute) and `2` (squared); the result rows carry
`k1_comparator_target_eligible: false`, `ineligible_reason: "stock selects one initial state"`,
`absolute_k1_difference: 1.0` and `2.0`. Note the returned scalar is a *fixed lexicographic pick*, not
a minimum over root pairs, so in general it is neither a valid upper nor a valid lower bound on the
coupled quantity — here it happens to fall below it.

Therefore the eight agreeing k=1 comparisons are agreements **conditional on a deterministic root**.
The audit's own fixture set is what detects this, which is a point in the audit's favour; it is not
evidence that PNOT handles the general case.

## 3. Does it produce any certificate? No — one float, duals discarded, status only printed

- Return type is a bare `double` at every layer: `solver.cpp:111`, `wrapper.cpp:11,14`,
  `pnot/solver.py:13-15`. No interval, no bound pair, no gap field.
- `solver.cpp:62-99` (`SolveOT`) allocates dual potentials (`solver.cpp:81-82`,
  `double* alpha = new double[n1]; double* beta = new double[n2];`) and the coupling
  (`solver.cpp:80`), then **frees all of them** (`solver.cpp:91-94`, `delete[] C; delete[] G;
  delete[] alpha; delete[] beta;`) and returns only the scalar `c` (`solver.cpp:97`). No dual
  feasibility check, no primal marginal residual, no outward rounding is possible from the API.
- `solver.cpp:83-89` — `uint64_t maxIter = 100000; int result = EMD_wrap(...); if (result != 1) { std::cout << "OT is not solved optimally" << std::endl; }`.
  Execution **continues** and the possibly non-optimal cost is returned; the status never reaches the
  caller. Detection therefore depends on scraping stdout (which the probe does, per
  `pnot_result_review.md`), not on the API.
- `solver.cpp:67-72` — the `n1 == 1 || n2 == 1` branch bypasses the LP and sums
  `wx[i] * cost[i][j] * wy[j]`; correct for a degenerate marginal, but again unverified at runtime.
- Continuation values are accumulated in double precision (`solver.cpp:37-59`,
  `AddDppValue`/`AddDppValueMarkovian`) with no error accounting.

The artifact agrees: `pnot_result.json` records `certificate_frontier_eligible: false`,
`qualified_full_domain_comparator: false`, `scope: "DEVELOPMENT_NUMERICAL_AUDIT_ONLY"`,
`units: "V=AW_p^p"`. So what exists is **an exact-in-exact-arithmetic DP value on a tiny finite
model, returned as an unqualified float** — the `"exact"` output slot of
`objective.json:target.outputs` only, never `"certified_relative_gap_at_root"`.

## 4. Established (and only this)

1. **Backend identity and provenance.** `backend: "original_pnot_cpp_Nested_via_CLI"`,
   `python_fallback: false`, `native_threads: 1`, pinned `revision: 9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a`,
   with `source_sha256` (19 files), `probe_sha256`, `dataset_sha256`, `executable_sha256` recorded;
   `pnot_build.json` records a zero-return-code g++ 13.2.0 `-O2 -std=c++17 -fopenmp -include chrono`
   build with empty stdout/stderr and the only disclosed change being the forced `<chrono>` include
   (`"compatibility_change": "forced include chrono; original source bytes unchanged"`). The
   independent review re-matched all of this against the author archive and re-ran the 14 native calls.
2. **k=1 numerical agreement on the four deterministic-root fixtures × 2 cost families = 8
   comparisons**, all rows `native_quantization_and_k1_kernels_equal: true`, largest
   `absolute_k1_difference` = `1.1102230246251565e-16`.
3. **Objective convention pinned**: additive `V = AW_p^p`, no final p-th root, no time-zero charge
   (visible in `solver.cpp:202-232` looping `t = T-1 … 0` and `solver.cpp:238`).
4. **Two-sided k=2 separation** and **a working rejection mechanism** for the random-root case.

## 5. Not established

1. **k=2 in any form.** No adapter exists; the source has no k (§1).
2. **Random / non-Dirac initial laws.** Stock output is the wrong quantity there (§2).
3. **Any certificate, interval, dual residual or outward-rounded bound** (§3). The `epsilon: 0.005`
   relative root gap required by `objective.json` is not producible by stock PNOT.
4. **Anything at required scale or breadth.** Fixture horizons are `T ∈ {1, 2, 3, 4, 5}` with 2–4
   sample paths; `required_T` is 50. Fixture `delta ∈ {1.0, 0.5}`; `required_delta` is
   `[0.5, 0.3, 0.18]` — only `0.5` appears, in one fixture. Fixtures are hand-made, not `ar1` or
   `nonmonotone_second_order`. **Zero of the six core cells is covered.**
5. **Any speed or quality result.** Times are recorded as
   `native_process_seconds_diagnostic_only` (e.g. `0.08032819999789353` s on the first row, which
   includes first-call warm-up), single-threaded, one repeat, no
   `end_to_end_from_paths` / `solver_only_on_fixed_representation` / `cold_start` split, against the
   engineering default of 5 timing repeats and 5 confirmation seeds. No comparison to our candidate
   was made or may be quoted.
6. **General quantization equivalence.** Agreement holds for binary-exact grid values only. The
   quantizer is `utils.cpp:42`, `adaptedX(i,j) = std::floor(X(i,j)/grid_size + 0.5) * grid_size;` —
   round-half-**up**, not round-half-even, and there is **no grid-shift parameter** in the C++ at all,
   so any shift must be pushed into the coordinates by the caller (the fixtures do exactly this, with
   `shift ∈ {0.5, 0.125, -0.5}`). Tie behaviour and floating-point drift at general scales
   (`δ = 0.3`, `0.18`) are untested.
7. **Preregistration chronology.** `pnot_cases.json` asserts `registered_before_execution: true`, but
   per `pnot_result_review.md` this is self-attestation with no immutable pre-execution ledger.
   Treat the five cases as fixed development fixtures; do not call them preregistered.
8. **Population / statistical claims.** A finite-model exact value is not a population certificate
   (`objective.json:target.estimator_track`).
9. **Robustness of the backend assertion in future runs.** `pnot/solver.py:16` is a bare `except:`
   that silently falls back to the slow Python solver (`pnot/solver.py:17-23`). This audit bypassed the
   wrapper (direct `Nested(...)` via CLI harness) and recorded `python_fallback: false`; any later run
   through the Python API must re-assert this or its timings are meaningless.

## 6. What would make PNOT an *eligible competitor* under `objective.json:comparison`

All of the following are necessary, and none is satisfied today.

1. **Same task.** Output `V = AW_p^p` on the *same* finite, quantized k-window model, for
   `k ∈ {1, 2}`, `δ ∈ {0.5, 0.3, 0.18}`, `T = 50`, both `squared_distance` and `absolute_distance`,
   crossed over `ar1` and `nonmonotone_second_order`, every cell reported
   (`no_cross_cell_compensation: true`).
2. **Same information.** Observed paths only (`target.input_access`); no true kernels and no access to
   the reference value (`reference_value_not_available_to_candidate: true`). Kernel-oracle usage would
   move it to a separately labelled track.
3. **A k=2 adapter, reported separately.** Since no k exists in the source (`utils.cpp:103-109`), a
   k-window adapter is mandatory, and it must: (a) build the same k=2 conditional model as the common
   builder — key = last k states, empirical conditional probabilities as in `utils.cpp:136-145`;
   (b) keep the **original scalar successor-state stage cost** (`solver.cpp:25-35`, `SquareCost` on
   `cost_matrix[vx[i]][vy[j]]`) rather than a Euclidean distance between history vectors, per the
   guidance already in `notes.md`; (c) pass an independent kernel-key/probability equality audit at
   k=2, the analogue of the k=1 check recorded here; (d) be labelled **"PNOT + our k=2 adapter"**, a
   modified variant, never "stock PNOT" or "the published method"; and (e) have all of its
   construction time charged to PNOT under `comparison.time_includes` (representation construction,
   all grid shifts, repair/fallback, warm-up).
4. **Root handling.** Either the comparison is restricted to Dirac-root instances — which is a
   narrowing of the operating domain and cannot be used to qualify PNOT for the general task — or the
   adapter adds the missing time-0 transport over the two initial marginals on top of `V[0][·][·]`,
   again as a separately labelled and separately timed variant. Without one of these, PNOT's scalar is
   not the target quantity (§2).
5. **Track separation.** `exact_and_certified_results_separate: true`. Stock PNOT can enter only the
   **exact** speed track (time-to-exact-value on instances where exact DP is feasible). It cannot enter
   the certified-quality track at all until some wrapper emits a valid root interval `[L, U]` with
   `(U − L)/L ≤ 0.005`, with every certification step timed. Nothing in the source can supply that
   (§3), so this too would be adapter work.
6. **Timing hygiene.** Pinned threads and asserted compiled backend (`python_fallback: false`), 5
   timing repeats, 5 confirmation seeds, and the four separate reports
   (`end_to_end_from_paths`, `solver_only_on_fixed_representation`, `cold_start`,
   `amortized_if_applicable`), with quantization, grid shifts and kernel construction counted in the
   end-to-end number.
7. **Validity gating per solve.** Because a non-optimal LP status is only printed
   (`solver.cpp:87-89`) and never returned, every eligible run must capture stdout and fail on
   `"OT is not solved optimally"`, and must record external marginal/dual residual checks. Otherwise
   its "exact" value cannot be used as a reference at all.

## 7. Recommended lane-B position

Keep PNOT as the **priority exact k=1 comparator on Dirac-root instances**, with
`certificate_frontier_eligible: false` and `qualified_full_domain_comparator: false` left as they
stand. Do not report any PNOT number for k=2, for random roots, or in the certified-quality track
until an audited, separately labelled adapter exists. A missing adapter is a gap in the comparison,
not evidence in our favour.
