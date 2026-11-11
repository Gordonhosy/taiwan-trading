import sqlite3
import pandas as pd

conn = sqlite3.connect('data/taifex.db')

ref = pd.read_sql("SELECT * FROM institutional_futures WHERE 日期=20261110 AND 商品名稱='臺股期貨'", conn)
print('Reference (20261110 TX):')
print(ref[['身份別', '多空交易契約金額淨額_千元', '多空未平倉口數淨額']].to_string())
print()

bad_dates = [20260302, 20260303, 20260304, 20260305, 20260401, 20260501, 20260601]
for d in bad_dates:
    q = pd.read_sql(f"SELECT * FROM institutional_futures WHERE 日期={d} AND 商品名稱='臺股期貨'", conn)
    if not q.empty:
        match = (q[['多空交易契約金額淨額_千元', '多空未平倉口數淨額']].values == ref[['多空交易契約金額淨額_千元', '多空未平倉口數淨額']].values).all()
        print(f'{d} TX matches Nov10 data? {match} (rows: {len(q)})')
    else:
        print(f'{d}: No TX data')

conn.close()
