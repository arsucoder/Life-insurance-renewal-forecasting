import streamlit as st
import pandas as pd
import os


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Duration Bucket Analysis",
    page_icon="⏳",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("⏳ Policy Duration Analysis")

st.markdown(
    """
    Analyze renewal premium collection, policy volume, and
    renewal performance across different policy duration buckets.
    """
)

st.divider()


# ============================================================
# DATA PATH
# ============================================================

DURATION_FILE = (
    "data/processed/monthly_by_duration_bucket.csv"
)


# ============================================================
# CHECK FILE
# ============================================================

if not os.path.exists(DURATION_FILE):

    st.error(
        f"Dataset not found:\n\n`{DURATION_FILE}`"
    )

    st.info(
        "Run the aggregation script to create "
        "monthly_by_duration_bucket.csv."
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DURATION_FILE)

df.columns = df.columns.str.strip()


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "collection_month",
    "duration_bucket",
    "total_policies",
    "renewed_policies",
    "total_premium",
    "renewed_premium",
    "renewal_rate"
]


missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]


if missing_columns:

    st.error(
        f"Missing columns: {missing_columns}"
    )

    st.write(
        "Available columns:",
        df.columns.tolist()
    )

    st.stop()


# ============================================================
# DATE CONVERSION
# ============================================================

df["collection_month"] = pd.to_datetime(
    df["collection_month"],
    errors="coerce"
)


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    [
        "duration_bucket",
        "collection_month"
    ]
).reset_index(drop=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔎 Duration Filters")


duration_buckets = sorted(
    df["duration_bucket"]
    .dropna()
    .unique()
)


selected_duration = st.sidebar.selectbox(
    "Select Duration Bucket",
    duration_buckets
)


# ============================================================
# DATE FILTER
# ============================================================

min_date = df["collection_month"].min()
max_date = df["collection_month"].max()


date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(
        min_date.date(),
        max_date.date()
    ),
    min_value=min_date.date(),
    max_value=max_date.date()
)


# ============================================================
# FILTER DATA
# ============================================================

duration_df = df[
    df["duration_bucket"] == selected_duration
].copy()


if len(date_range) == 2:

    start_date = pd.Timestamp(
        date_range[0]
    )

    end_date = pd.Timestamp(
        date_range[1]
    )

    duration_df = duration_df[
        (
            duration_df["collection_month"]
            >= start_date
        )
        &
        (
            duration_df["collection_month"]
            <= end_date
        )
    ]


# ============================================================
# EMPTY CHECK
# ============================================================

