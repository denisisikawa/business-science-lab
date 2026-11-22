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
