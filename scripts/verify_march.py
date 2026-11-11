import sqlite3
import pandas as pd

conn = sqlite3.connect('data/taifex.db')

print('March 2026 dates with data:')
df = pd.read_sql("SELECT 日期, COUNT(*) as rows FROM institutional_futures WHERE 日期 LIKE '202603%' GROUP BY 日期 ORDER BY 日期", conn)
print(df.to_string())
print()

print('Sample for 20260302:')
sample = pd.read_sql("SELECT * FROM institutional_futures WHERE 日期=20260302 AND 商品名稱='臺股期貨'", conn)
if sample.empty:
    print('No data for 20260302 (good)')
else:
    print(sample[['身份別', '多空交易契約金額淨額_千元', '多空未平倉口數淨額']].to_string())

print()
print('Current total distinct dates:', pd.read_sql('SELECT COUNT(DISTINCT 日期) FROM institutional_futures', conn).iloc[0,0])

conn.close()
