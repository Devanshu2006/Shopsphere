select
    customer_id,
    lower(trim(email)) as email,
    trim(full_name) as full_name,
    lower(trim(segment)) as segment,
    signup_date,
    updated_at
from {{ source('raw', 'customers') }}