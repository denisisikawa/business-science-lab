-- Every reporting grain must preserve exact BRL amounts and transaction counts.
-- Full outer join detects missing and unexpected groups, not only changed totals.
with expected as (
    select month, cost_center, category,
           cast(sum(amount_brl) as decimal(18, 2)) as expected_amount_brl,
           count(*) as expected_transaction_count
    from {{ ref('stg_finance_costs') }}
    group by month, cost_center, category
), actual as (
    select month, cost_center, category, total_amount_brl, transaction_count,
           1 as actual_present
    from {{ ref('fct_monthly_costs') }}
)
select
    coalesce(e.month, a.month) as month,
    coalesce(e.cost_center, a.cost_center) as cost_center,
    coalesce(e.category, a.category) as category,
    e.expected_amount_brl, a.total_amount_brl,
    e.expected_transaction_count, a.transaction_count
from expected e
full outer join actual a
  on e.month = a.month
 and e.cost_center = a.cost_center
 and e.category = a.category
where e.expected_transaction_count is null
   or a.actual_present is null
   or a.total_amount_brl is null
   or a.transaction_count is null
   or e.expected_amount_brl <> a.total_amount_brl
   or e.expected_transaction_count <> a.transaction_count
