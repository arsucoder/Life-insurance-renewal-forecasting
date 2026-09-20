import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Life Insurance Forecasting",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# FILE PATHS
# ============================================================

POLICY_DATA_PATH = (
    "data/processed/Insurance_renewal_preprocessed.csv"
)

MONTHLY_DATA_PATH = (
    "data/processed/monthly_renewal_premium.csv"
)

INSURER_DATA_PATH = (
    "data/processed/monthly_by_insurer.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

try:

    policy_df = pd.read_csv(
        POLICY_DATA_PATH
    )

    monthly_df = pd.read_csv(
        MONTHLY_DATA_PATH
    )

    insurer_df = pd.read_csv(
        INSURER_DATA_PATH
    )

except FileNotFoundError as e:

    st.error(
        f"Dataset not found.\n\n{e}"
    )

    st.stop()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

policy_df.columns = (
    policy_df.columns
    .str.strip()
    .str.lower()
)

monthly_df.columns = (
    monthly_df.columns
    .str.strip()
    .str.lower()
)

insurer_df.columns = (
    insurer_df.columns
    .str.strip()
    .str.lower()
)


# ============================================================
# DATE CONVERSION
# ============================================================

if "collection_date" in policy_df.columns:

    policy_df["collection_date"] = pd.to_datetime(
        policy_df["collection_date"],
        errors="coerce"
    )

if "collection_month" in policy_df.columns:

    policy_df["collection_month"] = pd.to_datetime(
        policy_df["collection_month"],
        errors="coerce"
    )

if "collection_month" in monthly_df.columns:

    monthly_df["collection_month"] = pd.to_datetime(
        monthly_df["collection_month"],
        errors="coerce"
    )

if "collection_month" in insurer_df.columns:

    insurer_df["collection_month"] = pd.to_datetime(
        insurer_df["collection_month"],
        errors="coerce"
    )


# ============================================================
# CLEAN INSURER NAMES
# ============================================================

if "insurer" in policy_df.columns:

    policy_df["insurer"] = (
        policy_df["insurer"]
        .astype(str)
        .str.strip()
    )

if "insurer" in insurer_df.columns:

    insurer_df["insurer"] = (
        insurer_df["insurer"]
        .astype(str)
        .str.strip()
    )


# ============================================================
# NUMERIC COLUMNS
# ============================================================

for column in [
    "premium_amount",
    "renewal_flag",
    "customer_age"
]:

    if column in policy_df.columns:

        policy_df[column] = pd.to_numeric(
            policy_df[column],
            errors="coerce"
        )


for column in [
    "total_policies",
    "renewed_policies",
    "total_premium",
    "renewed_premium",
    "renewal_rate"
]:

    if column in monthly_df.columns:

        monthly_df[column] = pd.to_numeric(
            monthly_df[column],
            errors="coerce"
        )

    if column in insurer_df.columns:

        insurer_df[column] = pd.to_numeric(
            insurer_df[column],
            errors="coerce"
        )


# ============================================================
# TITLE
# ============================================================

st.title(
    " Life Insurance Renewal Intelligence"
)


st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")

insurer_list = sorted(
    insurer_df["insurer"]
    .dropna()
    .unique()
    .tolist()
)

selected_insurer = st.sidebar.selectbox(
    "Select Insurer",
    ["All Insurers"] + insurer_list
)


# ============================================================
# FILTER INSURER DATA
# ============================================================

if selected_insurer == "All Insurers":

    filtered_insurer_df = insurer_df.copy()

else:

    filtered_insurer_df = insurer_df[
        insurer_df["insurer"] == selected_insurer
    ].copy()


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Records",
        f"{len(policy_df):,}"
    )


with col2:

    st.metric(
        "Number of Insurers",
        f"{policy_df['insurer'].nunique():,}"
    )


with col3:

    st.metric(
        "Historical Months",
        f"{policy_df['collection_month'].nunique():,}"
    )


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_policies = (
    filtered_insurer_df[
        "total_policies"
    ].sum()
)

