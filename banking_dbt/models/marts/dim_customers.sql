select
  customer_id,
  first_name,
  last_name,
  email,
  country,
  kyc_status,
  cast(created_at as timestamp) as created_at,
  _loaded_at,
  _source_system
from {{ ref('stg_customers') }}

