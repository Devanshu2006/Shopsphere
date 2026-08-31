select
    p.category,
    sum(f.quantity) as units_sold,
    sum(f.order_amount) as total_revenue
from {{ ref('fact_orders') }} f
join {{ ref('dim_product') }} p
    on f.product_id = p.product_id
group by p.category
order by total_revenue desc