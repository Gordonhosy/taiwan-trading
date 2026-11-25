import streamlit as st

main_page = st.Page("pages/0_Main_Page.py", title="Main Page", icon="🏠", default=True)
futures_page = st.Page("pages/1_Futures.py", title="Futures", icon="📈")
usdtwd_page = st.Page("pages/2_USDTWD.py", title="USDTWD", icon="💱")

pg = st.navigation([main_page, futures_page, usdtwd_page])
pg.run()
