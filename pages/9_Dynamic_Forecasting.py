from urllib.parse import quote

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# UI DESIGN TOKENS
# ============================================================

NAVY = "#12233F"
BLUE = "#2F6BD8"
TEAL = "#0F9B86"
AMBER = "#C97A0C"
FONT = "DM Sans"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dynamic Insurance Forecasting",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# FILE PATHS
# ============================================================

HOME_PAGE = "App.py"


GROUPS = {
    "desc": dict(accent="#2f6bd8", tint="#eaf1fd", edge="#a9c3f0"),
}

KPI_STYLES = {
    "total": dict(accent="#2f6bd8", tint="#eaf1fd", icon="shield"),
    "renewed": dict(accent="#0f9b86", tint="#e3f6f2", icon="check"),
    "rate": dict(accent="#c97a0c", tint="#fdf0dc", icon="trend"),
    "premium": dict(accent="#5b4bd6", tint="#eeecfd", icon="rupee"),
}

CARD_META = {
    "overview": ("desc", "shield"),
    "insurer": ("desc", "building"),
    "region": ("desc", "pin"),
    "payment": ("desc", "card"),
    "policy": ("desc", "shield"),
    "timeseries": ("desc", "trend"),
    "model": ("desc", "trend"),
    "forecast": ("desc", "trend"),
    "business": ("desc", "rupee"),
    "ai": ("desc", "check"),
}

PAGES = {
    "overview": "pages/01_Overview.py",
    "insurer": "pages/2_Insurer_Analysis.py",
    "region": "pages/5_Region_Analysis.py",
    "payment": "pages/3_Payment_Analysis.py",
    "policy": "pages/4_Policy_Type_Analysis.py",
    "timeseries": "pages/7_Time_Series_Analysis.py",
    "model": "pages/8_Model_Comparison.py",
    "forecast": "pages/9_Dynamic_Forecasting.py",
    "business": "pages/10_Business_Insights.py",
    "ai": "pages/12_AI_Assistant.py",
}

ICONS = {
    "building": (
        "<path d='M4 21V7l8-4 8 4v14'/><path d='M9 21v-6h6v6'/>"
        "<path d='M8 10h.01M12 10h.01M16 10h.01'/>"
    ),
    "pin": (
        "<path d='M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z'/>"
        "<circle cx='12' cy='10' r='2.5'/>"
    ),
    "card": "<rect x='3' y='5' width='18' height='14' rx='2.5'/><path d='M3 10h18M7 15h4'/>",
    "shield": "<path d='M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z'/><path d='M9 12l2 2 4-4'/>",
    "check": "<circle cx='12' cy='12' r='9'/><path d='M8 12.5l3 3 5-6'/>",
    "trend": "<path d='M3 3v18h18'/><path d='M7 15l4-5 3 3 5-7'/>",
    "rupee": "<path d='M6 5h12M6 10h12M9 5c5 0 6.5 2 6.5 5S14 15 9 15h-.5L15 21'/>",
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

    for group, c in GROUPS.items():
        rules.append(
            f'[class*="st-key-card_{group}_"] '
            f'{{ --accent: {c["accent"]}; --tint: {c["tint"]}; --edge: {c["edge"]}; }}'
        )

    for page, (group, icon) in CARD_META.items():
        rules.append(
            f'.st-key-card_{group}_{page} a::before '
            f'{{ background-image: url("{icon_url(icon, GROUPS[group]["accent"])}"); }}'
        )

    for kind, k in KPI_STYLES.items():
        rules.append(
            f'.kpi-{kind} {{ --accent: {k["accent"]}; --tint: {k["tint"]}; }}'
        )
        rules.append(
            f'.kpi-{kind} .kpi-icon '
            f'{{ background-image: url("{icon_url(k["icon"], k["accent"])}"); }}'
        )

    rules.extend([
        '.st-key-card_desc_overview a::before { background-image: url("%s"); }' % icon_url("shield", GROUPS["desc"]["accent"]),
        '.st-key-card_desc_timeseries a::before { background-image: url("%s"); }' % icon_url("trend", GROUPS["desc"]["accent"]),
        '.st-key-card_desc_model a::before { background-image: url("%s"); }' % icon_url("trend", GROUPS["desc"]["accent"]),
        '.st-key-card_desc_forecast a::before { background-image: url("%s"); }' % icon_url("trend", GROUPS["desc"]["accent"]),
        '.st-key-card_desc_business a::before { background-image: url("%s"); }' % icon_url("rupee", GROUPS["desc"]["accent"]),
        '.st-key-card_desc_ai a::before { background-image: url("%s"); }' % icon_url("check", GROUPS["desc"]["accent"]),
    ])
    return "\n".join(rules)


# ============================================================
# CUSTOM CSS
# ============================================================

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg: #f3f6fb;

    --navy: #0e1b33;
    --muted: #5b6b85;

    /* One spacing value for rows, columns and sections */
    --gap: 16px;
    --card-h: 92px;

    --display: 'Bricolage Grotesque', 'DM Sans', system-ui, sans-serif;
    --body: 'DM Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

html, body, .stApp,
[data-testid="stMarkdownContainer"],
[data-testid="stPageLink"] a,
[data-testid="stExpander"] summary {
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
    text-decoration: none !important;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04);
    transition: border-color 0.16s ease, box-shadow 0.16s ease;
}

