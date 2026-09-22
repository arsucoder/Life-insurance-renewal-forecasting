import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Payment Analysis",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = "data/processed/monthly_by_payment_mode.csv"

# ----------------------------------------------------------------
# PALETTE
# ----------------------------------------------------------------
NAVY_DARK = "#0B1B3A"
BLUE = "#2563EB"
TEAL = "#14B8A6"
GREEN = "#16A34A"
PURPLE = "#7C3AED"
ORANGE = "#F97316"
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
        div[data-testid="stAppViewContainer"] { background-color: #EFF3FA; }

        /* ---------- HERO BANNER ---------- */
        .hero {
            background: linear-gradient(115deg, #0B1B3A 0%, #122A5C 55%, #1E4E9C 100%);
            border-radius: 18px;
            padding: 22px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            box-shadow: 0 10px 30px rgba(11,27,58,0.25);
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.14);
            color: #CBD5E1;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 999px;
            margin-bottom: 8px;
        }
        .hero-title {
            color: #F8FAFC;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
            margin: 0 0 10px 0;
        }
        .hero-pills { display: flex; gap: 8px; flex-wrap: wrap; }
        .hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            background: rgba(0,0,0,0.28);
            border: 1px solid rgba(255,255,255,0.10);
            color: #E2E8F0;
            font-size: 0.74rem;
            font-weight: 600;
            padding: 5px 13px;
            border-radius: 999px;
        }
        .pill-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
        .hero-art { opacity: 0.95; flex-shrink: 0; }

        /* ---------- FILTER CARD ----------
           The white card is painted onto the columns row that holds the
           filter labels + widgets (it uniquely contains .filter-label). */
        div[data-testid="stHorizontalBlock"]:has(.filter-label) {
            background: #FFFFFF;
            border: 1px solid #E5EAF1;
            border-radius: 16px;
            padding: 16px 22px 14px 22px;
            margin-bottom: 16px;
            box-shadow: 0 2px 10px rgba(15,23,42,0.05);
            align-items: center;
        }
        .filter-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: #334155;
            margin-bottom: 4px;
        }
        .filter-info {
            font-size: 0.82rem;
            color: #64748B;
            text-align: right;
            padding-top: 26px;
            line-height: 1.5;
        }
        .filter-info b { color: #0F172A; }

        /* dark navy selectbox (react-aria ComboBox) */
        div[data-testid="stSelectbox"] .react-aria-ComboBox {
            background-color: #0A1930 !important;
            border: 1px solid #1E3A5F !important;
            border-radius: 10px !important;
            overflow: hidden !important;
            min-height: 40px;
        }
        div[data-testid="stSelectbox"] .react-aria-ComboBox div {
            background-color: #0A1930 !important;
        }
        div[data-testid="stSelectbox"] .react-aria-ComboBox input {
            background: transparent !important;
            color: #FFFFFF !important;
        }
        div[data-testid="stSelectbox"] .react-aria-ComboBox input::placeholder {
            color: rgba(255,255,255,0.55) !important;
        }
        div[data-testid="stSelectbox"] .react-aria-ComboBox button {
            background: transparent !important;
            color: #FFFFFF !important;
        }
        div[data-testid="stSelectbox"] .react-aria-ComboBox button svg {
            fill: #FFFFFF !important;
        }

        /* dark navy date input (react-aria DateField) */
        div[data-testid="stDateInput"] .react-aria-DateField,
        div[data-testid="stDateInputField"] {
            background-color: #0A1930 !important;
            border: 1px solid #1E3A5F !important;
            border-radius: 10px !important;
            overflow: hidden !important;
            color: #FFFFFF !important;
            min-height: 40px;
        }
        div[data-testid="stDateInput"] .react-aria-DateField div,
        div[data-testid="stDateInput"] .react-aria-DateField span,
        div[data-testid="stDateInputField"] div,
        div[data-testid="stDateInputField"] span {
            background-color: #0A1930 !important;
            color: #FFFFFF !important;
        }
        div[data-testid="stDateInput"] input,
        div[data-testid="stDateInput"] [role="spinbutton"] {
            background: transparent !important;
            color: #FFFFFF !important;
        }
        div[data-testid="element-container"] { margin-bottom: 0.1rem; }

        /* ---------- SECTION LABEL ---------- */
        .section-label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.95rem;
            font-weight: 700;
            color: #1E293B;
            margin: 4px 0 10px 0;
        }
        .section-label .bar {
            width: 4px; height: 15px;
            border-radius: 2px;
            display: inline-block;
        }

        /* ---------- KPI CARDS ---------- */
        .kpi {
            background: #FFFFFF;
            border: 1px solid #E5EAF1;
            border-radius: 16px;
            padding: 16px 18px;
            display: flex;
            gap: 14px;
            align-items: flex-start;
            box-shadow: 0 2px 10px rgba(15,23,42,0.05);
            height: 100%;
        }
        .kpi-ico {
            width: 46px; height: 46px;
            border-radius: 13px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .kpi-label { font-size: 0.78rem; color: #64748B; font-weight: 600; margin-bottom: 2px; }
        .kpi-value { font-size: 1.55rem; font-weight: 800; color: #0F172A; line-height: 1.15; }
        .kpi-sub { font-size: 0.74rem; color: #94A3B8; margin-top: 2px; }

        /* ---------- CHART CARDS ----------
           Each chart lives inside st.container(border=True, key="chart_card_*"),
           which is a REAL DOM wrapper (unlike a markdown <div>, which Streamlit
           isolates per-block and can never wrap a chart). The key becomes a
           CSS class "st-key-chart_card_*", so this selector always finds the
           card — no DOM guessing needed. */
        div[class*="st-key-chart_card"] {
            background: #FFFFFF !important;
            border: 1px solid #E5EAF1 !important;
            border-radius: 16px !important;
            padding: 14px 16px 8px 16px !important;
            box-shadow: 0 2px 10px rgba(15,23,42,0.05) !important;
        }
        .chart-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 4px;
        }

        /* ---------- HIGHLIGHTS ---------- */
        .hl-row {
            display: flex;
            gap: 10px;
            align-items: flex-start;
            padding: 8px 0;
        }
        .hl-dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; margin-top: 5px; flex-shrink: 0; }
        .hl-text { font-size: 0.8rem; color: #475569; line-height: 1.5; }
        .hl-text b { color: #0F172A; }

        /* ---------- EXPANDER ---------- */
        div[data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid #E5EAF1;
            border-radius: 16px;
            margin-top: 10px;
        }

        /* ---------- KEEP EXPLORING ---------- */
        .explore-grid { display: flex; gap: 14px; }
        .explore-card {
            flex: 1;
            background: #FFFFFF;
            border: 1px solid #E5EAF1;
            border-radius: 16px;
            padding: 16px 18px;
            display: flex;
            gap: 14px;
            align-items: center;
            box-shadow: 0 2px 10px rgba(15,23,42,0.05);
        }
        .explore-ico {
            width: 46px; height: 46px;
            border-radius: 13px;
            background: #EFF6FF;
            color: #2563EB;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .explore-title { font-size: 0.88rem; font-weight: 700; color: #0F172A; }
        .explore-sub { font-size: 0.76rem; color: #64748B; margin-top: 2px; }
        .explore-arrow {
            margin-left: auto;
            width: 34px; height: 34px;
            border-radius: 50%;
            background: #EFF6FF;
            color: #2563EB;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            font-weight: 700;
            flex-shrink: 0;
        }

        /* ---------- FOOTER ---------- */
        .footer {
            text-align: center;
            color: #94A3B8;
            font-size: 0.76rem;
            margin-top: 18px;
            padding-bottom: 6px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()

    required_columns = [
        "collection_month",
        "payment_mode",
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

    df["collection_month"] = pd.to_datetime(df["collection_month"], errors="coerce")

    return df.sort_values(["payment_mode", "collection_month"]).reset_index(drop=True)


try:
    df = load_data()
except FileNotFoundError:
    st.error(f"Dataset not found: `{DATA_PATH}` — make sure it is inside data/processed/")
    st.stop()

# ----------------------------------------------------------------
# FILTER STATE (needed before the hero pills)
# ----------------------------------------------------------------
payment_modes = sorted(df["payment_mode"].dropna().unique())
if "selected_payment" not in st.session_state:
    st.session_state["selected_payment"] = payment_modes[0]
selected_payment = st.session_state["selected_payment"]

payment_df = df[df["payment_mode"] == selected_payment].copy()
min_date = payment_df["collection_month"].min().date()
max_date = payment_df["collection_month"].max().date()

# ----------------------------------------------------------------
# HERO BANNER
# ----------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <div>
            <div class="hero-badge">Payment performance</div>
            <div class="hero-title">Payment Analysis</div>
            <div class="hero-pills">
                <span class="hero-pill"><span class="pill-dot" style="background:#60A5FA;"></span>{selected_payment}</span>
                <span class="hero-pill"><span class="pill-dot" style="background:#2DD4BF;"></span>{min_date.strftime("%b %Y")} &ndash; {max_date.strftime("%b %Y")}</span>
            </div>
        </div>
        <svg class="hero-art" width="230" height="86" viewBox="0 0 230 86" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g fill="#3B82F6" opacity="0.35">
                <rect x="8"   y="54" width="13" height="24" rx="3"/>
                <rect x="27"  y="48" width="13" height="30" rx="3"/>
                <rect x="46"  y="50" width="13" height="28" rx="3"/>
                <rect x="65"  y="40" width="13" height="38" rx="3"/>
                <rect x="84"  y="44" width="13" height="34" rx="3"/>
                <rect x="103" y="34" width="13" height="44" rx="3"/>
                <rect x="122" y="38" width="13" height="40" rx="3"/>
                <rect x="141" y="28" width="13" height="50" rx="3"/>
                <rect x="160" y="32" width="13" height="46" rx="3"/>
                <rect x="179" y="22" width="13" height="56" rx="3"/>
            </g>
            <polyline points="14,52 33,46 52,49 71,38 90,42 109,32 128,36 147,26 166,30 185,20"
                      stroke="#2DD4BF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="185" cy="20" r="10" fill="#2DD4BF" opacity="0.25"/>
            <circle cx="185" cy="20" r="4.5" fill="#2DD4BF" stroke="#F8FAFC" stroke-width="2"/>
        </svg>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# FILTER CARD
# ----------------------------------------------------------------
f1, f2, f3 = st.columns([1, 1.4, 1])

with f1:
    st.markdown('<div class="filter-label">Payment Mode</div>', unsafe_allow_html=True)
    chosen = st.selectbox(
        "Select Payment Mode",
        payment_modes,
        index=payment_modes.index(selected_payment),
        label_visibility="collapsed",
        key="payment_mode_select",
    )
    if chosen != st.session_state["selected_payment"]:
        st.session_state["selected_payment"] = chosen
        st.rerun()

with f2:
    st.markdown('<div class="filter-label">Date range</div>', unsafe_allow_html=True)
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed",
        key="payment_date_range",
    )

with f3:
    st.markdown(
        f'<div class="filter-info"><b>{len(payment_modes)}</b> payment modes &middot; '
        f'data from <b>{min_date.strftime("%b %Y")}</b> to <b>{max_date.strftime("%b %Y")}</b></div>',
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------
# While the user has only picked the start date, date_range is a
# single-element tuple — fall back to the full range instead of
# erroring, and only apply the filter once both ends are picked.
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = payment_df[
        (payment_df["collection_month"].dt.date >= start_date)
        & (payment_df["collection_month"].dt.date <= end_date)
    ].copy()
else:
    filtered_df = payment_df.copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

n_months = filtered_df["collection_month"].nunique()

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_policies = filtered_df["total_policies"].sum()
renewed_policies = filtered_df["renewed_policies"].sum()

total_premium = filtered_df["total_premium"].sum()
renewed_premium = filtered_df["renewed_premium"].sum()

renewal_rate = renewed_policies / total_policies * 100 if total_policies > 0 else 0
average_premium = total_premium / total_policies if total_policies > 0 else 0
renewed_share = renewed_premium / total_premium * 100 if total_premium > 0 else 0

# -----------------------------
# OVERVIEW — KPI CARDS
# -----------------------------
st.markdown(
    '<div class="section-label"><span class="bar" style="background:#2563EB;"></span>Overview</div>',
    unsafe_allow_html=True,
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-ico" style="background:#DBEAFE;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2l8 3v6c0 5-3.5 8.6-8 10-4.5-1.4-8-5-8-10V5l8-3z"/>
                    <polyline points="9 12 11 14 15 10"/>
                </svg>
            </div>
            <div>
                <div class="kpi-label">Total policies</div>
                <div class="kpi-value">{total_policies:,.0f}</div>
                <div class="kpi-sub">Policies in the selected period</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-ico" style="background:#FFEDD5;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 17 9 11 13 15 21 7"/>
                    <polyline points="15 7 21 7 21 13"/>
                </svg>
            </div>
            <div>
                <div class="kpi-label">Renewal rate</div>
                <div class="kpi-value">{renewal_rate:.2f}%</div>
                <div class="kpi-sub">Renewed &divide; total policies</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-ico" style="background:#EDE9FE;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M6 3h12M6 8h12M6 13l8.5 8M6 13h3M9 13c6.667 0 6.667-10 0-10"/>
                </svg>
            </div>
            <div>
                <div class="kpi-label">Renewed premium</div>
                <div class="kpi-value">&#8377;{renewed_premium / 1e7:,.2f} Cr</div>
                <div class="kpi-sub">Premium from renewed policies</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-ico" style="background:#CCFBF1;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0D9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="6" width="20" height="12" rx="2"/>
                    <circle cx="12" cy="12" r="2.5"/>
                    <path d="M6 12h.01M18 12h.01"/>
                </svg>
            </div>
            <div>
                <div class="kpi-label">Avg premium / policy</div>
                <div class="kpi-value">&#8377;{average_premium:,.0f}</div>
                <div class="kpi-sub">Average ticket size</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# TRENDS
# -----------------------------
monthly_df = filtered_df.sort_values("collection_month").copy()

st.markdown(
    '<div class="section-label"><span class="bar" style="background:#14B8A6;"></span>Trends</div>',
    unsafe_allow_html=True,
)

# ----- Row: Monthly Renewal Rate + Premium Mix -----
t1, t2 = st.columns([1.65, 1])

with t1:
    with st.container(border=True, key="chart_card_renewal_rate"):
        st.markdown('<div class="chart-title">Monthly renewal rate</div>', unsafe_allow_html=True)

        fig_renewal = px.line(
            monthly_df,
            x="collection_month",
            y="renewal_rate",
            markers=True,
            color_discrete_sequence=[BLUE],
        )
        fig_renewal.update_layout(
            height=285,
            margin=dict(l=8, r=8, t=6, b=8),
            xaxis_title="",
            yaxis_title="Renewal rate (%)",
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig_renewal.update_yaxes(gridcolor="#EEF2F7", title_font=dict(size=11, color="#64748B"))
        fig_renewal.update_xaxes(showgrid=False, dtick="M12", tickformat="%Y")
        fig_renewal.update_traces(
            line_width=2.5,
            marker_size=6,
            hovertemplate="<b>%{x|%b %Y}</b><br>Renewal Rate: %{y:.2f}%<extra></extra>",
        )
        st.plotly_chart(fig_renewal, use_container_width=True, config={"displayModeBar": False})

with t2:
    with st.container(border=True, key="chart_card_premium_mix"):
        st.markdown('<div class="chart-title">Premium mix</div>', unsafe_allow_html=True)

        non_renewed_premium = max(total_premium - renewed_premium, 0)
        premium_df = pd.DataFrame({
            "Premium Type": ["Renewed Premium", "Non-Renewed Premium"],
            "Premium": [renewed_premium, non_renewed_premium],
        })

        fig_premium = px.pie(
            premium_df,
            names="Premium Type",
            values="Premium",
            hole=0.62,
            color="Premium Type",
            color_discrete_map={"Renewed Premium": TEAL, "Non-Renewed Premium": NON_RENEWED},
        )
        fig_premium.update_traces(
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>Premium: &#8377;%{value:,.0f}<br>Share: %{percent}<extra></extra>",
        )
        fig_premium.update_layout(
            height=285,
            margin=dict(l=8, r=8, t=6, b=8),
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5, font=dict(size=11)),
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text=f"<b style='font-size:22px;color:#0F172A;'>{renewed_share:.1f}%</b>",
                    x=0.5, y=0.54, showarrow=False, xanchor="center", yanchor="middle",
                ),
                dict(
                    text="<span style='font-size:11px;color:#64748B;'>renewed</span>",
                    x=0.5, y=0.44, showarrow=False, xanchor="center", yanchor="middle",
                ),
            ],
        )
        st.plotly_chart(fig_premium, use_container_width=True, config={"displayModeBar": False})

# ----- Full width: Monthly Renewed Premium (area) -----
with st.container(border=True, key="chart_card_renewed_premium"):
    st.markdown('<div class="chart-title">Monthly renewed premium</div>', unsafe_allow_html=True)

    area_df = monthly_df[["collection_month", "renewed_premium"]].copy()
    area_df["renewed_premium"] = area_df["renewed_premium"] / 1e7

    fig_area = px.area(
        area_df,
        x="collection_month",
        y="renewed_premium",
        color_discrete_sequence=[TEAL],
    )
    fig_area.update_layout(
        height=265,
        margin=dict(l=8, r=8, t=6, b=8),
        xaxis_title="",
        yaxis_title="Renewed premium (&#8377; Cr)",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    fig_area.update_yaxes(gridcolor="#EEF2F7", title_font=dict(size=11, color="#64748B"))
    fig_area.update_xaxes(showgrid=False, dtick="M6", tickformat="%b %Y")
    fig_area.update_traces(
        line=dict(width=2.5, color=TEAL),
        fillcolor="rgba(20,184,166,0.12)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Renewed Premium: &#8377;%{y:.2f} Cr<extra></extra>",
    )
    st.plotly_chart(fig_area, use_container_width=True, config={"displayModeBar": False})
# ----- Row: Premium Trend + Policy Trend -----
c3, c4 = st.columns(2)

with c3:
    with st.container(border=True, key="chart_card_premium_trend"):
        st.markdown('<div class="chart-title">Monthly premium trend</div>', unsafe_allow_html=True)

        prem_trend = monthly_df[["collection_month", "total_premium", "renewed_premium"]].copy()
        prem_trend["total_premium"] = prem_trend["total_premium"] / 1e7
        prem_trend["renewed_premium"] = prem_trend["renewed_premium"] / 1e7
        prem_melt = prem_trend.melt(id_vars="collection_month", var_name="Series", value_name="Premium")
        prem_melt["Series"] = prem_melt["Series"].map(
            {"total_premium": "Total Premium", "renewed_premium": "Renewed Premium"}
        )

        fig_prem_trend = px.line(
            prem_melt, x="collection_month", y="Premium", color="Series", markers=True,
            color_discrete_map={"Total Premium": BLUE, "Renewed Premium": PURPLE},
        )
        fig_prem_trend.update_layout(
            height=240,
            margin=dict(l=8, r=8, t=28, b=8),
            xaxis_title="", yaxis_title="",
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        )
        fig_prem_trend.update_yaxes(ticksuffix=" Cr", gridcolor="#EEF2F7")
        fig_prem_trend.update_xaxes(showgrid=False)
        fig_prem_trend.update_traces(
            line_width=2.5, marker_size=5,
            hovertemplate="<b>%{x|%b %Y}</b><br>%{fullData.name}: &#8377;%{y:.2f} Cr<extra></extra>",
        )
        st.plotly_chart(fig_prem_trend, use_container_width=True, config={"displayModeBar": False})

with c4:
    with st.container(border=True, key="chart_card_policy_trend"):
        st.markdown('<div class="chart-title">Monthly policy trend</div>', unsafe_allow_html=True)

        pol_trend = monthly_df[["collection_month", "total_policies", "renewed_policies"]].copy()
        pol_melt = pol_trend.melt(id_vars="collection_month", var_name="Series", value_name="Policies")
        pol_melt["Series"] = pol_melt["Series"].map(
            {"total_policies": "Total Policies", "renewed_policies": "Renewed Policies"}
        )

        fig_pol_trend = px.line(
            pol_melt, x="collection_month", y="Policies", color="Series", markers=True,
            color_discrete_map={"Total Policies": BLUE, "Renewed Policies": GREEN},
        )
        fig_pol_trend.update_layout(
            height=240,
            margin=dict(l=8, r=8, t=28, b=8),
            xaxis_title="", yaxis_title="",
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        )
        fig_pol_trend.update_yaxes(gridcolor="#EEF2F7")
        fig_pol_trend.update_xaxes(showgrid=False)
        fig_pol_trend.update_traces(
            line_width=2.5, marker_size=5,
            hovertemplate="<b>%{x|%b %Y}</b><br>%{fullData.name}: %{y:,.0f}<extra></extra>",
        )
        st.plotly_chart(fig_pol_trend, use_container_width=True, config={"displayModeBar": False})

# ----- Row: Mode Comparison + Highlights -----
c5, c6 = st.columns(2)

with c5:
    with st.container(border=True, key="chart_card_mode_comparison"):
        st.markdown('<div class="chart-title">Renewal rate by payment mode</div>', unsafe_allow_html=True)

        comparison = (
            df.groupby("payment_mode")
            .agg(
                total_policies=("total_policies", "sum"),
                renewed_policies=("renewed_policies", "sum"),
                total_premium=("total_premium", "sum"),
                renewed_premium=("renewed_premium", "sum"),
            )
            .reset_index()
        )
        comparison["renewal_rate"] = comparison["renewed_policies"] / comparison["total_policies"] * 100
        comparison["premium_renewal_rate"] = comparison["renewed_premium"] / comparison["total_premium"] * 100
        comparison = comparison.sort_values("renewal_rate", ascending=False)

        fig_comp = px.bar(comparison, x="payment_mode", y="renewal_rate", color_discrete_sequence=[BLUE])
        fig_comp.update_layout(
            height=230,
            margin=dict(l=8, r=8, t=6, b=8),
            xaxis_title="", yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        fig_comp.update_yaxes(ticksuffix="%", gridcolor="#EEF2F7")
        fig_comp.update_xaxes(showgrid=False)
        fig_comp.update_traces(hovertemplate="<b>%{x}</b><br>Renewal Rate: %{y:.2f}%<extra></extra>")
        st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})

with c6:
    with st.container(border=True, key="chart_card_highlights"):
        st.markdown('<div class="chart-title">Highlights</div>', unsafe_allow_html=True)

        best_idx = filtered_df["renewal_rate"].idxmax()
        worst_idx = filtered_df["renewal_rate"].idxmin()
        best_month = filtered_df.loc[best_idx]
        worst_month = filtered_df.loc[worst_idx]

        st.markdown(
            f"""
            <div class="hl-row">
                <span class="hl-dot" style="background:{GREEN};"></span>
                <div class="hl-text"><b>Best month</b> — {best_month["collection_month"].strftime("%B %Y")}<br>
                {best_month["renewal_rate"]:.2f}% renewal rate &middot; {best_month["renewed_policies"]:,.0f} policies renewed</div>
            </div>
            <div class="hl-row">
                <span class="hl-dot" style="background:{ORANGE};"></span>
                <div class="hl-text"><b>Lowest month</b> — {worst_month["collection_month"].strftime("%B %Y")}<br>
                {worst_month["renewal_rate"]:.2f}% renewal rate &middot; {worst_month["renewed_policies"]:,.0f} policies renewed</div>
            </div>
            <div class="hl-row">
                <span class="hl-dot" style="background:{BLUE};"></span>
                <div class="hl-text"><b>Coverage</b> — {n_months} months of data for <b>{selected_payment}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------
# DETAILED TABLES (collapsed)
# -----------------------------
with st.expander("Detailed tables"):
    st.markdown(
        '<div class="section-label"><span class="bar" style="background:#2563EB;"></span>Payment Mode Comparison</div>',
        unsafe_allow_html=True,
    )

    display_comparison = comparison.copy()
    display_comparison["total_premium"] = display_comparison["total_premium"] / 1e7
    display_comparison["renewed_premium"] = display_comparison["renewed_premium"] / 1e7
    display_comparison = display_comparison.rename(
        columns={
            "payment_mode": "Payment Mode",
            "total_policies": "Total Policies",
            "renewed_policies": "Renewed Policies",
            "total_premium": "Total Premium (₹ Cr)",
            "renewed_premium": "Renewed Premium (₹ Cr)",
            "renewal_rate": "Renewal Rate (%)",
            "premium_renewal_rate": "Premium Renewal Rate (%)",
        }
    )
    st.dataframe(display_comparison, use_container_width=True, hide_index=True)

    st.markdown(
        '<div class="section-label"><span class="bar" style="background:#2563EB;"></span>Monthly Data</div>',
        unsafe_allow_html=True,
    )

    display_df = filtered_df.copy()
    display_df["total_premium"] = display_df["total_premium"] / 1e7
    display_df["renewed_premium"] = display_df["renewed_premium"] / 1e7
    display_df = display_df.rename(
        columns={
            "collection_month": "Month",
            "payment_mode": "Payment Mode",
            "total_policies": "Total Policies",
            "renewed_policies": "Renewed Policies",
            "total_premium": "Total Premium (₹ Cr)",
            "renewed_premium": "Renewed Premium (₹ Cr)",
            "renewal_rate": "Renewal Rate (%)",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Payment Data",
        data=csv_data,
        file_name=f"{selected_payment}_monthly_analysis.csv",
        mime="text/csv",
    )

# -----------------------------
# KEEP EXPLORING
# -----------------------------
st.markdown(
    '<div class="section-label"><span class="bar" style="background:#2563EB;"></span>Keep exploring</div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="explore-grid">
        <div class="explore-card">
            <div class="explore-ico">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/>
                    <rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>
                </svg>
            </div>
            <div>
                <div class="explore-title">Previous: Insurer Analysis</div>
                <div class="explore-sub">Renewal performance and premium trends across insurers.</div>
            </div>
            <div class="explore-arrow">&larr;</div>
        </div>
        <div class="explore-card">
            <div class="explore-ico">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2l8 3v6c0 5-3.5 8.6-8 10-4.5-1.4-8-5-8-10V5l8-3z"/>
                </svg>
            </div>
            <div>
                <div class="explore-title">Next: Policy Type Analysis</div>
                <div class="explore-sub">Renewal behaviour across policy types.</div>
            </div>
            <div class="explore-arrow">&rarr;</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
nav_prev, nav_next = st.columns(2)
with nav_prev:
    if st.button("← Previous: Insurer Analysis", key="keep_prev_insurer", type="primary", use_container_width=True):
        st.switch_page("pages/2_Insurer_Analysis.py")
with nav_next:
    if st.button("Next: Policy Type Analysis →", key="keep_next_policy", type="primary", use_container_width=True):
        st.switch_page("pages/4_Policy_Type_Analysis.py")

st.markdown(
    '<div class="footer">Life Insurance Renewal Analytics and Forecasting System</div>',
    unsafe_allow_html=True,
)
