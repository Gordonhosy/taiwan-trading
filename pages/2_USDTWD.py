import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from zoneinfo import ZoneInfo
from utils.s3 import load_parquet_from_s3_or_local
from utils.dates import PRESETS, default_range

st.page_link("pages/0_Main_Page.py", label="← Back to Home", icon="🏠")

st.title("USDTWD Spot")

# date buttons CSS
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] { gap: 0.2rem !important; }
div[data-testid="stHorizontalBlock"] button {
    padding: 0.15rem 0.525rem !important;
    font-size: 0.75rem !important;
    min-height: 1.6rem !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

if "usdtwd_date_range" not in st.session_state:
    st.session_state.usdtwd_date_range = default_range()

cols = st.sidebar.columns(5, gap="small")
for i, (label, days) in enumerate(PRESETS.items()):
    if cols[i].button(label, key=f"usdtwd_{label}"):
        end = date.today()
        start = end - pd.Timedelta(days=days)
        st.session_state.usdtwd_date_range = (start, end)
        st.rerun()

date_range = st.sidebar.date_input("Date Range", value=st.session_state.usdtwd_date_range)
if isinstance(date_range, tuple) and len(date_range) == 2:
    st.session_state.usdtwd_date_range = date_range

df = load_parquet_from_s3_or_local("usdtwd/daily/2024/01", "data/usdtwd/daily/2024/01", "TAIFEX_S3_BUCKET", "TAIFEX_S3_REGION")
df["date"] = pd.to_datetime(df["date"]).dt.date

start_d, end_d = st.session_state.usdtwd_date_range
mask = (df["date"] >= start_d) & (df["date"] <= end_d)
filtered = df.loc[mask]

latest = df["date"].max().strftime("%Y-%m-%d")
try:
    with open("data/usdtwd/last_update.txt") as f:
        last_refreshed = f.read().strip()
except:
    last_refreshed = "N/A"
st.caption(f"Data up to: {latest} | Last refreshed: {last_refreshed} HKT")

fig = px.line(filtered, x="date", y="close", markers=True, title="USDTWD Daily Open", labels={"close": "Open"})
st.plotly_chart(fig, use_container_width=True)
