import html
import os
from urllib.parse import quote

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Business Insights",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

INSURER_FILE = "data/processed/monthly_by_insurer.csv"
BUSINESS_FILE = "reports/business_insights.csv"

NAVY = "#0e1b33"
BLUE = "#2456d6"
TEAL = "#0f9b86"
AMBER = "#c97a0c"
PURPLE = "#5b4bd6"
NON_RENEWED = "#dfe6f1"
FONT = "DM Sans, system-ui, sans-serif"
DISPLAY_FONT = "Bricolage Grotesque, DM Sans, system-ui, sans-serif"

PAGES = {

    "dynamic": (
        "pages/9_Dynamic_Forecasting.py",
        "Dynamic Forecasting",
        "Generate interactive future renewal premium forecasts.",
        "sliders"
    ),

    "duration": (
        "pages/11_Duration_Analysis.py",
        "Duration Analysis",
        "Analyze renewal performance across policy durations.",
        "spark"
    ),

}

PREV_PAGE = "dynamic"

NEXT_PAGE = "duration"

KPI_STYLES = {
    "policies": dict(accent="#2f6bd8", tint="#eaf1fd", icon="shield"),
    "renewed": dict(accent="#0f9b86", tint="#e3f6f2", icon="trend"),
    "premium": dict(accent="#5b4bd6", tint="#eeecfd", icon="rupee"),
    "rate": dict(accent="#c97a0c", tint="#fdf0dc", icon="rate"),
}

ICONS = {
    "shield": "<path d='M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z'/><path d='M9 12l2 2 4-4'/>",
    "trend": "<path d='M3 3v18h18'/><path d='M7 15l4-5 3 3 5-7'/>",
    "rupee": "<path d='M6 5h12M6 10h12M9 5c5 0 6.5 2 6.5 5S14 15 9 15h-.5L15 21'/>",
    "rate": "<circle cx='12' cy='12' r='8'/><path d='M8 12l2.5 2.5L16 9'/>",
    "sliders": "<path d='M4 6h9M17 6h3M4 12h3M11 12h9M4 18h11M19 18h1'/><circle cx='15' cy='6' r='2'/><circle cx='9' cy='12' r='2'/><circle cx='17' cy='18' r='2'/>",
    "spark": "<path d='M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z'/><path d='M19 16l.7 2 2 .7-.2 2-.7-2-2-.7 2-.7z'/>",
}

def icon_url(name, stroke):
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
           f"stroke='{stroke}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>{ICONS[name]}</svg>")
    return "data:image/svg+xml," + quote(svg)

def build_dynamic_css():
    rules = []
    for kind, style in KPI_STYLES.items():
        rules.append(f'.kpi-{kind} {{ --accent: {style["accent"]}; --tint: {style["tint"]}; }}')
        rules.append(f'.kpi-{kind} .kpi-icon {{ background-image: url("{icon_url(style["icon"], style["accent"])}"); }}')
    for slot, page_key in (("prev", PREV_PAGE), ("next", NEXT_PAGE)):
        icon = PAGES[page_key][3]
        rules.append(f'.st-key-card_desc_{slot} a::before {{ background-image: url("{icon_url(icon, "#2f6bd8")}"); }}')
    return "\n".join(rules)

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

/* Sidebar now hosts the "All pages" nav, so keep it usable - just
   hide Streamlit's own auto-generated multipage nav list inside it. */
[data-testid="stSidebarNav"] { display: none !important; }

[data-testid="stSidebar"] {
    background: var(--card);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.2rem;
}

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
   ALL-PAGES NAV (now lives in the sidebar - single column,
   slightly slimmer than the old bottom-of-page grid cards)
   ======================================================== */

