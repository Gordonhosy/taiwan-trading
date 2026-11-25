import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Page config is handled in app.py (main landing page)

st.page_link("pages/0_Main_Page.py", label="← Back to Home", icon="🏠")

@st.cache_data(ttl=300)
def load_data():
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("INSTALL aws; LOAD aws;")

    # Get config from Streamlit secrets (Cloud) or env vars (local)
    try:
        S3_BUCKET = st.secrets.get("TAIFEX_S3_BUCKET", os.environ.get("TAIFEX_S3_BUCKET", ""))
        S3_REGION = st.secrets.get("TAIFEX_S3_REGION", os.environ.get("TAIFEX_S3_REGION", "ap-southeast-2"))
        if "AWS_ACCESS_KEY_ID" in st.secrets:
            con.execute(f"SET s3_access_key_id = '{st.secrets.AWS_ACCESS_KEY_ID}';")
            con.execute(f"SET s3_secret_access_key = '{st.secrets.AWS_SECRET_ACCESS_KEY}';")
    except Exception:
        S3_BUCKET = os.environ.get("TAIFEX_S3_BUCKET", "")
        S3_REGION = os.environ.get("TAIFEX_S3_REGION", "ap-southeast-2")
    con.execute(f"SET s3_region = '{S3_REGION}';")

    local_path = "data/parquet/institutional_futures/*/*.parquet"

    if S3_BUCKET:
        s3_path = f"s3://{S3_BUCKET}/taifex/institutional_futures/*/*.parquet"
        try:
            df = con.execute(f"""
                SELECT * FROM read_parquet('{s3_path}', hive_partitioning = true)
            """).df()
            return df
        except Exception as e:
            st.error(f"Failed to load data from S3: {e}")
            st.info("Make sure TAIFEX_S3_BUCKET and AWS credentials are set in Streamlit secrets (or env vars locally).")
            st.stop()

    # Local fallback (only works when running locally with parquet files)
    try:
        df = con.execute(f"""
            SELECT * FROM read_parquet('{local_path}', hive_partitioning = true)
        """).df()
        return df
    except Exception:
        st.error("No data available. Please configure S3 or ensure local Parquet files exist.")
        st.stop()

df = load_data()
if df.empty:
    st.error("No data available.")
    st.stop()

# English mappings
institution_map = {
    "自營商": "Dealers",
    "投信": "Investment Trusts",
    "外資及陸資": "Foreign Investors"
}

# Remove "Futures Total" (期貨合計)
df = df[df["身份別"] != "期貨合計"]

df["Institution"] = df["身份別"].map(institution_map).fillna(df["身份別"])

# Sidebar filters
st.sidebar.header("Dates")

# Date range
df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
valid_dates = df["日期"].dropna()
if valid_dates.empty:
    st.error("No valid dates in data.")
    st.stop()
date_min = valid_dates.min().date()
date_max = valid_dates.max().date()

if "date_range" not in st.session_state:
    default_start = max(date_min, date_max - pd.Timedelta(days=30))
    st.session_state.date_range = (default_start, date_max)