.st-key-backlink a:hover {
    border-color: #9db8f5 !important;
    box-shadow: 0 4px 12px rgba(16, 38, 74, 0.10);
}

.st-key-backlink a p { margin: 0 !important; font-size: 13px !important; font-weight: 600; color: #2456d6 !important; }


/* ========================================================
   HERO
   ======================================================== */

.hero {
    position: relative;
    overflow: hidden;
    min-height: 160px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    padding: 26px 38px;
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

.hero-content { position: relative; z-index: 2; max-width: 680px; }

.hero-kicker {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    background: rgba(255, 255, 255, 0.07);
    color: #a9c8ff;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 12px;
}

.hero-title {
    font-family: var(--display);
    font-size: 34px;
    line-height: 1.08;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #ffffff;
    margin: 0;
}

.hero-description {
    font-size: 14px;
    line-height: 1.55;
    color: rgba(255, 255, 255, 0.74);
    max-width: 560px;
    margin-top: 10px;
}

.hero-features { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }

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

.hero-visual { position: relative; z-index: 1; width: 320px; flex-shrink: 0; }
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

.section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: var(--display);
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.005em;
    color: var(--navy);
    margin: 12px 0 8px 0;
}

.section-line { width: 4px; height: 18px; border-radius: 3px; display: inline-block; }


/* ========================================================
   KPI CARDS
   ======================================================== */

.kpi {
    box-sizing: border-box;
    height: 108px;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 0 18px;
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
   CHART / TABLE CARDS
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

[class*="st-key-chart_table"] {
    overflow: visible;
    padding: 14px 14px 14px 18px;
}

.table-title {
    font-family: var(--display);
    font-size: 15px;
    font-weight: 700;
    color: var(--navy);
}


/* ========================================================
   NAVIGATION CARDS (same system as the home page)
   ======================================================== */

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
    height: var(--card-h);
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
   EXPANDER + FOOTER
   ======================================================== */

[data-testid="stExpander"] {
    background: var(--card);
    border: 1px solid var(--border) !important;
    border-radius: 16px;
    overflow: hidden;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: var(--navy) !important;
    font-weight: 600;
}

[data-testid="stExpander"] summary svg { color: var(--navy) !important; }

[data-testid="stExpanderDetails"] p,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
    color: #33445f !important;
    font-size: 14px;
}

.overview-footer {
    text-align: center;
    color: #8fa0b8;
    font-size: 11px;
    margin-top: 8px;
}



/* ========================================================
   FORECASTING CONTROLS + RESULTS
   ======================================================== */
.forecast-control {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px 20px 14px 20px;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04), 0 6px 16px rgba(16, 38, 74, 0.04);
}
.forecast-control-title {
    font-family: var(--display);
    font-size: 15px;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 4px;
}
.forecast-control-copy {
    font-size: 12.5px;
    color: var(--muted);
    margin-bottom: 10px;
}
.forecast-note {
    padding: 11px 14px;
    border-radius: 12px;
    background: #f4f7fc;
    border: 1px solid #e1e8f3;
    color: #51617a;
    font-size: 12.5px;
    line-height: 1.5;
}
.forecast-table-wrap {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04), 0 6px 16px rgba(16, 38, 74, 0.04);
}
.st-key-generate_forecast button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    min-height: 46px !important;
}
.st-key-download_forecast button {
    border-radius: 12px !important;
    font-weight: 600 !important;
}
.st-key-forecast_control_insurer,
.st-key-forecast_control_horizon,
.st-key-forecast_control_model,
.st-key-model_info_card,
.st-key-forecast_info_card,
.st-key-generate_forecast {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px 16px 10px 16px;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04), 0 6px 16px rgba(16, 38, 74, 0.04);
}
.st-key-generate_forecast {
    padding: 10px;
}

