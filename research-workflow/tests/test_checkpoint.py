"""Recovery and stale-session guards; these tests make no scientific claims."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("checkpoint_workflow", ROOT / "workflow.py")
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        wf.write_new(self.root / "objective.json", {"id": "test-objective"})
        lock = wf.initialize(self.root)
        self.active = self.root / "status.orchestrator.json"
        self.old = {
            "scope_revision": lock,
            "scientific_objective_achieved": False,
            "legacy_solver_objective_achieved": False,
            "latest_user_selection": "decision.md",
            "review_coverage": {"pending": ["root claim"], "packet_revision": "unknown"},
            "workflow_route": {
                "task_id": "task_1", "stage": "screening", "next_action": "check lemma",
                "work_budget": {"max_constructions": 1},
                "progress": {"state": "in_progress", "constructions_started": 1,
                             "substantive_repairs_used": 0, "independent_reviews_assigned": 0}}}
        # Preserve Windows byte representation when snapshotting, too.
        self.old_bytes = (json.dumps(self.old, indent=2) + "\n").replace("\n", "\r\n").encode()
        self.active.write_bytes(self.old_bytes)
        self.expected = wf.digest(self.active)
        self.proposed = self.root / "proposed.json"
        self.new = copy.deepcopy(self.old)
        self.new["workflow_route"]["progress"]["substantive_repairs_used"] = 1

    def save(self, expected=None):
        self.proposed.write_text(json.dumps(self.new), encoding="utf-8")
        return wf.save_checkpoint(self.root, self.proposed, expected or self.expected)

    def test_success_keeps_exact_previous_bytes_and_progress(self):
        out = self.save()
        self.assertEqual(Path(out["previous_snapshot"]).read_bytes(), self.old_bytes)
        self.assertEqual(wf.read_json(self.active), self.new)
        self.assertEqual(out["checkpoint_sha256"], wf.digest(self.active))
        self.assertFalse(out["scientific_validation"])

    def test_stale_session_cannot_overwrite_newer_checkpoint(self):
        self.save()
        current = self.active.read_bytes()
        with self.assertRaisesRegex(ValueError, "Stale checkpoint"):
            self.save()
        self.assertEqual(self.active.read_bytes(), current)

    def test_interrupted_replace_preserves_active_and_recovery(self):
        real_replace = wf.os.replace
        def interrupted(src, dst):
            if Path(dst) == self.active:
                raise OSError("simulated interruption before active replace")
            return real_replace(src, dst)
        with mock.patch.object(wf.os, "replace", side_effect=interrupted):
            with self.assertRaises(OSError):
                self.save()
        self.assertEqual(self.active.read_bytes(), self.old_bytes)
        snapshots = list((self.root / "ledger/checkpoints").glob("recovery_*.json"))
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0].read_bytes(), self.old_bytes)
        self.assertEqual(list(self.root.rglob(".checkpoint-*.tmp")), [])
        self.save()  # Retrying the local save is safe; this does not replay research.

    def test_invalid_input_cannot_destroy_active(self):
        self.proposed.write_text('{"broken":', encoding="utf-8")
        with self.assertRaises(ValueError):
            wf.save_checkpoint(self.root, self.proposed, self.expected)
        self.assertEqual(self.active.read_bytes(), self.old_bytes)

    def test_reject_scope_completion_and_progress_reset(self):
        variants = []
        wrong_scope = copy.deepcopy(self.new)
        wrong_scope["scope_revision"]["objective_sha256"] = "0" * 64
        variants.append(wrong_scope)
        promoted = copy.deepcopy(self.new)
        promoted["scientific_objective_achieved"] = True
        variants.append(promoted)
        reset = copy.deepcopy(self.new)
        reset["workflow_route"]["progress"]["constructions_started"] = 0
        variants.append(reset)
        new_task = copy.deepcopy(self.new)
        new_task["workflow_route"]["task_id"] = "task_2"
        variants.append(new_task)
        for candidate in variants:
            with self.subTest(candidate=candidate):
                self.new = candidate
                with self.assertRaises(ValueError):
                    self.save()
                self.assertEqual(self.active.read_bytes(), self.old_bytes)

    def test_reject_stripped_handoff_and_malformed_invariant_types(self):
        for key in ("latest_user_selection", "review_coverage"):
            candidate = copy.deepcopy(self.new)
            candidate.pop(key)
            self.proposed.write_text(json.dumps(candidate), encoding="utf-8")
            with self.assertRaises(ValueError):
                wf.save_checkpoint(self.root, self.proposed, self.expected)
        for field, value in (("scientific_objective_achieved", 0), ("task_id", {}),
                             ("stage", True), ("next_action", "   ")):
            candidate = copy.deepcopy(self.new)
            target = candidate if field.endswith("achieved") else candidate["workflow_route"]
            target[field] = value
            self.proposed.write_text(json.dumps(candidate), encoding="utf-8")
            with self.assertRaises(ValueError):
                wf.save_checkpoint(self.root, self.proposed, self.expected)
        candidate = copy.deepcopy(self.new)
        candidate["review_coverage"].pop("pending")
        self.proposed.write_text(json.dumps(candidate), encoding="utf-8")
        with self.assertRaises(ValueError):
            wf.save_checkpoint(self.root, self.proposed, self.expected)
        self.assertEqual(self.active.read_bytes(), self.old_bytes)

    def test_response_loss_after_replace_does_not_justify_replay(self):
        real_replace = wf.os.replace
        def response_lost(src, dst):
            real_replace(src, dst)
            if Path(dst) == self.active:
                raise OSError("simulated loss after successful replacement")
        with mock.patch.object(wf.os, "replace", side_effect=response_lost):
            with self.assertRaises(OSError):
                self.save()
        self.assertEqual(wf.read_json(self.active), self.new)
        with self.assertRaisesRegex(ValueError, "Stale checkpoint"):
            self.save()


if __name__ == "__main__":
    unittest.main()