renewed_policies = (
    filtered_insurer_df[
        "renewed_policies"
    ].sum()
)

total_premium = (
    filtered_insurer_df[
        "total_premium"
    ].sum()
)

renewed_premium = (
    filtered_insurer_df[
        "renewed_premium"
    ].sum()
)


if total_policies > 0:

    overall_renewal_rate = (
        renewed_policies
        / total_policies
        * 100
    )

else:

    overall_renewal_rate = 0


if total_premium > 0:

    premium_renewal_rate = (
        renewed_premium
        / total_premium
        * 100
    )

else:

    premium_renewal_rate = 0


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
        f"₹{renewed_premium / 1e9:.2f} B"
    )

st.divider()
# ============================================================
# PREMIUM OVERVIEW
# ============================================================

st.subheader("Premium Overview")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Premium",
        f"₹{total_premium / 1e9:.2f} B"
    )


with col2:

    st.metric(
        "Renewed Premium",
        f"₹{renewed_premium / 1e9:.2f} B"
    )


with col3:

    st.metric(
        "Premium Renewal %",
        f"{premium_renewal_rate:.2f}%"
    )

st.divider()
# ============================================================
# HISTORICAL PERIOD
# ============================================================

st.subheader("Historical Period")

col1, col2 = st.columns(2)


with col1:

    start_date = (
        filtered_insurer_df[
            "collection_month"
        ].min()
    )

    if pd.notna(start_date):

        st.metric(
            "Start Date",
            start_date.strftime("%B %Y")
        )


with col2:

    end_date = (
        filtered_insurer_df[
            "collection_month"
        ].max()
    )

    if pd.notna(end_date):

        st.metric(
            "End Date",
            end_date.strftime("%B %Y")
        )

st.divider()
# ============================================================
# MONTHLY RENEWED PREMIUM
# ============================================================

st.subheader("Monthly Renewed Premium")


monthly_premium = (
    filtered_insurer_df
    .groupby("collection_month")[
        "renewed_premium"
    ]
    .sum()
    .reset_index()
)

monthly_premium["renewed_premium_cr"] = (
    monthly_premium["renewed_premium"]
    / 1e7
)


fig = px.line(
    monthly_premium,
    x="collection_month",
    y="renewed_premium_cr",
    markers=True,
    title="Monthly Renewed Premium"
)


fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Renewed Premium (₹ Cr)",
    hovermode="x unified"
)


fig.update_traces(
    hovertemplate=
    "<b>%{x|%b %Y}</b><br>"
    "Renewed Premium: ₹%{y:.2f} Cr"
    "<extra></extra>"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# MONTHLY RENEWAL RATE
# ============================================================

st.subheader("Monthly Renewal Rate")


monthly_rate = (
    filtered_insurer_df
    .groupby("collection_month")
    .agg(
        total_policies=(
            "total_policies",
            "sum"
        ),
        renewed_policies=(
            "renewed_policies",
            "sum"
        )
    )
    .reset_index()
)


monthly_rate["renewal_rate"] = (
    monthly_rate["renewed_policies"]
    / monthly_rate["total_policies"]
    * 100
)


fig = px.line(
    monthly_rate,
    x="collection_month",
    y="renewal_rate",
    markers=True,
    title="Monthly Renewal Rate"
)


fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Renewal Rate (%)",
    hovermode="x unified"
)


