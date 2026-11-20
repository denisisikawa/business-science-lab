"""Shared deterministic sandbox engine. No AI or external services."""
import csv
import tempfile
from pathlib import Path
from simulator import generate

def read(root, name):
    with (root / (name + ".csv")).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def reconcile(root):
    items = {r["item_id"]: r for r in read(root, "contract_items")}
    products = {r["product_id"]: r for r in read(root, "products")}
    billed = {(r["item_id"], r["period"]): r for r in read(root, "invoice_items")}
    rows, monthly = [], {}
    total_expected, total_actual, under, over = 0, 0, 0, 0
    for u in read(root, "service_usage"):
        key = (u["item_id"], u["period"])
        item = items[key[0]]
        product = products[item["product_id"]]
        quantity = int(u["delivered_quantity"]) if product["billing_model"] == "metered" else int(item["quantity"])
        expected = quantity * int(item["unit_price_cents"])
        invoice = billed.get(key)
        actual = int(invoice["billed_cents"]) if invoice else 0
        gap = expected - actual
        total_expected += expected
        total_actual += actual
        under += max(0, gap)
        over += max(0, -gap)
        month = monthly.setdefault(key[1], {"period": key[1], "expected": 0, "actual": 0})
        month["expected"] += expected
        month["actual"] += actual
        if gap:
            rows.append({"contract": item["contract_id"], "item": key[0], "period": key[1], "product": product["name"], "quantity": quantity, "unit_price": int(item["unit_price_cents"]), "invoice": invoice["invoice_item_id"] if invoice else None, "expected": expected, "actual": actual, "gap": gap, "defect": "MISSING_BILLING" if not invoice else ("UNDERBILLING" if gap > 0 else "OVERBILLING")})
    rows.sort(key=lambda r: abs(r["gap"]), reverse=True)
    return {"expected": total_expected, "actual": total_actual, "under": under, "over": over, "events": len(billed) + sum(r["invoice"] is None for r in rows), "rows": rows, "monthly": list(monthly.values())}

def evaluate(root, rows):
    # Isolated from detection; compare only after controls finish.
    truth = {(r["item_id"], r["period"], r["defect"]): int(r["exposure_cents"]) for r in read(root, "evaluation/ground_truth")}
    predictions = {(r["item"], r["period"], r["defect"]): r["gap"] for r in rows}
    matched = truth.keys() & predictions.keys()
    tp, fp, fn = len(matched), len(predictions)-len(matched), len(truth)-len(matched)
    return {"tp": tp, "fp": fp, "fn": fn, "precision": tp/(tp+fp) if tp+fp else None, "recall": tp/(tp+fn) if tp+fn else None, "amount_errors": sum(truth[k] != predictions[k] for k in matched)}

def run_scenario(customers=1000, months=12, seed=42, anomaly_rate=.035):
    if not 1 <= customers <= 10000 or not 1 <= months <= 12 or not 0 <= anomaly_rate <= .15:
        raise ValueError("Sandbox limits: 1–10,000 customers; 1–12 months; 0–15% anomalies")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        manifest = generate(root, customers, months, seed, anomaly_rate)
        result = reconcile(root)
        result["benchmark"] = evaluate(root, result["rows"])
        result["counts"] = manifest["row_counts"]
        return result
