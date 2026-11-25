-- The independently declared scope must have unique, nonblank month-start groups.
select month, cost_center, category
from {{ ref('finance_reporting_scope') }}
group by month, cost_center, category
having count(*) <> 1
    or month is null
    or month <> cast(date_trunc('month', month) as date)
    or cost_center is null or trim(cost_center) = ''
    or category is null or trim(category) = ''
