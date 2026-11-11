import sqlite3
import pandas as pd
conn = sqlite3.connect("data/taifex.db")
dates = pd.read_sql('SELECT DISTINCT 日期 FROM institutional_futures ORDER BY 日期', conn)
print("Distinct dates in DB:")
print(dates.to_string())
print()
total = pd.read_sql('SELECT COUNT(*) as c FROM institutional_futures', conn).iloc[0,0]
print("Total rows now:", total)
print()
sample = pd.read_sql('SELECT 日期, 商品名稱, 身份別, 多方交易口數, 多空未平倉口數淨額 FROM institutional_futures WHERE 日期="20261103" LIMIT 6', conn)
print("Sample rows for 20261103:")
print(sample.to_string())
conn.close()
