from urllib.parse import quote

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Policy Type Analysis",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONSTANTS
# ============================================================

DATA_PATH = "data/processed/monthly_by_policy_type.csv"

HOME_PAGE = "App.py"
HOME_CANDIDATES = [HOME_PAGE, "app.py", "Home.py", "home.py", "main.py", "streamlit_app.py"]

# Same design tokens as the Insurer / Region Analysis pages.
NAVY = "#0e1b33"
BLUE = "#2456d6"
TEAL = "#0f9b86"
PURPLE = "#7c5cfa"
AMBER = "#c97a0c"
NON_RENEWED = "#dfe6f1"
FONT = "DM Sans, system-ui, sans-serif"
DISPLAY_FONT = "Bricolage Grotesque, DM Sans, system-ui, sans-serif"

# ------------------------------------------------------------
# PAGE NAVIGATION (bottom of page only)
# ------------------------------------------------------------
PAGES = {
    "payment": ("pages/3_Payment_Analysis.py", "Payment Analysis", "Renewal behaviour across payment modes.", "card"),
    "region": ("pages/5_Region_Analysis.py", "Region Analysis", "Renewal behaviour and premium across regions.", "pin"),
}
PREV_PAGE = "payment"
NEXT_PAGE = "region"

# Chart heights - lower these if you want the page even more compact
RATE_H = 260
AREA_H = 220
TREND_H = 210


# ============================================================
# KPI STYLES + ICONS
# ============================================================

KPI_STYLES = {
    "total": dict(accent=BLUE, tint="#eaf1fd", icon="shield"),
    "rate": dict(accent=AMBER, tint="#fdf0dc", icon="trend"),
    "premium": dict(accent=PURPLE, tint="#efecfe", icon="rupee"),
    "avg": dict(accent=TEAL, tint="#e3f6f2", icon="bars"),
}

ICONS = {
    "shield": "<path d='M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z'/><path d='M9 12l2 2 4-4'/>",
    "trend": "<path d='M3 3v18h18'/><path d='M7 15l4-5 3 3 5-7'/>",
    "rupee": "<path d='M6 5h12M6 10h12M9 5c5 0 6.5 2 6.5 5S14 15 9 15h-.5L15 21'/>",
    "bars": "<path d='M5 21V11M12 21V4M19 21v-7'/>",
    "card": "<rect x='3' y='5' width='18' height='14' rx='2.5'/><path d='M3 10h18M7 15h4'/>",
    "pin": "<path d='M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z'/><circle cx='12' cy='10' r='2.5'/>",
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
# CUSTOM CSS (same design system as the Insurer / Region pages)
# ============================================================

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg: #f3f6fb;
    --card: #ffffff;
    --border: #e0e7f2;
    --navy: #0e1b33;
    --muted: #5b6b85;

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
    font-size: 25px;
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

.card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: var(--display);
    font-size: 14px;
    font-weight: 700;
    color: var(--navy);
    margin: 2px 0 8px 2px;
}

.card-title .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }


/* ========================================================
   WIDGETS
   ======================================================== */

[data-testid="stSelectbox"] label p,
[data-testid="stDateInput"] label p {
    color: var(--navy) !important;
    font-size: 13px !important;
    font-weight: 600;
}

div[data-testid="stDateInput"] { width: 100%; }
div[data-testid="stDateInput"] > div { min-width: 100%; }
div[data-testid="stDateInput"] input { font-size: 0.85rem; min-width: 105px; }


/* ========================================================
   HIGHLIGHTS
   ======================================================== */

.hl-item {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    padding: 4px 2px;
}

.hl-bar { width: 4px; align-self: stretch; border-radius: 3px; flex-shrink: 0; min-height: 52px; }

