select
    o.order_id,
    o.customer_id,
    oi.product_id,
    o.order_date::date as order_date,
    o.status,
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price as order_amount
from {{ ref('stg_orders') }} o
join {{ ref('stg_order_items') }} oi
    on o.order_id = oi.order_id