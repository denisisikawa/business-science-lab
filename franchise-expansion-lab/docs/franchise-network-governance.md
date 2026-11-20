# Franchise network performance and territory reallocation
**Status: proposed extension — requirements and financial evaluation design, not implemented in the current simulator.**

A franchise or an authorized partner must create new business while providing reliable support for existing retailers. The vendor should distinguish insufficient market potential, staffing constraints, operational limitations and persistent lack of commercial engagement before changing territory rights.

## 1. Sales enablement and incentives
- Run segment-specific campaigns, product launches, qualified lead distribution, co-funded marketing and time-limited sales incentives.
- Use gamification (team challenges, tiered rewards, scorecards and rankings) with fair targets adjusted to territorial opportunity and dedicated seller capacity.
- Reward activated and retained customers, net recurring revenue and sustainable contribution margin, not raw signatures. Include cancellation, customer satisfaction and support-quality gates to prevent mis-selling.
- Define campaign dates, eligible partners, budget, baseline, target, attribution window, reward rules and evaluation. Compare incremental contribution with incentive costs; stop campaigns with negative incremental economics or poor customer outcomes.

## 2. Franchise performance and engagement controls
Separate partner acquisition status (Kanban) from ongoing operational status after signing. Proposed data entities: partner-month performance, installed customer portfolio, service tickets/SLA, campaigns and incentives, improvement plans, territory rights and contract commitments.

| Dimension | Example evidence / KPI |
|---|---|
| Commercial engagement | Qualified opportunities, demos, CRM activity, campaign participation, dedicated seller FTE, agreed action completion |
| Commercial effectiveness | Activated customers vs. fair capacity-adjusted target, conversion, new net MRR, pipeline aging |
| Customer stewardship | Retention/churn, SLA attainment, backlog, escalations, customer satisfaction |
| Economics | Contribution margin, incentive spend, cost to serve, incremental return |
| Territory | Exclusive allocated prospects, market potential, overlap, unserved demand |

Do not infer a partner's motivation from low sales alone. Investigate demand, staffing, onboarding, product fit, sales execution, channel conflict and service workload. Record agreed targets, measurement rules and evidence of willingness to engage.

Illustrative governance workflow: monitor monthly → identify sustained gaps (e.g., three consecutive months below agreed target) → diagnose jointly → offer enablement and a time-bound improvement plan (e.g., 60–90 days) → review results and service risk → retain, adjust incentives, reallocate sales rights or consider replacement. Thresholds are configurable proposals, not validated market norms. Customer continuity and contractual feasibility are hard gates independent of sales performance.

## 3. Alternative commercial coverage
Compare at least three counterfactuals for the same territory and customer portfolio:
1. Maintain current partner and improve performance with training and incentives.
2. Keep current support responsibilities, but authorize another regional partner to prospect new customers (where permitted).
3. Transfer sales rights and, if necessary and agreed, migrate support for existing customers to a qualified replacement.

Use the territory model to identify local software houses whose radius, dedicated sales team, spare implementation capacity and product expertise are suitable. Deduplicate accounts and leads; separate the existing installed base from unconverted retail prospects. Before approval, validate commercial rights, conflicts, data permissions, customer communication and consent where applicable, continuity arrangements and relevant franchise/partner contracts with qualified legal and business reviewers. A sales transfer does not automatically require a support transfer.

### Proposed contract design
Subject to negotiation and legal review: explicit territory/scope, minimum sales activity and outcome objectives, assigned sales and implementation resources, review cadence, reporting/audit obligations, service-level commitments for current and new customers, escalation and remediation process, performance-linked incentives, change-of-scope/reallocation provisions, cure periods and exit/transition responsibilities. Preserve customer access, service history, billing continuity and support capacity; define acceptance criteria and rollback arrangements before any handover. Prefer measurable commercial proactivity over vague aggressive-sales obligations.

## 4. Incremental ROI of territory reallocation
Owner perspective: software vendor. Use the same horizon, currency, installed customer base and addressable new-prospect pool for every alternative. Forecast incremental cash contribution versus a realistic keep-and-improve baseline, not versus zero revenue.

For each scenario and month:
- Existing customers: opening active accounts × retention assumptions; net recurring revenue to vendor × contribution margin (or explicitly modeled variable cash costs, not both). Include any transfer-related churn.
- New customers: capacity-constrained activated wins, limited by unconverted prospects and implementation throughput; account for sales cycle, onboarding lag, ramp-up, cancellations and vendor share. Accumulate cohorts without double counting installed customers.
- Include recurring incremental support, enablement, commissions/incentives and commercial management costs only if not already captured in contribution margin.
- Include one-time switching costs: training, migration, integrations, communications, temporary dual support, contractual settlement where applicable and implementation contingency.

Define benefit B as the cumulative incremental cash contribution before incremental switching/program costs (including any negative contribution from churn or ramp-up). Define cost C as all incremental program/transition cash outlays for the candidate alternative versus baseline. If incremental costs are not strictly positive, report net incremental cash flow and NPV rather than a misleading percentage. Calculate:
- Net incremental cash flow = B − C.
- Incremental ROI = (B − C) / C, when C > 0.
- Payback = first month cumulative incremental net cash flow becomes nonnegative after an initial outlay; if never, report not reached.
- NPV = sum of monthly incremental net cash flows discounted at an explicit monthly rate; include month zero.
- Also report new customer wins, lost customers, SLA risk, customer retention, incremental MRR at horizon, and downside/base/upside sensitivity (conversion, activation lag, migration churn and costs).

Illustrative one-year scenario, not actual performance:
| Cash contribution / cost | BRL |
|---|---:|
| Incremental contribution from new activations vs. baseline | 120,000 |
| Contribution lost from additional customer churn | -18,000 |
| Incremental contribution before program costs (B) | 102,000 |
| Incremental transition and incentive costs (C) | 45,000 |
| Net incremental cash flow | 57,000 |
| Incremental ROI | 126.7% |

Payback and NPV require a monthly cash-flow schedule; they cannot be inferred from the annual totals. A positive ROI is not sufficient if service continuity, contract authorization or customer retention safeguards fail.

## 5. Planned implementation
- Partner health scorecard with commercial activity, normalized attainment and service indicators; statuses and reasons separate from acquisition stages.
- Campaign and incentive register with incremental ROI.
- Territory reassignment comparison using the same lead pool, installed-base simulation and monthly cash flows; rank eligible candidates and stress-test scenarios.
- Human-approved decision record: baseline, evidence, risks, contract checks, selected alternative, transition owner and post-transfer monitoring.
- Acceptance tests: zero cost handles undefined ROI; no duplicate customers or revenue; baseline equals alternative gives zero incremental net benefit; higher churn worsens ROI; capacity caps new activations; contractual and support gates block automatic approval.
