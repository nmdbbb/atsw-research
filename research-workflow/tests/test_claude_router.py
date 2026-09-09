import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "claude_router", Path(__file__).resolve().parents[1] / "claude_router.py")
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)

LIVE = ['claude-fable-5-1', 'claude-opus-5', 'claude-sonnet-5', 'claude-fable-5',
        'claude-opus-4-8', 'claude-opus-4-7', 'claude-sonnet-4-6', 'claude-opus-4-6',
        'claude-opus-4-5-20251101', 'claude-haiku-4-5-20251001', 'claude-sonnet-4-5-20250929']


class RoutingTests(unittest.TestCase):
    def test_upgrade_one_tier_and_cap(self):
        self.assertEqual(router.route("mechanical")["model"], "claude-sonnet-5")
        self.assertEqual(router.route("implementation")["model"], "claude-opus-5")
        self.assertEqual(router.route("theorem")["model"], "claude-opus-5")
        self.assertTrue(router.route("scientific_audit")["capped_at_highest_tier"])

    def test_live_session_models_resolve(self):
        for kind in router.TASKS:
            self.assertIn(router.route(kind, LIVE)["model"], LIVE)

    def test_no_silent_downgrade_or_unknown_role(self):
        with self.assertRaises(router.RoutingUnavailable):
            router.route("theorem", ["claude-sonnet-5"])
        with self.assertRaises(router.RoutingUnavailable):
            router.route("implementation", [])
        with self.assertRaises(ValueError):
            router.route("guess")

    def test_generation_lane_is_not_a_capability_rung(self):
        r = router.route("variant_synthesis", LIVE)
        self.assertEqual(r["lane"], "generation")
        self.assertIn(r["model"], router.GENERATION_LANE)
        with self.assertRaises(router.RoutingUnavailable):
            router.route("variant_synthesis", ["claude-opus-5"])

    def test_spawn_requires_context_and_drops_effort(self):
        kw = router.spawn_arguments("certificate", "check_proof",
                                    "Review the finite-horizon propagation proof",
                                    "Project ATSW, claim-gated discipline")
        self.assertEqual(set(kw), {"name", "task", "context_summary", "model"})
        self.assertNotIn("intended_effort", kw)
        self.assertNotIn("fork_turns", kw)
        with self.assertRaises(ValueError):
            router.spawn_arguments("certificate", "n", "t", "  ")

    def test_output_schema_passthrough_and_type_check(self):
        kw = router.spawn_arguments("literature", "read", "Read X", "ctx",
                                    output_schema={"type": "object"})
        self.assertEqual(kw["output_schema"], {"type": "object"})
        with self.assertRaises(ValueError):
            router.spawn_arguments("literature", "read", "Read X", "ctx", output_schema="obj")


if __name__ == "__main__":
    unittest.main()
