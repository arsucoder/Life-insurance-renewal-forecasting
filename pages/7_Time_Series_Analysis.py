"""Time Series Analysis page
Life Insurance Renewal Analytics and Forecasting System
"""

from __future__ import annotations

import re
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
    page_title="Time Series Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "data/processed/monthly_renewal_premium.csv"
HOME_PAGE = "App.py"

DATE_COL = "collection_month"
VALUE_COL = "renewed_premium"

NAVY = "#0e1b33"
BLUE = "#2456d6"
TEAL = "#0f9b86"
AMBER = "#c97a0c"
PURPLE = "#5b4bd6"
RED = "#d64545"

FONT = "DM Sans, system-ui, sans-serif"

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

CRORE = 1e7


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
    "calendar": (
        "<rect x='3' y='4' width='18' height='17' rx='2'/>"
        "<path d='M16 2v4M8 2v4M3 9h18'/>"
    ),
    "database": (
        "<ellipse cx='12' cy='5' rx='8' ry='3'/>"
        "<path d='M4 5v7c0 1.7 3.6 3 8 3s8-1.3 8-3V5'/>"
        "<path d='M4 12v7c0 1.7 3.6 3 8 3s8-1.3 8-3v-7'/>"
    ),
    "average": "<path d='M4 19V5M10 19V9M16 19V3M22 19H2'/>",
    "download": (
        "<path d='M12 3v12'/>"
        "<path d='M7 10l5 5 5-5'/>"
        "<path d='M5 21h14'/>"
    ),
}


def icon_url(name: str, stroke: str) -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' "
        "fill='none' "
        f"stroke='{stroke}' stroke-width='1.8' stroke-linecap='round' "
        f"stroke-linejoin='round'>{ICONS[name]}</svg>"
    )
    return "data:image/svg+xml," + quote(svg)


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

@keyframes draw-line {
    from { stroke-dashoffset: 1; }
    to   { stroke-dashoffset: 0; }
}

@keyframes fade-in {
    from { opacity: 0; }
    to   { opacity: 1; }
}

.hero-bars { animation: fade-in 0.8s ease-out both; }

.hero-line {
    stroke-dasharray: 1;
    animation: draw-line 1.4s ease-out 0.4s both;
}

.hero-dot { animation: fade-in 0.5s ease-out 1.6s both; }

@media (prefers-reduced-motion: reduce) {
    .hero-bars, .hero-line, .hero-dot { animation: none; }
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
}

