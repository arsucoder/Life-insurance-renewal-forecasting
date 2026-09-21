from urllib.parse import quote

import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Life Insurance Renewal Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PAGE ROUTES
# ============================================================

PAGES = {
    "overview": "pages/01_Overview.py",
    "insurer": "pages/2_Insurer_Analysis.py",
    "region": "pages/5_Region_Analysis.py",
    "payment": "pages/3_Payment_Analysis.py",
    "policy": "pages/4_Policy_Type_Analysis.py",
    "yearly": "pages/6_Yearly_Analysis.py",
    "timeseries": "pages/7_Time_Series_Analysis.py",
    "models": "pages/8_Model_Comparison.py",
    "dynamic": "pages/9_Dynamic_Forecasting.py",
    "insights": "pages/10_Business_Insights.py",
    "ai": "pages/12_AI_Assistant.py",
}


# ============================================================
# CARD STYLE SYSTEM
# ============================================================

GROUPS = {
    "quick": dict(accent="#2456d6", tint="#e7eeff", edge="#9db8f5", solid=True),
    "desc": dict(accent="#2f6bd8", tint="#eaf1fd", edge="#a9c3f0"),
    "fcst": dict(accent="#0f9b86", tint="#e3f6f2", edge="#8fd8ca"),
    "ai": dict(accent="#c97a0c", tint="#fdf0dc", edge="#eec78a"),
}

# page key -> (group, icon)
CARD_META = {
    "overview": ("quick", "grid"),
    "insurer": ("quick", "building"),
    "region": ("desc", "pin"),
    "payment": ("desc", "card"),
    "policy": ("desc", "shield"),
    "yearly": ("fcst", "calendar"),
    "timeseries": ("fcst", "trend"),
    "models": ("fcst", "bars"),
    "dynamic": ("fcst", "sliders"),
    "insights": ("fcst", "bulb"),
    "ai": ("ai", "spark"),
}


# ============================================================
# SVG ICONS
# ============================================================

