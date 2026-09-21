import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Insurer Analysis",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = "data/processed/monthly_by_insurer.csv"

# ----------------------------------------------------------------
# PALETTE
# ----------------------------------------------------------------
NAVY_DARK = "#0B1B3A"
NAVY_MID = "#142B52"
BLUE = "#2563EB"
PURPLE = "#7C3AED"
GREEN = "#16A34A"
NON_RENEWED = "#E2E8F0"

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0.6rem;
            max-width: 1400px;
        }
        #MainMenu, footer, header { visibility: hidden; }

        /* ---------- HERO BANNER (compact) ---------- */
        .hero {
            background: linear-gradient(135deg, #0B1B3A 0%, #142B52 55%, #0F2247 100%);
            border-radius: 16px;
            padding: 16px 26px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            color: #CBD5E1;
            font-size: 0.68rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 999px;
            margin-bottom: 6px;
        }
        .hero-badge-dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: #38BDF8; display: inline-block;
        }
        .hero-title {
            color: #F8FAFC;
            font-size: 1.5rem;
            font-weight: 800;
            line-height: 1.1;
            margin: 0;
        }
        .hero-spark { opacity: 0.9; }

        /* ---------- SECTION LABEL ---------- */
        .section-label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            color: #1E293B;
            margin: 2px 0 6px 0;
        }
        .section-label .bar {
            width: 4px; height: 13px;
            background: #2563EB;
            border-radius: 2px;
            display: inline-block;
        }

        /* ---------- CARD WRAPPER ---------- */
        .kcard {
            background: #F8FAFC;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 10px 14px 6px 14px;
        }
        .kcard-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: #1E293B;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 2px;
        }
        .kcard-title .dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }

        /* ---------- METRIC (KPI) STYLING ---------- */
        div[data-testid="stMetric"] {
            background: #F8FAFC;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 10px 14px 8px 14px;
        }
        div[data-testid="stMetricLabel"] { font-size: 0.74rem; color: #64748B; font-weight: 600; }
        div[data-testid="stMetricValue"] { font-size: 1.3rem; font-weight: 800; color: #0F172A; }

        div[data-testid="element-container"] { margin-bottom: 0.1rem; }

        /* ---------- FILTER LABELS ---------- */
        .filter-label {
            font-size: 0.72rem;
            font-weight: 600;
            color: #64748B;
            margin-bottom: 2px;
        }

        /* ---------- DATE INPUT FIX ----------
           Default Streamlit date-range widget can get squeezed
           inside a narrow column, which clips/wraps the two dates.
           Give it a fixed readable size and let it size to content
           instead of being force-shrunk by the column. */
        div[data-testid="stDateInput"] {
            width: 100%;
        }
        div[data-testid="stDateInput"] > div {
            min-width: 100%;
        }
        div[data-testid="stDateInput"] input {
            font-size: 0.82rem;
            padding: 6px 8px;
            min-width: 105px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# HERO BANNER
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div>
            <div class="hero-badge">
                <span class="hero-badge-dot"></span> Insurer performance
            </div>
            <div class="hero-title">Insurer Analysis</div>
        </div>
        <svg class="hero-spark" width="140" height="46" viewBox="0 0 170 70" xmlns="http://www.w3.org/2000/svg">
            <polyline points="0,55 25,42 50,48 75,22 100,30 125,14 150,18 170,6"
                      fill="none" stroke="#38BDF8" stroke-width="2.5"
                      stroke-linecap="round" stroke-linejoin="round" />
            <polyline points="100,30 125,14 150,18 170,6"
                      fill="none" stroke="#22D3EE" stroke-width="2.5"
                      stroke-dasharray="4,4"
                      stroke-linecap="round" stroke-linejoin="round" />
            <circle cx="100" cy="30" r="4" fill="#F8FAFC" stroke="#38BDF8" stroke-width="2"/>
        </svg>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "collection_month",
        "insurer",
        "total_policies",
        "renewed_policies",
        "total_premium",
        "renewed_premium",
        "renewal_rate",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"Missing columns: {missing_columns}")
        st.stop()

    df["collection_month"] = pd.to_datetime(df["collection_month"])

    return df.sort_values(["insurer", "collection_month"])


df = load_data()

# -----------------------------
# FILTERS
# -----------------------------
# Date range gets more room than the insurer dropdown so the two
# date boxes inside it never get squeezed/wrapped.
col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown('<div class="filter-label">Insurer</div>', unsafe_allow_html=True)
    insurers = sorted(df["insurer"].dropna().unique())
    selected_insurer = st.selectbox("Select Insurer", insurers, label_visibility="collapsed")

insurer_df = df[df["insurer"] == selected_insurer].copy()

min_date = insurer_df["collection_month"].min().date()
max_date = insurer_df["collection_month"].max().date()

with col2:
    st.markdown('<div class="filter-label">Date Range</div>', unsafe_allow_html=True)
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed",
    )

# While the user has only picked the start date, date_range is a
# single-element tuple — fall back to the full range instead of
# erroring, and only apply the filter once both ends are picked.
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = insurer_df[
        (insurer_df["collection_month"].dt.date >= start_date)
        & (insurer_df["collection_month"].dt.date <= end_date)
    ].copy()
else:
    filtered_df = insurer_df.copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_policies = filtered_df["total_policies"].sum()
renewed_policies = filtered_df["renewed_policies"].sum()

total_premium = filtered_df["total_premium"].sum()
renewed_premium = filtered_df["renewed_premium"].sum()

renewal_rate = (
    renewed_policies / total_policies * 100 if total_policies > 0 else 0
)

# -----------------------------
# KPI CARDS
# -----------------------------
st.markdown('<div class="section-label"><span class="bar"></span>Overview</div>', unsafe_allow_html=True)

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric("Total Policies", f"{total_policies:,.0f}")

with kpi2:
    st.metric("Renewal Rate", f"{renewal_rate:.2f}%")

with kpi3:
    st.metric("Renewed Premium", f"₹{renewed_premium:,.0f}")

# -----------------------------
# CHART DATA
# -----------------------------
monthly_df = filtered_df.sort_values("collection_month").copy()

st.markdown('<div class="section-label"><span class="bar"></span>Trends</div>', unsafe_allow_html=True)

# -----------------------------
# CHART ROW — Monthly Renewal Rate + Premium Mix
# -----------------------------
chart1, chart2 = st.columns(2)

with chart1:
    st.markdown(
        '<div class="kcard"><div class="kcard-title">'
        f'<span class="dot" style="background:{BLUE};"></span>'
        'Monthly Renewal Rate</div>',
        unsafe_allow_html=True,
    )

    fig_renewal = px.line(
        monthly_df,
        x="collection_month",
        y="renewal_rate",
        markers=True,
        color_discrete_sequence=[BLUE],
    )

    fig_renewal.update_layout(
        height=195,
        margin=dict(l=8, r=8, t=4, b=8),
        xaxis_title="",
        yaxis_title="",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_renewal.update_yaxes(ticksuffix="%", gridcolor="#EEF2F7")
    fig_renewal.update_xaxes(showgrid=False)
    fig_renewal.update_traces(
        line_width=2.5,
        marker_size=6,
        hovertemplate="<b>%{x|%b %Y}</b><br>Renewal Rate: %{y:.2f}%<extra></extra>",
    )

    st.plotly_chart(fig_renewal, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with chart2:
    st.markdown(
        '<div class="kcard"><div class="kcard-title">'
        f'<span class="dot" style="background:{PURPLE};"></span>'
        'Premium Mix</div>',
        unsafe_allow_html=True,
    )

    non_renewed_premium = max(total_premium - renewed_premium, 0)

    premium_df = pd.DataFrame({
        "Premium Type": ["Renewed Premium", "Non-Renewed Premium"],
        "Premium": [renewed_premium, non_renewed_premium],
    })

    fig_premium = px.pie(
        premium_df,
        names="Premium Type",
        values="Premium",
        hole=0.6,
        color="Premium Type",
        color_discrete_map={
            "Renewed Premium": GREEN,
            "Non-Renewed Premium": NON_RENEWED,
        },
    )

    fig_premium.update_traces(
        textinfo="percent",
        textfont_size=11,
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Premium: ₹%{value:,.0f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
    )

    fig_premium.update_layout(
        height=195,
        margin=dict(l=8, r=8, t=4, b=8),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.18, font=dict(size=10)),
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig_premium, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# RENEWED PREMIUM TREND
# -----------------------------
st.markdown(
    '<div class="kcard"><div class="kcard-title">'
    f'<span class="dot" style="background:{GREEN};"></span>'
    'Monthly Renewed Premium</div>',
    unsafe_allow_html=True,
)

fig_premium_trend = px.line(
    monthly_df,
    x="collection_month",
    y="renewed_premium",
    markers=True,
    color_discrete_sequence=[PURPLE],
)

fig_premium_trend.update_layout(
    height=150,
    margin=dict(l=8, r=8, t=4, b=8),
    xaxis_title="",
    yaxis_title="",
    hovermode="x unified",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
fig_premium_trend.update_yaxes(gridcolor="#EEF2F7")
fig_premium_trend.update_xaxes(showgrid=False)
fig_premium_trend.update_traces(
    line_width=2.5,
    marker_size=6,
    hovertemplate="<b>%{x|%b %Y}</b><br>Renewed Premium: ₹%{y:,.0f}<extra></extra>",
)

st.plotly_chart(fig_premium_trend, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)
