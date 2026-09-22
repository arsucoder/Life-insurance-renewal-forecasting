import os
import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Duration Analysis | Life Insurance Renewal Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# THEME / UI
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- Global ---------- */

    .stApp {
        background: #f7f9fc;
        color: #10264a;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    [data-testid="collapsedControl"] {
        display: none;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
    }

    /* ---------- Hide Streamlit chrome ---------- */

    header[data-testid="stHeader"] {
        background: transparent;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* ---------- Back button ---------- */

    .back-home {
        margin: 0 0 12px 0;
    }

    .back-home a {
        display: inline-flex !important;
        align-items: center;
        padding: 6px 14px !important;
        border-radius: 999px !important;
        border: 1px solid #d9e2f2 !important;
        background: #ffffff !important;
        color: #2563eb !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        box-shadow: 0 1px 2px rgba(16,38,74,0.04);
        transition: all 0.18s ease;
    }

    .back-home a:hover {
        border-color: #9db8f5 !important;
        color: #1d4ed8 !important;
        box-shadow: 0 5px 14px rgba(16,38,74,0.10);
    }

    /* ---------- Page links ---------- */

    div[data-testid="stPageLink-NavLink"] {
        margin: 8px 0 18px 0;
    }

    div[data-testid="stPageLink-NavLink"] a {
        display: inline-flex !important;
        align-items: center;
        justify-content: center;
        min-height: 38px;
        padding: 8px 16px !important;
        border-radius: 10px !important;
        border: 1px solid #1d4ed8 !important;
        background: #2563eb !important;
        color: #ffffff !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        text-decoration: none !important;
        box-shadow: 0 4px 10px rgba(37,99,235,0.18);
        transition: all 0.18s ease;
    }

    div[data-testid="stPageLink-NavLink"] a:hover {
        border-color: #1e40af !important;
        background: #1d4ed8 !important;
        color: #ffffff !important;
        box-shadow: 0 6px 14px rgba(37,99,235,0.28);
    }

    /* ---------- Navigation buttons ---------- */

    div[data-testid="stButton"] button {
        background: #ffffff !important;
        color: #2563eb !important;
        border: 1px solid #2563eb !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(37,99,235,0.10);
    }

    div[data-testid="stButton"] button:hover {
        background: #eff6ff !important;
        color: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
        box-shadow: 0 5px 12px rgba(37,99,235,0.18);
    }

    div[data-testid="stButton"] button p {
        color: inherit !important;
    }

    /* ---------- Hero ---------- */

    .hero {
    background: linear-gradient(
        135deg,
        #0f1f3d 0%,
        #172d55 100%
    );
    border-radius: 18px;
    padding: 32px 36px;
    margin-bottom: 24px;
    color: white;
    }

    .hero-content {
        max-width: 100%;
    }

    .hero-kicker {
        font-size: 13px;
        font-weight: 600;
        color: #9db8f5;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .hero-title {
        font-size: 36px;
        font-weight: 800;
        color: white;
        margin-bottom: 10px;
    }

    .hero-description {
        font-size: 15px;
        line-height: 1.6;
        color: #dbe7ff;
        max-width: 760px;
    }

    .hero-features {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 22px;
    }

    .hero-feature {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 13px;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        color: #eaf1ff;
        font-size: 12px;
        font-weight: 600;
    }

    .hero-feature i {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }

    /* ---------- Section headings ---------- */

    .section-heading {
        color: #10264a;
        font-size: 20px;
        font-weight: 750;
        margin: 24px 0 10px 0;
        letter-spacing: -0.01em;
    }

    .section-caption {
        color: #65748b;
        font-size: 13px;
        margin-bottom: 12px;
    }

    /* ---------- KPI cards ---------- */

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e4eaf3;
        border-radius: 18px;
        padding: 18px 18px 16px 18px;
        min-height: 112px;
        box-shadow: 0 5px 16px rgba(16,38,74,0.05);
    }

    .kpi-label {
        color: #687890;
        font-size: 12px;
        font-weight: 650;
        margin-bottom: 7px;
    }

    .kpi-value {
        color: #10264a;
        font-size: 26px;
        line-height: 1.15;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .kpi-note {
        color: #8290a5;
        font-size: 11px;
        margin-top: 7px;
    }

    /* ---------- Chart cards ---------- */

    .chart-card {
        background: #ffffff;
        border: 1px solid #e4eaf3;
        border-radius: 18px;
        padding: 16px 18px 10px 18px;
        box-shadow: 0 5px 16px rgba(16,38,74,0.045);
        margin-bottom: 16px;
    }

    /* ---------- Filter row ---------- */

    div[data-testid="stSelectbox"] > div,
    div[data-testid="stDateInput"] > div {
        background: #ffffff;
    }

    /* ---------- Dataframes ---------- */

    div[data-testid="stDataFrame"] {
        border: 1px solid #e4eaf3;
        border-radius: 14px;
        overflow: hidden;
    }

    /* ---------- Download ---------- */

    .download-note {
        color: #6d7b91;
        font-size: 12px;
        margin-bottom: 8px;
    }

    /* ---------- Navigation ---------- */

    .nav-card {
        background: #ffffff;
        border: 1px solid #e4eaf3;
        border-radius: 16px;
        padding: 15px 17px;
        box-shadow: 0 4px 14px rgba(16,38,74,0.04);
        min-height: 74px;
    }

    .nav-card .nav-label {
        color: #8390a5;
        font-size: 11px;
        font-weight: 650;
        text-transform: uppercase;
        letter-spacing: .04em;
    }

    .nav-card .nav-title {
        color: #10264a;
        font-size: 14px;
        font-weight: 750;
        margin-top: 5px;
    }

    .nav-card .nav-desc {
        color: #6d7b91;
        font-size: 11px;
        margin-top: 3px;
    }

    .nav-card + div[data-testid="stPageLink-NavLink"] a {
        width: 100%;
    }

    /* ---------- Mobile ---------- */

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero {
            min-height: 0;
            padding: 24px;
            border-radius: 20px;
        }

        .hero-title {
            font-size: 30px;
        }

        .hero-description {
            font-size: 14px;
        }

        .hero-features {
            gap: 7px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA
# ============================================================

DURATION_FILE = "data/processed/monthly_by_duration_bucket.csv"

if not os.path.exists(DURATION_FILE):
    st.error(f"Dataset not found: `{DURATION_FILE}`")
    st.info("Run the duration aggregation step to create monthly_by_duration_bucket.csv.")
    st.stop()

df = pd.read_csv(DURATION_FILE)
df.columns = df.columns.str.strip()

required_columns = [
    "collection_month",
    "duration_bucket",
    "total_policies",
    "renewed_policies",
    "total_premium",
    "renewed_premium",
    "renewal_rate",
]

missing_columns = [c for c in required_columns if c not in df.columns]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

df["collection_month"] = pd.to_datetime(
    df["collection_month"],
    errors="coerce",
)

for col in [
    "total_policies",
    "renewed_policies",
    "total_premium",
    "renewed_premium",
    "renewal_rate",
]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df = df.dropna(subset=["collection_month"]).copy()
df["duration_bucket"] = df["duration_bucket"].astype(str).str.strip()

df = df.sort_values(
    ["duration_bucket", "collection_month"]
).reset_index(drop=True)

duration_buckets = [
    x for x in df["duration_bucket"].dropna().unique().tolist()
    if x != ""
]

if not duration_buckets:
    st.error("No duration buckets are available in the dataset.")
    st.stop()

min_date = df["collection_month"].min()
max_date = df["collection_month"].max()


# ============================================================
# PAGE NAVIGATION
# ============================================================

if st.button("← Back to Home", type="primary"):
    st.switch_page("App.py")


# ============================================================
# HERO
# ============================================================

st.markdown(
    f"""
<div class="hero">
<div class="hero-content">

<div class="hero-kicker">
Policy duration intelligence
</div>

<div class="hero-title">
Duration Analysis
</div>

<div class="hero-description">
Analyze renewal premium collection, policy volume and renewal
performance across different policy duration buckets.
</div>

<div class="hero-features">

<span class="hero-feature">
<i style="background:#6ea8ff"></i>
{len(duration_buckets)} duration buckets
</span>

<span class="hero-feature">
<i style="background:#5eead4"></i>
{min_date.strftime("%b %Y")} – {max_date.strftime("%b %Y")}
</span>

<span class="hero-feature">
<i style="background:#fbbf5a"></i>
Renewal intelligence
</span>

</div>

</div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# FILTERS
# ============================================================

st.markdown(
    '<div class="section-heading">Analysis Controls</div>',
    unsafe_allow_html=True,
)

filter_col1, filter_col2 = st.columns([1, 1])

with filter_col1:
    selected_duration = st.selectbox(
        "Duration Bucket",
        duration_buckets,
        key="duration_bucket_selector",
    )

with filter_col2:
    date_range = st.date_input(
        "Date Range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
        key="duration_date_range",
    )

duration_df = df[df["duration_bucket"] == selected_duration].copy()

if len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    duration_df = duration_df[
        (duration_df["collection_month"] >= start_date)
        & (duration_df["collection_month"] <= end_date)
    ].copy()

if duration_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()


# ============================================================
# SELECTED DURATION KPIs
# ============================================================

total_policies = duration_df["total_policies"].sum()
renewed_policies = duration_df["renewed_policies"].sum()
total_premium = duration_df["total_premium"].sum()
renewed_premium = duration_df["renewed_premium"].sum()

renewal_rate = (
    renewed_policies / total_policies * 100
    if total_policies > 0
    else 0
)

premium_renewal_rate = (
    renewed_premium / total_premium * 100
    if total_premium > 0
    else 0
)

st.markdown(
    f"""
    <div class="section-heading">{selected_duration} Performance</div>
    <div class="section-caption">
        {len(duration_df)} monthly observations in the selected period.
    </div>
    """,
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)

kpis = [
    ("Total Policies", f"{total_policies:,.0f}", "Policy volume"),
    ("Renewed Policies", f"{renewed_policies:,.0f}", "Successfully renewed"),
    ("Renewal Rate", f"{renewal_rate:.2f}%", "Policy renewal performance"),
    ("Renewed Premium", f"₹{renewed_premium / 1e7:.2f} Cr", "Renewed premium value"),
]

for col, (label, value, note) in zip([k1, k2, k3, k4], kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# MONTHLY TRENDS
# ============================================================

st.markdown(
    '<div class="section-heading">Monthly Renewal Trends</div>',
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns(2)

premium_chart = duration_df[
    ["collection_month", "renewed_premium"]
].copy()

premium_chart["renewed_premium"] /= 1e7

fig_premium = px.line(
    premium_chart,
    x="collection_month",
    y="renewed_premium",
    markers=True,
    labels={
        "collection_month": "Month",
        "renewed_premium": "Renewed Premium (₹ Cr)",
    },
)

fig_premium.update_traces(
    line=dict(width=2.5),
    marker=dict(size=5),
)

fig_premium.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=330,
    hovermode="x unified",
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#10264a"),
)

with chart_col1:
    st.markdown(
        '<div class="chart-card"><b>Monthly Renewed Premium</b></div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        fig_premium,
        use_container_width=True,
        config={"displayModeBar": False},
    )

rate_chart = duration_df[
    ["collection_month", "renewal_rate"]
].copy()

fig_rate = px.line(
    rate_chart,
    x="collection_month",
    y="renewal_rate",
    markers=True,
    labels={
        "collection_month": "Month",
        "renewal_rate": "Renewal Rate (%)",
    },
)

fig_rate.update_traces(
    line=dict(width=2.5),
    marker=dict(size=5),
)

fig_rate.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=330,
    hovermode="x unified",
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#10264a"),
)

with chart_col2:
    st.markdown(
        '<div class="chart-card"><b>Monthly Renewal Rate</b></div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        fig_rate,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ============================================================
# ALL DURATION BUCKET COMPARISON
# ============================================================

comparison = (
    df.groupby("duration_bucket", as_index=False)
    .agg(
        total_policies=("total_policies", "sum"),
        renewed_policies=("renewed_policies", "sum"),
        total_premium=("total_premium", "sum"),
        renewed_premium=("renewed_premium", "sum"),
    )
)

comparison["renewal_rate"] = (
    comparison["renewed_policies"]
    / comparison["total_policies"].replace(0, pd.NA)
    * 100
).fillna(0)

comparison["premium_renewal_rate"] = (
    comparison["renewed_premium"]
    / comparison["total_premium"].replace(0, pd.NA)
    * 100
).fillna(0)

st.markdown(
    '<div class="section-heading">Duration Bucket Comparison</div>',
    unsafe_allow_html=True,
)

cmp_col1, cmp_col2 = st.columns(2)

fig_cmp_rate = px.bar(
    comparison,
    x="duration_bucket",
    y="renewal_rate",
    text_auto=".1f",
    labels={
        "duration_bucket": "Duration Bucket",
        "renewal_rate": "Renewal Rate (%)",
    },
)

fig_cmp_rate.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=350,
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#10264a"),
)

with cmp_col1:
    st.markdown(
        '<div class="chart-card"><b>Renewal Rate by Duration</b></div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        fig_cmp_rate,
        use_container_width=True,
        config={"displayModeBar": False},
    )

premium_comparison = comparison.copy()
premium_comparison["renewed_premium_cr"] = (
    premium_comparison["renewed_premium"] / 1e7
)

fig_cmp_premium = px.bar(
    premium_comparison,
    x="duration_bucket",
    y="renewed_premium_cr",
    text_auto=".2f",
    labels={
        "duration_bucket": "Duration Bucket",
        "renewed_premium_cr": "Renewed Premium (₹ Cr)",
    },
)

fig_cmp_premium.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=350,
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#10264a"),
)

with cmp_col2:
    st.markdown(
        '<div class="chart-card"><b>Renewed Premium by Duration</b></div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        fig_cmp_premium,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ============================================================
# COMPARISON TABLE
# ============================================================

st.markdown(
    '<div class="section-heading">Duration Performance Summary</div>',
    unsafe_allow_html=True,
)

display_comparison = comparison.copy()

display_comparison["total_premium"] /= 1e7
display_comparison["renewed_premium"] /= 1e7

display_comparison = display_comparison.rename(
    columns={
        "duration_bucket": "Duration Bucket",
        "total_policies": "Total Policies",
        "renewed_policies": "Renewed Policies",
        "total_premium": "Total Premium (₹ Cr)",
        "renewed_premium": "Renewed Premium (₹ Cr)",
        "renewal_rate": "Renewal Rate (%)",
        "premium_renewal_rate": "Premium Renewal Rate (%)",
    }
)

st.dataframe(
    display_comparison.round(2),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# SELECTED BUCKET MONTHLY DATA
# ============================================================

st.markdown(
    '<div class="section-heading">Monthly Duration Data</div>',
    unsafe_allow_html=True,
)

display_df = duration_df.copy()

display_df["total_premium"] /= 1e7
display_df["renewed_premium"] /= 1e7

display_df = display_df.rename(
    columns={
        "collection_month": "Month",
        "duration_bucket": "Duration Bucket",
        "total_policies": "Total Policies",
        "renewed_policies": "Renewed Policies",
        "total_premium": "Total Premium (₹ Cr)",
        "renewed_premium": "Renewed Premium (₹ Cr)",
        "renewal_rate": "Renewal Rate (%)",
    }
)

st.dataframe(
    display_df.round(2),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# DOWNLOAD
# ============================================================

csv_data = duration_df.to_csv(index=False).encode("utf-8")

download_col1, download_col2 = st.columns([1, 3])

with download_col1:
    st.download_button(
        label="⬇ Download Duration Data",
        data=csv_data,
        file_name=f"{selected_duration}_monthly_analysis.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# PAGE NAVIGATION
# ============================================================

st.markdown(
    '<div class="section-heading">Continue Exploring</div>',
    unsafe_allow_html=True,
)

nav1, nav2 = st.columns(2)

with nav1:
    st.markdown(
        """
        <div class="nav-card">
            <div class="nav-label">Previous</div>
            <div class="nav-title">Dynamic Forecasting</div>
            <div class="nav-desc">Explore future renewal premium forecasts.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "← Open Dynamic Forecasting",
        key="open_dynamic_forecasting",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/9_Dynamic_Forecasting.py")

with nav2:
    st.markdown(
        """
        <div class="nav-card">
            <div class="nav-label">Next</div>
            <div class="nav-title">AI Assistant</div>
            <div class="nav-desc">Ask questions about the insurance renewal data.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Duration is currently the last page in the requested flow.
    # Keep this destination configurable without breaking the page if the
    # next module is not yet present.
    next_page = "pages/12_AI_Assistant.py"
    if os.path.exists(next_page):
        if st.button(
            "Open AI Assistant →",
            key="open_ai_assistant",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page(next_page)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#8a96a8;
        font-size:11px;
        margin-top:28px;
        padding-top:16px;
        border-top:1px solid #e6ebf2;
    ">
        Life Insurance Renewal Intelligence • Duration Analysis
    </div>
    """,
    unsafe_allow_html=True,
)
