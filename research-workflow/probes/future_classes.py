"""Preregistered H_A01 probe, not a certified/SOTA solver.

See ledger/preregistered/H_A01_future_classes.json for predictions fixed
before running. Signatures sum normalized binary probabilities as Fractions;
there is no decimal rounding heuristic. Float conversion and LP execution
remain numerical. A control intentionally drops terminal output labels to
show why continuation equality alone cannot identify successor atoms.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from adapters.common_model import build_window_model, exact_dp, stage_cost, _transport_value
import workflow


@dataclass
class FutureClasses:
    future_labels: list[np.ndarray]
    atom_labels: list[np.ndarray]
    atom_representatives: list[np.ndarray]
    atom_futures: list[np.ndarray]
    class_rows: list[list[tuple]]
    initial: np.ndarray
    signature_seconds: float

    @property
    def future_counts(self):
        return [int(labels.max()) + 1 for labels in self.future_labels]

    @property
    def atom_counts(self):
        return [len(reps) for reps in self.atom_representatives]


def aggregate_exact(probabilities, labels):
    """Exact aggregation of the normalized declared binary floating row."""
    probabilities = np.asarray(probabilities)
    if not np.isfinite(probabilities).all() or (probabilities < 0).any():
        raise ValueError("Invalid probabilities")
    values = [(int(labels[i]), Fraction.from_float(float(probabilities[i])))
              for i in np.flatnonzero(probabilities)]
    total = sum((v for _, v in values), Fraction())
    if total <= 0:
        raise ValueError("Empty probability row")
    aggregate = {}
    for label, value in values:
        aggregate[label] = aggregate.get(label, Fraction()) + value / total
    return tuple(sorted(aggregate.items()))


def as_float_row(signature, size):
    row = np.zeros(size)
    for label, probability in signature:
        row[label] = float(probability)
    return row


def construct_classes(model, *, unsafe_terminal_merge=False):
    """F shares V; A=(output,F) preserves c+V at incoming transitions.

    unsafe_terminal_merge is a deliberately wrong negative control, used only
    on its analytic fixture. Production-style calls leave it False.
    """
    started = time.perf_counter()
    horizon = model.horizon
    f_labels, a_labels = [None] * (horizon + 1), [None] * (horizon + 1)
    a_reps, a_futures, class_rows = ([None] * (horizon + 1) for _ in range(3))
    for t in range(horizon, -1, -1):
        if t == horizon:
            f_labels[t] = np.zeros(len(model.states[t]), dtype=np.int64)
            class_rows[t] = [()]
        else:
            unique, rows, labels = {}, [], []
            for row in model.kernels[t]:
                signature = aggregate_exact(row, a_labels[t + 1])
                if signature not in unique:
                    unique[signature] = len(unique)
                    rows.append(signature)
                labels.append(unique[signature])
            f_labels[t] = np.array(labels, dtype=np.int64)
            class_rows[t] = rows
        unique, reps, futures, labels = {}, [], [], []
        for i, future in enumerate(f_labels[t]):
            future = int(future)
            output = float(model.representatives[t][i])
            if t == 0 or (unsafe_terminal_merge and t == horizon):
                key = (future,)
            else:
                key = (output.hex(), future)
            if key not in unique:
                unique[key] = len(unique)
                reps.append(output)
                futures.append(future)
            labels.append(unique[key])
        a_labels[t] = np.array(labels, dtype=np.int64)
        a_reps[t], a_futures[t] = np.array(reps), np.array(futures, dtype=np.int64)
    initial = as_float_row(aggregate_exact(model.initial, f_labels[0]), len(class_rows[0]))
    return FutureClasses(f_labels, a_labels, a_reps, a_futures, class_rows,
                         initial, time.perf_counter() - started)


def quotient_value(left, right, cost):
    horizon = len(left.future_labels) - 1
    if horizon != len(right.future_labels) - 1:
        raise ValueError("Different horizons")
    value = np.zeros((left.future_counts[-1], right.future_counts[-1]))
    calls = 0
    for t in range(horizon - 1, -1, -1):
        matrix = stage_cost(left.atom_representatives[t + 1], right.atom_representatives[t + 1], cost)
        matrix = matrix + value[np.ix_(left.atom_futures[t + 1], right.atom_futures[t + 1])]
        rows_left = [as_float_row(s, matrix.shape[0]) for s in left.class_rows[t]]
        rows_right = [as_float_row(s, matrix.shape[1]) for s in right.class_rows[t]]
        value = np.empty((len(rows_left), len(rows_right)))
        for i, a in enumerate(rows_left):
            for j, b in enumerate(rows_right):
                value[i, j] = _transport_value(a, b, matrix)
                calls += 1
    return _transport_value(left.initial, right.initial, value), calls


def fixture(epsilon):
    left, right = [], []
    for z in (-3, 3):
        n_positive = 8 + (int(16 * epsilon) if z == 3 else 0)
        left += [[z, 0, -1, 0]] * (16 - n_positive)
        left += [[z, 0, 1, 0]] * n_positive
    for w in (-4, 4):
        for c in (-2, 2):
            right += [[w, 0, c, 0]] * 8
    return (build_window_model(left, k=2, delta=1, shift=0.5),
            build_window_model(right, k=2, delta=1, shift=0.5))


def analytic_checks():
    rows = []
    for epsilon in (0, 1 / 16, 1 / 8):
        left, right = fixture(epsilon)
        lc, rc = construct_classes(left), construct_classes(right)
        for cost, slope in (("squared", 4), ("absolute", 1)):
            expected = 1 + slope * epsilon
            t0 = time.perf_counter()
            reference = exact_dp(left, right, cost)
            reference_seconds = time.perf_counter() - t0
            t0 = time.perf_counter()
            value, calls = quotient_value(lc, rc, cost)
            value_seconds = time.perf_counter() - t0
            assert abs(reference - expected) <= 1e-8
            assert abs(value - expected) <= 1e-8
            if epsilon == 0:
                assert calls == 3 and lc.future_counts == [1, 1, 1, 1]
            else:
                assert lc.future_counts[0] == 2 and lc.future_counts[1] == 2
            rows.append(dict(epsilon=epsilon, cost=cost, expected=expected, reference=reference,
                             quotient=value, fine_bellman_pairs=12, quotient_bellman_pairs=calls,
                             left_future_classes=lc.future_counts, left_atoms=lc.atom_counts,
                             signature_seconds=lc.signature_seconds + rc.signature_seconds,
                             reference_seconds=reference_seconds, quotient_value_seconds=value_seconds))
    x = build_window_model([[0, 0], [0, 2]], k=2, delta=1, shift=0.5)
    y = build_window_model([[0, 0]], k=2, delta=1, shift=0.5)
    good, _ = quotient_value(construct_classes(x), construct_classes(y), "squared")
    bad, _ = quotient_value(construct_classes(x, unsafe_terminal_merge=True),
                            construct_classes(y, unsafe_terminal_merge=True), "squared")
    assert abs(good - 2) <= 1e-8 and abs(bad - 0) <= 1e-8
    second_order = []
    x = [[0, -1, 0, -1], [0, 1, 0, 1]]
    y = [[0, -1, 0, 1], [0, 1, 0, -1]]
    for k, expected in ((1, 0), (2, 4)):
        a = build_window_model(x, k=k, delta=1, shift=0.5)
        b = build_window_model(y, k=k, delta=1, shift=0.5)
        value, _ = quotient_value(construct_classes(a), construct_classes(b), "squared")
        assert abs(value - expected) <= 1e-8
        second_order.append(dict(k=k, expected=expected, value=value))
    return dict(fixtures=rows, terminal_negative_control=dict(correct=good, intentionally_wrong=bad),
                second_order=second_order)


def generate_paths(process, side, seed, count=256, horizon=50):
    rng = np.random.default_rng(np.random.SeedSequence([seed, side]))
    paths = np.zeros((count, horizon + 1))
    for t in range(1, horizon + 1):
        if process == "ar1":
            drift = (0.7 if side == 0 else 0.55) * paths[:, t - 1]
        elif process == "nonmonotone_second_order":
            older = paths[:, t - 2] if t >= 2 else np.zeros(count)
            drift = (0.25 if side == 0 else 0.15) * paths[:, t - 1]
            drift += (0.7 if side == 0 else 0.6) * np.sin(2 * older)
        else:
            raise ValueError("Unknown process")
        paths[:, t] = drift + (1 if side == 0 else 1.15) * rng.standard_normal(count)
    return paths


def development_counts():
    rows = []
    for process in ("ar1", "nonmonotone_second_order"):
        for seed in (20260909, 20260910):
            xa, xb = [generate_paths(process, side, seed) for side in (0, 1)]
            for k in (1, 2):
                for delta in (0.5, 0.3, 0.18):
                    t0 = time.perf_counter()
                    left, right = [build_window_model(x, k=k, delta=delta, shift=0.37 * delta) for x in (xa, xb)]
                    build_seconds = time.perf_counter() - t0
                    lc, rc = construct_classes(left), construct_classes(right)
                    fine_by_t = [len(a) * len(b) for a, b in zip(left.states[:-1], right.states[:-1])]
                    quotient_by_t = [a * b for a, b in zip(lc.future_counts[:-1], rc.future_counts[:-1])]
                    atom_by_t = [a * b for a, b in zip(lc.atom_counts[:-1], rc.atom_counts[:-1])]
                    fine, quotient = sum(fine_by_t), sum(quotient_by_t)
                    reduction = 1 - quotient / fine
                    row = dict(process=process, seed=seed, k=k, delta=delta, T=50, paths=256,
                               fine_pairs=fine, quotient_pairs=quotient, atom_only_pairs=sum(atom_by_t),
                               pair_reduction=reduction, fine_pairs_by_t=fine_by_t,
                               quotient_pairs_by_t=quotient_by_t, build_seconds=build_seconds,
                               signature_seconds=lc.signature_seconds + rc.signature_seconds,
                               left_model_hash=left.model_hash, right_model_hash=right.model_hash,
                               root_value_computed=False, certificate_computed=False,
                               cost_applicability=["squared", "absolute"])
                    rows.append(row)
                    print(json.dumps({key: row[key] for key in ("process", "seed", "k", "delta", "pair_reduction", "signature_seconds")}), flush=True)
    medians = []
    for process in ("ar1", "nonmonotone_second_order"):
        for delta in (0.5, 0.3, 0.18):
            reduction = statistics.median(r["pair_reduction"] for r in rows if r["k"] == 2 and r["process"] == process and r["delta"] == delta)
            medians.append(dict(process=process, delta=delta, median_reduction=reduction, passed=reduction >= 0.25))
    return rows, medians


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "runs/cycle_1/H_A01_future_classes.json")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; preserve prior runs and choose a new --output")
    workflow.verify_contract(ROOT)
    prereg = ROOT / "ledger/preregistered/H_A01_future_classes.json"
    if not prereg.exists():
        parser.error("Register hypothesis before running")
    started = time.perf_counter()
    analytic = analytic_checks()
    rows, medians = development_counts()
    passed = all(r["passed"] for r in medians)
    result = dict(hypothesis="H_A01_future_classes", status="development_mechanism_supported" if passed else "development_performance_prediction_falsified",
                  analytic_checks=analytic, development_counts=rows, preregistered_k2_medians=medians,
                  source_sha256=workflow.digest(Path(__file__)), preregistration_sha256=workflow.digest(prereg),
                  objective_sha256=workflow.digest(ROOT / "objective.json"), total_probe_seconds=time.perf_counter() - started,
                  sota_comparison=False, exact_arithmetic_certificate=False,
                  interpretation="Structural small-sample work-count probe only; surviving this is not time-to-certificate or SOTA evidence.")
    workflow.write_new(args.output, result)
    workflow.append_event(ROOT, "experiment_result", {"hypothesis": result["hypothesis"], "status": result["status"],
                          "result_path": str(args.output.relative_to(ROOT)), "result_sha256": workflow.digest(args.output)})
    print(json.dumps({"status": result["status"], "medians": medians, "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
