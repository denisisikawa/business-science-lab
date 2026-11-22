import importlib.util
import os
import sys
import json
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "fp-cost-forecast" / "notebooks" / "it_cost_forecast.py"

spec = importlib.util.spec_from_file_location("it_cost_forecast", SCRIPT_PATH)
it_cost_forecast = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = it_cost_forecast
spec.loader.exec_module(it_cost_forecast)


def test_generate_synthetic_data_shape():
    df = it_cost_forecast.generate_synthetic_data(history_months=12)
    assert len(df) == 12 * 5
    assert set(df.columns) == {"month", "cost_center", "amount"}


def test_build_monthly_summary_pandas_columns():
    df = it_cost_forecast.generate_synthetic_data(history_months=6)
    summary = it_cost_forecast.build_monthly_summary_pandas(df)
    assert set(summary.columns) == {"month", "total_cost", "num_centers"}
    assert len(summary) == 6


def test_run_forecast_outputs(tmp_path):
    output = it_cost_forecast.run_forecast(
        output_dir=str(tmp_path), history_months=12, forecast_horizon=3
    )
    assert os.path.exists(output["forecast_csv"])
    assert os.path.exists(output["validation_csv"])
    assert {r['model'] for r in output['metrics']} == {'linear_regression', 'last_value'}
    assert output["history_months"] == 12
    assert output["forecast_horizon"] == 3


def test_future_observations_cannot_change_earlier_predictions():
    monthly = it_cost_forecast.build_monthly_summary_pandas(it_cost_forecast.generate_synthetic_data(25))
    before = it_cost_forecast.backtest(monthly)
    monthly.loc[24, 'total_cost'] *= 100
    after = it_cost_forecast.backtest(monthly)
    pd.testing.assert_series_equal(before['predicted'], after['predicted'])
    assert (before['train_end'] < before['month']).all()


def test_baselines_and_zero_denominator():
    monthly = pd.DataFrame({'month': pd.date_range('2023-01-01', periods=25, freq='MS'),
                            'total_cost': np.zeros(25)})
    rows = it_cost_forecast.backtest(monthly)
    assert set(rows['model']) == set(it_cost_forecast.MODELS)
    assert rows['error_pct'].isna().all()
    for row in it_cost_forecast.metrics(rows):
        assert row['mae_brl'] == 0 and row['bias_brl'] == 0 and row['wape_pct'] is None


def test_seasonal_baseline_uses_only_previous_year():
    assert list(it_cost_forecast.predict(range(1, 25), 3, 'seasonal_naive')) == [13, 14, 15]
    assert it_cost_forecast.predict(range(11), 1, 'seasonal_naive') is None


@pytest.mark.parametrize('mutation', ['duplicate', 'gap', 'missing_center', 'nan', 'inf', 'negative', 'midmonth', 'blank'])
def test_invalid_financial_inputs(mutation):
    data = it_cost_forecast.generate_synthetic_data(12)
    if mutation == 'duplicate': data = pd.concat([data, data.iloc[[0]]])
    elif mutation == 'gap': data = data[data['month'] != data.iloc[5]['month']]
    elif mutation == 'missing_center': data = data.drop(index=0)
    elif mutation in ('nan', 'inf', 'negative'): data.loc[0, 'amount'] = {'nan': np.nan, 'inf': np.inf, 'negative': -1}[mutation]
    elif mutation == 'midmonth': data.loc[0, 'month'] += pd.Timedelta(days=1)
    elif mutation == 'blank': data.loc[0, 'cost_center'] = ' '
    with pytest.raises(ValueError): it_cost_forecast.build_monthly_summary_pandas(data)


def test_metrics_coverage_and_reproducibility(tmp_path):
    a = it_cost_forecast.run_forecast(tmp_path / 'a', 25, 3)
    b = it_cost_forecast.run_forecast(tmp_path / 'b', 25, 3)
    assert a['metrics'] == b['metrics']
    for name in ('forecast_result.csv', 'forecast_validation.csv', 'forecast_metrics.json'):
        assert (tmp_path / 'a' / name).read_bytes() == (tmp_path / 'b' / name).read_bytes()
    report = json.loads((tmp_path / 'a/forecast_metrics.json').read_text())
    assert all(r['evaluated_months'] == 6 for r in report['metrics'])


@pytest.mark.parametrize('months,horizon', [(6, 3), (0, 3), (25, 0), (25, 37), (True, 3)])
def test_invalid_run_configuration(tmp_path, months, horizon):
    with pytest.raises(ValueError): it_cost_forecast.run_forecast(tmp_path, months, horizon)
