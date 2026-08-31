select
    product_id,
    trim(sku) as sku,
    trim(product_name) as product_name,
    lower(trim(category)) as category,
    price,
    updated_at
from {{ source('raw', 'products') }}