from urllib.parse import quote

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Life Insurance Renewal Overview",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# FILE PATHS
# ============================================================

HOME_PAGE = "App.py"  # change if your main file has another name

POLICY_DATA_PATH = "data/processed/Insurance_renewal_preprocessed.csv"
MONTHLY_DATA_PATH = "data/processed/monthly_renewal_premium.csv"
INSURER_DATA_PATH = "data/processed/monthly_by_insurer.csv"


# ============================================================
# LOAD DATA
# ============================================================

try:
    policy_df = pd.read_csv(POLICY_DATA_PATH)
    monthly_df = pd.read_csv(MONTHLY_DATA_PATH)
    insurer_df = pd.read_csv(INSURER_DATA_PATH)

except FileNotFoundError as e:
    st.error(f"Dataset not found.\n\n{e}")
    st.stop()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

for _df in (policy_df, monthly_df, insurer_df):
    _df.columns = _df.columns.str.strip().str.lower()


# ============================================================
# DATE CONVERSION
# ============================================================

if "collection_date" in policy_df.columns:
    policy_df["collection_date"] = pd.to_datetime(
        policy_df["collection_date"], errors="coerce"
    )

for _df in (policy_df, monthly_df, insurer_df):
    if "collection_month" in _df.columns:
        _df["collection_month"] = pd.to_datetime(
            _df["collection_month"], errors="coerce"
        )


# ============================================================
# CLEAN INSURER NAMES
# ============================================================

for _df in (policy_df, insurer_df):
    if "insurer" in _df.columns:
        _df["insurer"] = _df["insurer"].astype(str).str.strip()


# ============================================================
# NUMERIC COLUMNS
# ============================================================

for column in ["premium_amount", "renewal_flag", "customer_age"]:
    if column in policy_df.columns:
        policy_df[column] = pd.to_numeric(policy_df[column], errors="coerce")

for column in [
    "total_policies",
    "renewed_policies",
    "total_premium",
    "renewed_premium",
    "renewal_rate",
]:
    for _df in (monthly_df, insurer_df):
        if column in _df.columns:
            _df[column] = pd.to_numeric(_df[column], errors="coerce")


# ============================================================
# STYLE TOKENS (shared with the home page)
# ============================================================

NAVY = "#0e1b33"
BLUE = "#2456d6"
TEAL = "#0f9b86"
AMBER = "#c97a0c"
FONT = "DM Sans, system-ui, sans-serif"

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
    "insurer": ("desc", "building"),
    "region": ("desc", "pin"),
    "payment": ("desc", "card"),
    "policy": ("desc", "shield"),
}

