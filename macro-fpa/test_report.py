import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parent


class ReportTest(unittest.TestCase):
    def run_report(self, costs, output, fixtures=PROJECT / "fixtures"):
        return subprocess.run(
            [sys.executable, str(PROJECT / "report.py"), "--costs", str(costs),
             "--output", str(output), "--fixtures", str(fixtures)],
            capture_output=True, text=True, check=False,
        )

    def test_demo_calculations(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.csv"
            result = self.run_report(PROJECT / "example/costs.csv", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open(newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]["actual_brl_in_first_month_prices"], "100000.00")
            self.assertEqual(rows[-1]["month"], "2025-03")
            self.assertEqual(rows[-1]["variance_brl"], "-1000.00")
            self.assertEqual(rows[-1]["actual_usd"], "20000.00")
            self.assertEqual(rows[-1]["actual_brl_in_first_month_prices"], "102931.09")

    def test_missing_indicator_keeps_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            output = work / "report.csv"
            output.write_text("previous report", encoding="utf-8")
            (work / "fx.json").write_text("[]", encoding="utf-8")
            (work / "ipca.json").write_bytes((PROJECT / "fixtures/ipca.json").read_bytes())
            result = self.run_report(PROJECT / "example/costs.csv", output, work)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Missing BCB FX for 2025-01", result.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "previous report")

    def test_gap_fails_before_reporting(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            costs = work / "costs.csv"
            costs.write_text("month,actual_brl,budget_brl\n2025-01,1,1\n2025-03,1,1\n",
                             encoding="utf-8")
            output = work / "report.csv"
            result = self.run_report(costs, output)
            self.assertEqual(result.returncode, 1)
            self.assertIn("consecutive months", result.stderr)
            self.assertFalse(output.exists())
