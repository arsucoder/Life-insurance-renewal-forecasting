import streamlit as st
import pandas as pd
import os


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Yearly Analysis",
    page_icon="📅",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("Yearly Insurance Analysis")

st.divider()


# ============================================================
# DATA PATH
# ============================================================

YEARLY_FILE = "data/processed/yearly_renewal_premium.csv"


# ============================================================
# CHECK FILE
# ============================================================

if not os.path.exists(YEARLY_FILE):

    st.error(
        f"Dataset not found:\n\n`{YEARLY_FILE}`"
    )

    st.info(
        "Make sure yearly_renewal_premium.csv is inside "
        "data/processed/"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(YEARLY_FILE)

df.columns = df.columns.str.strip()


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "financial_year",
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
# CLEAN DATA
# ============================================================

numeric_columns = [
    "total_policies",
    "renewed_policies",
    "total_premium",
    "renewed_premium",
    "renewal_rate"
]


for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


df = df.dropna(
    subset=["financial_year"]
)


# ============================================================
# SORT
# ============================================================

df = df.reset_index(drop=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(" Yearly Filters")


# ============================================================
# FINANCIAL YEAR SELECTOR
# ============================================================

financial_years = df[
    "financial_year"
].astype(str).tolist()


selected_year = st.sidebar.selectbox(
    "Select Financial Year",
    ["All Years"] + financial_years
)


# ============================================================
# FILTER
# ============================================================

if selected_year == "All Years":

    yearly_df = df.copy()

else:

    yearly_df = df[
        df["financial_year"].astype(str)
        == selected_year
    ].copy()


if yearly_df.empty:

    st.warning(
        "No data available for the selected year."
    )

    st.stop()


# ============================================================
# OVERALL CALCULATIONS
# ============================================================

total_policies = yearly_df[
    "total_policies"
].sum()

renewed_policies = yearly_df[
    "renewed_policies"
].sum()

total_premium = yearly_df[
    "total_premium"
].sum()

renewed_premium = yearly_df[
    "renewed_premium"
].sum()


overall_renewal_rate = (
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


average_premium = (
    total_premium
    / total_policies
    if total_policies > 0
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("Key Performance Indicators")


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
# YEARLY RENEWAL RATE
# ============================================================

st.subheader(" 1. Renewal Rate by Financial Year")


renewal_chart = yearly_df[
    [
        "financial_year",
        "renewal_rate"
    ]
].copy()


renewal_chart["financial_year"] = (
    renewal_chart["financial_year"].astype(str)
)


renewal_chart = renewal_chart.set_index(
    "financial_year"
)


st.line_chart(
    renewal_chart["renewal_rate"]
)


# ============================================================
# PREMIUM TREND
# ============================================================

st.subheader(" 2. Yearly Premium Performance")


premium_chart = yearly_df[
    [
        "financial_year",
        "total_premium",
        "renewed_premium"
    ]
].copy()


premium_chart["financial_year"] = (
    premium_chart["financial_year"].astype(str)
)


premium_chart = premium_chart.set_index(
    "financial_year"
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

st.subheader(" 3. Yearly Policy Performance")


policy_chart = yearly_df[
    [
        "financial_year",
        "total_policies",
        "renewed_policies"
    ]
].copy()


policy_chart["financial_year"] = (
    policy_chart["financial_year"].astype(str)
)


policy_chart = policy_chart.set_index(
    "financial_year"
)


policy_chart.columns = [
    "Total Policies",
    "Renewed Policies"
]


st.line_chart(
    policy_chart
)


# ============================================================
# YEARLY RENEWAL RATE BAR CHART
# ============================================================

st.subheader(" 4. Yearly Renewal Rate")


bar_chart = yearly_df[
    [
        "financial_year",
        "renewal_rate"
    ]
].copy()


bar_chart["financial_year"] = (
    bar_chart["financial_year"].astype(str)
)


bar_chart = bar_chart.set_index(
    "financial_year"
)


st.bar_chart(
    bar_chart["renewal_rate"]
)


# ============================================================
# YEAR-OVER-YEAR GROWTH
# ============================================================

st.subheader(" 5. Year-over-Year Growth")


growth_df = df.copy()


growth_df["total_premium_growth"] = (
    growth_df["total_premium"]
    .pct_change()
    * 100
)


growth_df["renewed_premium_growth"] = (
    growth_df["renewed_premium"]
    .pct_change()
    * 100
)


growth_df["policy_growth"] = (
    growth_df["total_policies"]
    .pct_change()
    * 100
)


growth_df["financial_year"] = (
    growth_df["financial_year"].astype(str)
)


growth_chart = growth_df[
    [
        "financial_year",
        "total_premium_growth",
        "renewed_premium_growth",
        "policy_growth"
    ]
].copy()


growth_chart = growth_chart.set_index(
    "financial_year"
)


growth_chart.columns = [
    "Total Premium Growth (%)",
    "Renewed Premium Growth (%)",
    "Policy Growth (%)"
]


st.line_chart(
    growth_chart
)


# ============================================================
# BEST / WORST YEAR
# ============================================================

if len(df) > 1:

    best_idx = df[
        "renewal_rate"
    ].idxmax()

    worst_idx = df[
        "renewal_rate"
    ].idxmin()

    best_year = df.loc[best_idx]

    worst_year = df.loc[worst_idx]

    st.subheader("Yearly Performance Highlights")

    col1, col2 = st.columns(2)


    with col1:

        st.success(
            f"""
            **Highest Renewal Rate**

            Financial Year:
            **{best_year["financial_year"]}**

            Renewal Rate:
            **{best_year["renewal_rate"]:.2f}%**

            Renewed Premium:
            **₹{best_year["renewed_premium"] / 1e7:.2f} Cr**
            """
        )


    with col2:

        st.warning(
            f"""
            **Lowest Renewal Rate**

            Financial Year:
            **{worst_year["financial_year"]}**

            Renewal Rate:
            **{worst_year["renewal_rate"]:.2f}%**

            Renewed Premium:
            **₹{worst_year["renewed_premium"] / 1e7:.2f} Cr**
            """
        )


# ============================================================
# COMPLETE YEARLY TABLE
# ============================================================

st.divider()

st.subheader("Yearly Data")


display_df = df.copy()


display_df["total_premium"] = (
    display_df["total_premium"] / 1e7
)


display_df["renewed_premium"] = (
    display_df["renewed_premium"] / 1e7
)


display_df = display_df.rename(
    columns={
        "financial_year": "Financial Year",
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

csv_data = df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Yearly Analysis",
    data=csv_data,
    file_name="yearly_insurance_analysis.csv",
    mime="text/csv"
)