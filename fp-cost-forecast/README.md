# FP Cost Forecast

## Evaluation contract

The demo now uses chronological rolling-origin evaluation: for each of the last
six target months, fit only on earlier observations (at least six months).
Linear regression uses up to twelve previous months. Baselines are the last
observed value and, with enough history, the same month of the previous year.
Each validation row records `train_end`, target month, model and horizon=1.

`forecast_metrics.json` compares models on their common target months and reports
available/evaluated coverage, MAE in BRL, signed bias (prediction minus actual)
and WAPE. A zero total actual makes WAPE undefined (`null`); per-row percentage
errors are blank for zero actuals. No training R² is presented as forecast quality.
The default 25-month run permits all three models; shorter runs can omit the
seasonal baseline. Seven months is the minimum for a run with a backtest.

Input grain is month × cost center, with complete center coverage and consecutive
month-start dates. Duplicates, blanks, missing periods, negative costs and
non-finite values fail explicitly. Negative costs/credits require a different
forecast input policy. Synthetic data are reproducible for a fixed configuration.

Future multi-month forecasts are exported separately from the measured one-step
backtest. No multi-step accuracy, prediction intervals or business savings are
claimed. Costs and statistical predictions use floating-point arithmetic; this
is not an accounting ledger. A model can lose to a simple baseline.

```bash
python -m pytest tests/test_it_cost_forecast.py
python fp-cost-forecast/notebooks/it_cost_forecast.py --months 36 --output-dir reports
```

A synthetic IT cost forecasting demo designed to show how FP&A planning teams can model IT spend and validate forecast accuracy.

## Problem

FP&A teams need a transparent, repeatable way to forecast IT costs and compare predicted spend against actuals for budgeting and cost control.

## Value delivered

- demonstrates a complete forecast workflow from synthetic cost generation to validation
- provides business-friendly CSV output for forecasting and error review
- helps showcase how a finance team can move from raw cost data to actionable planning insight

## What it includes

- synthetic monthly IT cost data for multiple cost centers
- monthly aggregation and feature preparation
- linear regression forecast with the last 12 months of history
- chronological out-of-sample comparisons, MAE, WAPE and signed bias
- local CSV output for forecast and validation results

## Stack

- Python
- pandas
- numpy
- scikit-learn

## Run locally

```bash
python fp-cost-forecast/notebooks/it_cost_forecast.py
```

Open the notebook version for a more interactive walkthrough:

- `fp-cost-forecast/notebooks/it_cost_forecast.ipynb`

## Output

- `reports/forecast_result.csv`
- `reports/forecast_validation.csv`
- `reports/forecast_metrics.json`

> The `reports/` folder is ignored by Git and is used only for local demo outputs.

## Data confidentiality

All data in this project is synthetic and fictional. **No real Bradesco data is used or shared.**
