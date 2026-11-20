import csv
import tempfile
import unittest
from pathlib import Path

from simulator import generate


def read(root, name):
    with (root / f"{name}.csv").open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


class SimulatorTest(unittest.TestCase):
    def test_reproducibility_and_truth(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/"a", Path(directory)/"b"
            manifest = generate(a, 100, 12, 42)
            self.assertEqual(manifest, generate(b, 100, 12, 42))
            for file in a.rglob("*.csv"):
                self.assertEqual(file.read_bytes(), (b/file.relative_to(a)).read_bytes())
            items = {r["item_id"]: r for r in read(a, "contract_items")}
            usage = read(a, "service_usage")
            self.assertEqual(len(usage), 2400)
            expected = {(r["item_id"], r["period"]): int(r["delivered_quantity"])*int(items[r["item_id"]]["unit_price_cents"]) for r in usage}
            actual = {(r["item_id"], r["period"]): int(r["billed_cents"]) for r in read(a, "invoice_items")}
            changes = {k: v - actual.get(k, 0) for k, v in expected.items() if v != actual.get(k, 0)}
            truth = {(r["item_id"], r["period"]): int(r["exposure_cents"]) for r in read(a, "evaluation/ground_truth")}
            self.assertTrue(truth)
            self.assertEqual(changes, truth)
            ledger = {r["invoice_item_id"]: int(r["recognized_cents"]) for r in read(a, "journal_entries")}
            self.assertEqual(ledger, {r["invoice_item_id"]: int(r["billed_cents"]) for r in read(a, "invoice_items")})

    def test_invalid_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                generate(Path(directory), 0, 12, 42)


if __name__ == "__main__":
    unittest.main()
