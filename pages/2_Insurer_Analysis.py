import html
from urllib.parse import quote

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Insurer Analysis",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONSTANTS
# ============================================================

DATA_PATH = "data/processed/monthly_by_insurer.csv"

HOME_PAGE = "App.py"
HOME_CANDIDATES = [HOME_PAGE, "app.py", "Home.py", "home.py", "main.py", "streamlit_app.py"]

NAVY = "#0e1b33"
BLUE = "#2456d6"
TEAL = "#0f9b86"
NON_RENEWED = "#dfe6f1"
FONT = "DM Sans, system-ui, sans-serif"
DISPLAY_FONT = "Bricolage Grotesque, DM Sans, system-ui, sans-serif"

# ------------------------------------------------------------
# PAGE NAVIGATION
# Order follows your pages/ file numbers. To change where this
# page leads, just change PREV_PAGE / NEXT_PAGE below.
# ------------------------------------------------------------
PAGES = {
    "overview": ("pages/01_Overview.py", "Overview", "High-level view of policies, renewals and renewed premium.", "grid"),
    "payment": ("pages/3_Payment_Analysis.py", "Payment Analysis", "Renewal behaviour across payment modes.", "card"),
    "policy": ("pages/4_Policy_Type_Analysis.py", "Policy Type Analysis", "Renewal behaviour and premium across policy types.", "shield"),
    "region": ("pages/5_Region_Analysis.py", "Region Analysis", "Renewal performance across geographical regions.", "pin"),
    "yearly": ("pages/6_Yearly_Analysis.py", "Yearly Analysis", "Financial-year performance and year-over-year change.", "calendar"),
    "timeseries": ("pages/7_Time_Series_Analysis.py", "Time Series Analysis", "Trend, seasonality, stationarity, ACF and PACF.", "trend"),
    "models": ("pages/8_Model_Comparison.py", "Model Comparison", "Compare forecasting models using MAPE, MAE and RMSE.", "bars"),
    "dynamic": ("pages/9_Dynamic_Forecasting.py", "Dynamic Forecasting", "Generate interactive future renewal premium forecasts.", "sliders"),
    "insights": ("pages/10_Business_Insights.py", "Business Insights", "Automatic insights, growth outlook and insurer comparisons.", "bulb"),
    "ai": ("pages/12_AI_Assistant.py", "AI Assistant", "Ask questions about the insurance renewal data in plain language.", "spark"),
}

PREV_PAGE = "overview"
NEXT_PAGE = "payment"

# Chart heights - lower these if you want the page even more compact
RATE_H = 260
TREND_H = 230


# ============================================================
# KPI STYLES + ICONS
# ============================================================

KPI_STYLES = {
    "total": dict(accent="#2f6bd8", tint="#eaf1fd", icon="shield"),
    "rate": dict(accent="#c97a0c", tint="#fdf0dc", icon="trend"),
    "premium": dict(accent="#5b4bd6", tint="#eeecfd", icon="rupee"),
}

ICONS = {
    "shield": "<path d='M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z'/><path d='M9 12l2 2 4-4'/>",
    "trend": "<path d='M3 3v18h18'/><path d='M7 15l4-5 3 3 5-7'/>",
    "rupee": "<path d='M6 5h12M6 10h12M9 5c5 0 6.5 2 6.5 5S14 15 9 15h-.5L15 21'/>",
    "grid": (
        "<rect x='3' y='3' width='8' height='8' rx='1.5'/><rect x='13' y='3' width='8' height='5' rx='1.5'/>"
        "<rect x='13' y='10' width='8' height='11' rx='1.5'/><rect x='3' y='13' width='8' height='8' rx='1.5'/>"
    ),
    "card": "<rect x='3' y='5' width='18' height='14' rx='2.5'/><path d='M3 10h18M7 15h4'/>",
    "pin": "<path d='M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z'/><circle cx='12' cy='10' r='2.5'/>",
    "calendar": "<rect x='3' y='5' width='18' height='16' rx='2.5'/><path d='M3 10h18M8 3v4M16 3v4'/>",
    "bars": "<path d='M5 21V11M12 21V4M19 21v-7'/>",
    "sliders": (
        "<path d='M4 6h9M17 6h3M4 12h3M11 12h9M4 18h11M19 18h1'/>"
        "<circle cx='15' cy='6' r='2'/><circle cx='9' cy='12' r='2'/><circle cx='17' cy='18' r='2'/>"
    ),
    "bulb": (
        "<path d='M9 18h6M10 21h4'/>"
        "<path d='M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z'/>"
    ),
    "spark": (
        "<path d='M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z'/>"
        "<path d='M19 16l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7z'/>"
    ),
}


