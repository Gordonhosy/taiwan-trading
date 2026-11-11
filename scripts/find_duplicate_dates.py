import sqlite3
import pandas as pd

conn = sqlite3.connect('data/taifex.db')

ref = pd.read_sql("SELECT 商品名稱, 身份別, 多空交易契約金額淨額_千元, 多空未平倉口數淨額 FROM institutional_futures WHERE 日期=20261110", conn)
ref = ref.sort_values(['商品名稱','身份別']).reset_index(drop=True)

dates = pd.read_sql('SELECT DISTINCT 日期 FROM institutional_futures ORDER BY 日期', conn)['日期'].tolist()

bad_dates = []
for d in dates:
    if d == 20261110: 
        continue
    q = pd.read_sql(f"SELECT 商品名稱, 身份別, 多空交易契約金額淨額_千元, 多空未平倉口數淨額 FROM institutional_futures WHERE 日期={d}", conn)
    if len(q) == len(ref):
        q = q.sort_values(['商品名稱','身份別']).reset_index(drop=True)
        if (q.values == ref.values).all():
            bad_dates.append(int(d))

print('Dates with identical full data to 20261110:')
print(bad_dates)
print('Count:', len(bad_dates))

conn.close()
