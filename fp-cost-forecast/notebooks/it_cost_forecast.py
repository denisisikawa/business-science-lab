"""Synthetic forecast; chronological rolling-origin one-step evaluation."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

REPORT_DIR = Path(__file__).resolve().parents[2] / "reports"
MIN_TRAIN = 6
MODELS = ("linear_regression", "last_value", "seasonal_naive")

def positive_integer(value, name, maximum=120):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise ValueError(f"{name} must be an integer from 1 to {maximum}")

def generate_synthetic_data(history_months=25):
    positive_integer(history_months, "history_months")
    rng = np.random.default_rng(42)
    rows = []
    for i, month in enumerate(pd.date_range(end="2025-01-01", periods=history_months, freq="MS")):
        for center in range(1, 6):
            amount = 100000 * center * (1 + .08 * np.sin(2 * np.pi * i / 12))
            amount *= (1 + .005 * i) * (1 + rng.normal(0, .03))
            rows.append({"month": month, "cost_center": f"CC-{center:02d}", "amount": round(amount, 2)})
    return pd.DataFrame(rows)

def build_monthly_summary_pandas(df):
    required = ["month", "cost_center", "amount"]
    if not set(required).issubset(df.columns) or df.empty:
        raise ValueError("Nonempty data with month, cost_center and amount is required")
    data = df[required].copy()
    data["month"] = pd.to_datetime(data["month"], errors="raise")
    if data["month"].isna().any() or data["month"].dt.tz is not None:
        raise ValueError("Months must be non-null timezone-naive dates")
    if not data["month"].eq(data["month"].dt.to_period("M").dt.to_timestamp()).all():
        raise ValueError("month must be the first day of the month at midnight")
    if not data["cost_center"].map(lambda x: isinstance(x, str) and bool(x.strip())).all():
        raise ValueError("Nonempty cost centers are required")
    data["cost_center"] = data["cost_center"].str.strip()
    data["amount"] = pd.to_numeric(data["amount"], errors="raise")
    if not np.isfinite(data["amount"]).all() or (data["amount"] < 0).any():
        raise ValueError("Amounts must be finite and nonnegative")
    if data.duplicated(["month", "cost_center"]).any():
        raise ValueError("Expected one observation per month and cost center")
    monthly = data.groupby("month", as_index=False).agg(
        total_cost=("amount", "sum"), num_centers=("cost_center", "nunique")).sort_values("month")
    expected = pd.date_range(monthly["month"].min(), monthly["month"].max(), freq="MS")
    if list(monthly["month"]) != list(expected):
        raise ValueError("Missing calendar months")
    centers = set(data["cost_center"])
    if any(set(g["cost_center"]) != centers for _, g in data.groupby("month")):
        raise ValueError("Incomplete cost-center coverage")
    return monthly.reset_index(drop=True)

def predict(history, horizon, model):
    """Only pass observations available at the forecast origin."""
    values = np.asarray(history, dtype=float)
    if model == "last_value":
        return np.repeat(values[-1], horizon)
    if model == "seasonal_naive":
        if len(values) < 12:
            return None
        return np.array([values[-12 + (step % 12)] for step in range(horizon)])
    if model != "linear_regression":
        raise ValueError("Unknown model")
    train = values[-12:]
    estimator = LinearRegression().fit(np.arange(len(train)).reshape(-1, 1), train)
    return estimator.predict(np.arange(len(train), len(train) + horizon).reshape(-1, 1))

def backtest(monthly, validation_months=6):
    positive_integer(validation_months, "validation_months")
    if len(monthly) <= MIN_TRAIN:
        raise ValueError(f"Need at least {MIN_TRAIN + 1} months for out-of-sample evaluation")
    rows = []
    for target in range(max(MIN_TRAIN, len(monthly) - validation_months), len(monthly)):
        history = monthly["total_cost"].iloc[:target].to_numpy()
        actual = float(monthly["total_cost"].iloc[target])
        for model in MODELS:
            prediction = predict(history, 1, model)
            if prediction is None:
                continue
            predicted = float(prediction[0])
            rows.append({"month": monthly["month"].iloc[target], "model": model,
                         "train_end": monthly["month"].iloc[target - 1], "horizon": 1,
                         "actual": actual, "predicted": predicted, "error_brl": predicted - actual,
                         "error_pct": (predicted - actual) / actual * 100 if actual else None})
    return pd.DataFrame(rows)

def metrics(validation):
    """Compare all available models on the same target months; expose coverage."""
    common = set.intersection(*(set(g["month"]) for _, g in validation.groupby("model")))
    rows = []
    for model, all_rows in validation.groupby("model"):
        group = all_rows[all_rows["month"].isin(common)]
        errors = group["predicted"] - group["actual"]
        denominator = group["actual"].abs().sum()
        rows.append({"model": model, "evaluated_months": len(group),
                     "available_months": int(all_rows["month"].nunique()),
                     "mae_brl": float(errors.abs().mean()), "bias_brl": float(errors.mean()),
                     "wape_pct": float(errors.abs().sum() / denominator * 100) if denominator else None})
    return rows

def run_forecast(output_dir=None, history_months=25, forecast_horizon=3):
    positive_integer(history_months, "history_months")
    positive_integer(forecast_horizon, "forecast_horizon", 36)
    if history_months < MIN_TRAIN + 1:
        raise ValueError(f"history_months must be at least {MIN_TRAIN + 1}")
    monthly = build_monthly_summary_pandas(generate_synthetic_data(history_months))
    validation = backtest(monthly)
    future = pd.date_range(monthly["month"].iloc[-1] + pd.offsets.MonthBegin(),
                           periods=forecast_horizon, freq="MS")
    rows = [{"month": r.month, "cost": r.total_cost, "type": "actual", "model": "observed"}
            for r in monthly.itertuples()]
    for model in MODELS:
        predictions = predict(monthly["total_cost"], forecast_horizon, model)
        if predictions is not None:
            rows.extend({"month": m, "cost": float(v), "type": "forecast", "model": model}
                        for m, v in zip(future, predictions))
    output = Path(output_dir) if output_dir is not None else REPORT_DIR
    output.mkdir(parents=True, exist_ok=True)
    result_path, validation_path = output / "forecast_result.csv", output / "forecast_validation.csv"
    pd.DataFrame(rows).to_csv(result_path, index=False, date_format="%Y-%m-%d")
    validation.to_csv(validation_path, index=False, date_format="%Y-%m-%d")
    comparison = metrics(validation)
    (output / "forecast_metrics.json").write_text(json.dumps({
        "data_scope": "synthetic", "evaluation": "rolling_origin_one_step",
        "error_sign": "prediction_minus_actual", "metrics": comparison,
        "future_horizon": forecast_horizon,
        "limitations": "Future multi-step forecasts have no measured multi-step accuracy."
    }, indent=2, allow_nan=False), encoding="utf-8")
    return {"forecast_csv": str(result_path), "validation_csv": str(validation_path),
            "metrics": comparison, "history_months": history_months, "forecast_horizon": forecast_horizon}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(REPORT_DIR))
    parser.add_argument("--months", type=int, default=25)
    parser.add_argument("--forecast-horizon", type=int, default=3)
    args = parser.parse_args(argv)
    print(json.dumps(run_forecast(args.output_dir, args.months, args.forecast_horizon), indent=2))

if __name__ == "__main__":
    main()
