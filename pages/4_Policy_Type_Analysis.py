import streamlit as st
import pandas as pd
import os


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Policy Type Analysis",
    page_icon="📋",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📋 Policy Type Analysis")



st.divider()


# ============================================================
# DATA PATH
# ============================================================

POLICY_FILE = "data/processed/monthly_by_policy_type.csv"


# ============================================================
# CHECK FILE
# ============================================================

if not os.path.exists(POLICY_FILE):

    st.error(
        f"Dataset not found:\n\n`{POLICY_FILE}`"
    )

    st.info(
        "Make sure monthly_by_policy_type.csv is inside "
        "data/processed/"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(POLICY_FILE)

df.columns = df.columns.str.strip()


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "collection_month",
    "policy_type",
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
    ["policy_type", "collection_month"]
).reset_index(drop=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔎 Policy Filters")


# ============================================================
# POLICY TYPE SELECTOR
# ============================================================

policy_types = sorted(
    df["policy_type"].dropna().unique()
)

selected_policy_type = st.sidebar.selectbox(
    "Select Policy Type",
    policy_types
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

policy_df = df[
    df["policy_type"] == selected_policy_type
].copy()


if len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    policy_df = policy_df[
        (policy_df["collection_month"] >= start_date)
        &
        (policy_df["collection_month"] <= end_date)
    ]


# ============================================================
# EMPTY CHECK
# ============================================================

if policy_df.empty:

    st.warning(
        "No data available for the selected filters."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.header(
    f"📌 {selected_policy_type}"
)

st.caption(
    f"{len(policy_df)} monthly observations"
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_policies = policy_df[
    "total_policies"
].sum()

renewed_policies = policy_df[
    "renewed_policies"
].sum()

total_premium = policy_df[
    "total_premium"
].sum()

renewed_premium = policy_df[
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

renewal_chart = policy_df[
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

premium_chart = policy_df[
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

st.line_chart(premium_chart)


# ============================================================
# POLICY TREND
# ============================================================

st.subheader("📋 Monthly Policy Performance")

policy_chart = policy_df[
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

st.line_chart(policy_chart)


# ============================================================
# RENEWAL RATE BAR CHART
# ============================================================

st.subheader("📊 Renewal Rate by Month")

rate_chart = policy_df[
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

best_idx = policy_df[
    "renewal_rate"
].idxmax()

worst_idx = policy_df[
    "renewal_rate"
].idxmin()

best_month = policy_df.loc[best_idx]
worst_month = policy_df.loc[worst_idx]


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
# POLICY TYPE COMPARISON
# ============================================================

st.divider()

st.subheader("🔄 Policy Type Comparison")

comparison = (
    df.groupby("policy_type")
    .agg(
        total_policies=("total_policies", "sum"),
        renewed_policies=("renewed_policies", "sum"),
        total_premium=("total_premium", "sum"),
        renewed_premium=("renewed_premium", "sum")
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


comparison = comparison.sort_values(
    "renewal_rate",
    ascending=False
)


# ============================================================
# COMPARISON CHART
# ============================================================

comparison_chart = comparison[
    [
        "policy_type",
        "renewal_rate"
    ]
].set_index("policy_type")


st.bar_chart(comparison_chart)


# ============================================================
# COMPARISON TABLE
# ============================================================

display_comparison = comparison.copy()

display_comparison["total_premium"] = (
    display_comparison["total_premium"] / 1e7
)

display_comparison["renewed_premium"] = (
    display_comparison["renewed_premium"] / 1e7
)


display_comparison = display_comparison.rename(
    columns={
        "policy_type": "Policy Type",
        "total_policies": "Total Policies",
        "renewed_policies": "Renewed Policies",
        "total_premium": "Total Premium (₹ Cr)",
        "renewed_premium": "Renewed Premium (₹ Cr)",
        "renewal_rate": "Renewal Rate (%)",
        "premium_renewal_rate": "Premium Renewal Rate (%)"
    }
)


st.dataframe(
    display_comparison,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# MONTHLY DATA TABLE
# ============================================================

st.divider()

st.subheader("📄 Monthly Policy Type Data")

display_df = policy_df.copy()

display_df["total_premium"] = (
    display_df["total_premium"] / 1e7
)

display_df["renewed_premium"] = (
    display_df["renewed_premium"] / 1e7
)


display_df = display_df.rename(
    columns={
        "collection_month": "Month",
        "policy_type": "Policy Type",
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

csv_data = policy_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Policy Type Data",
    data=csv_data,
    file_name=f"{selected_policy_type}_monthly_analysis.csv",
    mime="text/csv"
)