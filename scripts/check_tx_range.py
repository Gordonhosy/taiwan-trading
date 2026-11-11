import sqlite3
import pandas as pd
conn = sqlite3.connect('data/taifex.db')
tx = pd.read_sql("SELECT 日期, 身份別, [多空交易契約金額淨額_千元] FROM institutional_futures WHERE 商品名稱='臺股期貨' ORDER BY 日期, 身份別", conn)
print('Clean TX data for dashboard ({} rows):'.format(len(tx)))
print(tx.to_string())
tx_dates = pd.read_sql("SELECT DISTINCT 日期 FROM institutional_futures WHERE 商品名稱='臺股期貨' ORDER BY 日期", conn)['日期'].tolist()
print()
print('TX dates now available:', tx_dates)
conn.close()
