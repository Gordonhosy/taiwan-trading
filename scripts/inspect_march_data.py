import sqlite3
import pandas as pd

conn = sqlite3.connect('data/taifex.db')

query = "SELECT 日期, COUNT(*) as rows FROM institutional_futures WHERE 日期 LIKE '202603%' GROUP BY 日期 ORDER BY 日期"
df = pd.read_sql(query, conn)
print("March 2026 dates and row counts:")
print(df.to_string())
print()

print("Sample rows for 20260302 (TX):")
sample = pd.read_sql("SELECT * FROM institutional_futures WHERE 日期=20260302 AND 商品名稱='臺股期貨'", conn)
print(sample[['日期','商品名稱','身份別','多空交易契約金額淨額_千元', '多空未平倉口數淨額']].to_string())
print()

print("Sample rows for a good date e.g. 20261110 (TX):")
good = pd.read_sql("SELECT * FROM institutional_futures WHERE 日期=20261110 AND 商品名稱='臺股期貨'", conn)
print(good[['日期','商品名稱','身份別','多空交易契約金額淨額_千元', '多空未平倉口數淨額']].to_string())

conn.close()
