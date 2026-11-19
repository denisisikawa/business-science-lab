"""One-time remote check for the official report and existing Pages deployment."""

import csv
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from urllib.request import urlopen

LAB = Path(__file__).resolve().parent


def test_live_apis_match_official_tables(tmp_path):
    output = tmp_path / "live.csv"
    run = subprocess.run(
        [sys.executable, str(LAB / "report.py"), "--costs", str(LAB / "example/costs.csv"),
         "--output", str(output)],
        capture_output=True, text=True, timeout=100,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    with output.open(newline="") as file:
        rows = list(csv.DictReader(file))
    expected = [("2025-01", "6.0218", "0.16"), ("2025-02", "5.7656", "1.31"), ("2025-03", "5.7468", "0.56")]
    assert [(row["month"], str(Decimal(row["usd_brl_avg"]).quantize(Decimal("0.0001"))),
             str(Decimal(row["ipca_month_pct"]).quantize(Decimal("0.01")))) for row in rows] == expected


def test_public_pages_reaches_architecture_section():
    with urlopen("https://denisisikawa.github.io/denis-isikawa-databricks/", timeout=15) as response:
        html = response.read().decode("utf-8")
    assert 'id="macro-executive"' in html and 'id="macro-technical"' in html
