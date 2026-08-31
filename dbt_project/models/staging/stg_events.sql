select
    event_id,
    customer_id,
    lower(trim(event_type)) as event_type,
    product_id,
    event_ts
from {{ source('raw', 'events') }}