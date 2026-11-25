-- Reconciliation can pass if a group disappears from BOTH staging and mart.
-- Compare both layers with an independent reporting scope instead.
with expected as (
    select month, cost_center, category, 1 as expected_present
    from {{ ref('finance_reporting_scope') }}
), staging as (
    select distinct month, cost_center, category, 1 as staging_present
    from {{ ref('stg_finance_costs') }}
), mart as (
    select distinct month, cost_center, category, 1 as mart_present
    from {{ ref('fct_monthly_costs') }}
), all_groups as (
    select month, cost_center, category from expected
    union
    select month, cost_center, category from staging
    union
    select month, cost_center, category from mart
)
select k.month, k.cost_center, k.category,
       coalesce(e.expected_present, 0) as expected_present,
       coalesce(s.staging_present, 0) as staging_present,
       coalesce(m.mart_present, 0) as mart_present
from all_groups k
left join expected e
  on k.month = e.month and k.cost_center = e.cost_center and k.category = e.category
left join staging s
  on k.month = s.month and k.cost_center = s.cost_center and k.category = s.category
left join mart m
  on k.month = m.month and k.cost_center = m.cost_center and k.category = m.category
where e.expected_present is null or s.staging_present is null or m.mart_present is null
