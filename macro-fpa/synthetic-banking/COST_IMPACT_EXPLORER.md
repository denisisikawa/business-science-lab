# Banking Cost Intelligence — Cost Impact Explorer v0.1

[Open the browser sandbox](https://denisisikawa.github.io/business-science-lab/banking-cost-sandbox/)

## Objective and boundaries
Explain increases and decreases in management costs by dimension, trace the amounts back to original synthetic source records, and reconcile the allocation and variance bridge to integer BRL cents. This is an independent fictional representation of banking scenarios; no employer data or financial outcomes are used. It extends [Banking costing methodology](../BANKING_COSTING.md) and uses the existing [synthetic banking tables](README.md). No paid service, API or generative AI is required.

## Source model
A checked-in snapshot of the seven existing CSVs is exported to `docs/banking-cost-sandbox/data.js`: 288 cost facts, 9 contracts, 312 allocation drivers, 24 capacity facts, 240 operational volumes, 3 products and 7 owning areas. The snapshot is versioned independently of the CSVs; regenerate it when the source files change. The cost grain is month × scenario × source item. Allocation output is source item × destination × channel × event (channel/event only when explicitly attributable). All amounts in output and export are integer cents. Unit price and time calculations may be fractional; stage endpoints are rounded to cents before differences are computed.

## Calculation
- Direct: compare fixed component; reprice change in billed units at the baseline reference tariff if it matches the baseline bill, otherwise at the implied base rate. Remaining variable difference is a residual tariff/charge effect, not proof of a negotiated tariff change. The three effects reconcile to the invoice fact.
- Shared: allocate base expense using base weights (largest remainder with stable product order), then current expense using base weights, then current expense using current weights. The first difference is source cost; the second is allocation. Across the complete cost pool, redistribution sums to zero. Zero or missing drivers move the pool to pending validation in both comparison endpoints, instead of silently distributing it.
- Corporate: retain in corporate destination; compare source cost.
- TDABC: reproduce the methodology's fixed sequence volume → mix → time → rate. Rate = group cost / practical minutes. Round each class's counterfactual at each step; capacity balance = group cost less attributed cost. Display the change in balance separately. If either endpoint exceeds practical capacity, classify both comparison balances under pending validation; the arithmetic still reconciles, but the balance is not a valid idle-capacity interpretation and the control flags overload.
- Combined: every destination row's effects sum to current minus base. Every source item's allocated rows sum to its original expense at each endpoint. Do not sum across different grouping levels, since the same underlying amounts recur. Positive denotes a cost increase, not necessarily a waste or actual recoverable saving.
- Causal interpretation: these are deterministic accounting decompositions subject to the chosen order, inputs and assumptions; operational root cause must be validated. FX and inflation attribution, distinct one-off attribution, profitability and automated AI commentary are not implemented because this source snapshot does not identify them separately.

## User experience
1. Executive summary, gross increases/decreases (by source allocation row), largest increases and reductions.
2. Compare any two 2025 month/scenario combinations; select dimension (product, owning area, category, contract/internal item, supplier, nature, allocation driver, channel, event). Drill down into another dimension with removable path chips.
3. Waterfall with labeled zoomed axis when needed and exact driver values; signed heatmap by group × effect with click-to-filter evidence; allocation flow from source item to destination, widths based on comparison cost, not variance.
4. Inspect source records, rule, parameters and calculation stages; export filtered amounts in cents and identifiers.
5. What-if: modify a copy of the selected comparison scenario, one source item at a time. Adjust fixed expense, hypothetical variable rate and integer billable volumes where applicable; change a shared driver for a product (all cost items sharing that driver are affected); change TDABC volumes, active time and practical capacity. Reset restores the source snapshot. No forecast is persisted; only language selection is saved. No data entry is sent to a server.
6. Reconciliation and input controls. Browser UI is bilingual; source field names and original records remain in their original terminology.

## Validation
Run `node macro-fpa/synthetic-banking/test-cost-impact.cjs` from repository root. Tests cover all 24 × 24 historical comparisons, source reconciliation, driver rollups, identical comparisons, non-destructive simulations, volume changes and overcapacity flags. No dependencies beyond Node.js. A real browser visual test is still required before claiming production-grade usability. The mock-DOM smoke check tested initialization, drilldown, simulation/reset, language switch and source detail; it is not a visual test.

## Roadmap
Expanded source coverage; independent Python/SQL implementation parity; integration with dbt/DuckDB; multi-item scenario batches; explicit FX and inflation drivers with appropriate evidence; unit economics per comparable operational event; source-backed AI commentary.