PAGES = {
    "insurer": "pages/2_Insurer_Analysis.py",
    "region": "pages/5_Region_Analysis.py",
    "payment": "pages/3_Payment_Analysis.py",
    "policy": "pages/4_Policy_Type_Analysis.py",
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

    return "\n".join(rules)


# ============================================================
# CUSTOM CSS
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

total_policies = insurer_df["total_policies"].sum()
renewed_policies = insurer_df["renewed_policies"].sum()
total_premium = insurer_df["total_premium"].sum()
renewed_premium = insurer_df["renewed_premium"].sum()

overall_renewal_rate = (
    renewed_policies / total_policies * 100 if total_policies > 0 else 0
)

premium_renewal_rate = (
    renewed_premium / total_premium * 100 if total_premium > 0 else 0
)


# ============================================================
# HISTORICAL PERIOD
# ============================================================

start_date = insurer_df["collection_month"].min()
end_date = insurer_df["collection_month"].max()

if pd.notna(start_date) and pd.notna(end_date):
    historical_period = (
        f"{start_date.strftime('%b %Y')} – {end_date.strftime('%b %Y')}"
    )
else:
    historical_period = "Historical period unavailable"

n_insurers = insurer_df["insurer"].nunique()
n_months = insurer_df["collection_month"].nunique()


# ============================================================
# BACK LINK + HEADER
# (HTML blocks below contain no blank lines on purpose)
# ============================================================

with st.container(key="backlink"):
    try:
        st.page_link(HOME_PAGE, label="← Back to home")
    except Exception:
        pass


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


HEADER_HTML = f"""<div class="hero">
<div class="hero-content">
<div class="hero-kicker">Executive dashboard</div>
<div class="hero-title">Life Insurance Renewal Overview</div>
<div class="hero-description">Historical renewal performance and insurer-level business trends.</div>
<div class="hero-features">
<span class="hero-feature"><i style="background:#6ea8ff"></i>{historical_period}</span>
<span class="hero-feature"><i style="background:#5eead4"></i>{n_insurers} insurers</span>
<span class="hero-feature"><i style="background:#fbbf5a"></i>{n_months} months of data</span>
</div>
</div>
<div class="hero-visual">{HERO_VISUAL}</div>
</div>"""

st.markdown(HEADER_HTML, unsafe_allow_html=True)


# ============================================================
# KPI SECTION
# ============================================================

section_heading("Renewal performance", BLUE)

k1, k2, k3, k4 = st.columns(4, gap="small")

with k1:
    kpi_card(
        "total",
        "Total policies",
        f"{total_policies:,.0f}",
        "Policies in the historical dataset",
    )

with k2:
    kpi_card(
        "renewed",
        "Renewed policies",
        f"{renewed_policies:,.0f}",
        "Policies successfully renewed",
    )

with k3:
    kpi_card(
        "rate",
        "Renewal rate",
        f"{overall_renewal_rate:.2f}%",
        "Overall policy renewal rate",
    )

with k4:
    kpi_card(
        "premium",
        "Renewed premium",
        f"₹{renewed_premium / 1e7:,.2f} Cr",
        "Premium from renewed policies",
    )


# ============================================================
# MONTHLY DATA
# ============================================================

monthly_premium = (
    insurer_df.groupby("collection_month")["renewed_premium"]
    .sum()
    .reset_index()
)

monthly_premium["renewed_premium_cr"] = monthly_premium["renewed_premium"] / 1e7


monthly_rate = (
    insurer_df.groupby("collection_month")
    .agg(
        total_policies=("total_policies", "sum"),
        renewed_policies=("renewed_policies", "sum"),
    )
    .reset_index()
)

monthly_rate["renewal_rate"] = (
    monthly_rate["renewed_policies"] / monthly_rate["total_policies"] * 100
)


# ============================================================
# RENEWAL TREND CHARTS
# ============================================================

section_heading("Historical renewal trends", BLUE)

chart_col1, chart_col2 = st.columns(2, gap="small")


with chart_col1:
    with st.container(key="chart_rate"):

        fig_rate = px.line(
            monthly_rate,
            x="collection_month",
            y="renewal_rate",
            markers=True,
        )

        style_fig(fig_rate, "Monthly renewal rate", "Renewal rate (%)", 350)

        fig_rate.update_layout(hovermode="x unified")

        fig_rate.update_traces(
            line=dict(width=2.6, color=BLUE),
            marker=dict(size=6, color=BLUE),
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Renewal Rate: %{y:.2f}%"
                "<extra></extra>"
            ),
        )

        st.plotly_chart(fig_rate, use_container_width=True)


with chart_col2:
    with st.container(key="chart_premium"):

        fig_premium = px.line(
            monthly_premium,
            x="collection_month",
            y="renewed_premium_cr",
            markers=True,
        )

        style_fig(fig_premium, "Monthly renewed premium", "Renewed premium (₹ Cr)", 350)

        fig_premium.update_layout(hovermode="x unified")

        fig_premium.update_traces(
            line=dict(width=2.6, color=TEAL),
            marker=dict(size=6, color=TEAL),
            fill="tozeroy",
            fillcolor="rgba(15, 155, 134, 0.08)",
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Renewed Premium: ₹%{y:.2f} Cr"
                "<extra></extra>"
            ),
        )

        st.plotly_chart(fig_premium, use_container_width=True)


# ============================================================
# INSURER ANALYSIS
# ============================================================

section_heading("Insurer performance", "#2f6bd8")


insurer_premium = (
    insurer_df.groupby("insurer")["renewed_premium"]
    .sum()
    .reset_index()
    .sort_values("renewed_premium", ascending=False)
)

insurer_premium["renewed_premium_cr"] = insurer_premium["renewed_premium"] / 1e7


insurer_rate = (
    insurer_df.groupby("insurer")
    .agg(
        total_policies=("total_policies", "sum"),
        renewed_policies=("renewed_policies", "sum"),
    )
    .reset_index()
)

insurer_rate["renewal_rate"] = (
    insurer_rate["renewed_policies"] / insurer_rate["total_policies"] * 100
)

insurer_rate = insurer_rate.sort_values("renewal_rate", ascending=False)


ins_col1, ins_col2 = st.columns(2, gap="small")


