import streamlit as st

st.set_page_config(
    page_title="Life Insurance Analytics",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Life Insurance Renewal Analytics")

st.markdown("""
## Welcome 👋

This dashboard provides an end-to-end analysis of life insurance
renewals, premiums, customer segments, forecasting and business insights.

Use the **sidebar** to navigate between the different sections.
""")

st.info(
    "👈 Select **01 Overview** from the sidebar to explore the main dashboard."
)