if duration_df.empty:

    st.warning(
        "No data available for the selected filters."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.header(
    f"📌 {selected_duration}"
)

st.caption(
    f"{len(duration_df)} monthly observations"
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_policies = duration_df[
    "total_policies"
].sum()

renewed_policies = duration_df[
    "renewed_policies"
].sum()

total_premium = duration_df[
    "total_premium"
].sum()

renewed_premium = duration_df[
    "renewed_premium"
].sum()


renewal_rate = (
    renewed_policies
    / total_policies
    * 100
    if total_policies > 0
    else 0
)


premium_renewal_rate = (
    renewed_premium
    / total_premium
    * 100
    if total_premium > 0
    else 0
)


# ============================================================
# KPI ROW
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Policies",
        f"{total_policies:,.0f}"
    )


with col2:

    st.metric(
        "Renewed Policies",
        f"{renewed_policies:,.0f}"
    )


with col3:

    st.metric(
        "Renewal Rate",
        f"{renewal_rate:.2f}%"
    )


with col4:

    st.metric(
        "Renewed Premium",
        f"₹{renewed_premium / 1e7:.2f} Cr"
    )


st.divider()


# ============================================================
# MONTHLY RENEWAL PREMIUM
# ============================================================

st.subheader(
    "💰 Monthly Renewed Premium"
)


premium_chart = duration_df[
    [
        "collection_month",
        "renewed_premium"
    ]
].copy()


premium_chart = premium_chart.set_index(
    "collection_month"
)


premium_chart["renewed_premium"] = (
    premium_chart["renewed_premium"]
    / 1e7
)


premium_chart.columns = [
    "Renewed Premium (₹ Cr)"
]


st.line_chart(
    premium_chart
)


# ============================================================
# MONTHLY RENEWAL RATE
# ============================================================

st.subheader(
    "📈 Monthly Renewal Rate"
)


rate_chart = duration_df[
    [
        "collection_month",
        "renewal_rate"
    ]
].copy()


rate_chart = rate_chart.set_index(
    "collection_month"
)


st.line_chart(
    rate_chart["renewal_rate"]
)


# ============================================================
# DURATION BUCKET COMPARISON
# ============================================================

st.divider()

st.subheader(
    "🔄 Duration Bucket Comparison"
)


comparison = (
    df.groupby("duration_bucket")
    .agg(
        total_policies=(
            "total_policies",
            "sum"
        ),

        renewed_policies=(
            "renewed_policies",
            "sum"
        ),

        total_premium=(
            "total_premium",
            "sum"
        ),

        renewed_premium=(
            "renewed_premium",
            "sum"
        )
    )
    .reset_index()
)


comparison["renewal_rate"] = (
    comparison["renewed_policies"]
    / comparison["total_policies"]
    * 100
)


comparison["premium_renewal_rate"] = (
    comparison["renewed_premium"]
    / comparison["total_premium"]
    * 100
)


# ============================================================
# COMPARISON CHART
# ============================================================

comparison_chart = comparison[
    [
        "duration_bucket",
        "renewal_rate"
    ]
].set_index(
    "duration_bucket"
)


st.bar_chart(
    comparison_chart
)


# ============================================================
# RENEWED PREMIUM BY DURATION
# ============================================================

st.subheader(
    "💵 Renewed Premium by Duration"
)


premium_comparison = (
    comparison[
        [
            "duration_bucket",
            "renewed_premium"
        ]
    ]
    .set_index("duration_bucket")
)


premium_comparison[
    "renewed_premium"
] = (
    premium_comparison[
        "renewed_premium"
    ] / 1e7
)


premium_comparison.columns = [
    "Renewed Premium (₹ Cr)"
]


st.bar_chart(
    premium_comparison
)


# ============================================================
# COMPARISON TABLE
# ============================================================

display_comparison = comparison.copy()


display_comparison["total_premium"] = (
    display_comparison["total_premium"]
    / 1e7
)


display_comparison["renewed_premium"] = (
    display_comparison["renewed_premium"]
    / 1e7
)


display_comparison = display_comparison.rename(
    columns={
        "duration_bucket":
            "Duration Bucket",

        "total_policies":
            "Total Policies",

        "renewed_policies":
            "Renewed Policies",

        "total_premium":
            "Total Premium (₹ Cr)",

        "renewed_premium":
            "Renewed Premium (₹ Cr)",

        "renewal_rate":
            "Renewal Rate (%)",

        "premium_renewal_rate":
            "Premium Renewal Rate (%)"
    }
)


st.dataframe(
    display_comparison.round(2),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# MONTHLY DATA
# ============================================================

st.divider()

st.subheader(
    "📄 Monthly Duration Data"
)


display_df = duration_df.copy()


display_df["total_premium"] = (
    display_df["total_premium"]
    / 1e7
)


display_df["renewed_premium"] = (
    display_df["renewed_premium"]
    / 1e7
)


display_df = display_df.rename(
    columns={
        "collection_month":
            "Month",

        "duration_bucket":
            "Duration Bucket",

        "total_policies":
            "Total Policies",

        "renewed_policies":
            "Renewed Policies",

        "total_premium":
            "Total Premium (₹ Cr)",

        "renewed_premium":
            "Renewed Premium (₹ Cr)",

        "renewal_rate":
            "Renewal Rate (%)"
    }
)


st.dataframe(
    display_df.round(2),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD
# ============================================================

csv_data = (
    duration_df
    .to_csv(index=False)
    .encode("utf-8")
)


st.download_button(
    label="⬇️ Download Duration Data",
    data=csv_data,
    file_name=(
        f"{selected_duration}_monthly_analysis.csv"
    ),
    mime="text/csv"
)