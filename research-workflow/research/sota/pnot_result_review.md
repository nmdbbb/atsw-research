# Independent PNOT result review

Verdict: **ACCEPT for the stated development-only numerical audit.** Qualification as a certified or full-domain comparator is rejected. Scientific preregistration chronology remains **UNRESOLVED**.

Reviewed 2026-09-09. Scope: `adapters/pnot_probe.py`, its generated native harness, `runs/cycle_1/pnot_cases.json`, `pnot_build.json`, `pnot_result.json`, `third_party/nestedot/AUDIT_PROVENANCE.json`, the pinned original C++ implementation and relevant common-model reference. Only this review file was written. No original source or run artifact was changed, and no full benchmark was run.

## Provenance and build

The pinned revision is `9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a`. Independently fetched the [pinned author archive](https://codeload.github.com/justinhou95/NestedOT/zip/9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a) into memory: SHA-256 `d226523bed07cc0483497c4fe61f4284f590970ce5a053bbdd5439b240a54b7f`, matching provenance. All 434 archive files exist locally and match their archive bytes, including bundled Eigen headers omitted from the run's selected source-hash manifest. No missing or differing files were found.

All 19 selected original-source hashes in the result match the present files. The probe, fixture, executable and generated-harness hashes also match; the harness text equals the adapter's embedded `HARNESS` constant. Key hashes:

- Probe: `45c9b343b1a2b90b469d72208bf5ea803e81dcaf46284207bf32c2d9917e008b`.
- Cases: `9c06e7a40f57269103a40247209c1635d42cdefa5d21c72bab72e5a5e5618f5d`.
- Harness: `0203d8bdb55bfbc9fa6a3bbbe63d3582163540f805f468269ea22da80c486a1f`.
- Executable: `f7df4f0e86b0e2cbf9bfab20b313365fc68e432589775bae964387f4adf8d2c4`.

The recorded successful build uses existing MSYS2 UCRT64 g++ 13.2.0, `-O2 -std=c++17 -fopenmp -include chrono`, the bundled Eigen/include directories, the harness, and original `solver.cpp`, `utils.cpp`, `emd_wrap.cpp`, and `printer.cpp`. Both build output streams are empty and return code is zero. The forced `<chrono>` include is disclosed and consistent with `solver.cpp` using `std::chrono` without its own include. Original source bytes were not patched. This review did not rebuild or independently reproduce the binary compilation; it verified source and artifact hashes, command contents, and executable behavior.

The harness calls original `Nested(..., markovian, 1, power, false)` directly. There is no call to the author's Python fallback, package initializer, or benchmark `main`; SciPy is only the separate numerical reference. Native exceptions/nonzero exits, nonfinite scalar results and the original nonoptimal-OT warning fail the probe. No installation fallback is present.

## Target and numerical conclusions

Original `utils.cpp` conditions on the current state for `markovian=True`, and on the entire prefix for `False`. Counts are normalized into empirical conditional probabilities. Original `solver.cpp` adds successor-state cost and continuation values through times 1..T, without charging time zero or taking a final p-th root. Thus the scalar is the additive finite-target value `V = AW_p^p` under this objective convention, with absolute cost for p=1 and squared cost for p=2.

The adapter supplies the shared integer cells times delta. The common model uses those values plus the same `shift + delta/2` on both sides, preserving both cost families by translation invariance. For these binary-exact grid choices, native quantization preserves all supplied coordinates. The probe explicitly compares native conditional keys, successor keys and probabilities against the common k=1 model. This establishes the recorded tiny-grid agreement, not unrestricted quantization equivalence for arbitrary floating-point scales.

| Fixture | Native Markov absolute / squared | Relevant reference or diagnostic |
|---|---:|---|
| preserve_first_cost | 2/3 / 4/3 | Analytic first-transition cost retained |
| shifted_branching | 0.8749999999999999 / 0.5625 | k=1 reference 0.875 / 0.5625 |
| second_order_matters | 0 / 0 | k=2 and native full history: 2 / 4 |
| full_history_is_not_k2 | 0 / 0 | k=2: 0 / 0; native full history: 2 / 4 |
| random_initial_law_is_rejected | 0 / 0 | Coupled initial-law target: 1 / 2; ineligible diagnostic |

All eight deterministic-root Markov comparisons agree within `1e-9`; the largest recorded difference is `1.1102230246251565e-16`. The random-initial-law fixture is correctly excluded from comparator eligibility. Original `Nested` returns `V[0][0][0]`, selecting the lexicographically first initial pair; it does not couple initial marginals. Deterministic roots remove that discrepancy for the four eligible fixtures.

The separation cases demonstrate why Markov mode cannot be scored as general k=2 and why full-history mode cannot replace k=2. Four full-history calls are diagnostics against the separate full-history reference. The ten reported case rows correspond to **14 actual native calls**: ten Markov calls plus four full-history calls. The CLI summary field `native_calls_recorded` counts rows, so its value ten must not be described as the total number of native solves.

The common `exact_dp` uses an independent unregularized SciPy/HiGHS LP implementation with primal residual checks, not exact arithmetic. Original PNOT deletes couplings and duals after each solve, and does not expose solver statuses through its scalar API. `EMD_wrap` can return a cost after hitting its iteration limit, but `SolveOT` prints a warning for every status other than optimal and this adapter rejects that warning. Absence of warnings and scalar agreement provide numerical evidence only, not outward-rounded certification. The recorded `certificate_frontier_eligible=false` and `qualified_full_domain_comparator=false` are warranted. No performance advantage, large-horizon correctness, k=2 adapter qualification, or population-law guarantee follows.

## Chronology and review execution

The five cases, expected values and tolerance are explicit in the inspected artifacts; no fixture selection or adaptive search occurs in the probe. Present filesystem creation/modification times put the cases and adapter before the harness/build/result. Their matching recorded hashes establish consistency of the present artifacts. However, there was no immutable pre-execution registration ledger, independently timestamped commitment or version-history proof. `registered_before_execution=true` and the adapter's ?preregistered? wording are self-attestation. Treat these as fixed development fixtures; scientific preregistration is unresolved and must not be claimed.

After verifying the executable hash, this review independently constructed stdin from the five JSON fixtures using scalar floor quantization and transposition, invoked only the existing harness from its recorded runtime directory, and parsed the returned `VALUE` records. All 14 tiny calls exited zero, emitted no nonoptimal-OT warning, returned finite values, and exactly reproduced their corresponding recorded native scalar. The full probe `main()` was not executed, avoiding changes to existing run artifacts. No new performance measurement was made. The rerun does not independently re-prove every kernel-comparison assertion; those checks were audited in source and their original PASS record was verified.

Rerun evidence follows; stdout digests refer to decoded stdout encoded as UTF-8:

```json
[
  {
    "case": "preserve_first_cost",
    "power": 1,
    "markovian": true,
    "value": 0.6666666666666666,
    "recorded_difference": 0.0,
    "stdout_sha256": "77ce4f84718cb01c46a15ab1c72d5cb1768007105fe361aa9ef2ed1f04dad2af"
  },
  {
    "case": "preserve_first_cost",
    "power": 2,
    "markovian": true,
    "value": 1.3333333333333333,
    "recorded_difference": 0.0,
    "stdout_sha256": "e18a5485dfcd88f12a1fb38e04dbc623104a512755426dace5fae3463617714b"
  },
  {
    "case": "shifted_branching",
    "power": 1,
    "markovian": true,
    "value": 0.8749999999999999,
    "recorded_difference": 0.0,
    "stdout_sha256": "e937c511e73af018d299b5c9cff72f31b2d02ed26c07015a14f42cb801db7650"
  },
  {
    "case": "shifted_branching",
    "power": 2,
    "markovian": true,
    "value": 0.5625,
    "recorded_difference": 0.0,
    "stdout_sha256": "2dd59d734e75feb068752e976d91482a097babae95a059fc4ca789197f218df5"
  },
  {
    "case": "second_order_matters",
    "power": 1,
    "markovian": true,
    "value": 0.0,
    "recorded_difference": 0.0,
    "stdout_sha256": "338f73a9b4c4dfe573110cdafd5b856e8f7ebc88937e7edb64c59874adcbedcb"
  },
  {
    "case": "second_order_matters",
    "power": 1,
    "markovian": false,
    "value": 2.0,
    "recorded_difference": 0.0,
    "stdout_sha256": "fa6e3c267e5e29d1fefcec69ee3435ca86a904de07b8d7ad6ba47afa12a55599"
  },
  {
    "case": "second_order_matters",
    "power": 2,
    "markovian": true,
    "value": 0.0,
    "recorded_difference": 0.0,
    "stdout_sha256": "338f73a9b4c4dfe573110cdafd5b856e8f7ebc88937e7edb64c59874adcbedcb"
  },
  {
    "case": "second_order_matters",
    "power": 2,
    "markovian": false,
    "value": 4.0,
    "recorded_difference": 0.0,
    "stdout_sha256": "7681ce0117caba4bb456e4b9f252fcdd5c6677030a55fed8365256b6959b59ad"
  },
  {
    "case": "full_history_is_not_k2",
    "power": 1,
    "markovian": true,
    "value": 0.0,
    "recorded_difference": 0.0,
    "stdout_sha256": "13390c25b35454de9965ec33850d309f1575c4c1984d8ad31e47ccab246f3b54"
  },
  {
    "case": "full_history_is_not_k2",
    "power": 1,
    "markovian": false,
    "value": 2.0,
    "recorded_difference": 0.0,
    "stdout_sha256": "d1cac6a4a779adb8c8a62b85d5500fe92c215974039cf006f59939e1cd5b8d82"
  },
  {
    "case": "full_history_is_not_k2",
    "power": 2,
    "markovian": true,
    "value": 0.0,
    "recorded_difference": 0.0,
    "stdout_sha256": "13390c25b35454de9965ec33850d309f1575c4c1984d8ad31e47ccab246f3b54"
  },
  {
    "case": "full_history_is_not_k2",
    "power": 2,
    "markovian": false,
    "value": 4.0,
    "recorded_difference": 0.0,
    "stdout_sha256": "b5302fc736fd8edbf7ced0f2861e29f5c942a63fccf9532d89c0953ec5b54667"
  },
  {
    "case": "random_initial_law_is_rejected",
    "power": 1,
    "markovian": true,
    "value": 0.0,
    "recorded_difference": 0.0,
    "stdout_sha256": "f1beec91ae92891e73aedaa1aa512286e89b69e70c6b1ba9281ec310f754684c"
  },
  {
    "case": "random_initial_law_is_rejected",
    "power": 2,
    "markovian": true,
    "value": 0.0,
    "recorded_difference": 0.0,
    "stdout_sha256": "f1beec91ae92891e73aedaa1aa512286e89b69e70c6b1ba9281ec310f754684c"
  }
]
```
