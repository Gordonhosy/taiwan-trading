import sqlite3
import pandas as pd
conn = sqlite3.connect('data/taifex.db')
df = pd.read_sql("SELECT 日期, 身份別 FROM institutional_futures WHERE 商品名稱='臺股期貨' ORDER BY 日期, 身份別", conn)
print('TX rows by date and identity:')
print(df.groupby('日期')['身份別'].apply(list).to_string())
print()
missing = []
for date, group in df.groupby('日期'):
    if '外資及陸資' not in group['身份別'].values:
        missing.append(date)
print('Missing 外資及陸資 for TX on these dates:')
print(missing)
conn.close()
