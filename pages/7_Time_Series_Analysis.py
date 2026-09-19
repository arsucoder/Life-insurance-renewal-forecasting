import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Time Series Analysis",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📈 Time Series Analysis")

st.markdown(
    """
    Analyze the historical monthly renewal-premium series
    before applying forecasting models such as ARIMA,
    SARIMA and Prophet.
    """
)

st.divider()


# ============================================================
# DATA PATH
# ============================================================

DATA_FILE = "data/processed/monthly_renewal_premium.csv"


if not os.path.exists(DATA_FILE):

    st.error(
        f"Dataset not found:\n\n`{DATA_FILE}`"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_FILE)

df.columns = df.columns.str.strip()


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "collection_month",
    "renewed_premium"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:

    st.error(f"Missing columns: {missing}")

    st.write(
        "Available columns:",
        df.columns.tolist()
    )

    st.stop()


# ============================================================
# PREPROCESS
# ============================================================

df["collection_month"] = pd.to_datetime(
    df["collection_month"],
    errors="coerce"
)

df["renewed_premium"] = pd.to_numeric(
    df["renewed_premium"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "collection_month",
        "renewed_premium"
    ]
)

df = df.sort_values(
    "collection_month"
)


# ============================================================
# TIME SERIES
# ============================================================

ts = df.set_index(
    "collection_month"
)["renewed_premium"]

ts = ts.asfreq("MS")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔎 Time Series Controls")


rolling_window = st.sidebar.slider(
    "Rolling Mean Window",
    min_value=2,
    max_value=12,
    value=3
)


# ============================================================
# BASIC INFORMATION
# ============================================================

st.subheader("📋 Time Series Information")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Observations",
        f"{len(ts):,}"
    )

with col2:

    st.metric(
        "Start",
        ts.index.min().strftime("%b %Y")
    )

with col3:

    st.metric(
        "End",
        ts.index.max().strftime("%b %Y")
    )

with col4:

    st.metric(
        "Average Premium",
        f"₹{ts.mean()/1e7:.2f} Cr"
    )


st.divider()


# ============================================================
# 1. ORIGINAL TIME SERIES
# ============================================================

st.subheader("1️⃣ Monthly Renewed Premium")

chart_df = pd.DataFrame({
    "Renewed Premium": ts
})

st.line_chart(
    chart_df
)

st.caption(
    "This is the original monthly renewed-premium time series "
    "used for forecasting."
)


# ============================================================
# 2. ROLLING MEAN
# ============================================================

st.subheader(
    f"2️⃣ Rolling Mean ({rolling_window}-Month)"
)

rolling_mean = ts.rolling(
    window=rolling_window
).mean()

rolling_df = pd.DataFrame({
    "Actual": ts,
    "Rolling Mean": rolling_mean
})

st.line_chart(
    rolling_df
)

st.info(
    """
    The rolling mean smooths short-term fluctuations.
    If the rolling mean moves consistently upward or downward,
    it indicates an underlying trend.
    """
)


# ============================================================
# 3. MONTHLY SEASONALITY
# ============================================================

st.subheader("3️⃣ Monthly Seasonality")

seasonal_df = pd.DataFrame({
    "month": ts.index.month,
    "premium": ts.values
})

monthly_avg = (
    seasonal_df
    .groupby("month")["premium"]
    .mean()
)

month_names = [
    "Jan", "Feb", "Mar",
    "Apr", "May", "Jun",
    "Jul", "Aug", "Sep",
    "Oct", "Nov", "Dec"
]

monthly_avg.index = [
    month_names[i - 1]
    for i in monthly_avg.index
]

st.bar_chart(
    monthly_avg
)

st.caption(
    "Higher values in particular months may indicate recurring "
    "seasonal behavior."
)


# ============================================================
# 4. MONTH-OVER-MONTH CHANGE
# ============================================================

st.subheader("4️⃣ Month-over-Month Change")

mom_change = ts.pct_change() * 100

mom_df = pd.DataFrame({
    "MoM Change (%)": mom_change
})

st.line_chart(
    mom_df
)


# ============================================================
# 5. DIFFERENCING
# ============================================================

st.subheader("5️⃣ First-Order Differencing")

diff_ts = ts.diff().dropna()

diff_df = pd.DataFrame({
    "Original": ts,
    "First Difference": diff_ts
})

st.line_chart(
    diff_df["First Difference"]
)