with ins_col1:
    with st.container(key="chart_insurer_premium"):

        fig_insurer_premium = px.bar(
            insurer_premium,
            x="insurer",
            y="renewed_premium_cr",
            text_auto=".2f",
        )

        style_fig(
            fig_insurer_premium,
            "Renewed premium by insurer",
            "Renewed premium (₹ Cr)",
            380,
            bottom=65,
        )

        fig_insurer_premium.update_xaxes(tickangle=-35)

        fig_insurer_premium.update_traces(
            marker_color=BLUE,
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Renewed Premium: ₹%{y:.2f} Cr"
                "<extra></extra>"
            ),
        )

        st.plotly_chart(fig_insurer_premium, use_container_width=True)


with ins_col2:
    with st.container(key="chart_insurer_rate"):

        fig_insurer_rate = px.bar(
            insurer_rate,
            x="insurer",
            y="renewal_rate",
            text_auto=".2f",
        )

        style_fig(
            fig_insurer_rate,
            "Renewal rate by insurer",
            "Renewal rate (%)",
            380,
            bottom=65,
        )

        fig_insurer_rate.update_xaxes(tickangle=-35)

        fig_insurer_rate.update_traces(
            marker_color=TEAL,
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Renewal Rate: %{y:.2f}%"
                "<extra></extra>"
            ),
        )

        st.plotly_chart(fig_insurer_rate, use_container_width=True)


# ============================================================
# INSURER SUMMARY
# ============================================================

section_heading("Insurer summary", "#2f6bd8")


insurer_summary = (
    insurer_df.groupby("insurer")
    .agg(
        total_policies=("total_policies", "sum"),
        renewed_policies=("renewed_policies", "sum"),
        total_premium=("total_premium", "sum"),
        renewed_premium=("renewed_premium", "sum"),
    )
    .reset_index()
)

insurer_summary["renewal_rate"] = (
    insurer_summary["renewed_policies"] / insurer_summary["total_policies"] * 100
)

insurer_summary["premium_renewal_rate"] = (
    insurer_summary["renewed_premium"] / insurer_summary["total_premium"] * 100
)


display_summary = insurer_summary.sort_values(
    "renewed_premium", ascending=False
).copy()

display_summary["total_premium"] = display_summary["total_premium"] / 1e7
display_summary["renewed_premium"] = display_summary["renewed_premium"] / 1e7

display_summary = display_summary.rename(
    columns={
        "insurer": "Insurer",
        "total_policies": "Total Policies",
        "renewed_policies": "Renewed Policies",
        "total_premium": "Total Premium (₹ Cr)",
        "renewed_premium": "Renewed Premium (₹ Cr)",
        "renewal_rate": "Renewal Rate (%)",
        "premium_renewal_rate": "Premium Renewal (%)",
    }
)

for column in [
    "Total Premium (₹ Cr)",
    "Renewed Premium (₹ Cr)",
    "Renewal Rate (%)",
    "Premium Renewal (%)",
]:
    display_summary[column] = display_summary[column].round(2)


with st.container(key="chart_table"):
    st.dataframe(
        display_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total Policies": st.column_config.NumberColumn(format="%d"),
            "Renewed Policies": st.column_config.NumberColumn(format="%d"),
            "Total Premium (₹ Cr)": st.column_config.NumberColumn(format="%.2f"),
            "Renewed Premium (₹ Cr)": st.column_config.NumberColumn(format="%.2f"),
            "Renewal Rate (%)": st.column_config.ProgressColumn(
                format="%.2f", min_value=0, max_value=100
            ),
            "Premium Renewal (%)": st.column_config.ProgressColumn(
                format="%.2f", min_value=0, max_value=100
            ),
        },
    )


# ============================================================
# DETAILED ANALYSIS NAVIGATION
# ============================================================

section_heading("Explore detailed analysis", TEAL)

nav1, nav2, nav3, nav4 = st.columns(4, gap="small")

with nav1:
    nav_card(
        "insurer",
        "Insurer Analysis",
        "Compare insurers on renewal performance and premium.",
    )

with nav2:
    nav_card(
        "region",
        "Region Analysis",
        "Renewal performance across geographical regions.",
    )

with nav3:
    nav_card(
        "payment",
        "Payment Analysis",
        "Renewal behaviour across payment modes.",
    )

with nav4:
    nav_card(
        "policy",
        "Policy Type Analysis",
        "Renewal behaviour and premium by policy type.",
    )


# ============================================================
# OPTIONAL DATA DETAILS
# ============================================================

with st.expander("Data details"):

    st.write(f"Policy-level records: {len(policy_df):,}")

    st.write(
        f"Historical months: {policy_df['collection_month'].nunique():,}"
    )

    st.write(
        f"Number of insurers: {policy_df['insurer'].nunique():,}"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="overview-footer">'
    "Life Insurance Renewal Analytics and Forecasting System"
    "</div>",
    unsafe_allow_html=True,
)