import sqlite3, pandas as pd
conn=sqlite3.connect('data/taifex.db')
tx = pd.read_sql("SELECT 日期, 身份別, 多空交易契約金額淨額_千元 FROM institutional_futures WHERE 商品名稱='臺股期貨' AND 日期 >= 20261109 ORDER BY 日期, 身份別", conn)
print('Recent TX data (from Nov 9):')
print(tx.to_string())
print()
tx_dates = pd.read_sql("SELECT DISTINCT 日期 FROM institutional_futures WHERE 商品名稱='臺股期貨' ORDER BY 日期", conn)['日期'].tolist()
print('All TX dates available:', tx_dates)
conn.close()
