"""Yearly Insurance Analysis page
Life Insurance Renewal Analytics and Forecasting System
"""

from __future__ import annotations

import re
from html import escape
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIG  (must be the first Streamlit call)
# ============================================================

st.set_page_config(
    page_title="Yearly Analysis",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "data/processed/yearly_renewal_premium.csv"
HOME_PAGE = "App.py"

YEAR_COL = "financial_year"
SUM_COLS = ["total_policies", "renewed_policies", "total_premium", "renewed_premium"]
RATE_COL = "renewal_rate"  # optional: reported rate stored in the file
REQUIRED_COLS = [YEAR_COL] + SUM_COLS

ALL_YEARS = "All years"
CRORE = 1e7

NAVY = "#0e1b33"
BLUE = "#2456d6"
LIGHT_BLUE = "#9db8f5"
TEAL = "#0f9b86"
AMBER = "#c97a0c"
PURPLE = "#5b4bd6"
RED = "#d64545"

FONT = "DM Sans, system-ui, sans-serif"


# ============================================================
# STREAMLIT VERSION COMPATIBILITY
# ------------------------------------------------------------
# `use_container_width` is deprecated/removed in current
# Streamlit releases and replaced by `width="stretch"`.
# ============================================================

def _streamlit_version() -> tuple[int, int]:
    nums = re.findall(r"\d+", st.__version__)[:2]
    return tuple(int(n) for n in nums)  # type: ignore[return-value]


STRETCH = (
    {"width": "stretch"}
    if _streamlit_version() >= (1, 50)
    else {"use_container_width": True}
)


# ============================================================
# ICON SYSTEM
# ============================================================

ICONS = {
    "file": (
        "<path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/>"
        "<path d='M14 2v6h6'/>"
        "<path d='M8 13h8M8 17h5'/>"
    ),
    "check": (
        "<circle cx='12' cy='12' r='9'/>"
        "<path d='M8 12.5l2.7 2.7L16 9.5'/>"
    ),
    "percent": (
        "<path d='M19 5L5 19'/>"
        "<circle cx='7' cy='7' r='2.5'/>"
        "<circle cx='17' cy='17' r='2.5'/>"
    ),
    "rupee": (
        "<path d='M6 5h12M6 9h12'/>"
        "<path d='M9 5c5 0 5 7 0 7H8l7 7'/>"
    ),
    "wallet": (
        "<path d='M3 7a2 2 0 0 1 2-2h13v4'/>"
        "<path d='M3 7v11a2 2 0 0 0 2 2h15V9H5a2 2 0 0 1-2-2z'/>"
        "<circle cx='16' cy='14.5' r='1'/>"
    ),
    "average": "<path d='M4 19V5M10 19V9M16 19V3M22 19H2'/>",
    "cross": (
        "<circle cx='12' cy='12' r='9'/>"
        "<path d='M9 9l6 6M15 9l-6 6'/>"
    ),
    "download": (
        "<path d='M12 3v12'/>"
        "<path d='M7 10l5 5 5-5'/>"
        "<path d='M5 21h14'/>"
    ),
    "grid": (
        "<rect x='3' y='3' width='8' height='8' rx='1.5'/><rect x='13' y='3' width='8' height='5' rx='1.5'/>"
        "<rect x='13' y='10' width='8' height='11' rx='1.5'/><rect x='3' y='13' width='8' height='8' rx='1.5'/>"
    ),
    "pin": "<path d='M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z'/><circle cx='12' cy='10' r='2.5'/>",
    "trend": "<path d='M3 3v18h18'/><path d='M7 15l4-5 3 3 5-7'/>",
}


def icon_url(name: str, stroke: str) -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' "
        "fill='none' "
        f"stroke='{stroke}' stroke-width='1.8' stroke-linecap='round' "
        f"stroke-linejoin='round'>{ICONS[name]}</svg>"
    )
    return "data:image/svg+xml," + quote(svg)


# kind -> (icon, icon colour, tile tint)
KPI_STYLES = {
    "policies":   ("file",    BLUE,   "#eaf1fd"),
    "renewed":    ("check",   TEAL,   "#e3f6f2"),
    "rate":       ("percent", PURPLE, "#eeecfd"),
    "rpremium":   ("rupee",   AMBER,  "#fdf0dc"),
    "tpremium":   ("wallet",  BLUE,   "#eaf1fd"),
    "avgpremium": ("average", PURPLE, "#eeecfd"),
    "prate":      ("percent", TEAL,   "#e3f6f2"),
    "lapsed":     ("cross",   RED,    "#fdeaea"),
}

KPI_CSS = "".join(
    f'.kpi-{kind} {{ --tint: {tint}; }} '
    f'.kpi-{kind} .kpi-icon {{ background-image: url("{icon_url(icon, color)}"); }} '
    for kind, (icon, color, tint) in KPI_STYLES.items()
)