/* ========================================================
   RESPONSIVE
   ======================================================== */

@media (max-width: 1100px) {
    .block-container { padding-left: 1.2rem; padding-right: 1.2rem; }
    .hero-visual { width: 260px; }
    .kpi-value { font-size: 23px; }
}

@media (max-width: 900px) {
    .hero { min-height: 140px; padding: 22px 24px; }
    .hero-visual { display: none; }
    .hero-title { font-size: 27px; }
    .block-container { padding-left: 1rem; padding-right: 1rem; }
}

@media (max-width: 700px) {
    :root { --card-h: 88px; }
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
        f'<div class="section-title"><span class="section-line" '
        f'style="background:{color}"></span>{title}</div>',
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


def nav_card(page: str, title: str, description: str) -> None:
    group, _ = CARD_META[page]

    with st.container(key=f"card_{group}_{page}"):
        st.page_link(PAGES[page], label=f"**{title}**\n\n{description}")


def style_fig(fig, title: str, y_title: str, height: int, bottom: int = 20):
    fig.update_layout(
        title=dict(
            text=title,
            x=0.0,
            xanchor="left",
            font=dict(size=16, color=NAVY, family=FONT),
        ),
        xaxis_title="",
        yaxis_title=y_title,
        height=height,
        margin=dict(l=10, r=10, t=56, b=bottom),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family=FONT, color="#1f2d47", size=12),
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


# ============================================================
# CALCULATE OVERALL KPIs
# ============================================================
insurer_df = pd.read_csv(
    "data/processed/monthly_by_insurer.csv"
)

insurer_df["collection_month"] = pd.to_datetime(
    insurer_df["collection_month"]
)

insurer_df["insurer"] = (
    insurer_df["insurer"]
    .astype(str)
    .str.strip()
)

total_policies = insurer_df["total_policies"].sum()
renewed_policies = insurer_df["renewed_policies"].sum()
total_premium = insurer_df["total_premium"].sum()
renewed_premium = insurer_df["renewed_premium"].sum()




# ============================================================
# PAGE / DATA PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOME_PAGE = "App.py"
MONTHLY_INSURER_FILE = PROJECT_ROOT / "data" / "processed" / "monthly_by_insurer.csv"
MODEL_SELECTION_FILE = PROJECT_ROOT / "reports" / "final_model_selection.csv"


# ============================================================
# DATA LOADING
# ============================================================

if not MONTHLY_INSURER_FILE.exists():
    st.error(f"Monthly insurer dataset not found:\n\n`{MONTHLY_INSURER_FILE}`")
    st.stop()


df = pd.read_csv(MONTHLY_INSURER_FILE)
df.columns = df.columns.str.strip().str.lower()

required_columns = ["collection_month", "insurer", "renewed_premium"]
missing_columns = [c for c in required_columns if c not in df.columns]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.write("Available columns:", df.columns.tolist())
    st.stop()


df["collection_month"] = pd.to_datetime(df["collection_month"], errors="coerce")
df["insurer"] = df["insurer"].astype(str).str.strip()
df["renewed_premium"] = pd.to_numeric(df["renewed_premium"], errors="coerce")
df = df.dropna(subset=required_columns).sort_values(["insurer", "collection_month"])

model_selection = None
if MODEL_SELECTION_FILE.exists():
    model_selection = pd.read_csv(MODEL_SELECTION_FILE)
    model_selection.columns = model_selection.columns.str.strip()


# ============================================================
# MODEL SELECTION HELPERS
# ============================================================

def get_auto_model(insurer: str):
    if model_selection is None or model_selection.empty:
        return None

    insurer_column = next(
        (c for c in model_selection.columns if c.lower() == "insurer"),
        None,
    )

    model_column = next(
        (
            c for c in ["final_model", "best_model", "model", "Final Model", "Best Model"]
            if c in model_selection.columns
        ),
        None,
    )

    if insurer_column is None or model_column is None:
        return None

    matching = model_selection[
        model_selection[insurer_column].astype(str).str.strip() == insurer
    ]

    if matching.empty:
        return None

    return str(matching.iloc[0][model_column]).strip()


def normalise_model_name(model_name: str) -> str:
    name = str(model_name).strip().lower()
    aliases = {
        "default prophet": "prophet",
        "seasonal naive": "seasonal naive",
        "seasonal_naive": "seasonal naive",
    }
    return aliases.get(name, name)


# ============================================================
# FORECAST ENGINE
# ============================================================

def generate_forecast(series, model_name, periods):
    series = series.dropna().sort_index()

    if len(series) < 2:
        raise ValueError("Not enough historical observations.")

    model_key = normalise_model_name(model_name)

    if model_key == "naive":
        forecast_values = np.repeat(series.iloc[-1], periods)

    elif model_key == "seasonal naive":
        season_length = 12
        if len(series) < season_length:
            forecast_values = np.repeat(series.iloc[-1], periods)
        else:
            seasonal_values = series.iloc[-season_length:].values
            forecast_values = np.array(
                [seasonal_values[i % season_length] for i in range(periods)]
            )

    elif model_key == "arima":
        from statsmodels.tsa.arima.model import ARIMA

        fitted_model = ARIMA(series, order=(1, 1, 1)).fit()
        forecast_values = fitted_model.forecast(steps=periods).values

    elif model_key == "sarima":
        from statsmodels.tsa.statespace.sarimax import SARIMAX

        fitted_model = SARIMAX(
            series,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 12),
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False)
        forecast_values = fitted_model.forecast(steps=periods).values

    elif model_key == "prophet":
        from prophet import Prophet

        prophet_df = pd.DataFrame({"ds": series.index, "y": series.values})
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
        )
        model.fit(prophet_df)
        future = model.make_future_dataframe(periods=periods, freq="MS")
        prediction = model.predict(future)
        forecast_values = prediction["yhat"].tail(periods).values

    else:
        raise ValueError(f"Unsupported model: {model_name}")

    last_date = series.index.max()
    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=periods,
        freq="MS",
    )

    return pd.DataFrame(
        {
            "month": future_dates,
            "forecast_renewed_premium": forecast_values,
        }
    )


