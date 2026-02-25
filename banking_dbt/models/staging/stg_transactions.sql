select

  txn_id as transaction_id,
  account_id,
  cast(amount as double) as amount,
  txn_type as transaction_type,
  try_cast(txn_date as timestamp) as transaction_ts,
  status,
  _loaded_at,
  _source_system
from {{ source('staging', 'transactions') }}
