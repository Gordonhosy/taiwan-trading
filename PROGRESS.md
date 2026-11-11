# analytics-platform Progress Log

**Last updated:** 2026-11-10

## Data Status
- Full historical institutional futures data from **2026-01-01 to 2026-11-10**
- **224 trading days** covered
- **16,352 rows** in `data/taifex.db`
- **25 contracts** (including 臺股期貨 / TX, 電子期貨, etc.)
- **4 institution types** (自營商/Dealers, 投信/Investment Trusts, 外資及陸資/Foreign Investors, 期貨合計/Futures Total)
- All columns preserved (trading volume + open interest, long/short/net, in contracts and value)
- Data fetched via https://www.taifex.com.tw/cht/3/futContractsDate?queryDate=...
- Raw HTML backups saved in `data/raw/`

**Note:** Some dates (mainly holidays) return no data from the source.

## Dashboard (dashboards/app.py)
- Fully translated to English
- **Single contract selector** (one at a time, dynamically filtered by date range)
- Two time series charts:
  1. **Net Open Interest (contracts)** – fixed chart on top
  2. **Selected metric** – flexible chart below (Net Trading Value, Net OI, or Net OI Value)
- Sidebar filters:
  - Date range
  - Contract (single select)
  - Institution Types (Dealers, Investment Trusts, Foreign Investors – Futures Total removed)
  - Metric selector
- Download button for filtered CSV
- Data table removed (per request)

## Scripts
- `scripts/download_historical_institutional.py` – main historical fetcher (polite mode with retries + random 4-7s delays)
- `scripts/download_taifex.py` – latest snapshot
- `scripts/store_to_sqlite.py` – legacy single-file loader

## Current State
- Data fully updated from Jan 1 2026 to present
- Dashboard is the main focus (contract selector + dual time series completed)
- All previous requests implemented (English UI, single contract, delete table, remove Futures Total, etc.)

## How to Resume
1. Activate venv:
   ```powershell
   cd C:\Users\User\analytics-platform
   .\.venv\Scripts\Activate.ps1
   ```
2. Run dashboard:
   ```powershell
   streamlit run dashboards/app.py --server.baseUrlPath=/dashboard --server.address 0.0.0.0
   ```
3. (Optional) Refresh data:
   ```powershell
   python scripts/download_historical_institutional.py --start 2026-01-01 --end 2026-11-10
   ```

## Open / Next Items
- Add more chart types (volume, comparison, etc.)
- Add more filters (e.g. by value thresholds)
- Improve contract selector UX if needed
- Add export options beyond CSV
- Any other features you want

---
**To continue:** Just say what you want to work on next (e.g. "add a volume chart" or "improve the date picker").
