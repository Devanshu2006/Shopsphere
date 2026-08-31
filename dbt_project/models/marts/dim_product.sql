select
    product_id,
    sku,
    product_name,
    category,
    price,
    updated_at
from {{ ref('stg_products') }}