# ============================================================
# NAVIGATION / HEADER
# ============================================================

with st.container(key="backlink"):
    try:
        st.page_link(HOME_PAGE, label="← Back to home")
    except Exception:
        pass


insurers = sorted(df["insurer"].dropna().unique())
selected_insurer = insurers[0]
auto_model = None


# ============================================================
# FORECAST CONFIGURATION
# ============================================================

section_heading("Forecast configuration", BLUE)

control_col1, control_col2, control_col3 = st.columns(3, gap="small")

with control_col1:
    with st.container(key="forecast_control_insurer"):
        st.markdown(
            '<div class="forecast-control-title">Insurer</div>'
            '<div class="forecast-control-copy">Choose the insurer whose renewed premium you want to forecast.</div>',
            unsafe_allow_html=True,
        )
        selected_insurer = st.selectbox(
            "Select insurer",
            insurers,
            label_visibility="collapsed",
        )

with control_col2:
    with st.container(key="forecast_control_horizon"):
        st.markdown(
            '<div class="forecast-control-title">Forecast horizon</div>'
            '<div class="forecast-control-copy">Select how many future monthly observations to generate.</div>',
            unsafe_allow_html=True,
        )
        forecast_months = st.selectbox(
            "Forecast horizon",
            [3, 6, 12, 18, 24],
            index=2,
            format_func=lambda x: f"{x} months",
            label_visibility="collapsed",
        )