def icon_url(name: str, stroke: str) -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        f"stroke='{stroke}' stroke-width='1.8' stroke-linecap='round' "
        f"stroke-linejoin='round'>{ICONS[name]}</svg>"
    )
    return "data:image/svg+xml," + quote(svg)


def build_dynamic_css() -> str:
    rules = []
    for kind, k in KPI_STYLES.items():
        rules.append(f'.kpi-{kind} {{ --accent: {k["accent"]}; --tint: {k["tint"]}; }}')
        rules.append(
            f'.kpi-{kind} .kpi-icon '
            f'{{ background-image: url("{icon_url(k["icon"], k["accent"])}"); }}'
        )

    for slot, page_key in (("prev", PREV_PAGE), ("next", NEXT_PAGE)):
        icon = PAGES[page_key][3]
        rules.append(
            f'.st-key-card_desc_{slot} a::before '
            f'{{ background-image: url("{icon_url(icon, "#2f6bd8")}"); }}'
        )

    return "\n".join(rules)


# ============================================================
# CUSTOM CSS (same design system as the other pages)
# ============================================================

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg: #f3f6fb;
    --card: #ffffff;
    --border: #e0e7f2;
    --navy: #0e1b33;
    --muted: #5b6b85;

    /* One spacing value for rows, columns and sections */
    --gap: 16px;

    --display: 'Bricolage Grotesque', 'DM Sans', system-ui, sans-serif;
    --body: 'DM Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

html, body, .stApp,
[data-testid="stMarkdownContainer"],
[data-testid="stPageLink"] a {
    font-family: var(--body);
}

.stApp {
    background:
        radial-gradient(900px 380px at 100% 0%, rgba(36, 86, 214, 0.06), transparent 70%),
        var(--bg);
}

[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] { display: none !important; }

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

header[data-testid="stHeader"] { height: 1.5rem; background: transparent; }

.block-container {
    max-width: 1400px;
    padding: 1rem 2rem 1.5rem 2rem;
}


/* ========================================================
   SPACING SYSTEM
   ======================================================== */

div[data-testid="stVerticalBlock"] { gap: var(--gap); }
div[data-testid="stHorizontalBlock"] { gap: var(--gap) !important; }

@media (min-width: 641px) {
    div[data-testid="stColumn"] { min-width: 0 !important; }
}


/* ========================================================
   BACK LINK
   ======================================================== */

.st-key-backlink { width: 100%; margin: 0 !important; padding: 0 !important; }

.st-key-backlink [data-testid="stPageLink"] {
    display: flex;
    justify-content: flex-start;
    margin: 0 !important;
}

.st-key-backlink a {
    width: auto !important;
    display: inline-flex !important;
    align-items: center;
    padding: 5px 14px !important;
    border-radius: 999px !important;
    border: 1px solid var(--border) !important;
    background: #ffffff !important;
    color: #2456d6 !important;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none !important;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04);
    transition: border-color 0.16s ease, box-shadow 0.16s ease;
}

.st-key-backlink a:hover {
    border-color: #9db8f5 !important;
    box-shadow: 0 4px 12px rgba(16, 38, 74, 0.10);
}

.st-key-backlink a p {
    margin: 0 !important;
    font-size: 13px !important;
    font-weight: 600;
    color: #2456d6 !important;
}


