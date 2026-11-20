"""Deterministic synthetic revenue assurance data; Python 3.10+, no dependencies."""
import argparse
import csv
import json
import random
from pathlib import Path


PRODUCTS = [
    ("P001", "ERP license", "recurring", 15000),
    ("P002", "Managed support", "recurring", 500000),
    ("P003", "Cloud compute", "metered", 2000),
    ("P004", "Analytics license", "recurring", 30000),
]


def generate(output: Path, customers: int = 100, months: int = 12, seed: int = 42, anomaly_rate: float = 0.035):
    if customers < 1 or not 1 <= months <= 120:
        raise ValueError("customers must be positive; months must be 1..120")
    if not 0 <= anomaly_rate <= 1:
        raise ValueError('anomaly_rate must be between 0 and 1')
    scale = anomaly_rate / .035
    rng = random.Random(seed)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "evaluation").mkdir(exist_ok=True)
    periods = [f"{2025 + i // 12:04d}-{i % 12 + 1:02d}" for i in range(months)]
    schemas = {
        "customers": "customer_id segment",
        "products": "product_id name billing_model unit_price_cents",
        "contracts": "contract_id customer_id start_period end_period",
        "contract_items": "item_id contract_id product_id unit_price_cents quantity",
        "service_usage": "item_id period delivered_quantity",
        "invoice_items": "invoice_item_id item_id period billed_cents",
        "journal_entries": "journal_id invoice_item_id period recognized_cents",
        "evaluation/ground_truth": "anomaly_id item_id period defect expected_cents actual_cents exposure_cents",
    }
    from contextlib import ExitStack
    with ExitStack() as stack:
        writers, counts = {}, dict.fromkeys(schemas, 0)
        for name, schema in schemas.items():
            stream = stack.enter_context((output / f"{name}.csv").open("w", newline="", encoding="utf-8"))
            writer = csv.writer(stream)
            writer.writerow(schema.split())
            writers[name] = writer

        def emit(name, *values):
            writers[name].writerow(values)
            counts[name] += 1

        for product in PRODUCTS:
            emit("products", *product)
        for i in range(1, customers + 1):
            customer_id, contract_id = f"C{i:07d}", f"CT{i:07d}"
            segment = rng.choices(["SMB", "Mid-market", "Enterprise"], [60, 30, 10])[0]
            emit("customers", customer_id, segment)
            emit("contracts", contract_id, customer_id, periods[0], periods[-1])
            for j, product in enumerate(rng.sample(PRODUCTS, 2), 1):
                product_id, _, model, list_price = product
                item_id = f"{contract_id}-{j}"
                quantity = 1 if product_id == "P002" else rng.randint(5, {"SMB": 30, "Mid-market": 120, "Enterprise": 500}[segment])
                price = list_price * rng.choice([85, 90, 95, 100]) // 100
                emit("contract_items", item_id, contract_id, product_id, price, quantity)
                for period in periods:
                    delivered = quantity if model == "recurring" else max(1, quantity * rng.randint(70, 140) // 100)
                    emit("service_usage", item_id, period, delivered)
                    expected = price * delivered
                    draw = rng.random()
                    defect, actual = None, expected
                    if draw < .01 * scale:
                        defect, actual = "MISSING_BILLING", 0
                    elif draw < .03 * scale:
                        defect, actual = "UNDERBILLING", expected * 80 // 100
                    elif draw < .035 * scale:
                        defect, actual = "OVERBILLING", expected * 125 // 100
                    key = f"{item_id}-{period}"
                    if defect != "MISSING_BILLING":
                        emit("invoice_items", f"I-{key}", item_id, period, actual)
                        emit("journal_entries", f"J-{key}", f"I-{key}", period, actual)
                    if defect:
                        emit("evaluation/ground_truth", f"A-{key}", item_id, period, defect, expected, actual, expected - actual)
    manifest = {"version": "0.1", "seed": seed, "customers": customers, "months": months, "currency": "USD", "amount_unit": "cent", "anomaly_rate": anomaly_rate, "row_counts": counts}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--customers", type=int, default=100)
    parser.add_argument("--months", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/generated"))
    args = parser.parse_args()
    print(json.dumps(generate(args.output, args.customers, args.months, args.seed), indent=2))
