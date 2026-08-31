select
    customer_id,
    email,
    full_name,
    segment,
    signup_date,
    dbt_valid_from,
    dbt_valid_to
from {{ ref('customers_snapshot') }}