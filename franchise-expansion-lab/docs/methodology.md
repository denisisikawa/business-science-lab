# Commercial methodology and data contract

## Two distinct funnels
1. Partner acquisition: prospecting → qualification → discovery → proposal → negotiation → signed or lost. The partner is a local software house, not an end customer.
2. Retail opportunity: a synthetic market of stores that a partner may prospect after qualification. The demo models potential and coverage, not actual retail sales or historical conversion.

## Data grain
| Entity | Grain | Fields |
|---|---|---|
| retail lead | store ID | synthetic region, vertical, latitude, longitude, illustrative monthly ticket in BRL |
| partner lead | partner ID | synthetic name, region, latitude, longitude, illustrative fit score, current stage |
| territory | region | synthetic lead count, potential monthly ticket sum, covered leads, eligible partners |

All records are generated in memory with a fixed seed. Regional anchor coordinates are approximate references for Greater São Paulo. Locations are synthetic and do not represent actual companies or addresses.

## Territory and funnel rules
Haversine distance measures great-circle distance, not drive time. For each retail lead, eligible partners are non-lost partners within the selected radius. Reachable counts may overlap; exclusive allocation assigns each lead to the nearest eligible partner, with partner ID as tie-breaker. Market coverage is distinct allocated stores divided by all filtered stores. No actual commercial territories, travel times, legal exclusivity, partner capacity or existing competitor data are assumed.

Partner fit score is synthetic; opportunity score combines 50% illustrative fit and 50% normalized allocated store count (cap at 50 stores). This is a transparent heuristic, not a trained ML model.

Funnel probabilities: prospect 10%, qualified 25%, discovery 40%, proposal 60%, negotiation 80%, signed 100%, lost 0%. These are assumptions, not historical conversion rates. Signed partners' modeled revenue is shown separately from the open weighted pipeline.

## Revenue model
Gross monthly opportunity = sum of illustrative store subscription tickets. Projected vendor monthly recurring revenue = exclusively allocated ticket sum × assumed retail penetration × assumed vendor revenue share. Open probability-weighted pipeline = projected revenue × partner stage probability. There are no real bookings, installed subscriptions, franchise fees, taxes, churn, delivery costs or recognized revenue. A signed partnership is not guaranteed end-customer revenue.

## Next actions
Prospect: identify decision-maker and verify company profile. Qualified: check retail expertise, installed base and channel conflict. Discovery: validate integration, territory and implementation capacity. Proposal: define product, margin sharing, pilot, responsibilities and support. Negotiation: validate commercial/legal terms and mutual plan. Signed: onboard, enable sales and monitor first retail wins. Lost: record reason and revisit only if justified.

## Roadmap
- V0.1 browser-only scenario and editable Kanban.
- V0.2 historical events, conversion by cohort, aging, partner capacity, retail opportunity funnel and overlap diagnostics.
- V0.3 optional governed public market data, road access / travel-time analysis, CRM integration, contract workflow and unit economics.
- V0.4 evidence-based decision support, cost monitoring and human-reviewed AI recommendations.

## Acceptance criteria
Deterministic seed; no double count in exclusive allocation; assigned leads ≤ filtered leads; assigned ticket sum ≤ total ticket sum; zero radius yields zero coverage for this generated scenario; lost partners excluded; weighted and signed projected revenue separated. User controls are scenario assumptions. Validate browser behavior before public portfolio release.
