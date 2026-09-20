import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(
    page_title="Business Insights",
    page_icon="💡",
    layout="wide"
)

st.title("Business Insights")
st.divider()
# ============================================================
# FILE PATHS
# ============================================================

INSURER_FILE = "data/processed/monthly_by_insurer.csv"
BUSINESS_FILE = "reports/business_insights.csv"

# ============================================================
# LOAD DATA
# ============================================================

if not os.path.exists(INSURER_FILE):
    st.error(f"Dataset not found: `{INSURER_FILE}`")
    st.stop()

if not os.path.exists(BUSINESS_FILE):
    st.error(f"Business insights file not found: `{BUSINESS_FILE}`")
    st.stop()

monthly = pd.read_csv(INSURER_FILE)
business = pd.read_csv(BUSINESS_FILE)

monthly.columns = monthly.columns.str.strip()
business.columns = business.columns.str.strip()

# ============================================================
# CLEAN DATA
# ============================================================

monthly["collection_month"] = pd.to_datetime(
    monthly["collection_month"],
    errors="coerce"
)

numeric_cols = [
    "total_policies",
    "renewed_policies",
    "total_premium",
    "renewed_premium",
    "renewal_rate"
]

for col in numeric_cols:
    if col in monthly.columns:
        monthly[col] = pd.to_numeric(
            monthly[col],
            errors="coerce"
        )

# ============================================================
# OVERALL BUSINESS KPIs
# ============================================================

total_policies = monthly["total_policies"].sum()
renewed_policies = monthly["renewed_policies"].sum()
total_premium = monthly["total_premium"].sum()
renewed_premium = monthly["renewed_premium"].sum()

overall_renewal_rate = (
    renewed_policies / total_policies * 100
    if total_policies > 0
    else 0
)

st.subheader("Overall Business Performance")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Total Policies",
        f"{total_policies:,.0f}"
    )

with c2:
    st.metric(
        "Renewed Policies",
        f"{renewed_policies:,.0f}"
    )

with c3:
    st.metric(
        "Total Premium",
        f"₹{total_premium / 1e7:,.2f} Cr"
    )

with c4:
    st.metric(
        "Renewed Premium",
        f"₹{renewed_premium / 1e7:,.2f} Cr"
    )

with c5:
    st.metric(
        "Overall Renewal Rate",
        f"{overall_renewal_rate:.2f}%"
    )

st.divider()

# ============================================================
# INSURER SELECTOR
# ============================================================

st.subheader("Insurer Business Analysis")

insurers = sorted(
    monthly["insurer"].dropna().unique()
)

selected_insurer = st.selectbox(
    "Select Insurer",
    insurers
)

insurer_monthly = monthly[
    monthly["insurer"] == selected_insurer
].copy()

insurer_business = business[
    business["Insurer"] == selected_insurer
].copy()

# ============================================================
# INSURER METRICS
# ============================================================

if not insurer_business.empty:

    row = insurer_business.iloc[0]

    avg_premium = row.get(
        "Historical Avg Premium",
        np.nan
    )

    historical_growth = row.get(
        "Historical Growth %",
        np.nan
    )

    forecast_total = row.get(
        "12 Month Forecast",
        np.nan
    )

    avg_forecast = row.get(
        "Average Forecast",
        np.nan
    )

    forecast_vs_history = row.get(
        "Forecast vs Historical %",
        np.nan
    )

    forecast_volatility = row.get(
        "Forecast Volatility %",
        np.nan
    )

    st.markdown(
        f"### {selected_insurer}"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Historical Avg Premium",
            f"₹{avg_premium / 1e7:.2f} Cr"
        )

    with c2:
        st.metric(
            "Historical Growth",
            f"{historical_growth:.2f}%"
        )

    with c3:
        st.metric(
            "12-Month Forecast",
            f"₹{forecast_total / 1e7:.2f} Cr"
        )

    with c4:
        st.metric(
            "Forecast vs Historical",
            f"{forecast_vs_history:.2f}%"
        )

    c5, c6 = st.columns(2)

    with c5:
        st.metric(
            "Average Monthly Forecast",
            f"₹{avg_forecast / 1e7:.2f} Cr"
        )

    with c6:
        st.metric(
            "Forecast Volatility",
            f"{forecast_volatility:.2f}%"
        )

