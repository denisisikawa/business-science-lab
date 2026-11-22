# AI Agent FP&A Query

## Execution modes and limits

**Local (default):** deterministic, parameterized SQLite queries over 48 synthetic
monthly category facts (June 2024–May 2025). This mode is a scoped query handler,
not an LLM or a live Genie deployment. It accepts only the documented question
templates with explicit YYYY-MM periods:

- `total IT cost for 2025-05` / `custo total de TI em 2025-05`
- `costs by category for 2025-05` / `custos por categoria em 2025-05`

Answers contain exact BRL cents, the query template, parameters, period, source
and dataset fingerprint. Ambiguous periods request clarification; missing periods
return no_data; other requests are unsupported and receive no invented amounts.
The local database is read-only while querying, and user input is never executed
as SQL. These controls apply to this small local scope, not arbitrary questions.

```bash
python ai-agent-fpa-query/notebooks/genie_query_handler.py --mode local --question "total IT cost for 2025-05"
python -m pytest tests/test_genie_query_handler.py
```

**Live Genie (explicit opt-in):** set DATABRICKS_HOST, DATABRICKS_TOKEN and
GENIE_SPACE_ID privately, then pass `--mode genie`. Missing configuration, HTTP
errors, failed/cancelled/expired messages and polling exhaustion fail explicitly;
there is no switch to synthetic answers. The adapter starts a conversation,
polls its message and retrieves query attachment results. HTTP timeouts and poll
counts are bounded. Redirects are not followed. No credentials are written to logs.

The endpoint flow was checked against the [official conversation API](https://docs.databricks.com/api/genie/v1/conversation).
Transport behavior is tested with mocks, not a Databricks workspace. Live replies
are marked completed_unverified / verified=false, including provider SQL and
results. The application does not execute that SQL itself or independently
reconcile provider values. It does not install a system prompt or enforce
workspace privileges: configure and test a least-privilege principal, approved
tables and Genie instructions in Databricks before any live use. Multi-user
authorization and a governed production deployment are not implemented.

Audit JSON Lines contains mode, status, verification, dataset fingerprint and
question hash; raw prompts, responses, SQL and tokens are omitted by default.
It is a local audit pattern, not a tamper-proof centralized audit service.

A portfolio demonstration of how AI agents can enable self-service analytics for finance teams.

## Problem

FP&A analysts often spend time waiting for data teams to answer cost and spend questions. This slows decision-making and increases ad hoc reporting workload.

## Value delivered

- shows how a natural-language query workflow can speed FP&A access to insights
- demonstrates a narrow question allowlist and exact local query results
- includes an explicit synthetic local mode independent of credentials
- provides an audit logging pattern to track and review AI query responses

## What it includes

- example Genie API wrapper for submitting natural-language questions
- computed synthetic local answers; no automatic fallback from live mode
- documented configuration boundary for Genie permissions and instructions
- logging and auditing pattern for query handling
- sample synthetic report generation for demo purposes

## Stack

- Python
- requests
- Databricks Genie API patterns
- SQL analytics patterns

## How to explore

Open the notebook:

- `ai-agent-fpa-query/notebooks/genie_query_handler.ipynb`

Run the script locally to see the demo flow and synthetic answer behavior:

```bash
python ai-agent-fpa-query/notebooks/genie_query_handler.py
```

## Data confidentiality

This example is intentionally synthetic. **No real Bradesco data or sensitive analytics are stored or shared.** It demonstrates architecture and interaction patterns only.

> The local demo uses synthetic answers and does not require Databricks credentials.