# ============================================================
# PAGE NAVIGATION
# Order follows the pages/ file numbers used across the app:
# Overview -> Insurer -> Payment -> Policy Type -> Region ->
# Yearly -> Time Series -> Model Comparison -> Dynamic
# Forecasting -> Business Insights -> AI Assistant.
# ============================================================

PAGES = {
    "region": ("pages/5_Region_Analysis.py", "Region Analysis", "Renewal performance across geographical regions.", "pin"),
    "timeseries": ("pages/7_Time_Series_Analysis.py", "Time Series Analysis", "Trend, seasonality, stationarity, ACF and PACF.", "trend"),
}

PREV_PAGE = "region"
NEXT_PAGE = "timeseries"

NAV_CSS = "".join(
    f'.st-key-card_desc_{slot} a::before '
    f'{{ background-image: url("{icon_url(PAGES[page_key][3], "#2f6bd8")}"); }} '
    for slot, page_key in (("prev", PREV_PAGE), ("next", NEXT_PAGE))
)

DYNAMIC_CSS = f"""
:root {{ --download-icon: url("{icon_url("download", BLUE)}"); }}
{KPI_CSS}
{NAV_CSS}
"""


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
    --gap: 16px;
    --display: 'Bricolage Grotesque', 'DM Sans', system-ui, sans-serif;
    --body: 'DM Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}

/* ---------- GLOBAL ---------- */

html, body, .stApp,
[data-testid="stMarkdownContainer"],
[data-testid="stPageLink"] a,
[data-testid="stExpander"] summary {
    font-family: var(--body);
}

.stApp {
    color: var(--navy);
    color-scheme: light;
    background:
        radial-gradient(900px 380px at 100% 0%, rgba(36, 86, 214, 0.06), transparent 70%),
        var(--bg);
}

[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
}

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

div[data-testid="stVerticalBlock"] { gap: var(--gap); }
div[data-testid="stHorizontalBlock"] { gap: var(--gap) !important; }

@media (min-width: 641px) {
    div[data-testid="stColumn"],
    div[data-testid="column"] { min-width: 0 !important; }
}

/* ---------- BACK LINK ---------- */

.st-key-backlink {
    width: 100%;
    margin: 0 !important;
    padding: 0 !important;
}

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
    transition: border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
}

.st-key-backlink a:hover {
    border-color: #9db8f5 !important;
    box-shadow: 0 4px 12px rgba(16, 38, 74, 0.10);
    transform: translateY(-1px);
}

.st-key-backlink a p {
    margin: 0 !important;
    font-size: 13px !important;
    font-weight: 600;
    color: #2456d6 !important;
}

/* ---------- HERO ---------- */

.hero {
    position: relative;
    overflow: hidden;
    min-height: 180px;
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
    right: -80px;
    top: -120px;
    width: 410px;
    height: 410px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(94, 234, 212, 0.20), transparent 65%);
}

.hero::after {
    content: "";
    position: absolute;
    left: 45%;
    bottom: -180px;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(36, 86, 214, 0.20), transparent 65%);
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 720px;
}

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
    max-width: 610px;
    margin-top: 10px;
}

.hero-features {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 17px;
}

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

.hero-feature i {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
}

.hero-visual {
    position: relative;
    z-index: 2;
    width: 330px;
    flex-shrink: 0;
}

.hero-visual svg {
    width: 100%;
    height: auto;
    display: block;
}

@keyframes fade-in {
    from { opacity: 0; }
    to   { opacity: 1; }
}

.hero-bars { animation: fade-in 0.8s ease-out both; }
.hero-best { animation: fade-in 0.6s ease-out 0.9s both; }

@media (prefers-reduced-motion: reduce) {
    .hero-bars, .hero-best { animation: none; }
}

/* ---------- SECTION HEADINGS ---------- */

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

.section-line {
    width: 4px;
    height: 18px;
    border-radius: 3px;
    display: inline-block;
}

/* ---------- KPI CARDS ---------- */

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
    overflow: hidden;
    text-overflow: ellipsis;
}

.kpi-value.kpi-value-sm { font-size: 20px; line-height: 1.4; }

.kpi-description {
    font-size: 11.5px;
    color: #8a97aa;
    margin-top: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ---------- CHART / TABLE CARDS ---------- */

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

.chart-note {
    font-size: 11.5px;
    color: #7d8ba1;
    padding: 0 4px 6px 4px;
}

.table-title {
    font-family: var(--display);
    font-size: 15px;
    font-weight: 700;
    color: var(--navy);
    margin: 4px 0 8px 0;
}

/* ---------- FILTER / INFO / HIGHLIGHT CARDS ---------- */

.control-card,
[class*="st-key-control_"] {
    box-sizing: border-box;
    min-height: 84px;
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px 16px;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.03);
}

[class*="st-key-control_"] { padding: 8px 16px 6px 16px; }

[class*="st-key-control_"] [data-testid="stWidgetLabel"] p {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8491a6 !important;
}

.control-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8491a6;
    font-weight: 700;
    margin-bottom: 2px;
}