# ============================================================
# HISTORICAL TREND
# ============================================================

st.subheader("Historical Renewal Premium")

chart_df = insurer_monthly[
    [
        "collection_month",
        "renewed_premium"
    ]
].copy()

chart_df = chart_df.set_index(
    "collection_month"
)

chart_df["renewed_premium"] = (
    chart_df["renewed_premium"] / 1e7
)

st.line_chart(
    chart_df,
    y="renewed_premium"
)

# ============================================================
# RENEWAL RATE
# ============================================================

st.subheader("Renewal Rate Trend")

rate_df = insurer_monthly[
    [
        "collection_month",
        "renewal_rate"
    ]
].copy()

rate_df = rate_df.set_index(
    "collection_month"
)

st.line_chart(
    rate_df,
    y="renewal_rate"
)

# ============================================================
# PREMIUM VS POLICIES
# ============================================================

st.subheader("Premium vs Renewed Policies")

comparison_df = insurer_monthly[
    [
        "collection_month",
        "renewed_policies",
        "renewed_premium"
    ]
].copy()

comparison_df["renewed_premium"] = (
    comparison_df["renewed_premium"] / 1e7
)

comparison_df = comparison_df.set_index(
    "collection_month"
)

st.dataframe(
    comparison_df,
    use_container_width=True
)
st.divider()
# ============================================================
# AUTOMATIC BUSINESS INSIGHTS
# ============================================================

st.subheader("Key Business Insights")

if not insurer_business.empty:

    row = insurer_business.iloc[0]

    historical_avg = row[
        "Historical Avg Premium"
    ]

    forecast_avg = row[
        "Average Forecast"
    ]

    growth = row[
        "Historical Growth %"
    ]

    forecast_change = row[
        "Forecast vs Historical %"
    ]

    volatility = row[
        "Forecast Volatility %"
    ]

    # --------------------------------------------------------
    # INSIGHT 1
    # --------------------------------------------------------

    st.info(
        f"""
        **Premium Performance**

        {selected_insurer} has an historical average
        monthly renewed premium of approximately
        **₹{historical_avg / 1e7:.2f} Cr**.
        """
    )

    # --------------------------------------------------------
    # INSIGHT 2
    # --------------------------------------------------------

    if growth > 0:

        st.success(
            f"""
            **Historical Growth**

            The insurer shows historical premium growth
            of approximately **{growth:.2f}%** over the
            available historical period.
            """
        )

    else:

        st.warning(
            f"""
            **Historical Growth**

            The historical premium growth is
            **{growth:.2f}%**.
            """
        )

    # --------------------------------------------------------
    # INSIGHT 3
    # --------------------------------------------------------

    if forecast_change > 0:

        st.success(
            f"""
            **Forecast Outlook**

            The average forecast is approximately
            **{forecast_change:.2f}% higher** than the
            historical average.
            """
        )

    else:

        st.warning(
            f"""
            **Forecast Outlook**

            The average forecast is approximately
            **{abs(forecast_change):.2f}% lower** than the
            historical average.
            """
        )

    # --------------------------------------------------------
    # INSIGHT 4
    # --------------------------------------------------------

    st.info(
        f"""
        **Forecast Stability**

        Forecast volatility is approximately
        **{volatility:.2f}%** across the forecast period.
        """
    )
st.divider()
# ============================================================
# INSURER COMPARISON
# ============================================================

st.subheader("Insurer Comparison")

comparison_columns = [
    "Insurer",
    "Historical Avg Premium",
    "Historical Growth %",
    "12 Month Forecast",
    "Forecast vs Historical %",
    "Forecast Volatility %"
]

available_columns = [
    col
    for col in comparison_columns
    if col in business.columns
]

comparison = business[
    available_columns
].copy()

if "Historical Avg Premium" in comparison.columns:
    comparison["Historical Avg Premium"] = (
        comparison["Historical Avg Premium"] / 1e7
    )

if "12 Month Forecast" in comparison.columns:
    comparison["12 Month Forecast"] = (
        comparison["12 Month Forecast"] / 1e7
    )

comparison = comparison.round(2)

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# DOWNLOAD
# ============================================================

st.subheader("⬇️ Download")

csv_data = business.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Business Insights CSV",
    csv_data,
    "business_insights.csv",
    "text/csv"
)