with control_col3:
    with st.container(key="forecast_control_model"):
        st.markdown(
            '<div class="forecast-control-title">Forecasting model</div>'
            '<div class="forecast-control-copy">Use the selected model or the insurer-wise model from validation.</div>',
            unsafe_allow_html=True,
        )
        auto_model = get_auto_model(selected_insurer)
        model_options = ["Auto Select", "Naive", "Seasonal Naive", "ARIMA", "SARIMA", "Prophet"]
        selected_model = st.selectbox(
            "Forecasting model",
            model_options,
            label_visibility="collapsed",
        )


actual_model = auto_model if selected_model == "Auto Select" and auto_model else (
    "Naive" if selected_model == "Auto Select" else selected_model
)

insurer_df = df[df["insurer"] == selected_insurer].copy().sort_values("collection_month")
ts = insurer_df.set_index("collection_month")["renewed_premium"]
first_date = insurer_df["collection_month"].min()
last_date = insurer_df["collection_month"].max()

historical_period = (
    f"{first_date.strftime('%b %Y')} – {last_date.strftime('%b %Y')}"
    if pd.notna(first_date) and pd.notna(last_date)
    else "Historical period unavailable"
)

# Hero visual intentionally follows the Overview visual language, but depicts forecasting.
HERO_VISUAL = """<svg viewBox="0 0 340 150" role="img" aria-label="Historical line continuing into a forecast line">
<line x1="10" y1="128" x2="330" y2="128" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<line x1="10" y1="90" x2="330" y2="90" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
<line x1="10" y1="52" x2="330" y2="52" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
<polyline points="15,104 48,84 81,92 114,68 147,77 180,57 213,69 246,47" fill="none" stroke="#7fb2ff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<polyline class="hero-line" pathLength="1" points="246,47 275,61 304,36 328,44" fill="none" stroke="#5eead4" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="0.18 0.02"/>
<circle class="hero-dot" cx="328" cy="44" r="4.5" fill="#ffffff" stroke="#5eead4" stroke-width="2"/>
</svg>"""

HEADER_HTML = f"""<div class="hero">
<div class="hero-content">
<div class="hero-kicker">Forecasting workspace</div>
<div class="hero-title">Dynamic Insurance Forecasting</div>
<div class="hero-description">Insurer-wise forecasting of future monthly renewed premium using the selected time-series model and forecast horizon.</div>
<div class="hero-features">
<span class="hero-feature"><i style="background:#6ea8ff"></i>{selected_insurer}</span>
<span class="hero-feature"><i style="background:#5eead4"></i>{historical_period}</span>
<span class="hero-feature"><i style="background:#fbbf5a"></i>{forecast_months}-month horizon</span>
</div>
</div>
<div class="hero-visual">{HERO_VISUAL}</div>
</div>"""

st.markdown(HEADER_HTML, unsafe_allow_html=True)


# ============================================================
# CURRENT SERIES KPIs
# ============================================================

section_heading("Historical context", BLUE)

