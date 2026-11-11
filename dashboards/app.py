import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys

# Make sure we can import from scripts/ when deployed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="TAIFEX Institutional Futures Explorer", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    conn = sqlite3.connect("data/taifex.db")
    df = pd.read_sql("SELECT * FROM institutional_futures", conn)
    conn.close()
    df["日期"] = pd.to_datetime(df["日期"].astype(str), format="%Y%m%d")
    return df

df = load_data()

# Support refreshing latest data in the current session (works on Streamlit Cloud)
if "fresh_data" not in st.session_state:
    st.session_state.fresh_data = pd.DataFrame()

if not st.session_state.fresh_data.empty:
    df = pd.concat([df, st.session_state.fresh_data], ignore_index=True)

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
st.sidebar.header("Filters")

# Data freshness + refresh (especially useful on Streamlit Cloud)
latest_date = df["日期"].max().strftime("%Y-%m-%d")
st.sidebar.caption(f"Data through: {latest_date}")

if st.sidebar.button("🔄 Check for newer data"):
    try:
        from scripts.download_historical_institutional import fetch_day
        today = datetime.now()
        found = False
        for delta in range(10):
            d = (today - timedelta(days=delta)).strftime("%Y/%m/%d")
            new_df = fetch_day(d, "data/raw")
            if not new_df.empty:
                new_df["日期"] = pd.to_datetime(new_df["日期"].astype(str), format="%Y%m%d")
                st.session_state.fresh_data = pd.concat(
                    [st.session_state.fresh_data, new_df], ignore_index=True
                )
                st.cache_data.clear()
                st.success(f"Loaded fresh data for {d}")
                st.rerun()
                found = True
                break
        if not found:
            st.sidebar.info("No newer data found in the last 10 days.")
    except Exception as e:
        st.sidebar.error(f"Could not fetch latest: {str(e)[:100]}")

# Date range
date_min = df["日期"].min().date()
date_max = df["日期"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max
)
if isinstance(date_range, tuple):
    start_d, end_d = date_range
else:
    start_d = end_d = date_range

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

# Preserve website order, only include contracts that exist in current data
available_contracts = [c for c in official_order if c in existing_contracts]

# If any contracts exist that are not in the official list, append them at the end
extra = [c for c in sorted(existing_contracts) if c not in official_order]
available_contracts.extend(extra)

# Single contract selector (one at a time)
st.sidebar.markdown("**Contract**")

if "selected_contract" not in st.session_state:
    st.session_state.selected_contract = "臺股期貨" if "臺股期貨" in available_contracts else (available_contracts[0] if available_contracts else None)

if st.session_state.selected_contract not in available_contracts and available_contracts:
    st.session_state.selected_contract = available_contracts[0]

selected_contract = st.sidebar.selectbox(
    "Select contract",
    available_contracts,
    index=available_contracts.index(st.session_state.selected_contract) if st.session_state.selected_contract in available_contracts else 0,
    key="contract_selectbox"
)

st.session_state.selected_contract = selected_contract

# For compatibility with existing filters (list of one)
selected_contracts = [selected_contract] if selected_contract else []

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
    "Category",
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
st.title("TAIFEX Institutional Futures Explorer")
st.caption("Interactive analysis of institutional trading and open interest data from TAIFEX")

# Show effective latest date (including any session refresh)
effective_latest = df["日期"].max().strftime("%Y-%m-%d")
st.caption(f"📅 Latest data: {effective_latest}")

# Single unified chart
st.subheader(chart_title)
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

# Download
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered CSV",
    csv,
    "taifex_filtered.csv",
    "text/csv"
)

st.caption("Data source: Taiwan Futures Exchange (TAIFEX) - Institutional Traders Details of Futures Contracts")