.kpi-description {
    font-size: 11.5px;
    color: #8a97aa;
    margin-top: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.kpi-observations { --accent: #2f6bd8; --tint: #eaf1fd; }
.kpi-start        { --accent: #5b4bd6; --tint: #eeecfd; }
.kpi-end          { --accent: #0f9b86; --tint: #e3f6f2; }
.kpi-average      { --accent: #c97a0c; --tint: #fdf0dc; }

.kpi-observations .kpi-icon { background-image: var(--icon-observations); }
.kpi-start .kpi-icon        { background-image: var(--icon-start); }
.kpi-end .kpi-icon          { background-image: var(--icon-end); }
.kpi-average .kpi-icon      { background-image: var(--icon-average); }

/* ---------- CHART CARDS ---------- */

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

/* ---------- ANALYSIS INTRO ---------- */

.analysis-intro {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 14px 16px;
    background: #ffffff;
    border: 1px solid var(--border);
    border-left: 4px solid #2f6bd8;
    border-radius: 12px;
    color: #53637c;
    font-size: 13px;
    line-height: 1.55;
}

.analysis-intro strong {
    color: var(--navy);
    white-space: nowrap;
}

/* ---------- CONTROL / SUMMARY CARDS ---------- */

.control-card,
.st-key-control_slider {
    box-sizing: border-box;
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px 16px;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.03);
}

.control-card { min-height: 84px; }

.st-key-control_slider {
    min-height: 84px;
    padding-top: 6px;
    padding-bottom: 2px;
}

.st-key-control_slider [data-testid="stWidgetLabel"] p {
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

/* ---------- TABLE CARD ---------- */

.table-title {
    font-family: var(--display);
    font-size: 15px;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 8px;
}

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
    .analysis-intro { flex-direction: column; gap: 4px; }
}
"""

DYNAMIC_CSS = f"""
:root {{
    --icon-observations: url("{icon_url("database", BLUE)}");
    --icon-start: url("{icon_url("calendar", PURPLE)}");
    --icon-end: url("{icon_url("calendar", TEAL)}");
    --icon-average: url("{icon_url("average", AMBER)}");
    --download-icon: url("{icon_url("download", BLUE)}");
}}
"""

st.markdown(f"<style>{BASE_CSS}{DYNAMIC_CSS}</style>", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================

def html(markup: str) -> None:
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
    html(
        f"""
        <div class="section-title">
            <span class="section-line" style="background:{color}"></span>
            {title}
        </div>
        """
    )


def kpi_card(kind: str, label: str, value: str, description: str = "") -> None:
    html(
        f"""
        <div class="kpi kpi-{kind}">
            <div class="kpi-icon"></div>
            <div class="kpi-body">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-description">{description}</div>
            </div>
        </div>
        """
    )


def info_card(label: str, value: str, sub: str = "") -> None:
    sub_html = f'<div class="control-sub">{sub}</div>' if sub else ""
    html(
        f"""
        <div class="control-card">
            <div class="control-label">{label}</div>
            <div class="control-value">{value}</div>
            {sub_html}
        </div>
        """
    )


def chart_note(text: str) -> None:
    html(f'<div class="chart-note">{text}</div>')


def premium_cr(value):
    """Convert rupees to crore rupees (works on scalars, arrays and Series)."""
    return value / CRORE


def style_fig(fig, title: str, y_title: str, height: int = 360, bottom: int = 20):
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
def load_series(path: str, mtime: float):
    """Load, clean and regularise the monthly series.

    `mtime` is only part of the cache key, so the cache refreshes when the
    file changes on disk.
    """
    raw = pd.read_csv(path)
    raw.columns = raw.columns.astype(str).str.strip()

    missing = [c for c in (DATE_COL, VALUE_COL) if c not in raw.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. "
            f"Available columns: {raw.columns.tolist()}"
        )

    data = raw[[DATE_COL, VALUE_COL]].copy()

    data[DATE_COL] = pd.to_datetime(data[DATE_COL], errors="coerce")

    values = data[VALUE_COL]
    if not pd.api.types.is_numeric_dtype(values):
        # Handles values such as "₹1,23,45,678" that would otherwise be dropped.
        values = values.astype(str).str.replace(r"[₹,\s]", "", regex=True)
    data[VALUE_COL] = pd.to_numeric(values, errors="coerce")

    clean = data.dropna(subset=[DATE_COL, VALUE_COL]).copy()
    if clean.empty:
        raise ValueError("No valid rows remain after cleaning the dataset.")

    # Snap every date to the first day of its month so asfreq("MS") lines up
    # even if the file stores month-end or mid-month dates.
    clean[DATE_COL] = clean[DATE_COL].dt.to_period("M").dt.to_timestamp()

    duplicates_merged = int(clean.duplicated(DATE_COL).sum())

    # asfreq() fails on duplicate index labels, so merge repeated months.
    monthly = clean.groupby(DATE_COL)[VALUE_COL].sum().sort_index()

    ts = monthly.asfreq("MS")
    ts.name = VALUE_COL

    info = {
        "raw_rows": int(len(raw)),
        "dropped_rows": int(len(data) - len(clean)),
        "duplicates_merged": duplicates_merged,
    }
    return ts, info


data_path = resolve_data_file()

if data_path is None:
    st.error(f"Dataset not found:\n\n`{DATA_FILE}`")
    st.stop()

try:
    ts, load_info = load_series(str(data_path), data_path.stat().st_mtime)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
except Exception as exc:  # noqa: BLE001
    st.error(f"Unable to load the dataset.\n\n{exc}")
    st.stop()


# ============================================================
# SERIES INFORMATION
# ============================================================

valid = ts.dropna()

n_expected = len(ts)
n_observations = len(valid)
n_missing = n_expected - n_observations

if n_observations < 4:
    st.warning(
        f"Only {n_observations} valid monthly observations were found. "
        "At least 4 are needed for this analysis."
    )
    st.stop()

start_date = ts.index.min()
end_date = ts.index.max()

historical_period = (
    f"{start_date.strftime('%b %Y')} – {end_date.strftime('%b %Y')}"
)

average_premium = valid.mean()
total_premium = valid.sum()
min_premium = valid.min()
max_premium = valid.max()


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
<svg viewBox="0 0 340 150" role="img" aria-label="Monthly premium trend visualization">
    <line x1="10" y1="128" x2="330" y2="128" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
    <line x1="10" y1="90" x2="330" y2="90" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
    <line x1="10" y1="52" x2="330" y2="52" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
    <g class="hero-bars" fill="rgba(127,178,255,0.42)">
        <rect x="14" y="96" width="20" height="32" rx="4"/>
        <rect x="46" y="78" width="20" height="50" rx="4"/>
        <rect x="78" y="91" width="20" height="37" rx="4"/>
        <rect x="110" y="68" width="20" height="60" rx="4"/>
        <rect x="142" y="74" width="20" height="54" rx="4"/>
        <rect x="174" y="55" width="20" height="73" rx="4"/>
        <rect x="206" y="62" width="20" height="66" rx="4"/>
        <rect x="238" y="42" width="20" height="86" rx="4"/>
        <rect x="270" y="49" width="20" height="79" rx="4"/>
        <rect x="302" y="28" width="20" height="100" rx="4"/>
    </g>
    <polyline class="hero-line" pathLength="1"
        points="24,86 56,69 88,80 120,58 152,65 184,45 216,52 248,32 280,39 312,18"
        fill="none" stroke="#5eead4" stroke-width="2.8"
        stroke-linecap="round" stroke-linejoin="round"/>
    <circle class="hero-dot" cx="312" cy="18" r="4.5" fill="#ffffff" stroke="#5eead4" stroke-width="2"/>
</svg>
"""

html(
    f"""
    <div class="hero">
        <div class="hero-content">
            <div class="hero-kicker">Analytical dashboard</div>
            <div class="hero-title">Time Series Analysis</div>
            <div class="hero-description">
                Explore monthly renewed-premium behaviour, rolling trends,
                seasonality, growth patterns, and first-order differencing
                before forecasting.
            </div>
            <div class="hero-features">
                <span class="hero-feature"><i style="background:#6ea8ff"></i>{historical_period}</span>
                <span class="hero-feature"><i style="background:#5eead4"></i>{n_observations} observations</span>
                <span class="hero-feature"><i style="background:#fbbf5a"></i>Monthly frequency</span>
            </div>
        </div>
        <div class="hero-visual">{HERO_VISUAL}</div>
    </div>
    """
)


# ============================================================
# INTRODUCTION
# ============================================================

html(
    """
    <div class="analysis-intro">
        <strong>Analysis scope</strong>
        <span>
            This dashboard examines the renewed-premium time series at
            monthly frequency. The views below are designed to identify
            trend, smoothing behaviour, recurring monthly patterns,
            short-term changes, and stationarity-oriented transformations.
        </span>
    </div>
    """
)

if n_missing:
    st.warning(
        f"{n_missing} calendar month(s) between {start_date.strftime('%b %Y')} "
        f"and {end_date.strftime('%b %Y')} have no data. They appear as gaps "
        "in the charts, and rolling / change calculations that touch them "
        "are left blank."
    )


# ============================================================
# KPI SECTION
# ============================================================

section_heading("Time series overview", BLUE)

k1, k2, k3, k4 = st.columns(4, gap="small")

with k1:
    kpi_card(
        "observations",
        "Observations",
        f"{n_observations:,}",
        "Monthly observations in the series",
    )

with k2:
    kpi_card(
        "start",
        "Start",
        start_date.strftime("%b %Y"),
        "First available monthly period",
    )

with k3:
    kpi_card(
        "end",
        "End",
        end_date.strftime("%b %Y"),
        "Latest available monthly period",
    )

with k4:
    kpi_card(
        "average",
        "Average Premium",
        f"₹{premium_cr(average_premium):,.2f} Cr",
        "Mean monthly renewed premium",
    )


# ============================================================
# CONTROLS  (in the main page: the sidebar is hidden by the CSS)
# ============================================================

max_window = min(12, n_observations - 1)

control_col1, control_col2 = st.columns([1, 3], gap="small")

with control_col1:
    with st.container(key="control_slider"):
        rolling_window = st.slider(
            "Rolling mean window (months)",
            min_value=2,
            max_value=max_window,
            value=min(3, max_window),
            key="rolling_window",
        )

with control_col2:
    info_card(
        "Series Coverage",
        f"₹{premium_cr(total_premium):,.2f} Cr total renewed premium",
    )


# ============================================================
# DERIVED SERIES
# ============================================================

rolling_mean = ts.rolling(window=rolling_window).mean()

mom_change = (
    ts.pct_change(fill_method=None)
    .replace([np.inf, -np.inf], np.nan)
    * 100
)

diff_ts = ts.diff().dropna()


# ============================================================
# 1. ORIGINAL TIME SERIES
# ============================================================

section_heading("1. Monthly renewed premium", BLUE)

with st.container(key="chart_original"):
    fig_original = go.Figure()

    fig_original.add_trace(
        go.Scatter(
            x=ts.index,
            y=premium_cr(ts.values),
            mode="lines+markers",
            name="Renewed Premium",
            line=dict(color=BLUE, width=2.8),
            marker=dict(size=6, color=BLUE),
            connectgaps=False,
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Renewed Premium: ₹%{y:.2f} Cr"
                "<extra></extra>"
            ),
        )
    )

    style_fig(fig_original, "Monthly renewed premium", "Renewed premium (₹ Cr)", 390)
    fig_original.update_layout(hovermode="x unified")

    show_chart(fig_original, "fig_original")

    chart_note(
        "Original monthly renewed-premium series used as the foundation "
        "for the subsequent time-series analysis."
    )


# ============================================================
# 2. ROLLING MEAN
# ============================================================

section_heading(f"2. Rolling mean — {rolling_window}-month window", TEAL)

with st.container(key="chart_rolling"):
    fig_rolling = go.Figure()

    fig_rolling.add_trace(
        go.Scatter(
            x=ts.index,
            y=premium_cr(ts.values),
            mode="lines",
            name="Actual",
            line=dict(color="#8a97aa", width=1.8),
            connectgaps=False,
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Actual: ₹%{y:.2f} Cr"
                "<extra></extra>"
            ),
        )
    )

    fig_rolling.add_trace(
        go.Scatter(
            x=rolling_mean.index,
            y=premium_cr(rolling_mean.values),
            mode="lines",
            name=f"{rolling_window}-Month Rolling Mean",
            line=dict(color=TEAL, width=3),
            connectgaps=False,
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Rolling Mean: ₹%{y:.2f} Cr"
                "<extra></extra>"
            ),
        )
    )

    style_fig(fig_rolling, f"{rolling_window}-month rolling mean", "Premium (₹ Cr)", 390)
    fig_rolling.update_layout(hovermode="x unified")

    show_chart(fig_rolling, "fig_rolling")

    chart_note(
        "The rolling mean smooths short-term fluctuations and highlights "
        "the underlying movement of the premium series."
    )


# ============================================================
# 3. MONTHLY SEASONALITY
# ============================================================

section_heading("3. Monthly seasonality", AMBER)

by_month = valid.groupby(valid.index.month)
monthly_avg = by_month.mean().reindex(range(1, 13))
month_counts = by_month.size()

seasonality_plot = pd.DataFrame(
    {
        "Month": MONTH_NAMES,
        "Premium": premium_cr(monthly_avg.values),  # values in ₹ Cr
    }
)

count_lo, count_hi = int(month_counts.min()), int(month_counts.max())
count_text = (
    f"{count_lo}" if count_lo == count_hi else f"{count_lo}–{count_hi}"
)

with st.container(key="chart_seasonality"):
    fig_seasonality = go.Figure()

    fig_seasonality.add_trace(
        go.Bar(
            x=seasonality_plot["Month"],
            y=seasonality_plot["Premium"],
            name="Average Premium",
            marker_color=AMBER,
            text=seasonality_plot["Premium"],
            texttemplate="%{y:.2f}",
            textposition="outside",
            textfont=dict(size=11, family=FONT, color="#1f2d47"),
            cliponaxis=False,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Average Premium: ₹%{y:.2f} Cr"
                "<extra></extra>"
            ),
        )
    )

    style_fig(
        fig_seasonality,
        "Average renewed premium by calendar month",
        "Average premium (₹ Cr)",
        390,
        bottom=25,
    )
    fig_seasonality.update_xaxes(categoryorder="array", categoryarray=MONTH_NAMES)

    show_chart(fig_seasonality, "fig_seasonality")

    chart_note(
        "Monthly averages show recurring calendar-month behaviour. Each "
        f"month is averaged over {count_text} observation(s), so treat "
        "the pattern as indicative when the history is short."
    )


