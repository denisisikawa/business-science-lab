"""Shared deterministic sandbox engine. No AI or external services."""
import csv
import re
from datetime import date
import tempfile
from pathlib import Path
from simulator import generate

def read(root, name, required=()):
    with (root / (name + ".csv")).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not set(required).issubset(fields):
            raise ValueError(name + ": invalid_headers")
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError(name + ": malformed_csv_row")
        return rows


def validated_rows(root, name, fields, keys, integer_fields=(), positive_fields=(), period=False):
    """Fail closed before indexing: a duplicate must never silently overwrite a fact."""
    rows = read(root, name, fields)
    seen = [set() for _ in keys]
    for number, row in enumerate(rows, 2):
        def reject(reason):
            # Identify the source position, not private identifiers or payload values.
            raise ValueError(name + ": row " + str(number) + ": " + reason)
        for field in fields:
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                reject("missing_" + field)
        # Keys and references must already be canonical; don't repair identity silently.
        for field in set(field for key in keys for field in key) | ({"product_id", "contract_id", "item_id"} & set(fields)):
            if row[field] != row[field].strip():
                reject("noncanonical_" + field)
        for key, values in zip(keys, seen):
            identity = tuple(row[field] for field in key)
            if identity in values:
                reject("duplicate_key_" + "_".join(key))
            values.add(identity)
        for field in integer_fields:
            if not re.fullmatch(r"[0-9]+", row[field]):
                reject("invalid_" + field)
            if field in positive_fields and int(row[field]) == 0:
                reject("nonpositive_" + field)
        if period:
            value = row["period"]
            try:
                if not re.fullmatch(r"[0-9]{4}-[0-9]{2}", value):
                    raise ValueError()
                date.fromisoformat(value + "-01")
            except ValueError:
                reject("invalid_period")
    return rows


def reconciliation_inputs(root):
    """Validate only the four datasets actually consumed by this billing control."""
    products = validated_rows(root, "products", ("product_id", "name", "billing_model", "unit_price_cents"),
                              (("product_id",),), ("unit_price_cents",), ("unit_price_cents",))
    items = validated_rows(root, "contract_items", ("item_id", "contract_id", "product_id", "unit_price_cents", "quantity"),
                           (("item_id",),), ("unit_price_cents", "quantity"), ("unit_price_cents", "quantity"))
    usage = validated_rows(root, "service_usage", ("item_id", "period", "delivered_quantity"),
                           (("item_id", "period"),), ("delivered_quantity",), period=True)
    invoices = validated_rows(root, "invoice_items", ("invoice_item_id", "item_id", "period", "billed_cents"),
                              (("invoice_item_id",), ("item_id", "period")), ("billed_cents",), period=True)
    products = {row["product_id"]: row for row in products}
    items = {row["item_id"]: row for row in items}
    for row in products.values():
        if row["billing_model"] not in ("recurring", "metered"):
            raise ValueError("products: invalid_billing_model")
    if any(row["product_id"] not in products for row in items.values()):
        raise ValueError("contract_items: unknown_product")
    if any(row["item_id"] not in items for row in usage):
        raise ValueError("service_usage: unknown_item")
    if any(row["item_id"] not in items for row in invoices):
        raise ValueError("invoice_items: unknown_item")
    delivered = {(row["item_id"], row["period"]) for row in usage}
    if any((row["item_id"], row["period"]) not in delivered for row in invoices):
        raise ValueError("invoice_items: missing_usage_evidence")
    return items, products, usage, {(row["item_id"], row["period"]): row for row in invoices}


def reconcile(root):
    items, products, usage, billed = reconciliation_inputs(root)
    rows, monthly = [], {}
    total_expected, total_actual, under, over = 0, 0, 0, 0
    for u in usage:
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
