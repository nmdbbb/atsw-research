"""Adversarial guard tests; synthetic fixtures are NOT scientific benchmark evidence."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("workflow", ROOT / "workflow.py")
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)


class ScreeningTests(unittest.TestCase):
    def setUp(self):
        self.config = wf.read_json(ROOT / "objective.json")
        self.config["engineering_defaults"]["confirmation_seeds_per_task"] = 1
        self.config["engineering_defaults"]["timing_repeats"] = 1
        self.report = {"route": "speed", "split": "confirmation", "comparison_issues": [],
            "eligible_competitors": ["strong", "weak"], "frontier_review": "synthetic",
            "independent_certificate_review": "synthetic", "frozen_experiment_manifest": "synthetic", "rows": []}
        for cost, process, k, delta, T in wf.required_tasks(self.config):
            self.report["rows"].append({"task": dict(cost=cost, process=process, k=k, delta=delta, T=T),
                "seed": 7, "candidate": dict(lower=100, upper=100.2, total_seconds=[0.8]),
                "competitors": [dict(id="strong", lower=100, upper=100.2, total_seconds=[1.0]),
                                dict(id="weak", lower=100, upper=100.2, total_seconds=[2.0])]})

    def screen(self):
        return wf.check_report(self.report, self.config)

    def test_full_synthetic_screen_is_never_scientific_success(self):
        result = self.screen()
        self.assertEqual(result["errors"], [])
        self.assertFalse(result["scientific_success"])

    def test_missing_expensive_cell_blocks(self):
        self.report["rows"] = [r for r in self.report["rows"] if not (r["task"]["k"] == 2 and r["task"]["delta"] == 0.18)]
        self.assertTrue(self.screen()["errors"])

    def test_geometric_mean_cannot_hide_regression(self):
        self.report["rows"][0]["candidate"]["total_seconds"] = [1.01]
        self.assertTrue(any("Regression" in e for e in self.screen()["errors"]))

    def test_cannot_choose_weaker_baseline(self):
        self.report["rows"][0]["candidate"]["total_seconds"] = [1.5]
        self.assertTrue(self.screen()["errors"])

    def test_wrong_denominator_cannot_pass(self):
        r = self.report["rows"][0]["candidate"]
        r.update(lower=100, upper=100.501)
        self.assertTrue(self.screen()["errors"])

    def test_nan_and_reversed_interval_rejected(self):
        for lower, upper in [(float("nan"), 100), (101, 100), (0, 1), (-1, 0)]:
            with self.subTest(lower=lower):
                with self.assertRaises(ValueError):
                    wf.interval_gap(dict(lower=lower, upper=upper))

    def test_exact_zero_gap_cannot_be_beaten_by_positive_gap(self):
        self.report["route"] = "quality"
        for row in self.report["rows"]:
            row["total_budget_seconds"] = 3
            row["competitors"][0]["upper"] = 100
        self.assertTrue(self.screen()["errors"])

    def test_disjoint_certificates_for_same_target_rejected(self):
        for row in self.report["rows"]:
            for competitor in row["competitors"]:
                competitor.update(lower=200, upper=200.4)
        self.assertTrue(any("intersection" in e for e in self.screen()["errors"]))

    def test_bool_cannot_impersonate_k1(self):
        for row in self.report["rows"]:
            if row["task"]["k"] == 1:
                row["task"]["k"] = True
        self.assertTrue(self.screen()["errors"])

    def test_duplicate_seed_is_not_replication(self):
        self.report["rows"].append(copy.deepcopy(self.report["rows"][0]))
        self.assertTrue(any("Duplicate" in e for e in self.screen()["errors"]))

    def test_evidence_text_is_not_a_witness(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                wf.check_evidence(Path(td), {"path": "absent", "sha256": "made_up"})

    def test_template_cannot_be_registered(self):
        with self.assertRaises(ValueError):
            wf.validate_hypothesis(wf.read_json(ROOT / "hypotheses/H_TEMPLATE.json"))

    def test_contract_edits_and_ledger_edits_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = root / "objective.json"
            p.write_text(json.dumps(self.config), encoding="utf-8")
            wf.initialize(root)
            wf.verify_contract(root)
            p.write_text(json.dumps({**self.config, "id": "changed"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                wf.verify_contract(root)
            ledger = root / "ledger/events.jsonl"
            ledger.write_text(ledger.read_text(encoding="utf-8").replace("contract_frozen", "changed"), encoding="utf-8")
            with self.assertRaises(ValueError):
                wf.verify_ledger(root)

    def test_registered_record_cannot_change_after_freeze(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wf.write_new(root / "objective.json", self.config)
            wf.initialize(root)
            record = root / "ledger/preregistered/H_SYNTHETIC.json"
            wf.write_new(record, {"prediction": "before measurement"})
            wf.append_event(root, "hypothesis_preregistered", {"id": "H_SYNTHETIC", "record_sha256": wf.digest(record)})
            wf.verify_contract(root)
            record.write_text('{"prediction":"changed after measurement"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                wf.verify_contract(root)


if __name__ == "__main__":
    unittest.main()