latest_value = float(ts.iloc[-1]) if len(ts) else 0.0
historical_average = float(ts.mean()) if len(ts) else 0.0

k1, k2, k3, k4 = st.columns(4, gap="small")
with k1:
    kpi_card("total", "Insurer", selected_insurer, "Selected insurer for forecasting")
with k2:
    kpi_card("renewed", "Historical months", f"{len(insurer_df):,}", "Monthly observations available")
with k3:
    kpi_card("rate", "Last renewed premium", f"₹{latest_value / 1e7:,.2f} Cr", "Most recent historical month")
with k4:
    kpi_card("premium", "Historical average", f"₹{historical_average / 1e7:,.2f} Cr", "Average monthly renewed premium")


# ============================================================
# MODEL INFORMATION
# ============================================================

section_heading("Model selection", TEAL)

info1, info2 = st.columns(2, gap="small")
with info1:
    with st.container(key="model_info_card"):
        st.markdown(
            '<div class="forecast-control-title">Model used for this forecast</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="color:#12233F; font-size:28px; font-weight:700;">{actual_model}</div>',
            unsafe_allow_html=True
        )
        if selected_model == "Auto Select":
            if auto_model:
                st.markdown(
                    '<div class="forecast-note">Auto Select is using the insurer-wise model stored in the final model-selection report.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="forecast-note">No insurer-specific model was found, so the dashboard falls back to Naive forecasting.</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="forecast-note">The model was manually selected for this forecast run.</div>',
                unsafe_allow_html=True,
            )

