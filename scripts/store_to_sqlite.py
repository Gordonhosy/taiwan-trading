import os
import sys
import glob
import re
import argparse
import sqlite3
import pandas as pd

def clean_col(c):
    c = str(c).lower().strip()
    c = re.sub(r'[^0-9a-z\u4e00-\u9fff]+', '_', c)
    c = re.sub(r'_+', '_', c).strip('_')
    return c

def get_latest_csv(search_dir='data/raw'):
    pats = os.path.join(search_dir, '*.csv')
    files = glob.glob(pats)
    if not files:
        raise FileNotFoundError('No CSV in ' + search_dir)
    return max(files, key=os.path.getmtime)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('csv', nargs='?', default=None)
    args = p.parse_args()
    if args.csv:
        csv_path = args.csv
    else:
        csv_path = get_latest_csv()
    print('Loading:', csv_path)
    df = pd.read_csv(csv_path, encoding='utf-8')
    df.columns = [clean_col(c) for c in df.columns]
    os.makedirs('data', exist_ok=True)
    db_path = 'data/taifex.db'
    conn = sqlite3.connect(db_path)
    table = 'institutional_futures'
    key_cols = ['日期', '商品名稱', '身份別']
    try:
        exist = pd.read_sql_query(f"SELECT {','.join([k for k in key_cols])} FROM {table}", conn)
        exist_keys = set(tuple(row) for row in exist.values) if not exist.empty else set()
    except Exception:
        exist_keys = set()
    df['_k'] = df[key_cols].apply(lambda r: tuple(r), axis=1)
    before = len(df)
    df = df[~df['_k'].isin(exist_keys)].copy()
    inserted = len(df)
    df = df.drop(columns=['_k'])
    if inserted > 0:
        dtype_map = {}
        for col in df.columns:
            if pd.api.types.is_integer_dtype(df[col]):
                dtype_map[col] = 'INTEGER'
            elif pd.api.types.is_float_dtype(df[col]):
                dtype_map[col] = 'REAL'
            else:
                dtype_map[col] = 'TEXT'
        df.to_sql(table, conn, if_exists='append', index=False, dtype=dtype_map)
    conn.commit()
    total = pd.read_sql_query(f"SELECT COUNT(*) as c FROM {table}", conn).iloc[0, 0]
    print(f'Rows inserted: {inserted}')
    print(f'Total rows in table: {total}')
    print('Sample rows:')
    sample = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5", conn)
    print(sample.to_string())
    conn.close()

if __name__ == '__main__':
    main()
