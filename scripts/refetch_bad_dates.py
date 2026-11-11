import sys
sys.path.append('scripts')
from download_historical_institutional import fetch_day, store_df
import time
import random

bad_dates = [
    '20260101','20260212','20260213','20260216','20260217','20260218',
    '20260219','20260220','20260223','20260224','20260225','20260226',
    '20260227','20260302','20260403','20260406','20260501','20260619',
    '20260710','20260925','20260928','20261009','20261023','20261026'
]

print(f'Re-fetching {len(bad_dates)} potentially bad dates with validation...')
for d in bad_dates:
    print(f'Fetching {d}...')
    df = fetch_day(d, 'data/raw')
    ins = store_df(df, 'data/taifex.db')
    print(f'  -> inserted {ins} rows')
    time.sleep(random.uniform(4.5, 7.5))

print('Done re-fetching bad dates.')