with info2:
    with st.container(key="forecast_info_card"):
        st.markdown(
            '<div class="forecast-control-title">Forecast target</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="color:#12233F; font-size:28px; font-weight:700;">Monthly renewed premium</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="forecast-note">The model learns the insurer\'s historical monthly renewed-premium series and generates future monthly premium estimates.</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# GENERATE FORECAST
# ============================================================

section_heading("Generate forecast", BLUE)

with st.container(key="generate_forecast"):
    generate = st.button(
        "Generate Forecast",
        type="primary",
        use_container_width=True,
    )


if generate:
    try:
        with st.spinner("Training model and generating forecast..."):
            forecast_df = generate_forecast(ts, actual_model, forecast_months)

        total_forecast = float(forecast_df["forecast_renewed_premium"].sum())
        average_forecast = float(forecast_df["forecast_renewed_premium"].mean())
        minimum_forecast = float(forecast_df["forecast_renewed_premium"].min())
        maximum_forecast = float(forecast_df["forecast_renewed_premium"].max())

        # ====================================================
        # FORECAST KPIs
        # ====================================================
        section_heading("Forecast summary", TEAL)

        c1, c2, c3, c4 = st.columns(4, gap="small")
        with c1:
            kpi_card("total", "Total forecast", f"₹{total_forecast / 1e7:,.2f} Cr", f"Next {forecast_months} months")
        with c2:
            kpi_card("renewed", "Average / month", f"₹{average_forecast / 1e7:,.2f} Cr", "Mean forecasted monthly premium")
        with c3:
            kpi_card("rate", "Forecast minimum", f"₹{minimum_forecast / 1e7:,.2f} Cr", "Lowest forecasted month")
        with c4:
            kpi_card("premium", "Forecast maximum", f"₹{maximum_forecast / 1e7:,.2f} Cr", "Highest forecasted month")

        # ====================================================
        # HISTORICAL + FORECAST CHART
        # ====================================================
        section_heading("Historical vs future forecast", BLUE)

        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=ts.index,
                y=ts.values / 1e7,
                mode="lines+markers",
                name="Historical",
                line=dict(color=BLUE, width=2.8),
                marker=dict(size=5, color=BLUE),
                hovertemplate="<b>%{x|%b %Y}</b><br>Historical: ₹%{y:.2f} Cr<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecast_df["month"],
                y=forecast_df["forecast_renewed_premium"] / 1e7,
                mode="lines+markers",
                name="Forecast",
                line=dict(color=TEAL, width=2.8, dash="dash"),
                marker=dict(size=6, color=TEAL),
                hovertemplate="<b>%{x|%b %Y}</b><br>Forecast: ₹%{y:.2f} Cr<extra></extra>",
            )
        )
        fig.add_vline(
            x=last_date,
            line_width=1.5,
            line_dash="dot",
            line_color=AMBER,
        )
        fig.add_annotation(
            x=last_date,
            y=1,
            yref="paper",
            text="Forecast starts",
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
            font=dict(size=11, color=AMBER, family=FONT),
        )
        style_fig(fig, f"{selected_insurer} — historical and forecasted renewed premium", "Renewed premium (₹ Cr)", 430, bottom=45)
        fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.08, x=0))

        with st.container(key="chart_forecast"):
            st.plotly_chart(fig, use_container_width=True)

        # ====================================================
        # FORECAST TABLE + BAR CHART
        # ====================================================
        section_heading("Monthly forecast", BLUE)
        table_col, bar_col = st.columns(2, gap="small")

        display_forecast = forecast_df.copy()
        display_forecast["Forecast Premium (₹ Cr)"] = (
            display_forecast["forecast_renewed_premium"] / 1e7
        ).round(2)
        display_forecast["Month"] = display_forecast["month"].dt.strftime("%b %Y")
        display_forecast = display_forecast[["Month", "Forecast Premium (₹ Cr)"]]

        with table_col:
            with st.container(key="chart_forecast_table"):
                st.markdown('<div class="table-title">Forecast values</div>', unsafe_allow_html=True)
                st.dataframe(
                    display_forecast,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Forecast Premium (₹ Cr)": st.column_config.NumberColumn(format="%.2f")
                    },
                )

        with bar_col:
            with st.container(key="chart_forecast_bar"):
                import plotly.express as px
                bar_df = display_forecast.copy()
                bar_fig = px.bar(
                    bar_df,
                    x="Month",
                    y="Forecast Premium (₹ Cr)",
                )
                style_fig(bar_fig, "Forecast by month", "Renewed premium (₹ Cr)", 360, bottom=55)
                bar_fig.update_traces(marker_color=TEAL, hovertemplate="<b>%{x}</b><br>Forecast: ₹%{y:.2f} Cr<extra></extra>")
                st.plotly_chart(bar_fig, use_container_width=True)

        # ====================================================
        # DOWNLOAD
        # ====================================================
        csv_data = forecast_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Forecast CSV",
            data=csv_data,
            file_name=f"{selected_insurer}_{forecast_months}_month_forecast.csv",
            mime="text/csv",
            key="download_forecast",
        )

    except Exception as e:
        st.error("Forecast generation failed.")
        st.exception(e)


# ============================================================
# KEEP EXPLORING
# ============================================================

section_heading("Keep exploring", TEAL)

explore1, explore2, explore3 = st.columns(3, gap="small")
with explore1:
    nav_card("timeseries", "Time Series Analysis", "Understand trend, seasonality and historical premium behaviour.")
with explore2:
    nav_card("model", "Model Comparison", "Compare forecasting models and validation performance.")
with explore3:
    nav_card("business", "Business Insights", "Translate forecasts and historical patterns into business insights.")


# ============================================================
# DATA DETAILS + FOOTER
# ============================================================

with st.expander("Forecasting data details"):
    st.write(f"Selected insurer: {selected_insurer}")
    st.write(f"Historical observations: {len(insurer_df):,}")
    st.write(f"Historical period: {historical_period}")
    st.write(f"Forecast target: Monthly renewed premium")
    st.write(f"Selected model: {actual_model}")
    st.write(f"Forecast horizon: {forecast_months} months")
    st.write(f"Model-selection report available: {'Yes' if model_selection is not None else 'No'}")

st.markdown(
    '<div class="overview-footer">Life Insurance Renewal Analytics and Forecasting System</div>',
    unsafe_allow_html=True,
)
