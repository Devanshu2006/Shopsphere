select distinct
    order_date::date as date_day,
    extract(year from order_date)::int as year,
    extract(month from order_date)::int as month,
    extract(day from order_date)::int as day,
    extract(quarter from order_date)::int as quarter
from {{ ref('stg_orders') }}
