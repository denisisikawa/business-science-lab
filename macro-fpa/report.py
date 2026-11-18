"""Build a monthly FP&A context report from public macro data and synthetic costs."""

import argparse
import csv
import json
import os
import sys
import tempfile
from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal, DecimalException
from pathlib import Path
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

FX_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.3696/dados"
IPCA_URL = "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/63/p"
FIELDS = (
    "month", "actual_brl", "budget_brl", "variance_brl", "usd_brl_avg",
    "ipca_month_pct", "actual_usd", "actual_brl_in_first_month_prices",
)


def month_start(value):
    if len(value) != 7:
        raise ValueError(f"Expected YYYY-MM, got {value!r}")
    return date.fromisoformat(value + "-01")


def number(value):
    result = Decimal(value)
    if not result.is_finite():
        raise ValueError(f"Non-finite value: {value!r}")
    return result


def fetch(url):
    for attempt in range(3):
        try:
            with urlopen(url, timeout=15) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        sleep(2 ** attempt)


def read_costs(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not {"month", "actual_brl", "budget_brl"}.issubset(reader.fieldnames or []):
            raise ValueError("Costs CSV requires month, actual_brl and budget_brl")
        costs = {}
        for row in reader:
            month = month_start(row["month"])
            actual, budget = number(row["actual_brl"]), number(row["budget_brl"])
            if month in costs or min(actual, budget) < 0:
                raise ValueError(f"Duplicate month or negative cost: {month:%Y-%m}")
            costs[month] = actual, budget
    months = sorted(costs)
    if not months:
        raise ValueError("Costs CSV has no observations")
    span = (months[-1].year - months[0].year) * 12 + months[-1].month - months[0].month + 1
    if span != len(months) or span > 120:
        raise ValueError("Costs must contain 1–120 consecutive months")
    if months[-1] >= date.today().replace(day=1):
        raise ValueError("Report accepts completed calendar months only")
    return {month: costs[month] for month in months}


def read_fx(payload):
    if not isinstance(payload, list):
        raise ValueError("Unexpected BCB response")
    result = {}
    for row in payload:
        month = datetime.strptime(row["data"], "%d/%m/%Y").date().replace(day=1)
        value = number(row["valor"])
        if month in result or value <= 0:
            raise ValueError(f"Duplicate month or invalid FX: {month:%Y-%m}")
        result[month] = value
    return result


def read_ipca(payload):
    if not isinstance(payload, list) or not payload or payload[0].get("V") != "Valor":
        raise ValueError("Unexpected IBGE response")
    month_fields = [key for key, label in payload[0].items()
                    if key.endswith("C") and label.casefold() == "mês (código)"]
    if len(month_fields) != 1:
        raise ValueError("Expected one SIDRA month column")
    result = {}
    for row in payload[1:]:
        period = row[month_fields[0]]
        if len(period) != 6 or not period.isascii() or not period.isdecimal():
            raise ValueError(f"Invalid SIDRA month: {period!r}")
        month = month_start(period[:4] + "-" + period[4:])
        value = number(row["V"])
        if month in result or value <= -100:
            raise ValueError(f"Duplicate month or invalid IPCA: {month:%Y-%m}")
        result[month] = value
    return result


def build_report(costs, fx, ipca):
    rows = []
    price_index = Decimal(1)
    for month, (actual, budget) in sorted(costs.items()):
        missing = [source for source, values in (("BCB FX", fx), ("IBGE IPCA", ipca))
                   if month not in values]
        if missing:
            raise ValueError(f"Missing {', '.join(missing)} for {month:%Y-%m}")
        if rows:
            price_index *= 1 + ipca[month] / 100
        rows.append((
            month.strftime("%Y-%m"), f"{actual:.2f}", f"{budget:.2f}",
            f"{actual - budget:.2f}", format(fx[month], "f"), format(ipca[month], "f"),
            f"{actual / fx[month]:.2f}", f"{actual / price_index:.2f}",
        ))
    return rows


def write_report(path, rows):
    # Replace only once validation and the entire CSV write succeed.
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False
        ) as file:
            temporary_path = Path(file.name)
            writer = csv.writer(file)
            writer.writerow(FIELDS)
            writer.writerows(rows)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--costs", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fixtures", type=Path, help="Directory with mocked fx.json and ipca.json")
    args = parser.parse_args()
    try:
        if args.costs.resolve() == args.output.resolve():
            raise ValueError("Output must be different from the input costs file")
        costs = read_costs(args.costs)
        start, end = min(costs), max(costs)
        last_day = end.replace(day=monthrange(end.year, end.month)[1])
        query = urlencode({
            "formato": "json", "dataInicial": start.strftime("%d/%m/%Y"),
            "dataFinal": last_day.strftime("%d/%m/%Y"),
        })
        if args.fixtures:
            fx = json.loads((args.fixtures / "fx.json").read_text(encoding="utf-8"))
            ipca = json.loads((args.fixtures / "ipca.json").read_text(encoding="utf-8"))
        else:
            fx = fetch(f"{FX_URL}?{query}")
            period = f"{start:%Y%m}" if start == end else f"{start:%Y%m}-{end:%Y%m}"
            ipca = fetch(f"{IPCA_URL}/{period}")
        rows = build_report(costs, read_fx(fx), read_ipca(ipca))
        write_report(args.output, rows)
    except (OSError, ValueError, DecimalException, KeyError, TypeError, AttributeError) as error:
        print(f"Report failed: {error}", file=sys.stderr)
        return 1
    mode = "mocked API fixtures" if args.fixtures else "BCB SGS and IBGE SIDRA"
    print(f"Wrote {len(rows)} months to {args.output} ({mode}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