/* ========================================================
   HERO (compact)
   ======================================================== */

.hero {
    position: relative;
    overflow: hidden;
    min-height: 124px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    padding: 20px 34px;
    border-radius: 22px;
    background: linear-gradient(115deg, #0b1a36 0%, #12305f 58%, #1b4b8c 100%);
    box-shadow: 0 14px 34px rgba(11, 26, 54, 0.22);
}

.hero::before {
    content: "";
    position: absolute;
    right: -70px;
    top: -110px;
    width: 380px;
    height: 380px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(94, 234, 212, 0.20), transparent 65%);
}

.hero-content { position: relative; z-index: 2; max-width: 720px; }

.hero-kicker {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    background: rgba(255, 255, 255, 0.07);
    color: #a9c8ff;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 10px;
}

.hero-title {
    font-family: var(--display);
    font-size: 32px;
    line-height: 1.08;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #ffffff;
    margin: 0;
}

.hero-features { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }

.hero-feature {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 5px 13px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.16);
    background: rgba(255, 255, 255, 0.06);
    color: #eaf2ff;
    font-size: 12.5px;
    font-weight: 600;
}

.hero-feature i { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }

.hero-visual { position: relative; z-index: 1; width: 250px; flex-shrink: 0; }
.hero-visual svg { width: 100%; height: auto; display: block; }

@keyframes draw-line { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade-in   { from { opacity: 0; } to { opacity: 1; } }

.hero-bars { animation: fade-in 0.8s ease-out both; }
.hero-line { stroke-dasharray: 1; animation: draw-line 1.4s ease-out 0.4s both; }
.hero-dot  { animation: fade-in 0.5s ease-out 1.6s both; }

@media (prefers-reduced-motion: reduce) {
    .hero-bars, .hero-line, .hero-dot { animation: none; }
}


/* ========================================================
   SECTION HEADINGS
   ======================================================== */

.section-block { margin: 10px 0 6px 0; }

.section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: var(--display);
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.005em;
    color: var(--navy);
    margin: 0;
}

.section-line { width: 4px; height: 18px; border-radius: 3px; display: inline-block; }


/* ========================================================
   KPI CARDS
   ======================================================== */

.kpi {
    box-sizing: border-box;
    height: 100px;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 0 20px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04), 0 6px 16px rgba(16, 38, 74, 0.04);
}

.kpi-icon {
    flex: 0 0 48px;
    width: 48px;
    height: 48px;
    border-radius: 14px;
    background-color: var(--tint);
    background-repeat: no-repeat;
    background-position: center;
    background-size: 24px 24px;
}

.kpi-body { min-width: 0; }

