import sqlite3
import pandas as pd
conn = sqlite3.connect('data/taifex.db')
df = pd.read_sql("SELECT 日期, 商品名稱, 身份別 FROM institutional_futures WHERE 商品名稱='臺股期貨' AND 日期=20261110", conn)
print(df.to_string())
conn.close()
