import streamlit as st

st.set_page_config(
    page_title="TAIFEX Analytics Hub",
    page_icon="📊",
    layout="centered"
)

st.title("📊 TAIFEX Analytics Platform")
st.markdown("### Select a dashboard")

st.divider()

# Futures Dashboard
st.page_link(
    "pages/1_Futures.py",
    label="**Futures Institutional Explorer**",
    icon="📈",
    help="View institutional trading and open interest data for TAIFEX futures contracts"
)

st.divider()

st.info("More dashboards will be added in the future.")
st.caption("Data source: Taiwan Futures Exchange (TAIFEX)")
