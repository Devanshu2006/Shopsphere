select
    order_id,
    customer_id,
    order_date,
    lower(trim(status)) as status,
    updated_at
from {{ source('raw', 'orders') }}