import yfinance as yf
import pandas as pd
import boto3
import os
from datetime import datetime
from zoneinfo import ZoneInfo

ticker = "USDTWD=X"
start = "2024-01-01"
df = yf.download(ticker, start=start, progress=False)
df = df[["Open"]].reset_index()
df.columns = ["date", "close"]
df["date"] = pd.to_datetime(df["date"]).dt.date
df = df.sort_values("date")

bucket = os.environ["TAIFEX_S3_BUCKET"]
key = "usdtwd/daily/2024/01/usdtwd.parquet"
s3 = boto3.client("s3", region_name=os.environ.get("TAIFEX_S3_REGION", "ap-southeast-2"))
s3.put_object(Bucket=bucket, Key=key, Body=df.to_parquet(index=False))

last = datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M")
s3.put_object(Bucket=bucket, Key="usdtwd/last_update.txt", Body=last)
print("Uploaded", len(df), "rows")
