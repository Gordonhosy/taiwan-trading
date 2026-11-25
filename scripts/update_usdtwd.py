import yfinance as yf
import pandas as pd
import boto3
import os
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

bucket = os.environ["TAIFEX_S3_BUCKET"]
region = os.environ.get("TAIFEX_S3_REGION", "ap-southeast-2")
s3 = boto3.client("s3", region_name=region)

# download last 3 days to catch any missing
end = date.today()
start = end - timedelta(days=3)
df_new = yf.download("USDTWD=X", start=start.isoformat(), progress=False)[["Open"]].reset_index()
df_new.columns = ["date", "close"]
df_new["date"] = pd.to_datetime(df_new["date"]).dt.date

# merge with existing if any (simple append for now)
key = "usdtwd/daily/2024/01/usdtwd.parquet"
try:
    obj = s3.get_object(Bucket=bucket, Key=key)
    df_old = pd.read_parquet(obj["Body"])
    df = pd.concat([df_old, df_new]).drop_duplicates("date").sort_values("date")
except:
    df = df_new

os.makedirs("data/usdtwd/daily/2024/01", exist_ok=True)
df.to_parquet("data/usdtwd/daily/2024/01/usdtwd.parquet", index=False)

last = datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M")
with open("data/usdtwd/last_update.txt", "w") as f:
    f.write(last)
print("Updated", len(df), "rows")