.kpi-label {
    font-size: 12.5px;
    font-weight: 600;
    color: var(--muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.kpi-value {
    font-family: var(--display);
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.15;
    color: var(--navy);
    margin-top: 2px;
    white-space: nowrap;
}

.kpi-description {
    font-size: 11.5px;
    color: #8a97aa;
    margin-top: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}


/* ========================================================
   CHART / FILTER CARDS
   ======================================================== */

[class*="st-key-chart_"] {
    box-sizing: border-box;
    width: 100%;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 8px 14px 6px 14px;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04), 0 6px 16px rgba(16, 38, 74, 0.04);
    overflow: hidden;
}

/* The filter card must not clip the dropdown / calendar pop-overs */
[class*="st-key-chart_filters"] { overflow: visible; padding: 14px 18px 16px 18px; }

.filter-note { margin-top: 30px; font-size: 13px; color: var(--muted); }
.filter-note strong { color: var(--navy); font-weight: 600; }


/* ========================================================
   WIDGETS
   ======================================================== */

[data-testid="stSelectbox"] label p,
[data-testid="stDateInput"] label p {
    color: var(--navy) !important;
    font-size: 13px !important;
    font-weight: 600;
}

/* Keep the two dates of the range picker readable inside a column */
div[data-testid="stDateInput"] { width: 100%; }
div[data-testid="stDateInput"] > div { min-width: 100%; }
div[data-testid="stDateInput"] input { font-size: 0.85rem; min-width: 105px; }


/* ========================================================
   PREVIOUS / NEXT PAGE CARDS
   ======================================================== */

[class*="st-key-card_desc_"] { --accent: #2f6bd8; --tint: #eaf1fd; --edge: #a9c3f0; }

[class*="st-key-card_"],
[class*="st-key-card_"] > div,
[class*="st-key-card_"] [data-testid="stPageLink"] {
    width: 100% !important;
    min-width: 0 !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

[class*="st-key-card_"] a {
    position: relative;
    overflow: hidden;
    box-sizing: border-box;
    width: 100% !important;
    height: 92px;
    min-height: 0 !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center;
    gap: 14px;
    padding: 0 56px 0 16px !important;
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04), 0 6px 16px rgba(16, 38, 74, 0.04);
    color: var(--navy) !important;
    text-decoration: none !important;
    transition: border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
}

[class*="st-key-card_"] a:hover {
    border-color: var(--edge) !important;
    box-shadow: 0 10px 24px rgba(16, 38, 74, 0.11);
    transform: translateY(-2px);
}

[class*="st-key-card_"] a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

[class*="st-key-card_"] a::before {
    content: "";
    flex: 0 0 44px;
    width: 44px;
    height: 44px;
    border-radius: 13px;
    background-color: var(--tint);
    background-repeat: no-repeat;
    background-position: center;
    background-size: 22px 22px;
}

[class*="st-key-card_"] a::after {
    content: "→";
    position: absolute;
    right: 16px;
    top: 50%;
    transform: translateY(-50%);
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--tint);
    color: var(--accent);
    font-size: 15px;
    font-weight: 700;
    transition: background-color 0.16s ease, color 0.16s ease, right 0.16s ease;
}

[class*="st-key-card_"] a:hover::after { background: var(--accent); color: #ffffff; right: 13px; }

/* "Previous" card: arrow points back */
.st-key-card_desc_prev a::after { content: "←"; }
.st-key-card_desc_prev a:hover::after { right: 16px; }

[class*="st-key-card_"] a [data-testid="stMarkdownContainer"] {
    flex: 1 1 auto;
    min-width: 0;
    overflow: hidden;
}

[class*="st-key-card_"] a p { margin: 0 !important; line-height: 1.4 !important; }

[class*="st-key-card_"] a p:first-of-type {
    font-size: 15px !important;
    font-weight: 700;
    color: var(--navy) !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

[class*="st-key-card_"] a p + p {
    font-size: 12.5px !important;
    font-weight: 400;
    color: var(--muted) !important;
    margin-top: 3px !important;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
}

[class*="st-key-card_"] a strong { font-weight: 700; }


/* ========================================================
   ALL-PAGES GRID (compact cards)
   ======================================================== */

/* ========================================================
   FOOTER
   ======================================================== */

.page-footer {
    text-align: center;
    color: #8fa0b8;
    font-size: 11px;
    margin-top: 8px;
}


/* ========================================================
   RESPONSIVE
   ======================================================== */

@media (max-width: 1100px) {
    .block-container { padding-left: 1.2rem; padding-right: 1.2rem; }
    .hero-visual { width: 210px; }
    .kpi-value { font-size: 23px; }
}

@media (max-width: 900px) {
    .hero { min-height: 110px; padding: 20px 24px; }
    .hero-visual { display: none; }
    .hero-title { font-size: 26px; }
    .block-container { padding-left: 1rem; padding-right: 1rem; }
}

@media (max-width: 640px) {
    .filter-note { margin-top: 0; }
}
"""

st.markdown(
    f"<style>{BASE_CSS}\n{build_dynamic_css()}</style>",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def section_heading(title: str, color: str = BLUE) -> None:
    st.markdown(
        f'<div class="section-block"><div class="section-title">'
        f'<span class="section-line" style="background:{color}"></span>{title}'
        f"</div></div>",
        unsafe_allow_html=True,
    )


def kpi_card(kind: str, label: str, value: str, description: str = "") -> None:
    st.markdown(
        f'<div class="kpi kpi-{kind}"><div class="kpi-icon"></div>'
        f'<div class="kpi-body"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-description">{description}</div></div></div>',
        unsafe_allow_html=True,
    )


def nav_card(slot: str, page_key: str, prefix: str) -> None:
    path, title, description, _icon = PAGES[page_key]

    with st.container(key=f"card_desc_{slot}"):
        st.page_link(path, label=f"**{prefix}: {title}**\n\n{description}")


def chart_title(text: str) -> dict:
    return dict(
        text=text,
        x=0.0,
        xanchor="left",
        font=dict(size=16, color=NAVY, family=FONT),
    )


def style_fig(fig, title: str, y_title: str, height: int):
    fig.update_layout(
        title=chart_title(title),
        xaxis_title="",
        yaxis_title=y_title,
        height=height,
        margin=dict(l=10, r=10, t=50, b=16),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family=FONT, color="#1f2d47", size=12),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#dfe7f2",
            font=dict(family=FONT, size=12, color=NAVY),
        ),
    )

    axis_text = dict(color="#1f2d47", size=12, family=FONT)
    axis_title = dict(color=NAVY, size=13, family=FONT)

    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor="#9fb0c8",
        tickfont=axis_text,
        title_font=axis_title,
    )
    fig.update_yaxes(
        gridcolor="#e3e9f2",
        zeroline=False,
        tickfont=axis_text,
        title_font=axis_title,
    )
    return fig


PLOT_CONFIG = {"displayModeBar": False}


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_raw() -> pd.DataFrame:
    raw = pd.read_csv(DATA_PATH)
    raw.columns = raw.columns.str.strip()
    return raw


try:
    df = load_raw().copy()
except FileNotFoundError:
    st.error(f"Dataset not found: `{DATA_PATH}`")
    st.info("Make sure monthly_by_insurer.csv is inside data/processed/")
    st.stop()

required_columns = [
    "collection_month",
    "insurer",
    "total_policies",
    "renewed_policies",
    "total_premium",
    "renewed_premium",
    "renewal_rate",
]

missing_columns = [c for c in required_columns if c not in df.columns]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()

df["collection_month"] = pd.to_datetime(df["collection_month"], errors="coerce")
df["insurer"] = df["insurer"].astype(str).str.strip()

for col in [
    "total_policies",
    "renewed_policies",
    "total_premium",
    "renewed_premium",
    "renewal_rate",
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = (
    df.dropna(subset=["collection_month"])
    .sort_values(["insurer", "collection_month"])
    .reset_index(drop=True)
)


# ============================================================
# BACK LINK
# Tries the usual main-file names; falls back to a plain link.
# ============================================================

with st.container(key="backlink"):
    for candidate in HOME_CANDIDATES:
        try:
            st.page_link(candidate, label="← Back to home")
            break
        except Exception:
            continue
    else:
        st.markdown(
            '<a href="./" target="_self">← Back to home</a>',
            unsafe_allow_html=True,
        )


# The hero shows the selected insurer, but should sit ABOVE the filters,
# so reserve its slot now and fill it once the filters have been read.
hero_slot = st.empty()


# ============================================================
# FILTERS
# ============================================================

insurers = sorted(df["insurer"].dropna().unique())

with st.container(key="chart_filters"):
    f1, f2, f3 = st.columns([1, 1.4, 1.2], gap="small")

    with f1:
        selected_insurer = st.selectbox("Insurer", insurers)

    insurer_df = df[df["insurer"] == selected_insurer].copy()

    min_date = insurer_df["collection_month"].min().date()
    max_date = insurer_df["collection_month"].max().date()

    with f2:
        date_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    with f3:
        st.markdown(
            f'<div class="filter-note"><strong>{len(insurers)}</strong> insurers · '
            f'data from <strong>{df["collection_month"].min().strftime("%b %Y")}</strong> to '
            f'<strong>{df["collection_month"].max().strftime("%b %Y")}</strong></div>',
            unsafe_allow_html=True,
        )


# While only the start date is picked, date_range has a single element:
# fall back to the full range until both ends are chosen.
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
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


# ============================================================
# HERO
# (HTML blocks contain no blank lines on purpose)
# ============================================================

period_start = filtered_df["collection_month"].min()
period_end = filtered_df["collection_month"].max()

HERO_VISUAL = """<svg viewBox="0 0 340 150" role="img" aria-label="Renewed premium bars with a renewal rate line">
<line x1="10" y1="128" x2="330" y2="128" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<line x1="10" y1="90" x2="330" y2="90" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
<line x1="10" y1="52" x2="330" y2="52" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
<g class="hero-bars" fill="rgba(127,178,255,0.42)">
<rect x="14" y="98" width="20" height="30" rx="4"/>
<rect x="46" y="84" width="20" height="44" rx="4"/>
<rect x="78" y="90" width="20" height="38" rx="4"/>
<rect x="110" y="70" width="20" height="58" rx="4"/>
<rect x="142" y="76" width="20" height="52" rx="4"/>
<rect x="174" y="58" width="20" height="70" rx="4"/>
<rect x="206" y="64" width="20" height="64" rx="4"/>
<rect x="238" y="44" width="20" height="84" rx="4"/>
<rect x="270" y="50" width="20" height="78" rx="4"/>
<rect x="302" y="30" width="20" height="98" rx="4"/>
</g>
<polyline class="hero-line" pathLength="1" points="24,86 56,72 88,78 120,58 152,64 184,46 216,52 248,32 280,38 312,18" fill="none" stroke="#5eead4" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
<circle class="hero-dot" cx="312" cy="18" r="4.5" fill="#ffffff" stroke="#5eead4" stroke-width="2"/>
</svg>"""

HERO_HTML = f"""<div class="hero">
<div class="hero-content">
<div class="hero-kicker">Insurer performance</div>
<div class="hero-title">Insurer Analysis</div>
<div class="hero-features">
<span class="hero-feature"><i style="background:#6ea8ff"></i>{html.escape(selected_insurer)}</span>
<span class="hero-feature"><i style="background:#5eead4"></i>{period_start.strftime("%b %Y")} – {period_end.strftime("%b %Y")}</span>
<span class="hero-feature"><i style="background:#fbbf5a"></i>{len(filtered_df)} months</span>
</div>
</div>
<div class="hero-visual">{HERO_VISUAL}</div>
</div>"""

hero_slot.markdown(HERO_HTML, unsafe_allow_html=True)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_policies = filtered_df["total_policies"].sum()
renewed_policies = filtered_df["renewed_policies"].sum()

total_premium = filtered_df["total_premium"].sum()
renewed_premium = filtered_df["renewed_premium"].sum()

renewal_rate = renewed_policies / total_policies * 100 if total_policies > 0 else 0

premium_share = renewed_premium / total_premium * 100 if total_premium > 0 else 0


# ============================================================
# KPI CARDS
# ============================================================

section_heading("Overview", BLUE)

k1, k2, k3 = st.columns(3, gap="small")

with k1:
    kpi_card("total", "Total policies", f"{total_policies:,.0f}", "Policies in the selected period")

with k2:
    kpi_card("rate", "Renewal rate", f"{renewal_rate:.2f}%", "Renewed ÷ total policies")

with k3:
    kpi_card("premium", "Renewed premium", f"₹{renewed_premium / 1e7:,.2f} Cr", "Premium from renewed policies")


# ============================================================
# CHART DATA
# ============================================================

monthly_df = filtered_df.sort_values("collection_month").copy()
monthly_df["renewed_premium_cr"] = monthly_df["renewed_premium"] / 1e7

section_heading("Trends", TEAL)


# ============================================================
# CHART ROW - Monthly renewal rate + premium mix
# ============================================================

chart1, chart2 = st.columns([1.5, 1], gap="small")

with chart1:
    with st.container(key="chart_rate"):

        fig_renewal = px.line(
            monthly_df,
            x="collection_month",
            y="renewal_rate",
            markers=True,
        )

        style_fig(fig_renewal, "Monthly renewal rate", "Renewal rate (%)", RATE_H)

        fig_renewal.update_yaxes(ticksuffix="%")

        fig_renewal.update_traces(
            line=dict(width=2.6, color=BLUE),
            marker=dict(size=6, color=BLUE),
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Renewal Rate: %{y:.2f}%"
                "<extra></extra>"
            ),
        )

        st.plotly_chart(fig_renewal, use_container_width=True, config=PLOT_CONFIG)


with chart2:
    with st.container(key="chart_mix"):

        non_renewed_premium = max(total_premium - renewed_premium, 0)

        premium_df = pd.DataFrame(
            {
                "Premium Type": ["Renewed Premium", "Non-Renewed Premium"],
                "Premium": [renewed_premium / 1e7, non_renewed_premium / 1e7],
            }
        )

        fig_mix = px.pie(
            premium_df,
            names="Premium Type",
            values="Premium",
            hole=0.64,
            color="Premium Type",
            color_discrete_map={
                "Renewed Premium": TEAL,
                "Non-Renewed Premium": NON_RENEWED,
            },
        )

        fig_mix.update_traces(
            textinfo="none",
            sort=False,
            marker=dict(line=dict(color="white", width=3)),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Premium: ₹%{value:,.2f} Cr<br>"
                "Share: %{percent}"
                "<extra></extra>"
            ),
        )

        fig_mix.update_layout(
            title=chart_title("Premium mix"),
            height=RATE_H,
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor="white",
            font=dict(family=FONT, color="#1f2d47", size=12),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.02,
                xanchor="center",
                x=0.5,
                font=dict(family=FONT, size=12, color="#1f2d47"),
            ),
            annotations=[
                dict(
                    text=f"{premium_share:.1f}%",
                    x=0.5,
                    y=0.53,
                    showarrow=False,
                    font=dict(size=24, color=NAVY, family=DISPLAY_FONT),
                ),
                dict(
                    text="renewed",
                    x=0.5,
                    y=0.41,
                    showarrow=False,
                    font=dict(size=12, color="#5b6b85", family=FONT),
                ),
            ],
        )

        st.plotly_chart(fig_mix, use_container_width=True, config=PLOT_CONFIG)


# ============================================================
# RENEWED PREMIUM TREND
# ============================================================

with st.container(key="chart_premium"):

    fig_premium_trend = px.line(
        monthly_df,
        x="collection_month",
        y="renewed_premium_cr",
        markers=True,
    )

    style_fig(fig_premium_trend, "Monthly renewed premium", "Renewed premium (₹ Cr)", TREND_H)

    fig_premium_trend.update_traces(
        line=dict(width=2.6, color=TEAL),
        marker=dict(size=6, color=TEAL),
        fill="tozeroy",
        fillcolor="rgba(15, 155, 134, 0.08)",
        hovertemplate=(
            "<b>%{x|%b %Y}</b><br>"
            "Renewed Premium: ₹%{y:,.2f} Cr"
            "<extra></extra>"
        ),
    )

    st.plotly_chart(fig_premium_trend, use_container_width=True, config=PLOT_CONFIG)


# ============================================================
# PREVIOUS / NEXT PAGE
# ============================================================

section_heading("Keep exploring", TEAL)

nav1, nav2 = st.columns(2, gap="small")

with nav1:
    nav_card("prev", PREV_PAGE, "Previous")

with nav2:
    nav_card("next", NEXT_PAGE, "Next")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="page-footer">'
    "Life Insurance Renewal Analytics and Forecasting System"
    "</div>",
    unsafe_allow_html=True,
)