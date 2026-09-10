"""Checkpoint/preregistration and conservative numerical report screening.

This is NOT an LLM service, a mathematical certificate verifier or a SOTA oracle.
It never executes commands supplied in JSON and never marks scientific success.
Run tests with: python -m unittest discover -s research-workflow/tests -v
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import re
import statistics
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def write_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")


def verify_ledger(root):
    previous = "0" * 64
    ledger = root / "ledger/events.jsonl"
    if not ledger.exists():
        return previous
    for number, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        event = json.loads(line)
        claimed = event.pop("hash")
        expected = hashlib.sha256(canonical(event).encode()).hexdigest()
        if event["previous_hash"] != previous or expected != claimed:
            raise ValueError(f"Ledger integrity failure on line {number}")
        if event["kind"] == "hypothesis_preregistered":
            payload = event["payload"]
            hid = payload["id"]
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{1,79}", hid):
                raise ValueError("Invalid registered hypothesis ID in ledger")
            record = root / "ledger/preregistered" / (hid + ".json")
            if not record.is_file() or digest(record) != payload["record_sha256"]:
                raise ValueError(f"Preregistration integrity failure: {hid}")
        previous = claimed
    return previous


def append_event(root, kind, payload):
    event = {"utc": datetime.now(timezone.utc).isoformat(), "kind": kind,
             "payload": payload, "previous_hash": verify_ledger(root)}
    event["hash"] = hashlib.sha256(canonical(event).encode()).hexdigest()
    p = root / "ledger/events.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(canonical(event) + "\n")


def verify_contract(root):
    lock = read_json(root / "ledger/contract.json")
    if digest(root / "objective.json") != lock["objective_sha256"]:
        raise ValueError("Objective changed after lock. Record a reviewed contract revision; do not silently reinitialize.")
    verify_ledger(root)
    return lock


def initialize(root):
    lockpath = root / "ledger/contract.json"
    if lockpath.exists():
        return verify_contract(root)
    lock = {"objective_sha256": digest(root / "objective.json"),
            "objective_id": read_json(root / "objective.json")["id"]}
    write_new(lockpath, lock)
    append_event(root, "contract_frozen", lock)
    return lock


def save_checkpoint(root, path, expected_sha256):
    """Single-writer PO save: validate, snapshot old bytes, atomically replace.

    This guards stale sessions and partial writes, not scientific semantics or
    simultaneous writers. Root must serialize saves. Recovery snapshots never
    authorize automatic replay of tasks or external side effects.
    """
    root, path = Path(root), Path(path)
    lock = verify_contract(root)
    active = root / "status.orchestrator.json"
    if path.resolve() == active.resolve():
        raise ValueError("Stage the proposed checkpoint in a separate file")
    old_bytes = active.read_bytes()
    old_hash = hashlib.sha256(old_bytes).hexdigest()
    if old_hash != expected_sha256:
        raise ValueError("Stale checkpoint: reread active state; do not overwrite newer work")
    old, candidate = json.loads(old_bytes), read_json(path)
    if not isinstance(candidate, dict):
        raise ValueError("Checkpoint must be a JSON object")
    for key, value in old.items():
        if key not in candidate or (value is not None and type(candidate[key]) is not type(value)):
            raise ValueError(f"Preserve existing checkpoint field and type: {key}")
    if isinstance(old.get("review_coverage"), dict):
        if not old["review_coverage"].keys() <= candidate["review_coverage"].keys():
            raise ValueError("Preserve review coverage fields; record resolved claims explicitly")
    for key in ("scope_revision", "workflow_route"):
        if not isinstance(candidate.get(key), dict):
            raise ValueError(f"Checkpoint missing object: {key}")
    # Serialize before any mutation: reject malformed/nonfinite payloads.
    new_bytes = (json.dumps(candidate, ensure_ascii=False, indent=2,
                           allow_nan=False) + "\n").encode("utf-8")
    for key in ("objective_id", "objective_sha256"):
        if candidate["scope_revision"][key] != lock[key]:
            raise ValueError("Checkpoint scope must match the verified contract")
    for key in ("scientific_objective_achieved", "legacy_solver_objective_achieved"):
        if not isinstance(candidate.get(key), bool) or candidate[key] != old.get(key):
            raise ValueError("Checkpoint save cannot change scientific completion flags")
    route, old_route = candidate["workflow_route"], old["workflow_route"]
    for key in ("task_id", "stage", "next_action", "work_budget", "progress"):
        if not route.get(key):
            raise ValueError(f"Checkpoint route missing {key}")
    for key in ("task_id", "stage", "next_action"):
        if not isinstance(route[key], str) or not route[key].strip():
            raise ValueError(f"Checkpoint route requires a nonempty string: {key}")
    if not isinstance(route["progress"], dict) or not isinstance(route["work_budget"], dict):
        raise ValueError("Progress and work_budget must be objects")
    for key in ("constructions_started", "substantive_repairs_used", "independent_reviews_assigned"):
        value = route["progress"][key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"Invalid progress counter: {key}")
        if route["task_id"] == old_route["task_id"] and value < old_route["progress"][key]:
            raise ValueError(f"Cannot reset progress for the same task: {key}")
    if route["task_id"] != old_route["task_id"]:
        disposition = route.get("previous_task_disposition")
        if not isinstance(disposition, str) or not disposition.strip():
            raise ValueError("Changing tasks requires previous_task_disposition with evidence/reason")
    backup = root / "ledger/checkpoints" / ("recovery_" + old_hash + ".json")
    backup.parent.mkdir(parents=True, exist_ok=True)
    if backup.exists():
        if backup.read_bytes() != old_bytes:
            raise ValueError("Existing recovery snapshot differs from its content hash")
    else:
        _atomic_replace_bytes(backup, old_bytes)
    if digest(active) != old_hash:
        raise ValueError("Checkpoint changed during save; reread active state")
    _atomic_replace_bytes(active, new_bytes)
    return {"saved": str(active), "checkpoint_sha256": digest(active),
            "previous_snapshot": str(backup), "scientific_validation": False}


def _atomic_replace_bytes(path, data):
    """Write beside the destination so replacement stays on one filesystem."""
    staged = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".checkpoint-", suffix=".tmp",
                                         dir=path.parent, delete=False) as f:
            staged = Path(f.name)
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(staged, path)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


def validate_hypothesis(h):
    required = {"id", "mechanism", "omitted_computation", "assumptions", "lemma_or_invariant",
                "nearest_prior_art", "prediction", "falsification_rule", "probe",
                "breadth_challenge", "ablation", "unresolved_objections", "status"}
    missing = required - h.keys()
    if missing:
        raise ValueError(f"Hypothesis missing fields: {sorted(missing)}")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{1,79}", h["id"]):
        raise ValueError("Invalid hypothesis ID")
    serialized = canonical(h)
    if "TODO" in serialized or "REPLACE" in serialized:
        raise ValueError("Template placeholders are not preregistration")
    if h["status"] != "proposed":
        raise ValueError("Preregister a proposed hypothesis, not a result")
    if not h["assumptions"] or not h["nearest_prior_art"]:
        raise ValueError("Assumptions and prior art are required")
    for field in required - {"probe", "unresolved_objections"}:
        if not h[field]:
            raise ValueError(f"Empty hypothesis field: {field}")
    for field in ("command", "seeds", "oracle", "cost_accounting"):
        if not h["probe"].get(field):
            raise ValueError(f"Probe missing {field}")


def register(root, path):
    lock = verify_contract(root)
    h = read_json(path)
    validate_hypothesis(h)
    record = {"objective_sha256": lock["objective_sha256"], "source_sha256": digest(path),
              "registered_utc": datetime.now(timezone.utc).isoformat(), "hypothesis": h}
    target = root / "ledger/preregistered" / (h["id"] + ".json")
    write_new(target, record)
    append_event(root, "hypothesis_preregistered", {"id": h["id"], "record_sha256": digest(target)})
    return {"registered": h["id"], "record": str(target)}


def number(value, name, minimum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return value


def interval_gap(result):
    """Gap relative to L for an upper-endpoint answer, in declared target units."""
    lower = number(result["lower"], "lower", 0)
    upper = number(result["upper"], "upper", 0)
    if lower > upper:
        raise ValueError("Reversed interval; no tolerance may conceal this")
    if lower == upper == 0:
        return 0.0
    if lower == 0:
        raise ValueError("L=0 requires a separately preregistered absolute-error protocol")
    return (upper - lower) / lower


def task_key(task):
    for name in ("k", "T"):
        if isinstance(task[name], bool) or not isinstance(task[name], int) or task[name] < 1:
            raise ValueError(f"{name} must be a positive integer, not a boolean")
    number(task["delta"], "delta", 0)
    if task["delta"] == 0:
        raise ValueError("delta must be positive")
    if not isinstance(task["cost"], str) or not isinstance(task["process"], str):
        raise ValueError("cost/process must be named families")
    return (task["cost"], task["process"], task["k"], task["delta"], task["T"])


def required_tasks(config):
    target, breadth = config["target"], config["breadth"]
    return set(itertools.product(breadth["cost_families"], breadth["process_families"],
                                 target["required_k"], target["required_delta"], [target["required_T"]]))


def check_evidence(root, ref):
    """Presence/hash check only: never interprets a witness as a proof."""
    if not isinstance(ref, dict) or not ref.get("path") or not ref.get("sha256"):
        raise ValueError("Evidence requires a path and sha256")
    path = (root / ref["path"]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Evidence must be a file within the workflow directory")
    if digest(path) != ref["sha256"]:
        raise ValueError(f"Evidence hash mismatch: {ref['path']}")


def check_report(report, config, evidence_root=None):
    """Conservative NUMERICAL screen. Independent semantic/statistical review remains required.

    Every row is one task/seed, with matched repeated full-pipeline times and
    candidate/competitor root intervals. Eligible competitors must be declared
    per task; unresolved eligibility must remain an open comparison issue.
    A timeout needs a reviewed censoring analysis; this simple screen rejects it.
    """
    if config.get("schema_version", 1) >= 3:
        return {"status": "NOT_READY", "scientific_success": False,
                "errors": ["The legacy solver screen does not validate relational scope v3. "
                           "Freeze a decision protocol and obtain independent guarantee review first."],
                "diagnostics": [],
                "notice": "No ranking, risk, coverage or scientific-completion claim is validated."}
    errors, diagnostics = [], []
    defaults = config["engineering_defaults"]
    route = report.get("route")
    if route not in ("speed", "quality"):
        errors.append("route must be speed or quality, preregistered before running")
    if report.get("split") != "confirmation":
        errors.append("Development/screening results cannot pass confirmation")
    if report.get("comparison_issues") != []:
        errors.append("Comparator eligibility/reproduction issues unresolved or undeclared")
    if not report.get("eligible_competitors"):
        errors.append("An eligible SOTA panel is required; POT alone is not a panel audit")
    for kind in ("frontier_review", "independent_certificate_review", "frozen_experiment_manifest"):
        if evidence_root is not None:
            try:
                check_evidence(evidence_root, report.get(kind))
            except ValueError as exc:
                errors.append(f"{kind}: {exc}")
        elif not report.get(kind):
            errors.append(f"Missing {kind}")
    observed, seen = {}, set()
    material = False
    for index, row in enumerate(report.get("rows", [])):
        try:
            key = task_key(row["task"])
            seed = row["seed"]
            if isinstance(seed, bool) or not isinstance(seed, int):
                raise ValueError("seed must be an integer")
            if (key, seed) in seen:
                raise ValueError("Duplicate task/seed")
            seen.add((key, seed))
            observed.setdefault(key, set()).add(seed)
            if key not in required_tasks(config):
                raise ValueError("Task outside frozen coverage; cannot replace a required task")
            candidate = row["candidate"]
            gap = interval_gap(candidate)
            if gap > config["target"]["epsilon"]:
                raise ValueError(f"Candidate certificate gap {gap:g} exceeds epsilon")
            def times(result):
                values = result["total_seconds"]
                if len(values) < defaults["timing_repeats"]:
                    raise ValueError("Insufficient raw full-pipeline timing repeats")
                for v in values:
                    number(v, "total_seconds", 0)
                    if v == 0:
                        raise ValueError("Zero elapsed time is not a measurement")
                return statistics.median(values)
            ct = times(candidate)
            competitors = row["competitors"]
            ids = [c["id"] for c in competitors]
            if len(ids) != len(set(ids)) or set(ids) != set(report["eligible_competitors"]):
                raise ValueError("Missing or duplicate eligible competitor result")
            if not competitors:
                raise ValueError("No competitor results")
            metrics = []
            for competitor in competitors:
                bgap, bt = interval_gap(competitor), times(competitor)
                if route == "speed":
                    if bgap > config["target"]["epsilon"]:
                        raise ValueError("Competitor did not reach target: requires reviewed timeout/censoring analysis")
                    metrics.append(bt)
                elif route == "quality":
                    budget = number(row["total_budget_seconds"], "total_budget_seconds", 0)
                    if max(candidate["total_seconds"] + competitor["total_seconds"]) > budget:
                        raise ValueError("Matched total budget exceeded")
                    metrics.append(bgap)
            all_results = [candidate] + competitors
            if max(r["lower"] for r in all_results) > min(r["upper"] for r in all_results):
                raise ValueError("Certificates for the same target have no common intersection")
            if route == "speed":
                ratio = ct / min(metrics)
            elif route == "quality":
                best = min(metrics)
                ratio = gap / best if best else (1.0 if gap == 0 else math.inf)
            else:
                raise ValueError("Invalid route")
            if ratio > 1.0:
                raise ValueError(f"Regression against strongest eligible competitor: ratio={ratio:g}")
            material |= ratio <= 1 - defaults["material_improvement_fraction"]
            diagnostics.append({"task": row["task"], "seed": seed, "ratio": ratio,
                                "candidate_gap": gap, "candidate_seconds": ct})
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
            errors.append(f"row {index}: {exc}")
    for key in sorted(required_tasks(config)):
        if len(observed.get(key, set())) < defaults["confirmation_seeds_per_task"]:
            errors.append(f"Coverage or seed deficit: {key}")
    if not material:
        errors.append("No preregistered material improvement demonstrated")
    return {"status": "NUMERICAL_SCREEN_PASSED_REVIEW_REQUIRED" if not errors else "NOT_READY",
            "scientific_success": False, "errors": errors, "diagnostics": diagnostics,
            "pending_independent_reviews": ["target/input equivalence", "certificate witness mathematics and numerics",
                "statistical significance and repeated-testing accounting", "SOTA panel completeness/fairness",
                "tree mechanism, ablation and nearest-prior-art contribution"],
            "notice": "File hashes and numerical screens are not proof verification or a SOTA claim."}


def main():
    # Windows terminals may default to a legacy code page even though every
    # workflow artifact is UTF-8.  A status message must not fail merely
    # because it contains Vietnamese text.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    checkpoint = sub.add_parser("checkpoint")
    checkpoint.add_argument("path", type=Path)
    checkpoint.add_argument("--expected-sha256", required=True)
    reg = sub.add_parser("register")
    reg.add_argument("path", type=Path)
    check = sub.add_parser("check-report")
    check.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = initialize(ROOT)
        elif args.command == "status":
            result = {"contract": verify_contract(ROOT),
                      "checkpoint_source": "status.orchestrator.json" if (ROOT / "status.orchestrator.json").exists() else "status.json",
                      "checkpoint": read_json(ROOT / "status.orchestrator.json") if (ROOT / "status.orchestrator.json").exists() else read_json(ROOT / "status.json"),
                      "checkpoint_sha256": digest(ROOT / "status.orchestrator.json") if (ROOT / "status.orchestrator.json").exists() else None,
                      "legacy_checkpoint_source": "status.json",
                      "registered": sorted(p.stem for p in (ROOT / "ledger/preregistered").glob("*.json"))}
        elif args.command == "checkpoint":
            result = save_checkpoint(ROOT, args.path, args.expected_sha256)
        elif args.command == "register":
            result = register(ROOT, args.path)
        else:
            lock = verify_contract(ROOT)
            report = read_json(args.path)
            if report.get("objective_sha256") != lock["objective_sha256"]:
                raise ValueError("Report belongs to another or unfrozen objective")
            result = check_report(report, read_json(ROOT / "objective.json"), ROOT)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 1 if result.get("status") == "NOT_READY" else 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
