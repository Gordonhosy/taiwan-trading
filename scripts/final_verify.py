import sqlite3, pandas as pd
conn=sqlite3.connect('data/taifex.db')
all_dates = pd.read_sql('SELECT DISTINCT 日期 FROM institutional_futures ORDER BY 日期', conn)['日期'].tolist()
tx_dates = pd.read_sql("SELECT DISTINCT 日期 FROM institutional_futures WHERE 商品名稱='臺股期貨' ORDER BY 日期", conn)['日期'].tolist()
total = pd.read_sql('SELECT COUNT(*) as c FROM institutional_futures', conn).iloc[0,0]
print('Historical data updated from 2026-10-16')
print('All dates:', all_dates)
print('TX dates for dashboard:', tx_dates)
print('Total rows in DB:', total)
conn.close()
