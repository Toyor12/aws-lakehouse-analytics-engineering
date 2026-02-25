select
  cast(account_id as varchar)   as account_id,
  cast(customer_id as varchar)  as customer_id,
  cast(account_type as varchar) as account_type,
  cast(balance as double)       as balance,
  cast(status as varchar)       as status,
  cast(opened_date as date)     as opened_date,
  cast(_loaded_at as timestamp) as _loaded_at,
  cast(_source_system as varchar) as _source_system
from {{ source('staging', 'accounts') }}
