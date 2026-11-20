# Data model and simulation contract

## Scope and grain
All entities are synthetic. USD integer cents avoid floating point currency errors. Monthly billing periods use YYYY-MM; UTC dates and real accounting calendars will be introduced in a future version. V0.1 models fully delivered recurring services or measured cloud usage under contracts active for the entire simulation horizon. Tax, foreign exchange, credits, late-arriving records and contract amendments are out of scope.

| Dataset | Grain / primary key | Main relationships |
|---|---|---|
| customers.csv | customer_id | segment |
| products.csv | product_id | billing_model, unit_price_cents |
| contracts.csv | contract_id | customer_id, first and last billing month |
| contract_items.csv | item_id | contract_id, product_id, price and committed quantity |
| service_usage.csv | item_id + period | delivered quantity |
| invoice_items.csv | invoice_item_id | item_id + period, actual charge |
| journal_entries.csv | journal_id | invoice_item_id, period, recognized revenue |
| evaluation/ground_truth.csv | anomaly_id | item_id + period, defect and signed exposure |
| manifest.json | simulation run | seed, parameters, row counts |

Invoice items are a deliberately flattened billing extract; invoice headers and receivables follow in v0.2. Journal records are revenue-only extracts, not balanced double-entry journals.

## Expected billing
- Recurring charge = contracted quantity × negotiated unit price if delivery is active.
- Metered charge = delivered usage × negotiated unit price.
- V0.1 invoices and journal entries derive from billed amounts. A missing billing event produces no invoice or matching journal.
- Exposure = expected cents − actual cents. Positive means underbilling; negative means potential overbilling. Never offset one category against the other for reporting.
- The expected amount is reconstructed from contracts and usage by controls, never read from ground truth.

## Injected defects
Default per item-month probabilities are 1% missing billing, 2% underbilling (20% reduction, rounded down), and 0.5% overbilling (25% addition, rounded down). These are design assumptions, not estimates of real enterprise incidence. One defect at most per item-month. The remaining records are clean. All generated tariffs are positive and large enough for injected adjustments to be nonzero.

| ID | Mutation | Expected control |
|---|---|---|
| MISSING_BILLING | omit billing event | active/delivered item-month without invoice |
| UNDERBILLING | reduce actual charge | expected > actual on existing invoice |
| OVERBILLING | increase actual charge | expected < actual on existing invoice |

Each defect is labeled only in the restricted evaluation directory with correct expected amount, actual amount and signed exposure. The label file is not an ingestion source. Never use labels to tune or execute production-like detection; evaluate on held-out seeds and keep development/benchmark splits separate.

## Data quality
Validate unique primary keys, foreign keys, item-month uniqueness, period coverage, nonnegative money, and invoice-to-ledger agreement. Intentional defects are business failures, not structural corruption. Future scenarios include duplicate invoices, missed indexation, unauthorized discounts, posting-period shifts, cancellations and meter failures.

## Privacy
No real customer names, identifiers, documents, contracts, bank information or employer data. IDs are generated from counters. Dataset is reproducible by seed and configuration.
