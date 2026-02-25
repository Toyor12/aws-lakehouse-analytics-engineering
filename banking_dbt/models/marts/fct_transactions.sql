select
  t.transaction_id,
  t.account_id,
  a.customer_id,
  t.amount,
  t.transaction_type,
  t.transaction_ts,
  t.status,
  t._loaded_at,
  t._source_system
from {{ ref('stg_transactions') }} t
left join {{ ref('stg_accounts') }} a
  on t.account_id = a.account_id
