# Architecture decisions and roadmap

## Design principles
1. Financial calculations are deterministic and use minor units. An LLM may explain and retrieve evidence, never act as the source of monetary truth.
2. Preserve source grain, stable business keys, provenance and explicit reconciliation rules. No silent correction of raw records.
3. Local-first and zero-service-cost baseline. Avoid cloud dependency until the core simulation and controls are validated.
4. Separate runtime evidence from offline truth labels. Public portfolio uses synthetic data only.
5. Read-only AI tools; allowlisted queries, bounded results, no credentials in source control, human approval for proposed remediation.

## Milestones
| Stage | Deliverable | Exit gate |
|---|---|---|
| v0.1 | Seeded source simulator, three anomaly types, data contract | Reproducible records; smoke tests pass locally |
| v0.2 | Parquet, DuckDB, expanded lifecycle and dbt staging/models | Keys, amount and reconciliation tests pass |
| v0.3 | Financial rules, exposure marts, offline benchmark | Report precision, recall and exposure coverage on held-out seeds |
| v0.4 | Evidence-backed AI agent, skill interfaces, cost guardrails | Grounded answers and abstention evaluated; no truth access |
| v0.5 | Dashboard and authenticated Telegram bot | Demo validated, authorization and limits tested |
| v1.0 | Public portfolio case study | Reproducible run, documented limitations and verified results |

## Benchmark plan
Join detections to truth at item-period grain. Report true/false positives, recall and precision by defect type. Report underbilling and overbilling separately, exposure coverage by category, and amount error. Compare deterministic controls with optional ML on a separate noise scenario. For AI measure unsupported claims, evidence citations, latency and token/cost per investigation. No synthetic recovery is presented as realized revenue.

## Open decisions
- Extend contract/line cardinality and churn before scaling to the target million rows.
- Add realistic correlated defects, amendments, effective dates and invoice lifecycle.
- Choose hosting only after profiling local runtime; free hosted APIs have quotas and terms that may change.
- Keep the website landing page unchanged during development; feature the case only when validated.
