import json
import os
import unittest
from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from intelligence import analyze, commentary, read_detail
from report import read_costs

ROOT = Path(__file__).resolve().parent / "example"


class IntelligenceTest(unittest.TestCase):
    def setUp(self):
        self.control = read_costs(ROOT / "costs.csv")
        self.detail = read_detail(ROOT / "cost-detail.csv", self.control)
        self.quarter = analyze(self.detail, None)

    def test_abc_and_variance_bridge(self):
        self.assertEqual(self.quarter["variance"], Decimal(3000))
        self.assertEqual(self.quarter["overruns"], Decimal(14000))
        self.assertEqual(self.quarter["offsets"], Decimal(-11000))
        self.assertEqual([(row["category"], row["class"]) for row in self.quarter["categories"]],
                         [("Cloud", "A"), ("Licenças", "A"), ("Serviços", "A"),
                          ("Conectividade", "B"), ("Outros", "C")])
        self.assertEqual(self.quarter["categories"][-1]["cumulative_share"], Decimal(100))
        march = analyze(self.detail, date(2025, 3, 1))
        self.assertEqual(march["variance"], Decimal(-1000))
        self.assertIn("Serviços", commentary(march, "rules", "")["text"]["pt"])

    def test_exact_threshold_and_zero_actual(self):
        month = date(2025, 1, 1)
        values = {"A": (Decimal(80), Decimal(0)), "B": (Decimal(15), Decimal(0)),
                  "C": (Decimal(5), Decimal(0)), "D": (Decimal(0), Decimal(0))}
        result = analyze({month: values}, None)
        self.assertEqual([row["class"] for row in result["categories"]], ["A", "B", "C", "C"])
        empty = analyze({month: {"A": (Decimal(0), Decimal(0))}}, None)
        self.assertIsNone(empty["categories"][0]["class"])
        self.assertIsNone(empty["variance_pct"])

    def test_reconciliation(self):
        self.control[date(2025, 3, 1)] = Decimal(0), Decimal(0)
        with self.assertRaisesRegex(ValueError, "does not reconcile.*2025-03"):
            read_detail(ROOT / "cost-detail.csv", self.control)

    def test_structured_ai_plan_and_reviewable_commentary(self):
        plan = {"first_focus": "concentration", "check": "usage"}
        response = {"status": "completed", "output": [{"content": [
            {"type": "output_text", "text": json.dumps(plan)}
        ]}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("intelligence.urlopen", return_value=BytesIO(json.dumps(response).encode())) as call:
                result = commentary(self.quarter, "openai", "test-model")
        payload = json.loads(call.call_args.args[0].data)
        self.assertFalse(payload["store"])
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertEqual(result["source"], "openai")
        text = result["text"]["pt"]
        self.assertLess(text.index("89,6%"), text.index("Cloud"))
        self.assertIn("A causa operacional requer evidência.", text)

    def test_invalid_ai_output_falls_back(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            with patch("intelligence.plan_with_ai", return_value={"first_focus": "missing", "check": "usage"}):
                result = commentary(self.quarter, "openai", "test-model")
        self.assertEqual(result["source"], "rules_fallback")
        self.assertEqual(result["text"], commentary(self.quarter, "rules", "")["text"])