.hl-label {
    font-size: 11.5px;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.hl-month {
    font-family: var(--display);
    font-size: 16px;
    font-weight: 800;
    color: var(--navy);
    margin-top: 2px;
}

.hl-detail { font-size: 12px; color: #64748B; margin-top: 2px; }


/* ========================================================
   EXPANDER (detailed tables)
   ======================================================== */

div[data-testid="stExpander"] {
    background: var(--card);
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04), 0 6px 16px rgba(16, 38, 74, 0.04);
}

div[data-testid="stExpander"] summary {
    font-weight: 600;
    color: var(--navy);
}


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
    .kpi-value { font-size: 21px; }
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


def card_title(text: str, color: str) -> None:
    st.markdown(
        f'<div class="card-title"><span class="dot" style="background:{color}"></span>{text}</div>',
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
        font=dict(size=15, color=NAVY, family=FONT),
    )


def style_fig(fig, title: str, y_title: str, height: int):
    fig.update_layout(
        title=chart_title(title),
        xaxis_title="",
        yaxis_title=y_title,
        height=height,
        margin=dict(l=10, r=10, t=44, b=14),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family=FONT, color="#1f2d47", size=12),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#dfe7f2",
            font=dict(family=FONT, size=12, color=NAVY),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="right",
            x=1,
            font=dict(family=FONT, size=11, color="#1f2d47"),
        ),
    )

    axis_text = dict(color="#1f2d47", size=11.5, family=FONT)
    axis_title = dict(color=NAVY, size=12.5, family=FONT)

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
def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()

    required_columns = [
        "collection_month",
        "policy_type",
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

    return df.sort_values(["policy_type", "collection_month"]).reset_index(drop=True)


try:
    df = load_data()
except FileNotFoundError:
    st.error(f"Dataset not found: `{DATA_PATH}` — make sure it is inside data/processed/")
    st.stop()

policy_types = sorted(df["policy_type"].dropna().unique())


# ============================================================
# BACK LINK
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


# The hero shows the selected policy type, but sits ABOVE the filters,
# so reserve its slot now and fill it once the filters have been read.
hero_slot = st.empty()


# ============================================================
# FILTERS
# ============================================================

with st.container(key="chart_filters"):
    f1, f2, f3 = st.columns([1, 1.4, 1.2], gap="small")

    with f1:
        if "selected_policy_type" not in st.session_state:
            st.session_state["selected_policy_type"] = policy_types[0]
        selected_policy_type = st.selectbox(
            "Policy type",
            policy_types,
            key="selected_policy_type",
        )

    policy_df = df[df["policy_type"] == selected_policy_type].copy()

    min_date = policy_df["collection_month"].min().date()
    max_date = policy_df["collection_month"].max().date()

    with f2:
        date_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    with f3:
        st.markdown(
            f'<div class="filter-note"><strong>{len(policy_types)}</strong> policy types · '
            f'data from <strong>{df["collection_month"].min().strftime("%b %Y")}</strong> to '
            f'<strong>{df["collection_month"].max().strftime("%b %Y")}</strong></div>',
            unsafe_allow_html=True,
        )

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = policy_df[
        (policy_df["collection_month"].dt.date >= start_date)
        & (policy_df["collection_month"].dt.date <= end_date)
    ].copy()
else:
    filtered_df = policy_df.copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

n_months = filtered_df["collection_month"].nunique()


# ============================================================
# HERO
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
<div class="hero-kicker">Policy performance</div>
<div class="hero-title">Policy Type Analysis</div>
<div class="hero-features">
<span class="hero-feature"><i style="background:#6ea8ff"></i>{selected_policy_type}</span>
<span class="hero-feature"><i style="background:#5eead4"></i>{period_start.strftime("%b %Y")} – {period_end.strftime("%b %Y")}</span>
<span class="hero-feature"><i style="background:#fbbf5a"></i>{n_months} months</span>
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
average_premium = total_premium / total_policies if total_policies > 0 else 0
renewed_share = renewed_premium / total_premium * 100 if total_premium > 0 else 0


# ============================================================
# KPI CARDS
# ============================================================

section_heading("Overview", BLUE)

k1, k2, k3, k4 = st.columns(4, gap="small")

with k1:
    kpi_card("total", "Total policies", f"{total_policies:,.0f}", "Policies in the selected period")

with k2:
    kpi_card("rate", "Renewal rate", f"{renewal_rate:.2f}%", "Renewed ÷ total policies")

with k3:
    kpi_card("premium", "Renewed premium", f"₹{renewed_premium / 1e7:,.2f} Cr", "Premium from renewed policies")

with k4:
    kpi_card("avg", "Avg premium / policy", f"₹{average_premium:,.0f}", "Average ticket size")


# ============================================================
# CHART DATA
# ============================================================

monthly_df = filtered_df.sort_values("collection_month").copy()

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
            hovertemplate="<b>%{x|%b %Y}</b><br>Renewal Rate: %{y:.2f}%<extra></extra>",
        )
        st.plotly_chart(fig_renewal, use_container_width=True, config=PLOT_CONFIG)

