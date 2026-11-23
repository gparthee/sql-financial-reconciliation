WITH l AS (SELECT txn_id,currency,count(*) n,sum(amount_cents) amount FROM ledger GROUP BY txn_id,currency),
r AS (SELECT txn_id,currency,count(*) n,sum(amount_cents) amount FROM processor GROUP BY txn_id,currency),
keys AS (SELECT txn_id,currency FROM l UNION SELECT txn_id,currency FROM r)
SELECT k.txn_id,k.currency,l.amount AS ledger_cents,r.amount AS processor_cents,
coalesce(l.amount,0)-coalesce(r.amount,0) AS variance_cents,
CASE WHEN coalesce(l.n,0)>1 OR coalesce(r.n,0)>1 THEN 'DUPLICATE'
WHEN l.n IS NULL THEN 'MISSING_LEDGER'
WHEN r.n IS NULL THEN 'MISSING_PROCESSOR'
WHEN l.amount<>r.amount THEN 'AMOUNT_MISMATCH'
ELSE 'MATCHED' END AS status
FROM keys k LEFT JOIN l USING(txn_id,currency) LEFT JOIN r USING(txn_id,currency)
ORDER BY k.txn_id,k.currency;