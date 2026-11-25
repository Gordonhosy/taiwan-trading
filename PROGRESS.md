# Progress Log - Taifex Futures Dashboard

## Latest Changes (as of latest session)
- Added quick date range buttons (1W, 1M, 3M, 6M, 1Y) with tight spacing
- Default date range set to last 30 days
- Removed 3Y and 5Y buttons
- Removed "Download filtered CSV" button
- Changed main title to "Taifex Futures"
- Removed subtitle caption
- Changed sidebar header from "Filters" to "Dates"
- Changed "Category" label to "Value"
- Added English tickers to contract dropdown (e.g. 臺股期貨 (TX))
- Changed data source caption to direct TAIFEX link
- Removed bold "Contract" label
- Changed "Select contract" to "Contract"
- Removed big subheader chart title above the plot
- Wrapped date selection in a way that avoids partial date errors
- Fixed multiple Streamlit errors (empty data, string dates, secrets, scope issues)
- Improved S3 loading and local fallback handling

## Current State
- Dashboard reads from S3 (primary) with local fallback
- Historical data from 2020–2024 uploaded to S3
- UI is clean with minimal labels and compact date buttons
- Live updates when selecting full date range

## Known Issues / Next Steps
- None currently reported

## Notes
- Always run `streamlit run app.py` for local testing (not individual pages)
- Use `git add -A && git commit -m "update" && git push` after changes