fig.update_traces(
    hovertemplate=
    "<b>%{x|%b %Y}</b><br>"
    "Renewal Rate: %{y:.2f}%"
    "<extra></extra>"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# INSURER-WISE RENEWED PREMIUM
# ============================================================

st.subheader(
    "Insurer-wise Renewed Premium"
)


insurer_premium = (
    filtered_insurer_df
    .groupby("insurer")[
        "renewed_premium"
    ]
    .sum()
    .reset_index()
    .sort_values(
        "renewed_premium",
        ascending=False
    )
)


insurer_premium["renewed_premium_cr"] = (
    insurer_premium["renewed_premium"]
    / 1e7
)


fig = px.bar(
    insurer_premium,
    x="insurer",
    y="renewed_premium_cr",
    title="Total Renewed Premium by Insurer",
    text_auto=".2f"
)


fig.update_layout(
    xaxis_title="Insurer",
    yaxis_title="Renewed Premium (₹ Cr)",
    xaxis_tickangle=-35
)


fig.update_traces(
    hovertemplate=
    "<b>%{x}</b><br>"
    "Renewed Premium: ₹%{y:.2f} Cr"
    "<extra></extra>"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# INSURER-WISE RENEWAL RATE
# ============================================================

st.subheader(
    "Insurer-wise Renewal Rate"
)


insurer_rate = (
    filtered_insurer_df
    .groupby("insurer")
    .agg(
        total_policies=(
            "total_policies",
            "sum"
        ),
        renewed_policies=(
            "renewed_policies",
            "sum"
        )
    )
    .reset_index()
)


insurer_rate["renewal_rate"] = (
    insurer_rate["renewed_policies"]
    / insurer_rate["total_policies"]
    * 100
)


insurer_rate = insurer_rate.sort_values(
    "renewal_rate",
    ascending=False
)


fig = px.bar(
    insurer_rate,
    x="insurer",
    y="renewal_rate",
    title="Renewal Rate by Insurer",
    text_auto=".2f"
)


fig.update_layout(
    xaxis_title="Insurer",
    yaxis_title="Renewal Rate (%)",
    xaxis_tickangle=-35
)


fig.update_traces(
    hovertemplate=
    "<b>%{x}</b><br>"
    "Renewal Rate: %{y:.2f}%"
    "<extra></extra>"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# INSURER SUMMARY
# ============================================================

st.subheader("Insurer Summary")


insurer_summary = (
    filtered_insurer_df
    .groupby("insurer")
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


insurer_summary["renewal_rate"] = (
    insurer_summary["renewed_policies"]
    / insurer_summary["total_policies"]
    * 100
)


insurer_summary["premium_renewal_rate"] = (
    insurer_summary["renewed_premium"]
    / insurer_summary["total_premium"]
    * 100
)


# ============================================================
# DISPLAY-FRIENDLY TABLE
# ============================================================

display_summary = insurer_summary.copy()


display_summary["total_premium"] = (
    display_summary["total_premium"]
    / 1e7
)


display_summary["renewed_premium"] = (
    display_summary["renewed_premium"]
    / 1e7
)


display_summary = display_summary.rename(
    columns={
        "insurer": "Insurer",
        "total_policies": "Total Policies",
        "renewed_policies": "Renewed Policies",
        "total_premium":
            "Total Premium (₹ Cr)",
        "renewed_premium":
            "Renewed Premium (₹ Cr)",
        "renewal_rate":
            "Renewal Rate (%)",
        "premium_renewal_rate":
            "Premium Renewal (%)"
    }
)


display_summary[
    "Total Premium (₹ Cr)"
] = display_summary[
    "Total Premium (₹ Cr)"
].round(2)


display_summary[
    "Renewed Premium (₹ Cr)"
] = display_summary[
    "Renewed Premium (₹ Cr)"
].round(2)


display_summary[
    "Renewal Rate (%)"
] = display_summary[
    "Renewal Rate (%)"
].round(2)


display_summary[
    "Premium Renewal (%)"
] = display_summary[
    "Premium Renewal (%)"
].round(2)


st.dataframe(
    display_summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# RAW DATA PREVIEW
# ============================================================

with st.expander("🔍 View Policy-Level Data"):

    st.dataframe(
        policy_df.head(100),
        use_container_width=True,
        hide_index=True
    )


with st.expander("🔍 View Monthly Aggregated Data"):

    st.dataframe(
        monthly_df,
        use_container_width=True,
        hide_index=True
    )


with st.expander("🔍 View Insurer Aggregated Data"):

    st.dataframe(
        insurer_df,
        use_container_width=True,
        hide_index=True
    )