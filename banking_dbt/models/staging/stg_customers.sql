select
  cast(customer_id as varchar)  as customer_id,
  cast(first_name as varchar)   as first_name,
  cast(last_name as varchar)    as last_name,
  cast(email as varchar)        as email,
  cast(country as varchar)      as country,
  cast(kyc_status as varchar)   as kyc_status,
  cast(created_at as timestamp) as created_at,
  cast(_loaded_at as timestamp) as _loaded_at,
  cast(_source_system as varchar) as _source_system
from {{ source('staging', 'customers') }}