ICONS = {
    "grid": (
        "<rect x='3' y='3' width='8' height='8' rx='1.5'/>"
        "<rect x='13' y='3' width='8' height='5' rx='1.5'/>"
        "<rect x='13' y='10' width='8' height='11' rx='1.5'/>"
        "<rect x='3' y='13' width='8' height='8' rx='1.5'/>"
    ),
    "building": (
        "<path d='M4 21V7l8-4 8 4v14'/>"
        "<path d='M9 21v-6h6v6'/>"
        "<path d='M8 10h.01M12 10h.01M16 10h.01'/>"
    ),
    "pin": (
        "<path d='M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z'/>"
        "<circle cx='12' cy='10' r='2.5'/>"
    ),
    "card": (
        "<rect x='3' y='5' width='18' height='14' rx='2.5'/>"
        "<path d='M3 10h18M7 15h4'/>"
    ),
    "shield": (
        "<path d='M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z'/>"
        "<path d='M9 12l2 2 4-4'/>"
    ),
    "calendar": (
        "<rect x='3' y='5' width='18' height='16' rx='2.5'/>"
        "<path d='M3 10h18M8 3v4M16 3v4'/>"
    ),
    "trend": "<path d='M3 3v18h18'/><path d='M7 15l4-5 3 3 5-7'/>",
    "bars": "<path d='M5 21V11M12 21V4M19 21v-7'/>",
    "sliders": (
        "<path d='M4 6h9M17 6h3M4 12h3M11 12h9M4 18h11M19 18h1'/>"
        "<circle cx='15' cy='6' r='2'/>"
        "<circle cx='9' cy='12' r='2'/>"
        "<circle cx='17' cy='18' r='2'/>"
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


def build_card_css() -> str:
    rules = []

    for group, c in GROUPS.items():
        rules.append(
            f'[class*="st-key-card_{group}_"] '
            f'{{ --accent: {c["accent"]}; --tint: {c["tint"]}; --edge: {c["edge"]}; }}'
        )

    for page, (group, icon) in CARD_META.items():
        stroke = "#ffffff" if GROUPS[group].get("solid") else GROUPS[group]["accent"]
        rules.append(
            f'.st-key-card_{group}_{page} a::before '
            f'{{ background-image: url("{icon_url(icon, stroke)}"); }}'
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

    /* ONE spacing value used everywhere: between rows, columns and sections */
    --gap: 16px;

    /* Fixed card heights so every card in a row/column is identical */
    --card-h: 92px;
    --card-h-lg: 104px;

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

header[data-testid="stHeader"] {
    height: 1.5rem;
    background: transparent;
}

.block-container {
    max-width: 1400px;
    padding: 1rem 2rem 1.5rem 2rem;
}


/* ========================================================
   SPACING SYSTEM
   Vertical gaps and horizontal column gaps are forced to the
   same value, so the grid rhythm is constant.
   ======================================================== */

div[data-testid="stVerticalBlock"] { gap: var(--gap); }

div[data-testid="stHorizontalBlock"] { gap: var(--gap) !important; }

/* Let columns shrink instead of overflowing into their neighbour */
@media (min-width: 641px) {
    div[data-testid="stColumn"] { min-width: 0 !important; }
}


/* ========================================================
   HERO
   ======================================================== */

.hero {
    position: relative;
    overflow: hidden;
    min-height: 190px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    padding: 28px 38px;
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

.hero-content { position: relative; z-index: 2; max-width: 640px; }

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
    font-size: 38px;
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

.hero-visual { position: relative; z-index: 1; width: 360px; flex-shrink: 0; }
.hero-visual svg { width: 100%; height: auto; display: block; }

@keyframes draw-line { from { stroke-dashoffset: 1; } to { stroke-dashoffset: 0; } }
@keyframes fade-in   { from { opacity: 0; } to { opacity: 1; } }

.chart-actual   { stroke-dasharray: 1; animation: draw-line 1.4s ease-out both; }
.chart-forecast { animation: fade-in 0.7s ease-out 1.2s both; }
.chart-band     { animation: fade-in 0.9s ease-out 1.4s both; }

@media (prefers-reduced-motion: reduce) {
    .chart-actual, .chart-forecast, .chart-band { animation: none; }
}


/* ========================================================
   SECTION HEADINGS
   28px of air above (12 margin + 16 gap), 16px below.
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
   CARD WRAPPERS
   Strip every margin/padding Streamlit puts around a card
   so the only space between cards is --gap.
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


/* ========================================================
   CARD
   ======================================================== */

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

[class*="st-key-card_"] a:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}

/* Icon tile */
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

/* Arrow chip */
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

[class*="st-key-card_"] a:hover::after {
    background: var(--accent);
    color: #ffffff;
    right: 13px;
}

/* Text: title on one line, description clamped to two lines */
[class*="st-key-card_"] a [data-testid="stMarkdownContainer"] {
    flex: 1 1 auto;
    min-width: 0;
    overflow: hidden;
}

[class*="st-key-card_"] a p {
    margin: 0 !important;
    line-height: 1.4 !important;
}

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


/* ---------- Quick access: taller, solid icon tile ---------- */

[class*="st-key-card_quick_"] a {
    height: var(--card-h-lg);
    padding-left: 20px !important;
    border-color: #cfdcf7 !important;
    background: linear-gradient(100deg, #ffffff 55%, #f1f6ff) !important;
}

[class*="st-key-card_quick_"] a::before {
    flex-basis: 52px;
    width: 52px;
    height: 52px;
    border-radius: 15px;
    background-color: var(--accent);
    background-size: 26px 26px;
    box-shadow: 0 6px 14px rgba(36, 86, 214, 0.28);
}

[class*="st-key-card_quick_"] a p:first-of-type { font-size: 17px !important; }
[class*="st-key-card_quick_"] a p + p { font-size: 13px !important; }


/* ---------- AI assistant: full width ---------- */

[class*="st-key-card_ai_"] a {
    background: linear-gradient(100deg, #fff6e6 0%, #ffffff 70%) !important;
    border-color: #f0d7a4 !important;
}


/* ========================================================
   FOOTER
   ======================================================== */

.footer {
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
    .hero-visual { width: 300px; }
}

@media (max-width: 900px) {
    .hero { min-height: 150px; padding: 22px 24px; }
    .hero-visual { display: none; }
    .hero-title { font-size: 28px; }
    .block-container { padding-left: 1rem; padding-right: 1rem; }
}

@media (max-width: 700px) {
    :root { --card-h: 88px; --card-h-lg: 96px; }
    [class*="st-key-card_"] a { padding-right: 52px !important; }
}
"""

st.markdown(
    f"<style>{BASE_CSS}\n{build_card_css()}</style>",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def section(title: str, color: str) -> None:
    st.markdown(
        f'<div class="section-title"><span class="section-line" '
        f'style="background:{color}"></span>{title}</div>',
        unsafe_allow_html=True,
    )


def card(page: str, title: str, description: str) -> None:
    group, _ = CARD_META[page]

    with st.container(key=f"card_{group}_{page}"):
        st.page_link(
            PAGES[page],
            label=f"**{title}**\n\n{description}",
        )


# ============================================================
# HERO
# Keep this block free of blank lines - Streamlit's markdown
# parser ends an HTML block at the first empty line.
# ============================================================

HERO_HTML = """<div class="hero">
<div class="hero-content">
<div class="hero-kicker">Insurance analytics and forecasting</div>
<div class="hero-title">Life Insurance Renewal Analytics</div>
<div class="hero-description">Analyze renewal performance, explore business patterns, evaluate forecasting models and generate data-driven insights.</div>
<div class="hero-features">
<span class="hero-feature"><i style="background:#6ea8ff"></i>Analyze</span>
<span class="hero-feature"><i style="background:#5eead4"></i>Forecast</span>
<span class="hero-feature"><i style="background:#fbbf5a"></i>Understand</span>
</div>
</div>
<div class="hero-visual">
<svg viewBox="0 0 340 150" role="img" aria-label="Actual renewal premium followed by a forecast with a confidence band">
<line x1="10" y1="128" x2="330" y2="128" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
<line x1="10" y1="90" x2="330" y2="90" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
<line x1="10" y1="52" x2="330" y2="52" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
<line x1="10" y1="14" x2="330" y2="14" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
<rect x="190" y="6" width="140" height="122" fill="rgba(255,255,255,0.04)"/>
<line x1="190" y1="6" x2="190" y2="128" stroke="rgba(255,255,255,0.25)" stroke-width="1" stroke-dasharray="3 4"/>
<polygon class="chart-band" points="190,58 215,44 240,46 265,26 290,26 315,10 330,4 330,52 315,54 290,66 265,62 240,70 215,62" fill="rgba(94,234,212,0.16)"/>
<polyline class="chart-actual" pathLength="1" points="10,120 30,108 50,114 70,94 90,102 110,82 130,88 150,68 170,74 190,58" fill="none" stroke="#7fb2ff" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
<polyline class="chart-forecast" points="190,58 215,52 240,58 265,42 290,46 315,32 330,28" fill="none" stroke="#5eead4" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 5"/>
<circle class="chart-forecast" cx="190" cy="58" r="4.5" fill="#ffffff" stroke="#7fb2ff" stroke-width="2"/>
<text x="12" y="145" font-size="10" fill="rgba(255,255,255,0.55)" font-family="DM Sans, sans-serif">Actual</text>
<text x="200" y="145" font-size="10" fill="rgba(255,255,255,0.55)" font-family="DM Sans, sans-serif">Forecast</text>
</svg>
</div>
</div>"""

st.markdown(HERO_HTML, unsafe_allow_html=True)


# ============================================================
# QUICK ACCESS
# ============================================================

section("Quick access", "#2456d6")

qa1, qa2 = st.columns(2, gap="small")

with qa1:
    card(
        "overview",
        "Overview",
        "High-level view of policies, renewals, renewal rate and renewed premium.",
    )

with qa2:
    card(
        "insurer",
        "Insurer Analysis",
        "Compare insurers on renewal performance, premium and policy trends.",
    )


# ============================================================
# ANALYSIS + FORECASTING
# ============================================================

left, right = st.columns([1, 1.3], gap="small")

with left:
    section("Descriptive analysis", "#2f6bd8")

    card(
        "region",
        "Region Analysis",
        "Renewal performance across geographical regions.",
    )
    card(
        "payment",
        "Payment Analysis",
        "Renewal behaviour across payment modes.",
    )
    card(
        "policy",
        "Policy Type Analysis",
        "Renewal behaviour and premium across policy types.",
    )

with right:
    section("Forecasting", "#0f9b86")

    f1, f2 = st.columns(2, gap="small")
    with f1:
        card(
            "yearly",
            "Yearly Analysis",
            "Financial-year performance and year-over-year change.",
        )
    with f2:
        card(
            "timeseries",
            "Time Series Analysis",
            "Trend, seasonality, stationarity, ACF and PACF.",
        )

    f3, f4 = st.columns(2, gap="small")
    with f3:
        card(
            "models",
            "Model Comparison",
            "Compare forecasting models using MAPE, MAE and RMSE.",
        )
    with f4:
        card(
            "dynamic",
            "Dynamic Forecasting",
            "Generate interactive future renewal premium forecasts.",
        )

    card(
        "insights",
        "Business Insights",
        "Automatic insights, growth outlook and insurer comparisons.",
    )


# ============================================================
# AI ASSISTANT
# ============================================================

section("AI assistant", "#c97a0c")

card(
    "ai",
    "AI Assistant",
    "Ask questions about the insurance renewal data in plain language.",
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">Life Insurance Renewal Analytics and Forecasting System</div>',
    unsafe_allow_html=True,
)