[class*="st-key-mini_desc_"] { --accent: #2f6bd8; --tint: #eaf1fd; --edge: #a9c3f0; }
[class*="st-key-mini_fcst_"] { --accent: #0f9b86; --tint: #e3f6f2; --edge: #8fd8ca; }
[class*="st-key-mini_ai_"]   { --accent: #c97a0c; --tint: #fdf0dc; --edge: #eec78a; }

[class*="st-key-mini_"],
[class*="st-key-mini_"] > div,
[class*="st-key-mini_"] [data-testid="stPageLink"] {
    width: 100% !important;
    min-width: 0 !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

[class*="st-key-mini_"] a {
    position: relative;
    overflow: hidden;
    box-sizing: border-box;
    width: 100% !important;
    height: 60px;
    min-height: 0 !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center;
    gap: 12px;
    padding: 0 40px 0 12px !important;
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04), 0 4px 12px rgba(16, 38, 74, 0.04);
    color: var(--navy) !important;
    text-decoration: none !important;
    transition: border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
}

[class*="st-key-mini_"] a:hover {
    border-color: var(--edge) !important;
    box-shadow: 0 8px 20px rgba(16, 38, 74, 0.10);
    transform: translateY(-2px);
}

[class*="st-key-mini_"] a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

[class*="st-key-mini_"] a::before {
    content: "";
    flex: 0 0 36px;
    width: 36px;
    height: 36px;
    border-radius: 11px;
    background-color: var(--tint);
    background-repeat: no-repeat;
    background-position: center;
    background-size: 19px 19px;
}

[class*="st-key-mini_"] a::after {
    content: "→";
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--tint);
    color: var(--accent);
    font-size: 12px;
    font-weight: 700;
    transition: background-color 0.16s ease, color 0.16s ease;
}

[class*="st-key-mini_"] a:hover::after { background: var(--accent); color: #ffffff; }

[class*="st-key-mini_"] a [data-testid="stMarkdownContainer"] {
    flex: 1 1 auto;
    min-width: 0;
    overflow: hidden;
}

[class*="st-key-mini_"] a p {
    margin: 0 !important;
    line-height: 1.3 !important;
    font-size: 13px !important;
    font-weight: 700;
    color: var(--navy) !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

[class*="st-key-mini_"] a strong { font-weight: 700; }

.sidebar-nav-title {
    font-family: var(--display);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: var(--muted);
    margin: 4px 4px 10px 4px;
}


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

[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] { display: none !important; }

.insight-card {
    box-sizing: border-box;
    height: 100%;
    padding: 18px 20px;
    border: 1px solid var(--border);
    border-radius: 16px;
    background: var(--card);
    box-shadow: 0 1px 2px rgba(16,38,74,.04), 0 6px 16px rgba(16,38,74,.04);
}
.insight-title { font-family: var(--display); font-size: 14px; font-weight: 700; color: var(--navy); margin-bottom: 6px; }
.insight-text { font-size: 13px; line-height: 1.55; color: var(--muted); }

.st-key-chart_table {
    box-sizing: border-box;
    width: 100%;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px;
    box-shadow: 0 1px 2px rgba(16,38,74,.04), 0 6px 16px rgba(16,38,74,.04);
}

"""
st.markdown(f"<style>{BASE_CSS}\n{build_dynamic_css()}</style>", unsafe_allow_html=True)

def section_heading(title, color=BLUE):
    st.markdown(
        f'<div class="section-block"><div class="section-title"><span class="section-line" style="background:{color}"></span>{html.escape(title)}</div></div>',
        unsafe_allow_html=True,
    )

def kpi_card(kind, label, value, description):
    st.markdown(
        f'<div class="kpi kpi-{kind}"><div class="kpi-icon"></div><div class="kpi-body"><div class="kpi-label">{html.escape(label)}</div><div class="kpi-value">{html.escape(value)}</div><div class="kpi-description">{html.escape(description)}</div></div></div>',
        unsafe_allow_html=True,
    )

def nav_card(slot, page_key, prefix):
    path, title, description, _ = PAGES[page_key]
    with st.container(key=f"card_desc_{slot}"):
        st.page_link(path, label=f"**{prefix}: {title}**\n\n{description}")

def chart_title(text):
    return dict(text=text, x=0.0, xanchor="left", font=dict(size=16, color=NAVY, family=FONT))

def style_fig(fig, title, y_title, height=270):
    fig.update_layout(title=chart_title(title), xaxis_title="", yaxis_title=y_title, height=height,
                      margin=dict(l=10, r=10, t=50, b=16), plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(family=FONT, color="#1f2d47", size=12), hovermode="x unified",
                      hoverlabel=dict(bgcolor="white", bordercolor="#dfe7f2", font=dict(family=FONT, size=12, color=NAVY)))
    axis_text = dict(color="#1f2d47", size=12, family=FONT)
    axis_title = dict(color=NAVY, size=13, family=FONT)
    fig.update_xaxes(showgrid=False, showline=True, linecolor="#9fb0c8", tickfont=axis_text, title_font=axis_title)
    fig.update_yaxes(gridcolor="#e3e9f2", zeroline=False, tickfont=axis_text, title_font=axis_title)
    return fig

PLOT_CONFIG = {"displayModeBar": False}

# -------------------- DATA --------------------
if not os.path.exists(INSURER_FILE):
    st.error(f"Dataset not found: `{INSURER_FILE}`")
    st.stop()
if not os.path.exists(BUSINESS_FILE):
    st.error(f"Business insights file not found: `{BUSINESS_FILE}`")
    st.stop()

monthly = pd.read_csv(INSURER_FILE)
business = pd.read_csv(BUSINESS_FILE)
monthly.columns = monthly.columns.str.strip()
business.columns = business.columns.str.strip()
required = ["collection_month", "insurer", "total_policies", "renewed_policies", "total_premium", "renewed_premium", "renewal_rate"]
missing = [c for c in required if c not in monthly.columns]
if missing:
    st.error(f"Missing required columns in `{INSURER_FILE}`: {missing}")
    st.stop()
monthly["collection_month"] = pd.to_datetime(monthly["collection_month"], errors="coerce")
monthly["insurer"] = monthly["insurer"].astype(str).str.strip()
for col in required[2:]:
    monthly[col] = pd.to_numeric(monthly[col], errors="coerce")
monthly = monthly.dropna(subset=["collection_month", "insurer"]).sort_values(["insurer", "collection_month"]).reset_index(drop=True)
if "Insurer" in business.columns:
    business["Insurer"] = business["Insurer"].astype(str).str.strip()

# -------------------- BACK HOME --------------------
with st.container(key="backlink"):
    st.page_link("App.py", label="← Back to Home")

# -------------------- HERO --------------------
period_start = monthly["collection_month"].min()
period_end = monthly["collection_month"].max()
insurer_count = monthly["insurer"].nunique()
HERO_VISUAL = """<svg viewBox="0 0 340 150" role="img" aria-label="Business performance chart"><line x1="10" y1="128" x2="330" y2="128" stroke="rgba(255,255,255,0.22)"/><line x1="10" y1="90" x2="330" y2="90" stroke="rgba(255,255,255,0.07)"/><line x1="10" y1="52" x2="330" y2="52" stroke="rgba(255,255,255,0.07)"/><g class="hero-bars" fill="rgba(127,178,255,0.42)"><rect x="14" y="98" width="20" height="30" rx="4"/><rect x="46" y="84" width="20" height="44" rx="4"/><rect x="78" y="90" width="20" height="38" rx="4"/><rect x="110" y="70" width="20" height="58" rx="4"/><rect x="142" y="76" width="20" height="52" rx="4"/><rect x="174" y="58" width="20" height="70" rx="4"/><rect x="206" y="64" width="20" height="64" rx="4"/><rect x="238" y="44" width="20" height="84" rx="4"/><rect x="270" y="50" width="20" height="78" rx="4"/><rect x="302" y="30" width="20" height="98" rx="4"/></g><polyline class="hero-line" pathLength="1" points="24,86 56,72 88,78 120,58 152,64 184,46 216,52 248,32 280,38 312,18" fill="none" stroke="#5eead4" stroke-width="2.8" stroke-linecap="round"/><circle class="hero-dot" cx="312" cy="18" r="4.5" fill="#fff" stroke="#5eead4" stroke-width="2"/></svg>"""
HERO_HTML = f"""<div class="hero"><div class="hero-content"><div class="hero-kicker">Business intelligence workspace</div><div class="hero-title">Business Insights</div><div class="hero-features"><span class="hero-feature"><i style="background:#6ea8ff"></i>{insurer_count} insurers</span><span class="hero-feature"><i style="background:#5eead4"></i>{period_start.strftime('%b %Y')} – {period_end.strftime('%b %Y')}</span><span class="hero-feature"><i style="background:#fbbf5a"></i>Renewal intelligence</span></div></div><div class="hero-visual">{HERO_VISUAL}</div></div>"""
st.markdown(HERO_HTML, unsafe_allow_html=True)

# -------------------- OVERALL KPIs --------------------
section_heading("Overall business performance", BLUE)
total_policies = monthly["total_policies"].sum()
renewed_policies = monthly["renewed_policies"].sum()
total_premium = monthly["total_premium"].sum()
renewed_premium = monthly["renewed_premium"].sum()
overall_rate = renewed_policies / total_policies * 100 if total_policies else 0
k1, k2, k3, k4 = st.columns(4, gap="small")
with k1: kpi_card("policies", "Total policies", f"{total_policies:,.0f}", "Policies in the historical dataset")
with k2: kpi_card("renewed", "Renewed policies", f"{renewed_policies:,.0f}", "Policies successfully renewed")
with k3: kpi_card("premium", "Renewed premium", f"₹{renewed_premium / 1e7:,.2f} Cr", "Premium from renewed policies")
with k4: kpi_card("rate", "Overall renewal rate", f"{overall_rate:.2f}%", "Renewed policies ÷ total policies")

# -------------------- INSURER ANALYSIS --------------------
section_heading("Insurer business analysis", TEAL)
insurers = sorted(monthly["insurer"].dropna().unique())
selected_insurer = st.selectbox("Select insurer", insurers, label_visibility="collapsed")
insurer_monthly = monthly[monthly["insurer"] == selected_insurer].copy()
if "Insurer" in business.columns:
    insurer_business = business[business["Insurer"] == selected_insurer].copy()
else:
    insurer_business = pd.DataFrame()
row = insurer_business.iloc[0] if not insurer_business.empty else pd.Series(dtype=object)

def safe_number(key):
    value = pd.to_numeric(row.get(key, np.nan), errors="coerce")
    return float(value) if pd.notna(value) else np.nan

avg_premium = safe_number("Historical Avg Premium")
historical_growth = safe_number("Historical Growth %")
forecast_total = safe_number("12 Month Forecast")
forecast_vs_history = safe_number("Forecast vs Historical %")
forecast_volatility = safe_number("Forecast Volatility %")

m1, m2, m3, m4 = st.columns(4, gap="small")
with m1: kpi_card("premium", "Historical avg premium", f"₹{avg_premium/1e7:.2f} Cr" if pd.notna(avg_premium) else "N/A", "Average monthly renewed premium")
with m2: kpi_card("rate", "Historical growth", f"{historical_growth:.2f}%" if pd.notna(historical_growth) else "N/A", "Growth across historical period")
with m3: kpi_card("premium", "12-month forecast", f"₹{forecast_total/1e7:.2f} Cr" if pd.notna(forecast_total) else "N/A", "Forecasted renewed premium")
with m4: kpi_card("renewed", "Forecast vs history", f"{forecast_vs_history:.2f}%" if pd.notna(forecast_vs_history) else "N/A", "Forecast level vs historical average")

# -------------------- TRENDS --------------------
section_heading("Premium and renewal trends", TEAL)
trend_df = insurer_monthly.sort_values("collection_month").copy()
trend_df["renewed_premium_cr"] = trend_df["renewed_premium"] / 1e7
c1, c2 = st.columns([1.45, 1], gap="small")
with c1:
    with st.container(key="chart_premium"):
        fig = px.line(trend_df, x="collection_month", y="renewed_premium_cr", markers=True)
        style_fig(fig, "Monthly renewed premium", "Renewed premium (₹ Cr)", 285)
        fig.update_traces(line=dict(color=TEAL, width=2.6), marker=dict(color=TEAL, size=6), fill="tozeroy", fillcolor="rgba(15,155,134,0.08)", hovertemplate="<b>%{x|%b %Y}</b><br>Renewed Premium: ₹%{y:,.2f} Cr<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)
with c2:
    with st.container(key="chart_rate"):
        fig = px.line(trend_df, x="collection_month", y="renewal_rate", markers=True)
        style_fig(fig, "Monthly renewal rate", "Renewal rate (%)", 285)
        fig.update_yaxes(ticksuffix="%")
        fig.update_traces(line=dict(color=BLUE, width=2.6), marker=dict(color=BLUE, size=6), hovertemplate="<b>%{x|%b %Y}</b><br>Renewal Rate: %{y:.2f}%<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)

# -------------------- BUSINESS OUTLOOK --------------------
section_heading("Business outlook", AMBER)

def insight(title, text):
    st.markdown(f'<div class="insight-card"><div class="insight-title">{html.escape(title)}</div><div class="insight-text">{text}</div></div>', unsafe_allow_html=True)

a, b = st.columns(2, gap="small")
with a:
    text = f"{html.escape(selected_insurer)} has an historical average monthly renewed premium of approximately <strong>₹{avg_premium/1e7:.2f} Cr</strong>." if pd.notna(avg_premium) else "Historical average premium is not available in the business-insights report."
    insight("Premium performance", text)
with b:
    text = f"Forecast volatility is approximately <strong>{forecast_volatility:.2f}%</strong> across the forecast period." if pd.notna(forecast_volatility) else "Forecast volatility is not available in the business-insights report."
    insight("Forecast stability", text)
a, b = st.columns(2, gap="small")
with a:
    text = f"Historical premium growth is approximately <strong>{historical_growth:.2f}%</strong>." if pd.notna(historical_growth) else "Historical growth is not available in the business-insights report."
    insight("Historical growth", text)
with b:
    if pd.notna(forecast_vs_history):
        direction = "higher" if forecast_vs_history >= 0 else "lower"
        text = f"The average forecast is approximately <strong>{abs(forecast_vs_history):.2f}%</strong> {direction} than the historical average."
    else:
        text = "Forecast comparison is not available in the business-insights report."
    insight("Forecast outlook", text)

# -------------------- INSURER COMPARISON --------------------
section_heading("Insurer comparison", BLUE)
comparison_columns = ["Insurer", "Historical Avg Premium", "Historical Growth %", "12 Month Forecast", "Forecast vs Historical %", "Forecast Volatility %"]
available_columns = [c for c in comparison_columns if c in business.columns]
comparison = business[available_columns].copy()
for col in ["Historical Avg Premium", "12 Month Forecast"]:
    if col in comparison.columns:
        comparison[col] = pd.to_numeric(comparison[col], errors="coerce") / 1e7
for col in ["Historical Growth %", "Forecast vs Historical %", "Forecast Volatility %"]:
    if col in comparison.columns:
        comparison[col] = pd.to_numeric(comparison[col], errors="coerce")
comparison = comparison.round(2)
with st.container(key="chart_table"):
    st.dataframe(comparison, use_container_width=True, hide_index=True)

# -------------------- EXPORT --------------------
section_heading("Export", PURPLE)
csv_data = business.to_csv(index=False).encode("utf-8")
st.download_button("Download Business Insights CSV", csv_data, "business_insights.csv", "text/csv")

# -------------------- NAVIGATION --------------------
section_heading("Keep exploring", TEAL)
n1, n2 = st.columns(2, gap="small")
with n1: nav_card("prev", PREV_PAGE, "Previous")
with n2: nav_card("next", NEXT_PAGE, "Next")

st.markdown('<div class="page-footer">Life Insurance Renewal Analytics and Forecasting System</div>', unsafe_allow_html=True)
