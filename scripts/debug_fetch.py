import requests
import pandas as pd
import sqlite3
from io import StringIO

def fetch_day(d):
    url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryDate={d}"
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    text = resp.text
    tables = pd.read_html(StringIO(text), flavor="lxml")
    df = tables[0]
    if len(df.columns) < 15:
        return pd.DataFrame()
    df = df.iloc[:, :15].copy()
    df.columns = [
        "序號","商品名稱","身份別",
        "多方交易口數","多方交易契約金額_千元",
        "空方交易口數","空方交易契約金額_千元",
        "多空交易口數淨額","多空交易契約金額淨額_千元",
        "多方未平倉口數","多方未平倉契約金額_千元",
        "空方未平倉口數","空方未平倉契約金額_千元",
        "多空未平倉口數淨額","多空未平倉契約金額淨額_千元"
    ]
    df = df[df["商品名稱"].notna() & (df["商品名稱"].astype(str).str.strip() != "")]
    df = df[df["身份別"].isin(["自營商","投信","外資及陸資"])]
    df["日期"] = d.replace("/","")
    for c in [c for c in df.columns if c not in ["序號","商品名稱","身份別","日期"]]:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",","").str.strip(), errors="coerce")
    return df

def store_df(df, db_path):
    if df.empty:
        return 0
    conn = sqlite3.connect(db_path)
    df2 = df.copy()
    df2.columns = [str(c).lower().strip().replace(" ","_").replace("(","").replace(")","").replace("/","_") for c in df2.columns]
    print("cols after lower:", list(df2.columns)[:6])
    keys = ["日期", "商品名稱", "身份別"]
    try:
        sel = ",".join([k for k in keys if k in df2.columns])
        exist = pd.read_sql_query(f"SELECT {sel} FROM institutional_futures", conn)
        print("exist ok, len=", len(exist))
        exist_keys = set(tuple(row) for row in exist.values) if not exist.empty else set()
    except Exception as e:
        print("exist FAIL:", repr(str(e)[:300]))
        exist_keys = set()
    df2["_k"] = df2.apply(lambda r: tuple(str(r.get(k,"")) for k in keys if k in df2.columns), axis=1)
    new = df2[~df2["_k"].isin(exist_keys)].drop(columns=["_k"])
    ins = len(new)
    if ins > 0:
        new.to_sql("institutional_futures", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    return ins

if __name__ == "__main__":
    for d in ["2026/11/03", "2026/11/06", "2026/11/10"]:
        df = fetch_day(d)
        print(d, "fetched rows:", len(df))
        print(df[["日期","商品名稱","身份別","多方交易口數"]].head(3))
        ins = store_df(df, "data/taifex.db")
        print(d, "inserted:", ins)
        print()