.control-value {
    font-family: var(--display);
    color: var(--navy);
    font-size: 20px;
    font-weight: 800;
}

.control-sub {
    color: #7d8ba1;
    font-size: 12px;
    margin-top: 4px;
}

.highlight-best  { border-left: 4px solid #0f9b86; }
.highlight-worst { border-left: 4px solid #c97a0c; }

/* ---------- DOWNLOAD AREA ---------- */

.download-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    padding: 18px 20px;
    background: linear-gradient(110deg, #ffffff, #f8faff);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.04);
}

.download-inner {
    display: flex;
    align-items: center;
    gap: 14px;
}

.download-title {
    font-family: var(--display);
    color: var(--navy);
    font-size: 15px;
    font-weight: 700;
}

.download-description {
    color: #738198;
    font-size: 12.5px;
    margin-top: 3px;
}

.download-icon {
    flex: 0 0 44px;
    width: 44px;
    height: 44px;
    border-radius: 13px;
    background-color: #eaf1fd;
    background-repeat: no-repeat;
    background-position: center;
    background-size: 22px 22px;
    background-image: var(--download-icon);
}

/* ---------- EXPANDER ---------- */

[data-testid="stExpander"] {
    background: var(--card);
    border: 1px solid var(--border) !important;
    border-radius: 16px;
    overflow: hidden;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpanderDetails"],
[data-testid="stExpanderDetails"] p {
    color: var(--navy) !important;
}

[data-testid="stExpander"] summary { font-weight: 600; }
[data-testid="stExpander"] summary svg { color: var(--navy) !important; }

/* ---------- PREVIOUS / NEXT PAGE CARDS ---------- */

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

/* ---------- FOOTER ---------- */

.analysis-footer {
    text-align: center;
    color: #8fa0b8;
    font-size: 11px;
    margin-top: 8px;
}

/* ---------- RESPONSIVE ---------- */

@media (max-width: 1100px) {
    .block-container { padding-left: 1.2rem; padding-right: 1.2rem; }
    .hero-visual { width: 260px; }
    .kpi-value { font-size: 23px; }
}

@media (max-width: 900px) {
    .hero { min-height: 145px; padding: 22px 24px; }
    .hero-visual { display: none; }
    .hero-title { font-size: 28px; }
    .block-container { padding-left: 1rem; padding-right: 1rem; }
}

@media (max-width: 700px) {
    .kpi { height: 96px; }
    .kpi-value { font-size: 22px; }
}
"""

st.markdown(f"<style>{BASE_CSS}{DYNAMIC_CSS}</style>", unsafe_allow_html=True)


# ============================================================
# FORMATTING & CALCULATION HELPERS
# ============================================================

def fmt_int(value) -> str:
    return "–" if pd.isna(value) else f"{value:,.0f}"


def fmt_cr(value) -> str:
    return "–" if pd.isna(value) else f"₹{value / CRORE:,.2f} Cr"


def fmt_rupee(value) -> str:
    return "–" if pd.isna(value) else f"₹{value:,.0f}"


def fmt_pct(value) -> str:
    return "–" if pd.isna(value) else f"{value:.2f}%"


def safe_div(numerator, denominator) -> float:
    """numerator / denominator, or NaN when it is undefined."""
    if pd.isna(numerator) or pd.isna(denominator) or denominator <= 0:
        return np.nan
    return numerator / denominator


def summarize(frame: pd.DataFrame) -> dict:
    """Totals for one or more years, with rates recomputed from the totals.

    Recomputing (instead of averaging per-year rates) keeps "All years"
    correctly weighted by policy count and premium.
    """
    s = {col: frame[col].sum(min_count=1) for col in SUM_COLS}
    s["policy_rate"] = safe_div(s["renewed_policies"], s["total_policies"]) * 100
    s["premium_rate"] = safe_div(s["renewed_premium"], s["total_premium"]) * 100
    s["avg_premium"] = safe_div(s["total_premium"], s["total_policies"])
    s["not_renewed"] = s["total_policies"] - s["renewed_policies"]
    return s


def change_text(current, previous, previous_label: str, kind: str) -> str:
    """'▲ 4.2% vs FY 2022-23' style comparison line for a KPI card."""
    if pd.isna(current) or pd.isna(previous):
        return f"No comparison with {previous_label}"
    if kind == "pp":
        delta, unit = current - previous, " pp"
    else:
        if previous == 0:
            return f"No comparison with {previous_label}"
        delta, unit = (current / previous - 1) * 100, "%"
    arrow = "▲" if delta >= 0 else "▼"
    return f"{arrow} {abs(delta):.1f}{unit} vs {previous_label}"


# ============================================================
# RENDER HELPERS
# ============================================================

def render_html(markup: str) -> None:
    """Render an HTML snippet safely through st.markdown.

    Markdown treats a blank line followed by 4+ spaces of indentation as a
    code block, which would show raw tags on the page. Collapsing every
    line to a single stripped line avoids that entirely.
    """
    compact = " ".join(
        line.strip() for line in markup.strip().splitlines() if line.strip()
    )
    st.markdown(compact, unsafe_allow_html=True)


def section_heading(title: str, color: str = BLUE) -> None:
    render_html(
        f"""
        <div class="section-title">
            <span class="section-line" style="background:{color}"></span>
            {escape(title)}
        </div>
        """
    )


def kpi_card(kind: str, label: str, value: str, description: str = "") -> None:
    size_class = " kpi-value-sm" if len(value) > 14 else ""
    render_html(
        f"""
        <div class="kpi kpi-{kind}">
            <div class="kpi-icon"></div>
            <div class="kpi-body">
                <div class="kpi-label">{escape(label)}</div>
                <div class="kpi-value{size_class}" title="{escape(value)}">{escape(value)}</div>
                <div class="kpi-description" title="{escape(description)}">{escape(description)}</div>
            </div>
        </div>
        """
    )


def info_card(label: str, value: str, sub: str = "", extra_class: str = "") -> None:
    sub_html = f'<div class="control-sub">{escape(sub)}</div>' if sub else ""
    render_html(
        f"""
        <div class="control-card {extra_class}">
            <div class="control-label">{escape(label)}</div>
            <div class="control-value">{escape(value)}</div>
            {sub_html}
        </div>
        """
    )


def chart_note(text: str) -> None:
    render_html(f'<div class="chart-note">{escape(text)}</div>')


def nav_card(slot: str, page_key: str, prefix: str) -> None:
    path, title, description, _icon = PAGES[page_key]

    with st.container(key=f"card_desc_{slot}"):
        st.page_link(path, label=f"**{prefix}: {title}**\n\n{description}")


def style_fig(fig, title: str, y_title: str, height: int = 380, bottom: int = 20):
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
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
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
        automargin=True,
    )
    return fig


def finish_year_chart(fig, years: list[str], selected: str) -> None:
    """Keep years in chronological order and shade the selected year."""
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=years)
    if selected != ALL_YEARS and selected in years:
        idx = years.index(selected)
        fig.add_vrect(
            x0=idx - 0.5,
            x1=idx + 0.5,
            fillcolor=BLUE,
            opacity=0.08,
            line_width=0,
            layer="below",
        )


def show_chart(fig, key: str) -> None:
    # theme=None keeps our own Plotly styling (Streamlit's theme would
    # otherwise override fonts/colours, especially in dark mode).
    st.plotly_chart(
        fig,
        key=key,
        theme=None,
        config={"displaylogo": False},
        **STRETCH,
    )


# ============================================================
# DATA LOADING
# ============================================================

def resolve_data_file() -> Path | None:
    """Find the CSV regardless of the directory Streamlit was started from."""
    here = Path(__file__).resolve().parent
    for base in (Path.cwd(), here, here.parent):
        candidate = base / DATA_FILE
        if candidate.is_file():
            return candidate
    return None


@st.cache_data(show_spinner=False)
def load_yearly(path: str, mtime: float):
    """Load, clean and enrich the yearly dataset.

    `mtime` is only part of the cache key, so the cache refreshes when the
    file changes on disk.
    """
    raw = pd.read_csv(path)

    # Trim names and match the expected columns case-insensitively.
    canonical = {c.lower(): c for c in REQUIRED_COLS + [RATE_COL]}
    raw.columns = [
        canonical.get(str(c).strip().lower(), str(c).strip()) for c in raw.columns
    ]

    missing = [c for c in REQUIRED_COLS if c not in raw.columns]
    if missing:
        raise ValueError(
            f"Missing columns: {missing}. Available columns: {raw.columns.tolist()}"
        )

    if RATE_COL not in raw.columns:
        raw[RATE_COL] = np.nan

    num_cols = SUM_COLS + [RATE_COL]
    data = raw[[YEAR_COL] + num_cols].copy()

    # Year labels: keep them as clean text ("2023-24", never "2023.0").
    data = data.dropna(subset=[YEAR_COL])
    year = data[YEAR_COL]
    if pd.api.types.is_numeric_dtype(year):
        year = year.round().astype("int64").astype(str)
    else:
        year = year.astype(str).str.strip()
    data[YEAR_COL] = year
    data = data[data[YEAR_COL] != ""]

    # Numbers: accept "₹1,234", "85%" and similar; drop inf.
    for col in num_cols:
        values = data[col]
        if not pd.api.types.is_numeric_dtype(values):
            values = values.astype(str).str.replace(r"[%₹,\s]", "", regex=True)
        data[col] = pd.to_numeric(values, errors="coerce")
    data[num_cols] = data[num_cols].replace([np.inf, -np.inf], np.nan)

    data = data.dropna(subset=num_cols, how="all")
    if data.empty:
        raise ValueError("No valid rows remain after cleaning the dataset.")

    dropped_rows = int(len(raw) - len(data))

    # A reported rate stored as a fraction (0.87) is converted to percent.
    rate = data[RATE_COL]
    rate_scaled = bool(rate.notna().any() and rate.max() <= 1.0)
    if rate_scaled:
        data[RATE_COL] = rate * 100

    # One row per financial year: repeated years are combined (counts and
    # premium summed) and every rate is then recomputed from the totals.
    duplicates_merged = int(data.duplicated(YEAR_COL).sum())
    grouped = data.groupby(YEAR_COL, sort=False)
    yearly = grouped[SUM_COLS].sum(min_count=1)
    yearly["reported_rate"] = grouped[RATE_COL].mean()
    yearly = yearly.reset_index()

    # Chronological order matters for year-over-year growth.
    start_year = yearly[YEAR_COL].str.extract(r"(\d{4})")[0]
    chronological = bool(start_year.notna().all())
    if chronological:
        yearly = (
            yearly.assign(_start=start_year.astype(int))
            .sort_values("_start", kind="stable")
            .drop(columns="_start")
        )
    yearly = yearly.reset_index(drop=True)

    tp = yearly["total_policies"].where(yearly["total_policies"] > 0)
    tprem = yearly["total_premium"].where(yearly["total_premium"] > 0)

    yearly["policy_renewal_rate"] = yearly["renewed_policies"].div(tp) * 100
    yearly["premium_renewal_rate"] = yearly["renewed_premium"].div(tprem) * 100
    yearly["avg_premium_per_policy"] = yearly["total_premium"].div(tp)

    for out_col, src_col in [
        ("total_premium_growth_pct", "total_premium"),
        ("renewed_premium_growth_pct", "renewed_premium"),
        ("policy_growth_pct", "total_policies"),
    ]:
        yearly[out_col] = (
            yearly[src_col]
            .pct_change(fill_method=None)
            .replace([np.inf, -np.inf], np.nan)
            * 100
        )

    reported = yearly["reported_rate"]

    def matches(derived: pd.Series) -> int:
        return int(((reported - derived).abs() <= 0.5).sum())

    info = {
        "raw_rows": int(len(raw)),
        "dropped_rows": dropped_rows,
        "duplicates_merged": duplicates_merged,
        "rate_scaled": rate_scaled,
        "chronological": chronological,
        "reported_years": int(reported.notna().sum()),
        "match_policy": matches(yearly["policy_renewal_rate"]),
        "match_premium": matches(yearly["premium_renewal_rate"]),
    }
    return yearly, info


data_path = resolve_data_file()

if data_path is None:
    st.error(f"Dataset not found:\n\n`{DATA_FILE}`")
    st.info(
        "Make sure yearly_renewal_premium.csv is inside data/processed/"
    )
    st.stop()

try:
    yearly, load_info = load_yearly(str(data_path), data_path.stat().st_mtime)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
except Exception as exc:  # noqa: BLE001
    st.error(f"Unable to load the dataset.\n\n{exc}")
    st.stop()


years = yearly[YEAR_COL].tolist()
n_years = len(years)
period_label = f"{years[0]} – {years[-1]}" if n_years > 1 else years[0]


# ============================================================
# BACK NAVIGATION
# ============================================================

with st.container(key="backlink"):
    try:
        st.page_link(HOME_PAGE, label="← Back to home")
    except Exception:  # noqa: BLE001  (home page not registered)
        pass


# ============================================================
# HERO
# ============================================================

HERO_VISUAL = """
<svg viewBox="0 0 340 150" role="img" aria-label="Yearly total versus renewed policies visualization">
    <line x1="10" y1="128" x2="330" y2="128" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
    <line x1="10" y1="90" x2="330" y2="90" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
    <line x1="10" y1="52" x2="330" y2="52" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
    <g class="hero-bars" fill="rgba(127,178,255,0.42)">
        <rect x="14" y="68" width="36" height="60" rx="5"/>
        <rect x="66" y="56" width="36" height="72" rx="5"/>
        <rect x="118" y="62" width="36" height="66" rx="5"/>
        <rect x="170" y="42" width="36" height="86" rx="5"/>
        <rect x="222" y="34" width="36" height="94" rx="5"/>
        <rect x="274" y="18" width="36" height="110" rx="5"/>
    </g>
    <g class="hero-best" fill="#5eead4">
        <rect x="22" y="84" width="20" height="44" rx="4"/>
        <rect x="74" y="72" width="20" height="56" rx="4"/>
        <rect x="126" y="76" width="20" height="52" rx="4"/>
        <rect x="178" y="58" width="20" height="70" rx="4"/>
        <rect x="230" y="48" width="20" height="80" rx="4"/>
        <rect x="282" y="32" width="20" height="96" rx="4"/>
    </g>
</svg>
"""

render_html(
    f"""
    <div class="hero">
        <div class="hero-content">
            <div class="hero-kicker">Analytical dashboard</div>
            <div class="hero-title">Yearly Insurance Analysis</div>
            <div class="hero-description">
                Track policies, premium and renewal performance by financial
                year, with year-over-year growth and the strongest and
                weakest renewal years.
            </div>
            <div class="hero-features">
                <span class="hero-feature"><i style="background:#6ea8ff"></i>{escape(period_label)}</span>
                <span class="hero-feature"><i style="background:#5eead4"></i>{n_years} financial years</span>
                <span class="hero-feature"><i style="background:#fbbf5a"></i>Yearly frequency</span>
            </div>
        </div>
        <div class="hero-visual">{HERO_VISUAL}</div>
    </div>
    """
)


if not load_info["chronological"]:
    st.warning(
        "Financial-year labels do not contain a four-digit year, so the file "
        "order is used. Year-over-year growth is only meaningful if the file "
        "is already sorted from oldest to newest."
    )


# ============================================================
# FILTER
# ============================================================

section_heading("Yearly filter", BLUE)

filter_col1, filter_col2 = st.columns([1, 3], gap="small")

with filter_col1:
    with st.container(key="control_year"):
        selected_year = st.selectbox(
            "Financial year",
            [ALL_YEARS] + years,
            key="sel_year",
        )

with filter_col2:
    info_card(
        "Series Coverage",
        period_label,
        f"{n_years} financial year{'s' if n_years != 1 else ''} in the dataset",
    )


# ============================================================
# SELECTION & KPI VALUES
# ============================================================

if selected_year == ALL_YEARS:
    selection = yearly
    previous = None
    previous_label = ""
else:
    pos = years.index(selected_year)
    selection = yearly.iloc[[pos]]
    previous = yearly.iloc[[pos - 1]] if pos > 0 else None
    previous_label = years[pos - 1] if pos > 0 else ""

cur = summarize(selection)
prev = summarize(previous) if previous is not None else None


def kpi_description(key: str, kind: str, all_years_text: str) -> str:
    if selected_year == ALL_YEARS:
        return all_years_text
    if prev is None:
        return "First year in the series"
    return change_text(cur[key], prev[key], previous_label, kind)


sum_text = f"Sum across {n_years} financial year{'s' if n_years != 1 else ''}"


# ============================================================
# KPI SECTION
# ============================================================

section_heading("Key performance indicators", BLUE)

r1c1, r1c2, r1c3, r1c4 = st.columns(4, gap="small")

with r1c1:
    kpi_card(
        "policies",
        "Total Policies",
        fmt_int(cur["total_policies"]),
        kpi_description("total_policies", "pct", sum_text),
    )

with r1c2:
    kpi_card(
        "renewed",
        "Renewed Policies",
        fmt_int(cur["renewed_policies"]),
        kpi_description("renewed_policies", "pct", sum_text),
    )

with r1c3:
    kpi_card(
        "rate",
        "Renewal Rate",
        fmt_pct(cur["policy_rate"]),
        kpi_description("policy_rate", "pp", "Renewed ÷ total policies"),
    )

with r1c4:
    kpi_card(
        "rpremium",
        "Renewed Premium",
        fmt_cr(cur["renewed_premium"]),
        kpi_description("renewed_premium", "pct", sum_text),
    )

r2c1, r2c2, r2c3, r2c4 = st.columns(4, gap="small")

with r2c1:
    kpi_card(
        "tpremium",
        "Total Premium",
        fmt_cr(cur["total_premium"]),
        kpi_description("total_premium", "pct", sum_text),
    )

with r2c2:
    kpi_card(
        "avgpremium",
        "Average Premium / Policy",
        fmt_rupee(cur["avg_premium"]),
        kpi_description("avg_premium", "pct", "Total premium ÷ total policies"),
    )

with r2c3:
    kpi_card(
        "prate",
        "Premium Renewal Rate",
        fmt_pct(cur["premium_rate"]),
        kpi_description("premium_rate", "pp", "Renewed ÷ total premium"),
    )

with r2c4:
    kpi_card(
        "lapsed",
        "Not Renewed Policies",
        fmt_int(cur["not_renewed"]),
        kpi_description("not_renewed", "pct", "Total minus renewed policies"),
    )


# ============================================================
# 1. RENEWAL RATE BY FINANCIAL YEAR
# ============================================================

section_heading("1. Renewal rate by financial year", BLUE)

with st.container(key="chart_renewal_rate"):
    fig_rate = go.Figure()

    fig_rate.add_trace(
        go.Scatter(
            x=years,
            y=yearly["policy_renewal_rate"],
            mode="lines+markers",
            name="Policy renewal rate",
            line=dict(color=BLUE, width=2.8),
            marker=dict(size=7, color=BLUE),
            connectgaps=False,
            hovertemplate="<b>%{x}</b><br>Policy renewal rate: %{y:.2f}%<extra></extra>",
        )
    )

    fig_rate.add_trace(
        go.Scatter(
            x=years,
            y=yearly["premium_renewal_rate"],
            mode="lines+markers",
            name="Premium renewal rate",
            line=dict(color=TEAL, width=2.8),
            marker=dict(size=7, color=TEAL),
            connectgaps=False,
            hovertemplate="<b>%{x}</b><br>Premium renewal rate: %{y:.2f}%<extra></extra>",
        )
    )

    style_fig(fig_rate, "Renewal rate by financial year", "Renewal rate (%)")
    fig_rate.update_yaxes(ticksuffix="%")
    fig_rate.update_layout(hovermode="x unified")
    finish_year_chart(fig_rate, years, selected_year)

    show_chart(fig_rate, "fig_rate")

    chart_note(
        "Policy renewal rate = renewed policies ÷ total policies. "
        "Premium renewal rate = renewed premium ÷ total premium."
    )


# ============================================================
# 2. YEARLY PREMIUM PERFORMANCE
# ============================================================

section_heading("2. Yearly premium performance", TEAL)

with st.container(key="chart_premium"):
    fig_premium = go.Figure()

    fig_premium.add_trace(
        go.Bar(
            x=years,
            y=yearly["total_premium"] / CRORE,
            name="Total premium",
            marker_color=LIGHT_BLUE,
            hovertemplate="<b>%{x}</b><br>Total premium: ₹%{y:,.2f} Cr<extra></extra>",
        )
    )

    fig_premium.add_trace(
        go.Bar(
            x=years,
            y=yearly["renewed_premium"] / CRORE,
            name="Renewed premium",
            marker_color=TEAL,
            hovertemplate="<b>%{x}</b><br>Renewed premium: ₹%{y:,.2f} Cr<extra></extra>",
        )
    )

    style_fig(fig_premium, "Total vs renewed premium", "Premium (₹ Cr)")
    fig_premium.update_layout(barmode="group", bargap=0.25, hovermode="x unified")
    finish_year_chart(fig_premium, years, selected_year)

    show_chart(fig_premium, "fig_premium")

    chart_note(
        "The gap between the two bars is premium that was due but not renewed."
    )


# ============================================================
# 3. YEARLY POLICY PERFORMANCE
# ============================================================

section_heading("3. Yearly policy performance", AMBER)

with st.container(key="chart_policies"):
    fig_policies = go.Figure()

    fig_policies.add_trace(
        go.Bar(
            x=years,
            y=yearly["total_policies"],
            name="Total policies",
            marker_color=LIGHT_BLUE,
            hovertemplate="<b>%{x}</b><br>Total policies: %{y:,.0f}<extra></extra>",
        )
    )

    fig_policies.add_trace(
        go.Bar(
            x=years,
            y=yearly["renewed_policies"],
            name="Renewed policies",
            marker_color=AMBER,
            hovertemplate="<b>%{x}</b><br>Renewed policies: %{y:,.0f}<extra></extra>",
        )
    )

    style_fig(fig_policies, "Total vs renewed policies", "Policies")
    fig_policies.update_layout(barmode="group", bargap=0.25, hovermode="x unified")
    finish_year_chart(fig_policies, years, selected_year)

    show_chart(fig_policies, "fig_policies")

    chart_note("Policy counts per financial year, before and after renewal.")


# ============================================================
# 4. YEAR-OVER-YEAR GROWTH
# ============================================================

section_heading("4. Year-over-year growth", PURPLE)

growth_series = [
    ("total_premium_growth_pct", "Total premium growth", BLUE),
    ("renewed_premium_growth_pct", "Renewed premium growth", TEAL),
    ("policy_growth_pct", "Policy growth", AMBER),
]

has_growth = n_years > 1 and any(
    yearly[col].notna().any() for col, _, _ in growth_series
)

if has_growth:
    with st.container(key="chart_growth"):
        fig_growth = go.Figure()

        for col, name, color in growth_series:
            fig_growth.add_trace(
                go.Bar(
                    x=years,
                    y=yearly[col],
                    name=name,
                    marker_color=color,
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        f"{name}: %{{y:+.2f}}%"
                        "<extra></extra>"
                    ),
                )
            )

        fig_growth.add_hline(y=0, line_width=1, line_color="#aab6c8")

        style_fig(fig_growth, "Growth compared with the previous year", "Growth (%)")
        fig_growth.update_yaxes(ticksuffix="%")
        fig_growth.update_layout(barmode="group", bargap=0.25, hovermode="x unified")
        finish_year_chart(fig_growth, years, selected_year)

        show_chart(fig_growth, "fig_growth")

        chart_note(
            "Each year is compared with the year before it, so the first year "
            "has no growth value. Policy growth is based on total policies."
        )
else:
    st.info("At least two financial years are needed to show year-over-year growth.")


# ============================================================
# YEARLY PERFORMANCE HIGHLIGHTS
# ============================================================

section_heading("Yearly performance highlights", "#2f6bd8")

rated = yearly.dropna(subset=["policy_renewal_rate"])

if len(rated) > 1:
    best_row = rated.loc[rated["policy_renewal_rate"].idxmax()]
    worst_row = rated.loc[rated["policy_renewal_rate"].idxmin()]

    hl1, hl2 = st.columns(2, gap="small")

    with hl1:
        info_card(
            "Highest renewal rate",
            str(best_row[YEAR_COL]),
            f"Renewal rate {fmt_pct(best_row['policy_renewal_rate'])} · "
            f"Renewed premium {fmt_cr(best_row['renewed_premium'])}",
            "highlight-best",
        )

    with hl2:
        info_card(
            "Lowest renewal rate",
            str(worst_row[YEAR_COL]),
            f"Renewal rate {fmt_pct(worst_row['policy_renewal_rate'])} · "
            f"Renewed premium {fmt_cr(worst_row['renewed_premium'])}",
            "highlight-worst",
        )
else:
    st.info("At least two years with renewal data are needed to compare best and worst years.")


# ============================================================
# YEARLY DATA TABLE
# ============================================================

section_heading("Yearly data", TEAL)

table_df = pd.DataFrame(
    {
        "Financial Year": yearly[YEAR_COL],
        "Total Policies": yearly["total_policies"].map(fmt_int),
        "Renewed Policies": yearly["renewed_policies"].map(fmt_int),
        "Total Premium (₹ Cr)": (yearly["total_premium"] / CRORE).map(
            lambda v: "–" if pd.isna(v) else f"{v:,.2f}"
        ),
        "Renewed Premium (₹ Cr)": (yearly["renewed_premium"] / CRORE).map(
            lambda v: "–" if pd.isna(v) else f"{v:,.2f}"
        ),
        "Policy Renewal Rate (%)": yearly["policy_renewal_rate"].map(
            lambda v: "–" if pd.isna(v) else f"{v:.2f}"
        ),
        "Premium Renewal Rate (%)": yearly["premium_renewal_rate"].map(
            lambda v: "–" if pd.isna(v) else f"{v:.2f}"
        ),
        "Reported Rate (%)": yearly["reported_rate"].map(
            lambda v: "–" if pd.isna(v) else f"{v:.2f}"
        ),
    }
)

with st.container(key="chart_table"):
    render_html('<div class="table-title">All financial years</div>')
    st.dataframe(
        table_df,
        hide_index=True,
        height=min(35 * (len(table_df) + 1) + 3, 420),
        **STRETCH,
    )


# ============================================================
# DATA DETAILS
# ============================================================

with st.expander("Data details"):
    detail_col1, detail_col2 = st.columns(2, gap="small")

    with detail_col1:
        st.write(f"Source file: `{DATA_FILE}`")
        st.write(f"Raw records loaded: {load_info['raw_rows']:,}")
        st.write(f"Rows dropped (missing year or values): {load_info['dropped_rows']:,}")
        st.write(f"Repeated years combined: {load_info['duplicates_merged']:,}")
        st.write(
            "Year order: "
            + ("sorted chronologically" if load_info["chronological"] else "file order")
        )

    with detail_col2:
        st.write(f"Financial years: {n_years:,}")
        st.write(f"Period: {period_label}")
        if load_info["reported_years"]:
            st.write(
                f"Reported `renewal_rate` matches the policy-based rate in "
                f"{load_info['match_policy']} of {load_info['reported_years']} years "
                f"and the premium-based rate in {load_info['match_premium']} "
                "(within 0.5 percentage points)."
            )
            if load_info["rate_scaled"]:
                st.write("Reported rate was stored as a fraction and converted to %.")
        else:
            st.write("No reported `renewal_rate` values in the file.")


# ============================================================
# DOWNLOAD
# ============================================================

section_heading("Export yearly analysis", TEAL)

export_df = yearly.rename(columns={"reported_rate": "reported_renewal_rate"})
csv_data = export_df.to_csv(index=False).encode("utf-8")

download_col1, download_col2 = st.columns(
    [4, 1],
    gap="small",
    vertical_alignment="center",
)

with download_col1:
    render_html(
        """
        <div class="download-card">
            <div class="download-inner">
                <div class="download-icon"></div>
                <div>
                    <div class="download-title">Download yearly analysis</div>
                    <div class="download-description">
                        Export every financial year with the calculated renewal
                        rates, average premium and year-over-year growth.
                    </div>
                </div>
            </div>
        </div>
        """
    )

with download_col2:
    st.download_button(
        label="⬇ Download CSV",
        data=csv_data,
        file_name="yearly_insurance_analysis.csv",
        mime="text/csv",
        key="download_csv",
        **STRETCH,
    )


# ============================================================
# PREVIOUS / NEXT
# ============================================================

section_heading("Keep exploring", "#2f6bd8")

nav1, nav2 = st.columns(2, gap="small")

with nav1:
    nav_card("prev", PREV_PAGE, "Previous")

with nav2:
    nav_card("next", NEXT_PAGE, "Next")


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="analysis-footer">
        Life Insurance Renewal Analytics and Forecasting System
        · Yearly Analysis
    </div>
    """
)
