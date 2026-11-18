# Macro context for FP&A

A monthly report that combines a synthetic cost and budget series with Brazilian exchange rates and inflation. It lets a reviewer inspect budget variance, an indicative USD view and actual costs in constant BRL side by side.

## Implementation plan

1. Use two public, credential-free sources with monthly grain and document the series and units.
2. Retrieve the requested window in Python. Validate uniqueness, contiguous cost months and match coverage before writing the CSV.
3. Calculate budget variance, USD equivalents and inflation-adjusted actual costs. Supply mocked API responses for reproducible review.
4. Add an executive view and a technical view to the bilingual portfolio, then validate the report and page.

## Sources

| Provider | Series | Unit | Role |
| --- | --- | --- | --- |
| [Banco Central do Brasil, SGS](https://www3.bcb.gov.br/sgspub/) | 3696, USD selling rate, monthly average | BRL per USD | Approximate USD equivalent for monthly costs |
| [IBGE SIDRA](https://sidra.ibge.gov.br/tabela/1737) | Table 1737, variable 63, national IPCA monthly change | Percent | Convert nominal costs to first-month prices |

The input CSV contains one synthetic row per month. Both sources are joined to that month. A month can be over while its IPCA release is still pending. Use a window covered by both providers. Source revisions may change results across live reruns.

## Run

Python 3.11+, standard library only. From the repository root:

```bash
# Public API mode
python macro-fpa/report.py --costs macro-fpa/example/costs.csv --output macro-report.csv

# Reproducible mode using simulated API responses
python macro-fpa/report.py --costs macro-fpa/example/costs.csv --fixtures macro-fpa/fixtures --output macro-report.csv

python -m unittest discover -s macro-fpa -p "test_*.py"
```

The program retries transient network errors, fails on missing or duplicate months, and replaces the output only after validation and a complete write. Store reports from the two modes under distinct filenames when comparing them.

## Read the report

- **Budget variance** is actual minus budget. A positive value means spending above budget.
- **Indicative USD** is BRL actual divided by the monthly average FX rate. This estimates a reporting equivalent. Transaction settlement and hedging require their own rates.
- **Constant BRL** is actual divided by the compounded IPCA index, with the first month set to 1. The index compounds from the second month through each reported month. IPCA is a consumer price index used here as a proxy for the purchasing power of these costs.

In the simulated March 2025 row, BRL 105,000 actual versus BRL 106,000 budget gives a BRL 1,000 underspend. At 5.25 BRL per USD, the indicative equivalent is USD 20,000. Two months of 1% simulated inflation put actual costs at BRL 102,931.09 in January prices.

The lab runs locally in Python. The repository's dbt/DuckDB lab and Databricks reference pipeline have their own execution paths.
