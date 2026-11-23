import csv,sqlite3
from collections import Counter
from pathlib import Path
root=Path(__file__).parent
conn=sqlite3.connect(":memory:")
for t in ("ledger","processor"):
    conn.execute(f"CREATE TABLE {t}(txn_id TEXT,amount_cents INTEGER,currency TEXT)")
    with (root/"data"/f"{t}.csv").open() as f:
        r=csv.reader(f);next(r);conn.executemany(f"INSERT INTO {t} VALUES (?,?,?)",r)
cur=conn.execute((root/"reconcile.sql").read_text());rows=cur.fetchall()
assert sum(x[4] for x in rows)==sum(x[0] for x in conn.execute("SELECT amount_cents FROM ledger"))-sum(x[0] for x in conn.execute("SELECT amount_cents FROM processor"))
assert len({(x[0],x[1]) for x in rows})==len(rows)
out=root/"outputs";out.mkdir(exist_ok=True)
with (out/"reconciliation.csv").open("w",newline="") as f:
    w=csv.writer(f);w.writerow([d[0] for d in cur.description]);w.writerows(rows)
for status,count in sorted(Counter(x[-1] for x in rows).items()):print(f"{status}: {count}")
print(f"Net variance: ${sum(x[4] for x in rows)/100:,.2f}")
print("Control totals passed.")