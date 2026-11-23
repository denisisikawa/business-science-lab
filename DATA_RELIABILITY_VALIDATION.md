# Data reliability corrections — 2026-11-22

All financial inputs and results below are synthetic. No live Databricks workspace,
JDBC source or Genie space was used. This is evidence for the documented demo
scope, not a production certification or employer result.

## Forecast

`python -m pytest tests/test_it_cost_forecast.py`: 20 tests passed locally.
Tests cover temporal separation, baseline behavior, data coverage, malformed
inputs, zero denominators and reproducibility. Changing the last actual does not
change any earlier/current one-step prediction because it is never in its training
window. A separate 36-month demonstration regenerates the committed charts/CSVs.

For that synthetic run (six common one-step target months):

| Model | MAE BRL | Signed bias BRL | WAPE |
| --- | ---: | ---: | ---: |
| Last value | 53,220.55 | 14,790.96 | 3.23% |
| Linear regression | 161,857.49 | 138,775.26 | 9.82% |
| Seasonal naive | 93,183.83 | -93,183.83 | 5.65% |

These are fixture-specific measurements, not a ranking on real financial data.
Future six-month projections are not a measured six-month backtest. Full numeric
outputs are in images/forecast_metrics.json; no accuracy benefit is asserted.

## Pipeline

`python -m pytest tests/test_pipeline_contract.py`: 13 tests passed locally.
The local CSV example produces 5 input rows: 3 accepted, 1 rejected (unsupported
currency), 1 duplicate. Known BRL input amounts reconcile as 28,975 = 18,975 +
10,000 cents; the USD row is retained but excluded from BRL sums and marked as an
unknown BRL amount. Repeating the same command returns replayed=true without duplicating
current facts. Tests cover credits, late versions, source identity, conflicts and
atomic rollback. SQLite validates the small reference contract, not Delta I/O.

tests/test_pipeline_spark.py is an opt-in Spark transformation/parity test. The
Data Reliability workflow supplies Java 17 and Spark 3.5. Local execution skipped
this test because that runtime was not configured. Check the workflow result for
this revision before claiming a successful Spark execution. Delta MERGE, JDBC and
workspace permissions remain unverified even if the transformation test passes.

## Finance queries / Genie

`python -m pytest tests/test_genie_query_handler.py`: 26 tests passed locally.
Local totals for June 2024 (46,000,000 cents) and May 2025 (54,800,000 cents)
reconcile with the synthetic category records. Unsupported, ambiguous and missing
periods return no invented amount. HTTP shape, polling, failures, timeouts and
attachment retrieval use mocked responses. No live Genie answer is marked verified.

## Whole repository and documentation

`python -m pytest -q`: 72 passed, 1 optional Spark test skipped locally.
pytest.ini supplies the existing RevenueGuard import path for root-level test
discovery. No RevenueGuard business logic was changed.

The HTML semantic/translation checker passed: eight project cards, 308 translated
elements, twelve internal anchors. The extracted page JavaScript passed Node's
syntax check. Notebook launch cells use the adjacent tested scripts and clear old
outputs; scripts/sync_demo_notebooks.py maintains this relationship.

Local validation environment: Python 3.11, pandas 3.1.1, NumPy 2.4.6,
scikit-learn 1.9.1, requests 2.34.2 and pytest 9.2.0. Dependency ranges remain in
requirements.txt; the version list records this run rather than promising every
possible dependency combination was tested.

## dbt FP&A reconciliation — 2026-11-23

A new singular test reconciles staging to the monthly mart at month × cost center
× category grain using exact Decimal BRL sums and transaction counts. Full outer
join coverage detects missing and unexpected groups as well as mismatched or null
measures. Existing uniqueness/required-value tests remain complementary.

Local validation with Python 3.11, dbt-core 1.12.7, dbt-duckdb 1.11.1 and DuckDB
2.0.1: `dbt build --profiles-dir .` completed 18 nodes (one seed, two models and
15 data tests), with no errors or skips. The input remains 18 synthetic rows.
`python scripts/check_reconciliation_mutations.py` from dbt-finance-lab passed:
the unmodified build reconciled, all seven injected corruptions were detected,
and the baseline remained unchanged. Cases: missing group, unexpected group,
one-cent difference, wrong count, null amount, null count and offsetting errors
with unchanged grand total. Mutations run in isolated in-memory tables; the
original DuckDB file is attached read-only.

Root regression: 72 pytest tests passed, one optional Spark test skipped locally;
`node macro-fpa/synthetic-banking/test-cost-impact.cjs` passed 576 comparisons and
simulation checks. CI now runs the mutation check after dbt build; consult the
workflow result for this revision separately. No Databricks, JDBC, Genie or Power
BI execution is implied. RevenueGuard is not incorporated into this dbt project.
