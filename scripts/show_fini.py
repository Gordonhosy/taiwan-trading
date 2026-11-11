import sqlite3
import pandas as pd
conn = sqlite3.connect('data/taifex.db')
tx = pd.read_sql("SELECT COUNT(*) as c FROM institutional_futures WHERE 商品名稱='臺股期貨'", conn)
print('Total TX rows:', tx.iloc[0,0])
dates = pd.read_sql("SELECT DISTINCT 日期 FROM institutional_futures WHERE 商品名稱='臺股期貨' ORDER BY 日期", conn)['日期'].tolist()
print('TX dates:', dates)
conn.close()
