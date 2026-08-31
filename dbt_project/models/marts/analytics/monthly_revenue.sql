select
    date_trunc('month', order_date)::date as month,
    count(distinct order_id) as total_orders,
    sum(order_amount) as total_revenue
from {{ ref('fact_orders') }}
group by 1
order by 1
