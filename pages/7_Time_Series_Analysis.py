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

st.title("Time Series Analysis")

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

st.sidebar.header("Time Series Controls")


rolling_window = st.sidebar.slider(
    "Rolling Mean Window",
    min_value=2,
    max_value=12,
    value=3
)


# ============================================================
# BASIC INFORMATION
# ============================================================

st.subheader("Time Series Information")

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

st.subheader("1. Monthly Renewed Premium")

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
    f"2. Rolling Mean ({rolling_window}-Month)"
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



# ============================================================
# 3. MONTHLY SEASONALITY
# ============================================================

st.subheader("3. Monthly Seasonality")

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




# ============================================================
# 4. MONTH-OVER-MONTH CHANGE
# ============================================================

st.subheader("4. Month-over-Month Change")

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

st.subheader("5. First-Order Differencing")

diff_ts = ts.diff().dropna()

diff_df = pd.DataFrame({
    "Original": ts,
    "First Difference": diff_ts
})

st.line_chart(
    diff_df["First Difference"]
)





# ============================================================
# 9. TIME SERIES STATISTICS
# ============================================================

st.subheader("6. Time Series Statistics")

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
# DOWNLOAD
# ============================================================



csv_data = df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Time Series Data",
    data=csv_data,
    file_name="time_series_analysis.csv",
    mime="text/csv"
)