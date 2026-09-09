import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("router", Path(__file__).resolve().parents[1] / "model_router.py")
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)


class RoutingTests(unittest.TestCase):
    def test_upgrade_and_cap(self):
        self.assertEqual(router.route("mechanical")["model"], "gpt-5.6-terra")
        self.assertEqual(router.route("implementation")["model"], "gpt-5.6-sol")
        self.assertEqual(router.route("theorem")["model"], "gpt-6-astra")
        self.assertTrue(router.route("scientific_audit")["capped_at_highest_tier"])

    def test_no_downgrade_or_unknown_role(self):
        with self.assertRaises(router.RoutingUnavailable):
            router.route("theorem", ["gpt-5.6-sol"])
        with self.assertRaises(router.RoutingUnavailable):
            router.route("implementation", [])
        with self.assertRaises(ValueError):
            router.route("guess")

    def test_stronger_available_fallback(self):
        self.assertEqual(router.route("implementation", ["gpt-6-astra"])["model"], "gpt-6-astra")

    def test_spawn_spec_preserves_explicit_model(self):
        args = router.spawn_arguments("certificate", "check_proof", "Review finite-horizon proof")
        self.assertEqual(args["fork_turns"], "none")
        self.assertEqual(args["reasoning_effort"], "xhigh")
        self.assertEqual(set(args), {"task_name", "message", "model", "reasoning_effort", "fork_turns"})


if __name__ == "__main__":
    unittest.main()
