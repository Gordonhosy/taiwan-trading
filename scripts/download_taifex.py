import os
import time
import argparse
from datetime import datetime, timedelta
import requests
import pandas as pd

BASE_URL = "https://www.taifex.com.tw/data_gov/taifex_open_data.asp?data_name=MarketDataOfMajorInstitutionalTradersDetailsOfFuturesContractsBytheDate"

def get_trading_days(start, end):
    dates = pd.bdate_range(start, end)
    return [d.strftime("%Y%m%d") for d in dates]

def download_for_date(d, raw_dir):
    os.makedirs(raw_dir, exist_ok=True)
    url = f"{BASE_URL}&d={d}"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    raw_path = f"{raw_dir}/fut_inst_{d}_{datetime.now().strftime('%H%M%S')}.csv"
    with open(raw_path, "wb") as f:
        f.write(resp.content)
    return raw_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", default=(datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"))
    p.add_argument("--end", default=datetime.now().strftime("%Y-%m-%d"))
    args = p.parse_args()
    days = get_trading_days(args.start, args.end)
    print(f"Fetching {len(days)} trading days from {args.start} to {args.end}")
    for d in days:
        try:
            path = download_for_date(d, "data/raw")
            print(f"Downloaded {d}: {path}")
            time.sleep(1.5)
        except Exception as e:
            print(f"Skip {d}: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
