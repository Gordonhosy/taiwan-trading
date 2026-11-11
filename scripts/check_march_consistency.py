import sqlite3
import pandas as pd

conn = sqlite3.connect('data/taifex.db')

print('Institutions present for selected March dates (TX only):')
for d in [20260303, 20260304, 20260305, 20260309, 20260310]:
    q = pd.read_sql(f"SELECT 身份別 FROM institutional_futures WHERE 日期={d} AND 商品名稱='臺股期貨'", conn)
    insts = sorted(q['身份別'].tolist())
    print(f'{d} : {insts}')

print()
print('Row counts for March dates:')
df = pd.read_sql("SELECT 日期, COUNT(*) as rows FROM institutional_futures WHERE 日期 LIKE '202603%' GROUP BY 日期 ORDER BY 日期", conn)
print(df.to_string())

conn.close()