with chart2:
    with st.container(key="chart_mix"):
        non_renewed_premium = max(total_premium - renewed_premium, 0)

        premium_df = pd.DataFrame({
            "Premium Type": ["Renewed Premium", "Non-Renewed Premium"],
            "Premium": [renewed_premium / 1e7, non_renewed_premium / 1e7],
        })

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
            hovertemplate="<b>%{label}</b><br>Premium: ₹%{value:,.2f} Cr<br>Share: %{percent}<extra></extra>",
        )

        fig_mix.update_layout(
            title=chart_title("Premium mix"),
            height=RATE_H,
            margin=dict(l=10, r=10, t=44, b=10),
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
                dict(text=f"{renewed_share:.1f}%", x=0.5, y=0.53, showarrow=False,
                     font=dict(size=22, color=NAVY, family=DISPLAY_FONT)),
                dict(text="renewed", x=0.5, y=0.41, showarrow=False,
                     font=dict(size=12, color="#5b6b85", family=FONT)),
            ],
        )

        st.plotly_chart(fig_mix, use_container_width=True, config=PLOT_CONFIG)


# ============================================================
# MONTHLY RENEWED PREMIUM (full width area)
# ============================================================

with st.container(key="chart_area"):
    area_df = monthly_df[["collection_month", "renewed_premium"]].copy()
    area_df["renewed_premium"] = area_df["renewed_premium"] / 1e7

    fig_area = px.area(
        area_df,
        x="collection_month",
        y="renewed_premium",
    )
    style_fig(fig_area, "Monthly renewed premium", "Renewed premium (₹ Cr)", AREA_H)
    fig_area.update_traces(
        line=dict(width=2.6, color=TEAL),
        fillcolor="rgba(15, 155, 134, 0.10)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Renewed Premium: ₹%{y:.2f} Cr<extra></extra>",
    )
    st.plotly_chart(fig_area, use_container_width=True, config=PLOT_CONFIG)


# ============================================================
# CHART ROW - Premium trend + Policy trend
# ============================================================

chart3, chart4 = st.columns(2, gap="small")

with chart3:
    with st.container(key="chart_premium_trend"):
        prem_trend = monthly_df[["collection_month", "total_premium", "renewed_premium"]].copy()
        prem_trend["total_premium"] = prem_trend["total_premium"] / 1e7
        prem_trend["renewed_premium"] = prem_trend["renewed_premium"] / 1e7
        prem_melt = prem_trend.melt(id_vars="collection_month", var_name="Series", value_name="Premium")
        prem_melt["Series"] = prem_melt["Series"].map(
            {"total_premium": "Total Premium", "renewed_premium": "Renewed Premium"}
        )

        fig_prem_trend = px.line(
            prem_melt,
            x="collection_month",
            y="Premium",
            color="Series",
            markers=True,
            color_discrete_map={"Total Premium": BLUE, "Renewed Premium": PURPLE},
        )
        style_fig(fig_prem_trend, "Monthly premium trend", "", TREND_H)
        fig_prem_trend.update_yaxes(ticksuffix=" Cr")
        fig_prem_trend.update_traces(
            line=dict(width=2.4),
            marker=dict(size=5),
            hovertemplate="<b>%{x|%b %Y}</b><br>%{fullData.name}: ₹%{y:.2f} Cr<extra></extra>",
        )
        st.plotly_chart(fig_prem_trend, use_container_width=True, config=PLOT_CONFIG)

with chart4:
    with st.container(key="chart_policy_trend"):
        pol_trend = monthly_df[["collection_month", "total_policies", "renewed_policies"]].copy()
        pol_melt = pol_trend.melt(id_vars="collection_month", var_name="Series", value_name="Policies")
        pol_melt["Series"] = pol_melt["Series"].map(
            {"total_policies": "Total Policies", "renewed_policies": "Renewed Policies"}
        )

        fig_pol_trend = px.line(
            pol_melt,
            x="collection_month",
            y="Policies",
            color="Series",
            markers=True,
            color_discrete_map={"Total Policies": BLUE, "Renewed Policies": TEAL},
        )
        style_fig(fig_pol_trend, "Monthly policy trend", "", TREND_H)
        fig_pol_trend.update_traces(
            line=dict(width=2.4),
            marker=dict(size=5),
            hovertemplate="<b>%{x|%b %Y}</b><br>%{fullData.name}: %{y:,.0f}<extra></extra>",
        )
        st.plotly_chart(fig_pol_trend, use_container_width=True, config=PLOT_CONFIG)