# ============================================================
# 4. MONTH-OVER-MONTH CHANGE
# ============================================================

section_heading("4. Month-over-month change", PURPLE)

with st.container(key="chart_mom"):
    fig_mom = go.Figure()

    fig_mom.add_trace(
        go.Scatter(
            x=mom_change.index,
            y=mom_change.values,
            mode="lines+markers",
            name="MoM Change",
            line=dict(color=PURPLE, width=2.5),
            marker=dict(size=6, color=PURPLE),
            connectgaps=False,
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "MoM Change: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig_mom.add_hline(y=0, line_width=1, line_color="#aab6c8")

    style_fig(fig_mom, "Month-over-month premium change", "Change (%)", 370)
    fig_mom.update_layout(hovermode="x unified")

    show_chart(fig_mom, "fig_mom")

    chart_note(
        "Positive values represent month-over-month increases in renewed "
        "premium, while negative values represent declines."
    )


# ============================================================
# 5. FIRST-ORDER DIFFERENCING
# ============================================================

section_heading("5. First-order differencing", TEAL)

with st.container(key="chart_difference"):
    fig_diff = go.Figure()

    fig_diff.add_trace(
        go.Bar(
            x=diff_ts.index,
            y=premium_cr(diff_ts.values),
            name="First Difference",
            marker_color=[TEAL if v >= 0 else RED for v in diff_ts.values],
            hovertemplate=(
                "<b>%{x|%b %Y}</b><br>"
                "Difference: ₹%{y:.2f} Cr"
                "<extra></extra>"
            ),
        )
    )

    fig_diff.add_hline(y=0, line_width=1, line_color="#aab6c8")

    style_fig(
        fig_diff,
        "First-order difference of renewed premium",
        "Difference (₹ Cr)",
        370,
    )
    fig_diff.update_layout(bargap=0.15, hovermode="x unified")

    show_chart(fig_diff, "fig_diff")

    chart_note(
        "First-order differencing measures the absolute change between "
        "consecutive monthly observations (teal = increase, red = decrease) "
        "and is commonly examined before modelling a time series."
    )


# ============================================================
# 6. TIME SERIES STATISTICS
# ============================================================

section_heading("6. Time series statistics", BLUE)

# Everything is computed in ₹ Cr so the variance is a true ₹ Cr² value.
valid_cr = premium_cr(valid)

stats_rows = [
    ("Mean", valid_cr.mean(), "₹ Cr"),
    ("Median", valid_cr.median(), "₹ Cr"),
    ("Standard Deviation", valid_cr.std(), "₹ Cr"),
    ("Minimum", valid_cr.min(), "₹ Cr"),
    ("Maximum", valid_cr.max(), "₹ Cr"),
    ("Variance", valid_cr.var(), "₹ Cr²"),
]

stats_df = pd.DataFrame(stats_rows, columns=["Metric", "Value", "Unit"])
stats_df["Value"] = stats_df["Value"].map(lambda x: f"{x:,.2f}")

with st.container(key="chart_stats"):
    html('<div class="table-title">Descriptive statistics</div>')

    st.dataframe(
        stats_df,
        hide_index=True,
        height=35 * (len(stats_df) + 1) + 3,
        column_config={
            "Metric": st.column_config.TextColumn("Metric"),
            "Value": st.column_config.TextColumn("Value"),
            "Unit": st.column_config.TextColumn("Unit"),
        },
        **STRETCH,
    )


# ============================================================
# SERIES SUMMARY
# ============================================================

section_heading("Series summary", "#2f6bd8")

first_value = valid.iloc[0]
last_value = valid.iloc[-1]

change_text = (
    f"{(last_value / first_value - 1) * 100:+.2f}%"
    if first_value != 0
    else "n/a"
)

peak_month = valid.idxmax()
trough_month = valid.idxmin()

summary_col1, summary_col2, summary_col3 = st.columns(3, gap="small")

with summary_col1:
    info_card(
        "Highest Monthly Premium",
        f"₹{premium_cr(max_premium):,.2f} Cr",
        peak_month.strftime("%b %Y"),
    )

with summary_col2:
    info_card(
        "Lowest Monthly Premium",
        f"₹{premium_cr(min_premium):,.2f} Cr",
        trough_month.strftime("%b %Y"),
    )

with summary_col3:
    info_card(
        "First-to-Last Change",
        change_text,
        "Change across the observed period",
    )


# ============================================================
# DATA DETAILS
# ============================================================

with st.expander("Data details"):
    detail_col1, detail_col2 = st.columns(2, gap="small")

    with detail_col1:
        st.write(f"Source file: `{DATA_FILE}`")
        st.write(f"Raw records loaded: {load_info['raw_rows']:,}")
        st.write(f"Rows dropped (invalid date or value): {load_info['dropped_rows']:,}")
        st.write(f"Duplicate months merged (summed): {load_info['duplicates_merged']:,}")

    with detail_col2:
        st.write("Frequency: Monthly (`MS`)")
        st.write(f"Valid time-series observations: {n_observations:,}")
        st.write(f"Missing months in range: {n_missing:,}")
        st.write(f"Period: {start_date.strftime('%B %Y')} – {end_date.strftime('%B %Y')}")


# ============================================================
# DOWNLOAD
# ============================================================

section_heading("Export analysis data", TEAL)

export_df = pd.DataFrame(
    {
        "collection_month": ts.index.strftime("%Y-%m-%d"),
        "renewed_premium": ts.values,
        f"rolling_mean_{rolling_window}m": rolling_mean.values,
        "mom_change_pct": mom_change.values,
        "first_difference": ts.diff().values,
    }
)

csv_data = export_df.to_csv(index=False).encode("utf-8")

download_col1, download_col2 = st.columns(
    [4, 1],
    gap="small",
    vertical_alignment="center",
)

with download_col1:
    html(
        """
        <div class="download-card">
            <div class="download-inner">
                <div class="download-icon"></div>
                <div>
                    <div class="download-title">Download time series dataset</div>
                    <div class="download-description">
                        Export the monthly premium series with the rolling mean,
                        month-over-month change and first difference shown above.
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
        file_name="time_series_analysis.csv",
        mime="text/csv",
        key="download_csv",
        **STRETCH,
    )


# ============================================================
# FOOTER
# ============================================================

html(
    """
    <div class="analysis-footer">
        Life Insurance Renewal Analytics and Forecasting System
        · Time Series Analysis
    </div>
    """
)