st.info(
    """
    Differencing removes much of the trend from a time series.
    ARIMA/SARIMA models commonly use differencing to make a
    series more stationary.
    """
)


# ============================================================
# 6. STATIONARITY - ADF TEST
# ============================================================

st.subheader("6️⃣ Stationarity Test — Augmented Dickey-Fuller")

try:

    adf_original = adfuller(
        ts.dropna()
    )

    adf_diff = adfuller(
        diff_ts.dropna()
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Original Series")

        st.write(
            f"ADF Statistic: "
            f"**{adf_original[0]:.4f}**"
        )

        st.write(
            f"P-value: "
            f"**{adf_original[1]:.4f}**"
        )

        if adf_original[1] < 0.05:

            st.success(
                "Likely stationary (p < 0.05)"
            )

        else:

            st.warning(
                "Likely non-stationary (p ≥ 0.05)"
            )

    with col2:

        st.markdown("### First Difference")

        st.write(
            f"ADF Statistic: "
            f"**{adf_diff[0]:.4f}**"
        )

        st.write(
            f"P-value: "
            f"**{adf_diff[1]:.4f}**"
        )

        if adf_diff[1] < 0.05:

            st.success(
                "Likely stationary (p < 0.05)"
            )

        else:

            st.warning(
                "Still likely non-stationary"
            )

except Exception as e:

    st.warning(
        f"ADF test could not be calculated: {e}"
    )


# ============================================================
# 7. ACF
# ============================================================

st.subheader("7️⃣ Autocorrelation — ACF")

fig, ax = plt.subplots(
    figsize=(12, 4)
)

plot_acf(
    ts.dropna(),
    lags=min(20, len(ts)//2 - 1),
    ax=ax
)

ax.set_title(
    "Autocorrelation Function"
)

st.pyplot(
    fig,
    clear_figure=True
)


st.caption(
    """
    ACF shows how strongly the current value is related
    to previous observations. Strong spikes at particular
    lags can indicate time-series dependence or seasonality.
    """
)


# ============================================================
# 8. PACF
# ============================================================

st.subheader("8️⃣ Partial Autocorrelation — PACF")

fig, ax = plt.subplots(
    figsize=(12, 4)
)

plot_pacf(
    ts.dropna(),
    lags=min(20, len(ts)//2 - 1),
    ax=ax,
    method="ywm"
)

ax.set_title(
    "Partial Autocorrelation Function"
)

st.pyplot(
    fig,
    clear_figure=True
)


st.caption(
    """
    PACF helps identify the relationship between an observation
    and its lagged values after removing the effect of
    intermediate lags. It is useful when selecting ARIMA/SARIMA
    parameters.
    """
)


# ============================================================
# 9. TIME SERIES STATISTICS
# ============================================================

st.subheader("9️⃣ Time Series Statistics")

stats_df = pd.DataFrame({
    "Metric": [
        "Mean",
        "Median",
        "Standard Deviation",
        "Minimum",
        "Maximum",
        "Variance"
    ],
    "Value": [
        ts.mean(),
        ts.median(),
        ts.std(),
        ts.min(),
        ts.max(),
        ts.var()
    ]
})


stats_df["Value"] = (
    stats_df["Value"] / 1e7
)


stats_df["Value"] = stats_df[
    "Value"
].round(2)


st.dataframe(
    stats_df,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# 10. INTERPRETATION
# ============================================================

st.subheader("🧠 Time Series Interpretation")

st.markdown(
    """
    ### What we are checking

    **Trend**
    - Does renewed premium increase or decrease over time?

    **Seasonality**
    - Do certain months repeatedly show higher or lower
      renewal premiums?

    **Stationarity**
    - Does the statistical behavior of the series remain
      relatively stable over time?

    **Autocorrelation**
    - Does the current month's premium depend on previous
      months?

    **Differencing**
    - Can we remove trend and make the series more suitable
      for ARIMA/SARIMA?

    ### Connection with our forecasting models

    | Model | What it uses |
    |---|---|
    | Naive | Previous observation |
    | Seasonal Naive | Previous seasonal observation |
    | ARIMA | Autoregression + differencing + moving average |
    | SARIMA | ARIMA + seasonality |
    | Prophet | Trend + seasonality + changepoints |
    """
)


# ============================================================
# DOWNLOAD
# ============================================================

st.divider()

csv_data = df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Time Series Data",
    data=csv_data,
    file_name="time_series_analysis.csv",
    mime="text/csv"
)