# ============================================================
# CHART ROW - Type comparison + Highlights
# ============================================================

chart5, chart6 = st.columns(2, gap="small")

comparison = (
    df.groupby("policy_type")
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

with chart5:
    with st.container(key="chart_comparison"):
        fig_comp = px.bar(
            comparison,
            x="policy_type",
            y="renewal_rate",
            color_discrete_sequence=[BLUE],
        )
        style_fig(fig_comp, "Renewal rate by policy type", "", TREND_H)
        fig_comp.update_yaxes(ticksuffix="%")
        fig_comp.update_traces(hovertemplate="<b>%{x}</b><br>Renewal Rate: %{y:.2f}%<extra></extra>")
        st.plotly_chart(fig_comp, use_container_width=True, config=PLOT_CONFIG)

with chart6:
    with st.container(key="chart_highlights"):
        card_title("Highlights", TEAL)

        best_idx = filtered_df["renewal_rate"].idxmax()
        worst_idx = filtered_df["renewal_rate"].idxmin()
        best_month = filtered_df.loc[best_idx]
        worst_month = filtered_df.loc[worst_idx]

        best_label = best_month["collection_month"].strftime("%B %Y")
        worst_label = worst_month["collection_month"].strftime("%B %Y")
        best_rate = f"{best_month['renewal_rate']:.2f}%"
        worst_rate = f"{worst_month['renewal_rate']:.2f}%"
        best_pol = f"{best_month['renewed_policies']:,.0f}"
        worst_pol = f"{worst_month['renewed_policies']:,.0f}"

        h1, h2 = st.columns(2)

        with h1:
            st.markdown(
                f'<div class="hl-item"><div class="hl-bar" style="background:{TEAL}"></div>'
                f'<div><div class="hl-label">Best month</div>'
                f'<div class="hl-month">{best_label}</div>'
                f'<div class="hl-detail">{best_rate} · {best_pol} renewed</div></div></div>',
                unsafe_allow_html=True,
            )

        with h2:
            st.markdown(
                f'<div class="hl-item"><div class="hl-bar" style="background:{AMBER}"></div>'
                f'<div><div class="hl-label">Lowest month</div>'
                f'<div class="hl-month">{worst_label}</div>'
                f'<div class="hl-detail">{worst_rate} · {worst_pol} renewed</div></div></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div class="hl-item"><div class="hl-bar" style="background:{BLUE}"></div>'
            f'<div><div class="hl-label">Coverage</div>'
            f'<div class="hl-month">{n_months} months</div>'
            f'<div class="hl-detail">of data for {selected_policy_type}</div></div></div>',
            unsafe_allow_html=True,
        )


# ============================================================
# DETAILED TABLES (collapsed — keeps everything on one screen)
# ============================================================

with st.expander("Detailed tables"):
    section_heading("Policy type comparison", BLUE)

    display_comparison = comparison.copy()
    display_comparison["total_premium"] = display_comparison["total_premium"] / 1e7
    display_comparison["renewed_premium"] = display_comparison["renewed_premium"] / 1e7
    display_comparison = display_comparison.rename(
        columns={
            "policy_type": "Policy Type",
            "total_policies": "Total Policies",
            "renewed_policies": "Renewed Policies",
            "total_premium": "Total Premium (₹ Cr)",
            "renewed_premium": "Renewed Premium (₹ Cr)",
            "renewal_rate": "Renewal Rate (%)",
            "premium_renewal_rate": "Premium Renewal Rate (%)",
        }
    )
    st.dataframe(display_comparison, use_container_width=True, hide_index=True)

    section_heading("Monthly data", TEAL)

    display_df = filtered_df.copy()
    display_df["total_premium"] = display_df["total_premium"] / 1e7
    display_df["renewed_premium"] = display_df["renewed_premium"] / 1e7
    display_df = display_df.rename(
        columns={
            "collection_month": "Month",
            "policy_type": "Policy Type",
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
        label="Download Policy Type Data",
        data=csv_data,
        file_name=f"{selected_policy_type}_monthly_analysis.csv",
        mime="text/csv",
    )


# ============================================================
# PREVIOUS / NEXT PAGE
# (real st.page_link cards - the old version was plain HTML with
# no href, so the buttons looked clickable but did nothing)
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