import os
import time
import random
import argparse
from datetime import datetime, timedelta
import requests
import pandas as pd
import sqlite3
from io import StringIO

def get_trading_days(start, end):
    rng = pd.bdate_range(start, end)
    return [d.strftime("%Y/%m/%d") for d in rng]

def fetch_day(d, raw_dir, max_retries=3):
    os.makedirs(raw_dir, exist_ok=True)
    url = f"https://www.taifex.com.tw/cht/3/futContractsDate?queryDate={d}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.taifex.com.tw/cht/3/futContractsDate",
        "Connection": "keep-alive",
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=30, headers=headers)
            text = resp.text
            raw_path = f"{raw_dir}/futContractsDate_{d.replace('/', '')}.html"
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(text)

            # Validate that the page actually contains data for the requested date
            # (the site often returns latest data for old/missing dates)
            date_str1 = d.replace('/', '')          # 20260302
            date_str2 = f"{d[:4]}/{d[4:6]}/{d[6:]}" # 2026/03/02
            if date_str1 not in text and date_str2 not in text:
                print(f'  {d}: page does not contain the requested date (probably no data or fallback)')
                return pd.DataFrame()

            tables = pd.read_html(StringIO(text), flavor="lxml")
            if not tables:
                return pd.DataFrame()

            df = tables[0]
            for t in tables:
                if len(t) > len(df):
                    df = t
            if len(df.columns) < 15:
                return pd.DataFrame()

            df = df.iloc[:, :15].copy()
            df.columns = [
                "序號", "商品名稱", "身份別",
                "多方交易口數", "多方交易契約金額_千元",
                "空方交易口數", "空方交易契約金額_千元",
                "多空交易口數淨額", "多空交易契約金額淨額_千元",
                "多方未平倉口數", "多方未平倉契約金額_千元",
                "空方未平倉口數", "空方未平倉契約金額_千元",
                "多空未平倉口數淨額", "多空未平倉契約金額淨額_千元",
            ]
            df = df.drop(columns=["序號"], errors="ignore")
            df["身份別"] = df["身份別"].replace({"外資": "外資及陸資"})
            df = df[df["商品名稱"].notna() & (df["商品名稱"].astype(str).str.strip() != "")]
            if df.empty:
                return df

            df["日期"] = d.replace("/", "")
            num_cols = [c for c in df.columns if c not in ["序號", "商品名稱", "身份別", "日期"]]
            for c in num_cols:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "").str.strip(), errors="coerce")

            print(f"  {d}: parsed {len(df)} rows")
            return df

        except Exception as e:
            if attempt == max_retries - 1:
                print(f"  {d} parse error after retries: {e}")
                return pd.DataFrame()
            time.sleep(2 ** attempt + random.uniform(0.5, 1.5))
    return pd.DataFrame()

def store_df(df, db_path):
    if df.empty:
        return 0
    conn = sqlite3.connect(db_path)
    # lower and clean col names for consistency
    df.columns = [str(c).lower().strip().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_") for c in df.columns]
    keys = ["日期", "商品名稱", "身份別"]
    try:
        exist = pd.read_sql_query(f"SELECT {','.join([k for k in keys if k in df.columns])} FROM institutional_futures", conn)
        exist_keys = set(tuple(row) for row in exist.values) if not exist.empty else set()
    except:
        exist_keys = set()
    df["_k"] = df.apply(lambda r: tuple(str(r.get(k, "")) for k in keys if k in df.columns), axis=1)
    new = df[~df["_k"].isin(exist_keys)].drop(columns=["_k"])
    ins = len(new)
    if ins > 0:
        new.to_sql("institutional_futures", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()
    return ins

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=5)
    p.add_argument("--start", default=None)
    p.add_argument("--end", default=None)
    args = p.parse_args()
    if args.start and args.end:
        days = get_trading_days(args.start, args.end)
    else:
        end = datetime.now()
        start = end - timedelta(days=args.days + 20)
        days = get_trading_days(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))[-args.days:]
    print(f"Fetching {len(days)} trading days")
    total = 0
    ok = 0
    for d in days:
        try:
            df = fetch_day(d, "data/raw")
            ins = store_df(df, "data/taifex.db")
            total += ins
            if not df.empty:
                ok += 1
            print(f"{d}: {ins} new rows inserted")
        except Exception as e:
            print(f"{d} error: {e}")
        time.sleep(random.uniform(4.0, 7.0))  # More polite delay with jitter
    print(f"Done: {ok}/{len(days)} days with data, {total} total rows inserted.")

if __name__ == "__main__":
    main()
