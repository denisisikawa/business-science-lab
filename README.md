<div align="center">

<img src="assets/hero.svg" width="100%" alt="Denis Isikawa — Finance Systems, Data Platforms and Analytics Engineering" />

<br/>

**Business Science Lab · Business Science with Data & AI**

I use data and AI to explain cost variances, identify revenue leakage, and support financial planning decisions.

[**Explore the work ↓**](#featured-projects) &nbsp;·&nbsp; [**Architecture ↓**](https://denisisikawa.github.io/business-science-lab/#macro-fpa) &nbsp;·&nbsp; [**Connect on LinkedIn ↗**](https://www.linkedin.com/in/denisisikawa)

<br/>

[![Python CI](https://github.com/denisisikawa/business-science-lab/actions/workflows/python-ci.yml/badge.svg)](https://github.com/denisisikawa/business-science-lab/actions/workflows/python-ci.yml)
[![dbt Finance CI](https://github.com/denisisikawa/business-science-lab/actions/workflows/dbt-finance-ci.yml/badge.svg)](https://github.com/denisisikawa/business-science-lab/actions/workflows/dbt-finance-ci.yml)
[![Portfolio data scope](https://img.shields.io/badge/Data-Synthetic%20%2B%20public-56DCC5?style=flat-square&labelColor=122235)](#data-ethics--scope)

</div>

---

## Hi, I'm Denis.

**17+ years across finance, revenue systems, operations and data.** Currently a **Senior BI Analyst III** at Bradesco, working in the capacity of **FP&A Data & Analytics Technical Lead**, providing technical direction and cross-functional alignment for an **8-person team**.

I have built my career at the intersection of **financial controls and technology**: telecom billing and mediation systems, revenue assurance, management information systems, financial analytics, and end-to-end FP&A automation.

What interests me most is not a dashboard by itself. It's the system behind it: **trusted data, clear ownership, sound architecture and decisions people can defend.**

| Perspective | Where I focus |
| :-- | :-- |
| **Finance + Revenue** | FP&A, financial close, revenue assurance, billing, cost analysis |
| **Data platforms** | Databricks, PySpark, Python, SQL, Delta Lake patterns |
| **Analytics + automation** | Power BI, PowerApps, financial workflows and process controls |
| **Architecture + leadership** | Quality, governance, integration design, technical direction |
| **Learning in public** | dbt Analytics Engineering and Databricks certification preparation |

> **Career direction:** Finance Data Architecture · Finance Systems / EPM · Revenue Systems Transformation · Enterprise Analytics. I favor specialist and architecture-focused roles that combine technical depth with business outcomes.

---

## Featured projects

Four core projects use **synthetic financial records** and run independently of any employer environment.

<table>
<tr>
<td width="50%" valign="top">
  <a href="dbt-finance-lab/README.md"><img width="100%" src="assets/cards/dbt.svg" alt="dbt Finance Lab project art"></a>
  <h3>01 — Finance Analytics Engineering</h3>
  <p><b>dbt · DuckDB · SQL · data tests</b></p>
  <p>Models synthetic finance costs into a documented staging and monthly mart layer, with automated checks for grain, completeness and business constraints.</p>
  <p><b>Evidence:</b> reproducible local project + GitHub Actions dbt build.</p>
  <p><a href="dbt-finance-lab/README.md"><b>Explore project →</b></a></p>
</td>
<td width="50%" valign="top">
  <a href="databricks-pipeline-template/README.md"><img width="100%" src="assets/cards/pipeline.svg" alt="Delta Lake Pipeline project art"></a>
  <h3>02 — Lakehouse Finance Pipeline</h3>
  <p><b>Databricks · PySpark · Delta Lake</b></p>
  <p>A financial ingestion contract with a tested local SQLite acceptance backend, a Spark/Delta adapter, and versioned Genie Code skills for business-rule evolution, maintenance and release review.</p>
  <p><b>Scope:</b> reference architecture / demonstration, not a production deployment.</p>
  <p><a href="databricks-pipeline-template/README.md"><b>Explore project →</b></a></p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
  <a href="fp-cost-forecast/README.md"><img width="100%" src="assets/cards/forecast.svg" alt="FP&A Forecasting project art"></a>
  <h3>03 — Predictive Cost Forecasting</h3>
  <p><b>Python · pandas · scikit-learn</b></p>
  <p>Evaluates synthetic cost forecasts outside training periods against simple baselines, reporting MAE, WAPE, bias and coverage.</p>
  <p><b>Evidence:</b> executable local demo with tests and sample visuals.</p>
  <p><a href="fp-cost-forecast/README.md"><b>Explore project →</b></a></p>
</td>
<td width="50%" valign="top">
  <a href="ai-agent-fpa-query/README.md"><img width="100%" src="assets/cards/agent.svg" alt="Finance Query AI project art"></a>
  <h3>04 — AI-Assisted Finance Queries</h3>
  <p><b>Python · APIs · SQL · Genie patterns</b></p>
  <p>A scoped local query handler with calculated synthetic answers and source evidence; the separate live Genie adapter is opt-in and mock-tested.</p>
  <p><b>Scope:</b> demonstration of integration patterns, not an autonomous production agent.</p>
  <p><a href="ai-agent-fpa-query/README.md"><b>Explore project →</b></a></p>
</td>
</tr>
</table>

---

## Macro context for FP&A

The [macro FP&A lab](macro-fpa/README.md) enriches synthetic cost and budget data with monthly USD/BRL from BCB SGS and IPCA from IBGE SIDRA. The report shows budget variance, indicative USD costs and costs in constant BRL. The portfolio includes [executive and technical architecture views](https://denisisikawa.github.io/business-science-lab/#macro-fpa).

---

## The architecture mindset

<img src="assets/architecture.svg" width="100%" alt="Conceptual source-to-decision finance data architecture with transformation and quality controls"/>

**My design principles**

- **Make data trustworthy before making it beautiful.** Validate assumptions, grain and lineage before publishing a metric.
- **Bridge the business and the platform.** Financial definitions should be translated into repeatable engineering rules.
- **Keep controls inspectable.** Tests, traceability and clear failure behavior matter as much as successful runs.
- **Favor reproducibility.** Synthetic data and explicit steps help others judge the work rather than the presentation.

---

## Proof of work

The portfolio is not just a collection of technology names. Every featured project has documentation, and the runnable components have reproducible instructions.

| Project | What to inspect | Execution |
| :-- | :-- | :-- |
| [dbt Finance Lab](dbt-finance-lab/README.md) | SQL models, YAML tests, synthetic seed, CI, [learning roadmap](dbt-finance-lab/CERTIFICATION_ROADMAP.md) | Local dbt + DuckDB |
| [Lakehouse Pipeline](databricks-pipeline-template/README.md) | Schema contract, quarantine, transaction versions and replay tests | SQLite acceptance backend; Spark/Delta adapter |
| [Cost Forecasting](fp-cost-forecast/README.md) | Forecast notebook, generated charts, Python tests | Local Python |
| [Finance Query AI](ai-agent-fpa-query/README.md) | Scoped SQL templates, audit metadata and mocked API checks | Local Python demo |

<details>
<summary><b>See sample forecasting outputs</b></summary>
<br/>
<table>
<tr>
<td width="50%"><img src="images/forecast_plot.png" alt="Synthetic IT-cost forecasting example chart" width="100%"/></td>
<td width="50%"><img src="images/validation_plot.png" alt="Synthetic forecast validation example chart" width="100%"/></td>
</tr>
</table>
<sub>Illustrative charts from fictional input data. They do not represent a production forecast or employer performance.</sub>
</details>

---

## Reproduce the work

**Python projects**

```bash
python -m pip install -r requirements.txt
python -m pytest
```

- Windows: `./run_portfolio.ps1` from PowerShell
- macOS/Linux: `./run_portfolio.sh`

**dbt Finance Lab**

```bash
cd dbt-finance-lab
python -m pip install -r requirements-dbt.txt
# Copy profiles.example.yml to profiles.yml
dbt build --profiles-dir .
```

See each project's README for the full context, prerequisites and limitations.

---

## Currently sharpening

**dbt / Analytics Engineering:** SQL modeling, reusable transformations, test design, financial reconciliation and lineage.

**Databricks specialization:** strengthening Delta Lake, platform architecture and Unity Catalog concepts, with a [structured certification study plan](dbt-finance-lab/CERTIFICATION_ROADMAP.md). **No certification is claimed unless earned.**

---

## Data ethics & scope

Financial records are **synthetic**. The macro FP&A lab can use **public BCB and IBGE indicators** or simulated API responses. Nothing here is a disclosure of Bradesco datasets, internal architecture, confidential controls or other proprietary material. Examples are independent learning and portfolio artifacts; they are not represented as a single live enterprise system.

---

<div align="center">

### Build systems people can trust.

**Finance systems × Data engineering × Decision intelligence**

[LinkedIn](https://www.linkedin.com/in/denisisikawa) &nbsp;·&nbsp; [GitHub Profile](https://github.com/denisisikawa) &nbsp;·&nbsp; [Explore the dbt Lab](dbt-finance-lab/README.md)

</div>