st.sidebar.markdown("""
<style>
div[data-testid="stHorizontalBlock"] {
    gap: 0.2rem !important;
}
div[data-testid="stHorizontalBlock"] button {
    padding: 0.15rem 0.525rem !important;
    font-size: 0.75rem !important;
    min-height: 1.6rem !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

cols = st.sidebar.columns(5, gap="small")
presets = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
for i, (label, days) in enumerate(presets.items()):
    if cols[i].button(label, key=f"preset_{label}"):
        new_start = max(date_min, date_max - pd.Timedelta(days=days))
        st.session_state.date_range = (new_start, date_max)
        st.rerun()

date_range = st.sidebar.date_input(
    "Date Range",
    value=st.session_state.date_range,
    min_value=date_min,
    max_value=date_max
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    st.session_state.date_range = date_range
    start_d, end_d = date_range
else:
    # During partial selection or single date, use last valid range
    start_d, end_d = st.session_state.date_range

# Date-filtered contracts for selector
date_mask = (df["日期"].dt.date >= start_d) & (df["日期"].dt.date <= end_d)
existing_contracts = set(df.loc[date_mask, "商品名稱"].unique())

# Official order as they appear on the TAIFEX website table
official_order = [
    "臺股期貨",
    "電子期貨",
    "金融期貨",
    "小型臺指期貨",
    "微型臺指期貨",
    "小型電子期貨",
    "小型金融期貨",
    "股票期貨",
    "ETF期貨",
    "櫃買指數期貨",
    "非金電期貨",
    "富櫃200期貨",
    "臺灣中型100期貨",
    "臺灣永續期貨",
    "臺灣生技期貨",
    "半導體30期貨",
    "航運期貨",
    "東證期貨",
    "美國標普500期貨",
    "美國那斯達克100期貨",
    "美國道瓊期貨",
    "美國費城半導體期貨",
    "英國富時100期貨",
    "期貨 小計",
    "期貨合計",
]

ticker_map = {
    "臺股期貨": "TX",
    "電子期貨": "TE",
    "金融期貨": "TF",
    "小型臺指期貨": "MTX",
    "微型臺指期貨": "MXF",
    "小型電子期貨": "MTE",
    "小型金融期貨": "MTF",
}

# Preserve website order, only include contracts that exist in current data
available_contracts = []
contract_display_map = {}
for c in official_order:
    if c in existing_contracts:
        ticker = ticker_map.get(c, "")
        display_name = f"{c} ({ticker})" if ticker else c
        available_contracts.append(display_name)
        contract_display_map[display_name] = c

# If any contracts exist that are not in the official list, append them at the end
extra = [c for c in sorted(existing_contracts) if c not in official_order]
available_contracts.extend(extra)
for e in extra:
    contract_display_map[e] = e

# Single contract selector (one at a time)
if "selected_contract" not in st.session_state:
    st.session_state.selected_contract = "臺股期貨" if "臺股期貨" in available_contracts else (available_contracts[0] if available_contracts else None)

if st.session_state.selected_contract not in available_contracts and available_contracts:
    st.session_state.selected_contract = available_contracts[0]

selected_contract = st.sidebar.selectbox(
    "Contract",
    available_contracts,
    index=available_contracts.index(st.session_state.selected_contract) if st.session_state.selected_contract in available_contracts else 0,
    key="contract_selectbox"
)

st.session_state.selected_contract = selected_contract

# For compatibility with existing filters (list of one)
selected_contracts = [selected_contract] if selected_contract else []
selected_contracts = [contract_display_map.get(c, c) for c in selected_contracts]

# Institutions
all_institutions = sorted(df["Institution"].unique())
selected_institutions = st.sidebar.multiselect(
    "Institution Types",
    all_institutions,
    default=all_institutions
)

# Chart metric selectors (for the single plot)
measure = st.sidebar.selectbox(
    "Measure",
    ["Number of contracts", "Trading value (thousand NTD)"]
)

category = st.sidebar.selectbox(
    "Value",
    ["Open Interest", "Trading volume"]
)

if measure == "Number of contracts":
    if category == "Open Interest":
        y_col = "多空未平倉口數淨額"
        y_label = "Number of contracts"
        chart_title = "Net Open Interest (number of contracts) Over Time"
    else:
        y_col = "多空交易口數淨額"
        y_label = "Number of contracts"
        chart_title = "Net Trading Volume (number of contracts) Over Time"
else:
    if category == "Open Interest":
        y_col = "多空未平倉契約金額淨額_千元"
        y_label = "Trading value (thousand NTD)"
        chart_title = "Net Open Interest Value (thousand NTD) Over Time"
    else:
        y_col = "多空交易契約金額淨額_千元"
        y_label = "Trading value (thousand NTD)"
        chart_title = "Net Trading Value (thousand NTD) Over Time"

# Apply filters
mask = (
    (df["日期"].dt.date >= start_d) &
    (df["日期"].dt.date <= end_d) &
    df["商品名稱"].isin(selected_contracts) &
    df["Institution"].isin(selected_institutions)
)
filtered = df.loc[mask].copy()
filtered = filtered.sort_values(["日期", "Institution", "商品名稱"])

if filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# Main title
st.title("Taifex Futures")

# Show data freshness
latest = df["日期"].max().strftime("%Y-%m-%d")
try:
    with open("data/last_update.txt", encoding="utf-8") as f:
        last_refreshed = f.read().strip()
except Exception:
    # Fallback to file mtime (only happens before first scheduled update)
    last_refreshed = (
        datetime.fromtimestamp(os.path.getmtime("data/taifex.db"), tz=timezone.utc)
        .astimezone(ZoneInfo("Asia/Hong_Kong"))
        .strftime("%Y-%m-%d %H:%M")
    )
st.caption(f"Data up to: {latest} | Last refreshed: {last_refreshed} HKT")

# Single unified chart
fig = px.line(
    filtered,
    x="日期",
    y=y_col,
    color="Institution",
    markers=True,
    title=chart_title,
    labels={
        "日期": "Date",
        y_col: y_label,
        "Institution": "Institution",
        "商品名稱": "Contract"
    }
)
fig.update_traces(connectgaps=True)
st.plotly_chart(fig, use_container_width=True)

st.caption("Data source: https://www.taifex.com.tw/cht/3/futContractsDate")
