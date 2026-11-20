# Commercial methodology and data contract

## Two distinct funnels
1. Partner acquisition: prospecting → qualification → discovery → proposal → negotiation → signed or lost. The partner is a local software house, not an end customer.
2. Retail opportunity: a synthetic market of stores that a partner may prospect after qualification. The demo models potential and coverage, not actual retail sales or historical conversion.

## Data grain
| Entity | Grain | Fields |
|---|---|---|
| retail lead | store ID | synthetic region, vertical, latitude, longitude, illustrative monthly ticket in BRL |
| partner lead | partner ID | synthetic name, region, latitude, longitude, illustrative fit score, current stage, synthetic headcount, sales FTE, optional radius override |
| territory | region | synthetic lead count, potential monthly ticket sum, covered leads, eligible partners |

All records are generated in memory with a fixed seed. Regional anchor coordinates are approximate references for Greater São Paulo. Locations are synthetic and do not represent actual companies or addresses.

## Territory and funnel rules
Haversine distance measures great-circle distance, not drive time. For each retail lead, eligible partners are non-lost partners within their own effective radius (override or network default, 0–50 km). Reachable counts may overlap; exclusive allocation assigns each lead to the nearest eligible partner, with partner ID as tie-breaker. Market coverage is distinct allocated stores divided by all filtered stores. No actual commercial territories, travel times, legal exclusivity, partner capacity or existing competitor data are assumed.

Partner fit score is synthetic; opportunity score combines 50% illustrative fit and 50% normalized capacity-constrained expected customer wins in the horizon (cap at 50 customers). This is a transparent heuristic, not a trained ML model.

Funnel probabilities: prospect 10%, qualified 25%, discovery 40%, proposal 60%, negotiation 80%, signed 100%, lost 0%. These are assumptions, not historical conversion rates. Signed partners' modeled revenue is shown separately from the open weighted pipeline.

## Revenue model
Gross monthly opportunity = sum of illustrative store subscription tickets. Projected vendor monthly recurring revenue at the end of the selected horizon = capacity-constrained expected customer wins × average allocated monthly ticket × assumed vendor revenue share. Open probability-weighted pipeline = projected revenue × partner stage probability. There are no real bookings, installed subscriptions, franchise fees, taxes, churn, delivery costs or recognized revenue. A signed partnership is not guaranteed end-customer revenue.

## Next actions
Prospect: identify decision-maker and verify company profile. Qualified: check retail expertise, installed base and channel conflict. Discovery: validate integration, territory and implementation capacity. Proposal: define product, margin sharing, pilot, responsibilities and support. Negotiation: validate commercial/legal terms and mutual plan. Signed: onboard, enable sales and monitor first retail wins. Lost: record reason and revisit only if justified.

## Roadmap
- V0.1 browser-only scenario and editable Kanban.
- V0.2 per-partner staffing, monthly capacity and radius overrides; future work: historical events, cohorts, aging, retail opportunity funnel and richer overlap diagnostics.
- V0.3 optional governed public market data, road access / travel-time analysis, CRM integration, contract workflow and unit economics.
- V0.4 evidence-based decision support, cost monitoring and human-reviewed AI recommendations.
- Planned cross-cutting work: sales incentives and gamification, partner-engagement scorecards, improvement plans, customer-continuity safeguards and incremental territory-reallocation ROI. See [franchise network governance](franchise-network-governance.md).

## Acceptance criteria
Deterministic seed; no double count in exclusive allocation; assigned leads ≤ filtered leads; assigned ticket sum ≤ total ticket sum; zero radius yields zero coverage for this generated scenario; lost partners excluded; weighted and signed projected revenue separated. User controls are scenario assumptions. Validate browser behavior before public portfolio release.

## V0.2 — sales capacity and territory sizing

### Benchmark inputs and limitations (reviewed 2026-11-20)
- [Meetime: coaching in sales](https://meetime.com.br/blog/vendas/coaching/): historical survey median of 15 scheduled demos per seller per month. The model uses 15 opportunities per sales FTE per month as an **adjustable proxy**, not an observed qualified-opportunity rate.
- [Meetime: prospecting process](https://meetime.com.br/blog/prospeccao/processo-de-prospeccao/): ISBB 2022 reports about 63 leads approached per SDR/month. This is contextual; SDR contacts are not seller opportunities and are not multiplied into the forecast.
- [RD Station Panoramas 2026](https://www.rdstation.com/pesquisas/panoramas-rd-station/edicao-2026/vendas/maturidade-operacional/): 9% conversion for Software and Cloud based on 2025 RD Vendas data. Use as a contextual default; exact retail ERP franchise conversion and productivity are not verified.
- 80% effective productivity, synthetic headcount, initial sales FTE share (approximately 25%), 15% penetration, 70% vendor share and 12-month horizon after activation are scenario assumptions, not benchmarks. All are editable except the generator's initial staffing defaults, which can be overridden per partner.

### Formulas
For each non-lost partner: commercial monthly capacity = dedicated sales FTE × opportunities/FTE/month × win rate × effective productivity. Target wins over horizon = exclusively allocated retail leads × target penetration. Average target demand/month = target wins / horizon. Expected wins = min(target wins, monthly capacity × horizon). Average monthly wins = expected wins / horizon. Unmet target = target wins − expected wins. Required sales FTE = ceiling(monthly demand / wins per effective FTE), undefined if productivity is zero with positive demand. All win counts are expectations, not necessarily integers. No churn, additional customer arrivals, opening lag, implementation capacity or recognition is modeled. End-horizon MRR is conditional on activation, assumes retained customers and uses mean allocated ticket. Open probability-weighted forecasts and signed forecasts remain separate; network scenario includes all eligible partners hypothetically activated.

### Decision support
A staffing bottleneck indicates positive unmet target demand; otherwise market/territory limits the scenario. Location radius changes reach and exclusive allocation across the full network; overlap prevents double counting. Increasing a radius cannot guarantee more exclusive prospects or increased revenue for every partner. A larger radius does not model travel-time or field-sales productivity degradation. Per-partner overrides are in-session only. Review geography and commercial staffing before negotiating a franchise; verify actual sales productivity and implementation resources before hiring or making commitments.
