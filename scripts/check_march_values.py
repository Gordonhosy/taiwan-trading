import sqlite3
import pandas as pd

conn = sqlite3.connect('data/taifex.db')

print('TX Net Trading Value (千元) for March dates:')
dates = [20260303,20260304,20260305,20260309,20260310,20260311]
for d in dates:
    q = pd.read_sql(f"SELECT 身份別, 多空交易契約金額淨額_千元 FROM institutional_futures WHERE 日期={d} AND 商品名稱='臺股期貨' ORDER BY 身份別", conn)
    print(f'--- {d} ---')
    print(q.to_string())
    print()

conn.close()
