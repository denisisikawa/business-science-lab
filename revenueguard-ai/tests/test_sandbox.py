import tempfile
import unittest
from pathlib import Path
from simulator import generate
from sandbox_engine import run_scenario, reconcile, evaluate

class SandboxTests(unittest.TestCase):
    def test_clean(self):
        r = run_scenario(100, 12, 42, 0)
        self.assertEqual(r["events"], 2400)
        self.assertEqual(r["rows"], [])
        self.assertEqual(r["expected"], r["actual"])
        self.assertIsNone(r["benchmark"]["precision"])

    def test_defects(self):
        r = run_scenario(100, 12, 42, .035)
        self.assertGreater(len(r["rows"]), 0)
        self.assertEqual(r["benchmark"]["fp"], 0)
        self.assertEqual(r["benchmark"]["fn"], 0)
        self.assertEqual(r["benchmark"]["amount_errors"], 0)
        self.assertEqual(r["expected"]-r["actual"], r["under"]-r["over"])
        self.assertEqual(r, run_scenario(100, 12, 42, .035))

    def test_controls_do_not_read_labels(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            generate(root)
            (root / "evaluation" / "ground_truth.csv").unlink()
            self.assertTrue(reconcile(root)["rows"])
