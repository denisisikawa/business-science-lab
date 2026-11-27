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

## Runtime input boundary

Before reconciliation, the sandbox validates only `products`, `contract_items`,
`service_usage` and `invoice_items`, the datasets actually consumed by this
expected-versus-billed control:

| Input | Required uniqueness | Additional checks |
|---|---|---|
| Products | product_id | Name/model present; model recurring or metered; positive integer catalog tariff |
| Contract items | item_id | Contract ID present; known product; positive integer price and committed quantity |
| Usage | item_id × period | Known item; valid YYYY-MM; nonnegative integer delivered quantity |
| Invoice items | invoice_item_id AND item_id × period | Known item; matching usage evidence; nonnegative integer billed cents |

All required attributes must be nonblank. Identity/reference fields must not
contain surrounding whitespace. Required/matching CSV headers must exist even
for an empty file; duplicate headers, missing row values or extra row cells fail.
Additional named columns are permitted but do not become business rules.

Errors identify dataset, row position and reason without echoing raw payloads.
Input validation rejects structural corruption; it does not deduplicate it using
an arbitrary winner. Reconciliation produces no returned result on such failure.
There is no persistent quarantine/audit implementation in this sandbox.

A missing invoice is a legitimate MISSING_BILLING finding, not a schema error.
An existing invoice billed at zero is valid input and may produce UNDERBILLING.
An invoice without service-usage evidence raises an explicit input error instead
of disappearing from totals. Multiple invoices per item-period are unsupported
by this flattened model, even if they might be legitimate in another billing
system; supporting them needs a different grain and aggregation policy.

Contract/customer references and validity dates are not validated here, nor is
journal agreement. The manifest's currency is a synthetic scenario declaration,
not a multi-currency parser. No source completeness or freshness is inferred from
the rows received. Ground truth remains evaluation-only and is not read by the
billing detector.

Tests deliberately corrupt keys, references, periods, numeric domains, attributes
and CSV shape, preserve the missing/zero-billing business cases, and check equality
of local and browser-embedded Python source. This source parity check is not a
fresh execution of Pyodide or a production browser integration test.
