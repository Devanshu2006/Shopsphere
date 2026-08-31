select
    customer_id,
    count(distinct order_id) as total_orders,
    sum(order_amount) as total_spend
from {{ ref('fact_orders') }}
group by customer_id
order by total_spend desc