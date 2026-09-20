import streamlit as st
import pandas as pd
import os


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Insurer Analysis",
    page_icon="🏢",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🏢 Insurer Analysis")


st.divider()


# ============================================================
# DATA PATH
# ============================================================

INSURER_FILE = "data/processed/monthly_by_insurer.csv"


# ============================================================
# CHECK FILE
# ============================================================

if not os.path.exists(INSURER_FILE):

    st.error(
        f"Dataset not found:\n\n`{INSURER_FILE}`"
    )

    st.info(
        "Make sure monthly_by_insurer.csv is inside "
        "data/processed/"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INSURER_FILE)

df.columns = df.columns.str.strip()


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "collection_month",
    "insurer",
    "total_policies",
    "renewed_policies",
    "total_premium",
    "renewed_premium",
    "renewal_rate"
]


missing_columns = [
    col for col in required_columns
    if col not in df.columns
]


if missing_columns:

    st.error(
        f"Missing columns: {missing_columns}"
    )

    st.write("Available columns:")

    st.write(df.columns.tolist())

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
    ["insurer", "collection_month"]
).reset_index(drop=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔎 Insurer Filters")


# ============================================================
# INSURER SELECTOR
# ============================================================

insurers = sorted(
    df["insurer"].dropna().unique()
)


selected_insurer = st.sidebar.selectbox(
    "Select Insurer",
    insurers
)


# ============================================================
# DATE FILTER
# ============================================================

min_date = df["collection_month"].min()
max_date = df["collection_month"].max()


date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date()
)


# ============================================================
# FILTER DATA
# ============================================================

insurer_df = df[
    df["insurer"] == selected_insurer
].copy()


if len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])

    end_date = pd.Timestamp(date_range[1])


    insurer_df = insurer_df[
        (insurer_df["collection_month"] >= start_date)
        &
        (insurer_df["collection_month"] <= end_date)
    ]


# ============================================================
# NO DATA CHECK
# ============================================================

if insurer_df.empty:

    st.warning(
        "No data available for the selected filters."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.header(
    f"📌 {selected_insurer}"
)


st.caption(
    f"{len(insurer_df)} monthly observations"
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_policies = insurer_df[
    "total_policies"
].sum()


renewed_policies = insurer_df[
    "renewed_policies"
].sum()


total_premium = insurer_df[
    "total_premium"
].sum()


renewed_premium = insurer_df[
    "renewed_premium"
].sum()


overall_renewal_rate = (
    renewed_policies / total_policies * 100
    if total_policies > 0
    else 0
)


premium_renewal_rate = (
    renewed_premium / total_premium * 100
    if total_premium > 0
    else 0
)


average_premium = (
    total_premium / total_policies
    if total_policies > 0
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
        f"{overall_renewal_rate:.2f}%"
    )


with col4:

    st.metric(
        "Renewed Premium",
        f"₹{renewed_premium / 1e7:.2f} Cr"
    )


# ============================================================
# SECOND KPI ROW
# ============================================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Premium",
        f"₹{total_premium / 1e7:.2f} Cr"
    )


with col2:

    st.metric(
        "Average Premium / Policy",
        f"₹{average_premium:,.0f}"
    )


with col3:

    st.metric(
        "Premium Renewal Rate",
        f"{premium_renewal_rate:.2f}%"
    )


st.divider()


# ============================================================
# MONTHLY RENEWAL RATE
# ============================================================

st.subheader("📈 Monthly Renewal Rate")


renewal_chart = insurer_df[
    ["collection_month", "renewal_rate"]
].copy()


renewal_chart = renewal_chart.set_index(
    "collection_month"
)


st.line_chart(
    renewal_chart["renewal_rate"]
)


# ============================================================
# PREMIUM TREND
# ============================================================

st.subheader("💰 Monthly Premium Performance")


premium_chart = insurer_df[
    [
        "collection_month",
        "total_premium",
        "renewed_premium"
    ]
].copy()


premium_chart = premium_chart.set_index(
    "collection_month"
)


premium_chart = premium_chart / 1e7


premium_chart.columns = [
    "Total Premium (₹ Cr)",
    "Renewed Premium (₹ Cr)"
]


st.line_chart(
    premium_chart
)


# ============================================================
# POLICY TREND
# ============================================================

st.subheader("📋 Monthly Policy Performance")


policy_chart = insurer_df[
    [
        "collection_month",
        "total_policies",
        "renewed_policies"
    ]
].copy()


policy_chart = policy_chart.set_index(
    "collection_month"
)


policy_chart.columns = [
    "Total Policies",
    "Renewed Policies"
]


st.line_chart(
    policy_chart
)


# ============================================================
# RENEWAL RATE BY MONTH
# ============================================================

st.subheader("📊 Monthly Renewal Rate")


rate_chart = insurer_df[
    ["collection_month", "renewal_rate"]
].copy()


rate_chart = rate_chart.set_index(
    "collection_month"
)


st.bar_chart(
    rate_chart["renewal_rate"]
)


# ============================================================
# PERFORMANCE HIGHLIGHTS
# ============================================================

st.subheader("📅 Performance Highlights")


best_idx = insurer_df[
    "renewal_rate"
].idxmax()


worst_idx = insurer_df[
    "renewal_rate"
].idxmin()


best_month = insurer_df.loc[best_idx]

worst_month = insurer_df.loc[worst_idx]


col1, col2 = st.columns(2)


with col1:

    st.success(
        f"""
        **Highest Renewal Rate**

        **Month:** {best_month["collection_month"].strftime("%B %Y")}

        **Renewal Rate:** {best_month["renewal_rate"]:.2f}%

        **Renewed Policies:** {best_month["renewed_policies"]:,.0f}
        """
    )


with col2:

    st.warning(
        f"""
        **Lowest Renewal Rate**

        **Month:** {worst_month["collection_month"].strftime("%B %Y")}

        **Renewal Rate:** {worst_month["renewal_rate"]:.2f}%

        **Renewed Policies:** {worst_month["renewed_policies"]:,.0f}
        """
    )


# ============================================================
# DATA TABLE
# ============================================================

st.divider()

st.subheader("📄 Monthly Insurer Data")


display_df = insurer_df.copy()


display_df["total_premium"] = (
    display_df["total_premium"] / 1e7
)


display_df["renewed_premium"] = (
    display_df["renewed_premium"] / 1e7
)


display_df = display_df.rename(
    columns={
        "collection_month": "Month",
        "insurer": "Insurer",
        "total_policies": "Total Policies",
        "renewed_policies": "Renewed Policies",
        "total_premium": "Total Premium (₹ Cr)",
        "renewed_premium": "Renewed Premium (₹ Cr)",
        "renewal_rate": "Renewal Rate (%)"
    }
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD
# ============================================================

csv_data = insurer_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Insurer Data",
    data=csv_data,
    file_name=f"{selected_insurer}_monthly_analysis.csv",
    mime="text/csv"
)