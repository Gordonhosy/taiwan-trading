import sqlite3
import pandas as pd
conn = sqlite3.connect('data/taifex.db')
df = pd.read_sql('SELECT * FROM institutional_futures LIMIT 3', conn)
print('Columns:', list(df.columns))
print()
print('Sample row:')
print(df.iloc[0].to_dict())
print()
tx = pd.read_sql("SELECT 日期, 商品名稱, 身份別, [多空交易契約金額淨額_千元] FROM institutional_futures WHERE 商品名稱='臺股期貨' ORDER BY 日期 LIMIT 10", conn)
print('TX net trading value samples (first 10):')
print(tx.to_string())
conn.close()
