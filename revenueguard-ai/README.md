# RevenueGuard AI
## Enterprise Finance Data Simulator & Revenue Assurance Lab

**Status: v0.1 — development / foundation.** Independent synthetic-data project. No employer data, infrastructure, claims of realized savings, or production deployment.

### Business problem
A fictional B2B technology provider sells recurring software licenses, managed support, and consumption-based cloud services. CRM, contracts, service fulfillment, billing and general ledger systems can disagree. Revenue assurance reconciles independent evidence and prioritizes exceptions for investigation.

### Objective
Build an auditable, reproducible financial control platform that detects revenue leakage, overbilling and reconciliation gaps; quantifies financial exposure; and uses AI to explain *verified* findings, not invent financial amounts.

### System design
```mermaid
flowchart LR
    C[CRM and contracts] --> E[Expected charges]
    U[Service delivery and usage] --> E
    P[Product and pricing catalog] --> E
    B[Billing system] --> R[Reconciliation controls]
    E --> R
    G[General ledger] --> R
    R --> M[Risk and evidence marts]
    M --> A[AI investigation agent - planned]
    M --> D[Dashboard - planned]
    A --> T[Telegram bot - planned]
    E -. simulator only .-> Q[Restricted ground truth]
    R --> V[Offline evaluation]
    Q --> V
```

### Current implementation
- Seeded Python generator using only the standard library; CSV output in a chosen local directory.
- Independent customer, product, contract, usage, invoice-item and simplified journal datasets.
- Three mutually exclusive injected billing defects: missing charge, underbilling and overbilling.
- Restricted evaluation labels and generation manifest.
- Integer minor-unit amounts (USD cents); deterministic output for fixed seed/configuration.
- No cloud account, credentials or paid service required for this version.

### Quick start
From the repository root, using Python 3.10+:

```bash
cd revenueguard-ai
python simulator.py --customers 100 --months 12 --seed 42 --output data/generated
python -m unittest discover -s tests -v
```

The generator writes data locally. Do not commit generated datasets or credentials. The full-scale target is 10,000 customers, 12,000 contracts, 25,000 items and approximately one million total rows; this is a roadmap target, not a measured result. The initial generator uses two items per contract and one contract per customer.

### Technical documentation
- [Data contract and financial rules](docs/data-model.md)
- [Architecture decisions and delivery roadmap](docs/roadmap.md)

### Planned technology
Python, Parquet, DuckDB, dbt Core, deterministic SQL controls, optional anomaly detection, AI evidence retrieval, Telegram Bot API and a read-only dashboard. Local-first development; optional free-tier hosting evaluated separately.

### Evaluation
Measure control precision, recall, financial exposure coverage, false-positive costs and investigation evidence quality. Ground truth is isolated from analytical and AI runtime inputs. No accuracy or business impact claims until benchmarks are executed and documented.

This project is a work in progress and is not financial advice or a production accounting system.
