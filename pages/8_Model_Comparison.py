"""Forecasting Model Comparison page
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
    page_title="Model Comparison",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "reports/all_insurers_all_models_comparison.csv"
HOME_PAGE = "App.py"

KEY_COLS = ["Insurer", "Model"]
METRICS = ["MAPE", "MAE", "RMSE"]
REQUIRED_COLS = KEY_COLS + METRICS

# MAPE is treated as a percentage, as in the source report.
METRIC_LABEL = {"MAPE": "MAPE (%)", "MAE": "MAE", "RMSE": "RMSE"}

ALL_INSURERS = "All insurers"

NAVY = "#0e1b33"
BLUE = "#2456d6"
TEAL = "#0f9b86"
AMBER = "#c97a0c"
PURPLE = "#5b4bd6"

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
    "layers": (
        "<path d='M12 2l10 5-10 5L2 7z'/>"
        "<path d='M2 17l10 5 10-5'/>"
        "<path d='M2 12l10 5 10-5'/>"
    ),
    "building": (
        "<rect x='4' y='2' width='16' height='20' rx='2'/>"
        "<path d='M9 22v-4h6v4'/>"
        "<path d='M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01'/>"
    ),
    "award": (
        "<circle cx='12' cy='8' r='6'/>"
        "<path d='M15.5 13.5L17 22l-5-3-5 3 1.5-8.5'/>"
    ),
    "target": (
        "<circle cx='12' cy='12' r='9'/>"
        "<circle cx='12' cy='12' r='5'/>"
        "<circle cx='12' cy='12' r='1'/>"
    ),
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

.kpi-models    { --tint: #eaf1fd; }
.kpi-insurers  { --tint: #eeecfd; }
.kpi-best      { --tint: #e3f6f2; }
.kpi-lowest    { --tint: #fdf0dc; }

.kpi-models .kpi-icon   { background-image: var(--icon-models); }
.kpi-insurers .kpi-icon { background-image: var(--icon-insurers); }
.kpi-best .kpi-icon     { background-image: var(--icon-best); }
.kpi-lowest .kpi-icon   { background-image: var(--icon-lowest); }

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

/* ---------- FILTER CARDS ---------- */

[class*="st-key-control_"] {
    box-sizing: border-box;
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 8px 16px 6px 16px;
    box-shadow: 0 1px 2px rgba(16, 38, 74, 0.03);
}

[class*="st-key-control_"] [data-testid="stWidgetLabel"] p {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8491a6 !important;
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
    --icon-models: url("{icon_url("layers", BLUE)}");
    --icon-insurers: url("{icon_url("building", PURPLE)}");
    --icon-best: url("{icon_url("award", TEAL)}");
    --icon-lowest: url("{icon_url("target", AMBER)}");
    --download-icon: url("{icon_url("download", BLUE)}");
}}
"""

st.markdown(f"<style>{BASE_CSS}{DYNAMIC_CSS}</style>", unsafe_allow_html=True)


# ============================================================
# HELPERS
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
    # Values come from the data (model / insurer names), so escape them.
    size_class = " kpi-value-sm" if len(value) > 14 else ""
    render_html(
        f"""
        <div class="kpi kpi-{kind}">
            <div class="kpi-icon"></div>
            <div class="kpi-body">
                <div class="kpi-label">{escape(label)}</div>
                <div class="kpi-value{size_class}" title="{escape(value)}">{escape(value)}</div>
                <div class="kpi-description">{escape(description)}</div>
            </div>
        </div>
        """
    )


def chart_note(text: str) -> None:
    render_html(f'<div class="chart-note">{escape(text)}</div>')


def fmt_value(metric: str, value: float) -> str:
    if pd.isna(value):
        return "–"
    text = f"{value:,.2f}"
    return f"{text}%" if metric == "MAPE" else text


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


def show_table(frame: pd.DataFrame, number_cols: list[str]) -> None:
    config = {
        col: st.column_config.NumberColumn(col, format="%.2f")
        for col in number_cols
        if col in frame.columns
    }
    st.dataframe(
        frame,
        hide_index=True,
        height=min(35 * (len(frame) + 1) + 3, 420),
        column_config=config,
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
def load_comparison(path: str, mtime: float):
    """Load and clean the model comparison report.

    `mtime` is only part of the cache key, so the cache refreshes when the
    file changes on disk.
    """
    raw = pd.read_csv(path)

    # Trim names and match the required columns case-insensitively.
    canonical = {c.lower(): c for c in REQUIRED_COLS}
    raw.columns = [
        canonical.get(str(c).strip().lower(), str(c).strip()) for c in raw.columns
    ]

    missing = [c for c in REQUIRED_COLS if c not in raw.columns]
    if missing:
        raise ValueError(
            f"Missing columns: {missing}. Available columns: {raw.columns.tolist()}"
        )

    data = raw.copy()

    # Names: drop blanks first so NaN never becomes the text "nan".
    data = data.dropna(subset=KEY_COLS)
    for col in KEY_COLS:
        data[col] = data[col].astype(str).str.strip()
    data = data[(data["Insurer"] != "") & (data["Model"] != "")]

    # Metrics: accept values such as "12.5%" or "1,234.5"; drop inf.
    for col in METRICS:
        values = data[col]
        if not pd.api.types.is_numeric_dtype(values):
            values = values.astype(str).str.replace(r"[%₹,\s]", "", regex=True)
        data[col] = pd.to_numeric(values, errors="coerce")
    data[METRICS] = data[METRICS].replace([np.inf, -np.inf], np.nan)

    # Keep a row if at least one metric is usable; each view then drops rows
    # that lack the metric being shown.
    data = data.dropna(subset=METRICS, how="all")
    if data.empty:
        raise ValueError("No valid rows remain after cleaning the dataset.")

    # One row per (Insurer, Model): repeated pairs are averaged so every
    # chart, table and "best model" pick uses the same numbers.
    duplicates_merged = int(data.duplicated(KEY_COLS).sum())
    if duplicates_merged:
        other_cols = [c for c in data.columns if c not in REQUIRED_COLS]
        agg = {m: "mean" for m in METRICS}
        agg.update({c: "first" for c in other_cols})
        data = data.groupby(KEY_COLS, as_index=False, sort=True).agg(agg)
        data = data[KEY_COLS + METRICS + other_cols]

    data = data.sort_values(KEY_COLS).reset_index(drop=True)

    info = {
        "raw_rows": int(len(raw)),
        "dropped_rows": int(len(raw) - len(data) - duplicates_merged),
        "duplicates_merged": duplicates_merged,
        "columns": data.columns.tolist(),
    }
    return data, info


data_path = resolve_data_file()

if data_path is None:
    st.error(f"Model comparison file not found:\n\n`{DATA_FILE}`")
    st.stop()

try:
    df, load_info = load_comparison(str(data_path), data_path.stat().st_mtime)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
except Exception as exc:  # noqa: BLE001
    st.error(f"Unable to load the model comparison file.\n\n{exc}")
    st.stop()


insurers = sorted(df["Insurer"].unique())
models = sorted(df["Model"].unique())
available_metrics = [m for m in METRICS if df[m].notna().any()]


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
<svg viewBox="0 0 340 150" role="img" aria-label="Model error ranking visualization">
    <line x1="60" y1="8" x2="60" y2="140" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
    <g class="hero-bars" fill="rgba(127,178,255,0.42)">
        <rect x="60" y="34" width="130" height="18" rx="4"/>
        <rect x="60" y="60" width="170" height="18" rx="4"/>
        <rect x="60" y="86" width="215" height="18" rx="4"/>
        <rect x="60" y="112" width="260" height="18" rx="4"/>
    </g>
    <g class="hero-best">
        <rect x="60" y="8" width="90" height="18" rx="4" fill="#5eead4"/>
        <circle cx="166" cy="17" r="6" fill="#ffffff" stroke="#5eead4" stroke-width="2"/>
    </g>
</svg>
"""

render_html(
    f"""
    <div class="hero">
        <div class="hero-content">
            <div class="hero-kicker">Analytical dashboard</div>
            <div class="hero-title">Forecasting Model Comparison</div>
            <div class="hero-description">
                Compare forecasting models across insurers using MAPE, MAE
                and RMSE, and see which model wins overall and for each
                insurer.
            </div>
            <div class="hero-features">
                <span class="hero-feature"><i style="background:#6ea8ff"></i>{len(insurers)} insurers</span>
                <span class="hero-feature"><i style="background:#5eead4"></i>{len(models)} models</span>
                <span class="hero-feature"><i style="background:#fbbf5a"></i>Lower is better</span>
            </div>
        </div>
        <div class="hero-visual">{HERO_VISUAL}</div>
    </div>
    """
)


# ============================================================
# INTRODUCTION
# ============================================================

render_html(
    """
    <div class="analysis-intro">
        <strong>How to read this</strong>
        <span>
            Every metric measures forecast error, so a lower value is better.
            MAPE is scale-free and is treated as a percentage. MAE and RMSE
            are in the units of each insurer's own series, so they compare
            models within an insurer more fairly than across insurers.
        </span>
    </div>
    """
)


# ============================================================
# FILTERS  (in the main page: the sidebar is hidden by the CSS)
# ============================================================

section_heading("Comparison filters", BLUE)

filter_col1, filter_col2, filter_col3 = st.columns([1.2, 2.4, 1], gap="small")

with filter_col1:
    with st.container(key="control_insurer"):
        selected_insurer = st.selectbox(
            "Insurer",
            [ALL_INSURERS] + insurers,
            key="sel_insurer",
        )

with filter_col2:
    with st.container(key="control_models"):
        selected_models = st.multiselect(
            "Models",
            models,
            default=models,
            key="sel_models",
        )

with filter_col3:
    with st.container(key="control_metric"):
        metric = st.selectbox(
            "Performance metric",
            available_metrics,
            key="sel_metric",
        )

metric_label = METRIC_LABEL[metric]

if not selected_models:
    st.warning("Select at least one model to compare.")
    st.stop()


# ============================================================
# FILTER DATA
# ============================================================

view = df[df["Model"].isin(selected_models)]

if selected_insurer != ALL_INSURERS:
    view = view[view["Insurer"] == selected_insurer]

# Drop rows without the metric being analysed, so idxmin / means never see NaN.
view = view.dropna(subset=[metric])

if view.empty:
    st.warning(f"No {metric} values are available for the selected filters.")
    st.stop()


# ============================================================
# DERIVED RESULTS
# ============================================================

n_models = view["Model"].nunique()
n_insurers = view["Insurer"].nunique()

# Ranking of models by their average metric across the selected insurers.
model_avg = view.groupby("Model")[metric].mean().sort_values()
best_model = model_avg.index[0]
best_value = model_avg.iloc[0]

# Best model for each insurer (lowest value of the selected metric).
insurer_best = view.loc[view.groupby("Insurer")[metric].idxmin()]
wins = insurer_best["Model"].value_counts()
best_model_wins = int(wins.get(best_model, 0))

if n_insurers == 1:
    best_description = "Best model for this insurer"
    value_description = f"For {selected_insurer}"
else:
    best_description = f"Best for {best_model_wins} of {n_insurers} insurers"
    value_description = "Average across selected insurers"


# ============================================================
# KPI SECTION
# ============================================================

section_heading("Model performance overview", BLUE)

k1, k2, k3, k4 = st.columns(4, gap="small")

with k1:
    kpi_card(
        "models",
        "Models Compared",
        f"{n_models:,}",
        "Forecasting models in the comparison",
    )

with k2:
    kpi_card(
        "insurers",
        "Insurers Compared",
        f"{n_insurers:,}",
        "Insurers in the comparison",
    )

with k3:
    kpi_card(
        "best",
        "Best Model",
        str(best_model),
        best_description,
    )

with k4:
    kpi_card(
        "lowest",
        f"Best Average {metric_label}",
        fmt_value(metric, best_value),
        value_description,
    )


# ============================================================
# 1. MODEL RANKING
# ============================================================

section_heading(f"1. Model ranking by average {metric}", TEAL)

with st.container(key="chart_ranking"):
    fig_rank = go.Figure()

    fig_rank.add_trace(
        go.Bar(
            x=model_avg.values,
            y=model_avg.index,
            orientation="h",
            name=metric_label,
            marker_color=[TEAL if i == 0 else BLUE for i in range(len(model_avg))],
            text=[fmt_value(metric, v) for v in model_avg.values],
            textposition="outside",
            textfont=dict(size=12, family=FONT, color="#1f2d47"),
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                f"Average {metric_label}: %{{x:,.2f}}"
                "<extra></extra>"
            ),
        )
    )

    rank_title = (
        f"Average {metric_label} by model"
        if n_insurers > 1
        else f"{metric_label} by model — {selected_insurer}"
    )

    style_fig(
        fig_rank,
        rank_title,
        "",
        height=max(320, 46 * len(model_avg) + 120),
    )
    fig_rank.update_xaxes(
        title_text=f"Average {metric_label}" if n_insurers > 1 else metric_label,
        showgrid=True,
        gridcolor="#e3e9f2",
        range=[0, float(model_avg.max()) * 1.18],
    )
    fig_rank.update_yaxes(showgrid=False, autorange="reversed")

    show_chart(fig_rank, "fig_rank")

    rank_note = "The best model (lowest error) is highlighted in teal."
    if metric != "MAPE" and n_insurers > 1:
        rank_note += (
            " MAE and RMSE follow each insurer's own scale, so large insurers "
            "weigh more here; switch to MAPE for a scale-free ranking."
        )
    chart_note(rank_note)


# ============================================================
# 2. INSURER x MODEL HEATMAP
# ============================================================

section_heading(f"2. {metric} by insurer and model", AMBER)

if n_insurers > 1:
    model_order = list(model_avg.index)  # best model first
    pivot_df = (
        view.pivot_table(index="Insurer", columns="Model", values=metric, aggfunc="mean")
        .reindex(columns=model_order)
        .sort_index()
    )

    text = [
        ["" if pd.isna(v) else f"{v:,.2f}" for v in row]
        for row in pivot_df.values
    ]

    with st.container(key="chart_heatmap"):
        fig_heat = go.Figure()

        fig_heat.add_trace(
            go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns.tolist(),
                y=pivot_df.index.tolist(),
                text=text,
                texttemplate="%{text}",
                textfont=dict(size=12, family=FONT, color=NAVY),
                colorscale=[
                    [0.0, "#d5f3ec"],
                    [0.5, "#fdf0dc"],
                    [1.0, "#f6c2b8"],
                ],
                xgap=2,
                ygap=2,
                hoverongaps=False,
                colorbar=dict(title=dict(text=metric_label), thickness=12, len=0.8),
                hovertemplate=(
                    "<b>%{y}</b> · %{x}<br>"
                    f"{metric_label}: %{{z:,.2f}}"
                    "<extra></extra>"
                ),
            )
        )

        # Outline the best (lowest) cell in every insurer row.
        for row_idx, insurer in enumerate(pivot_df.index):
            row = pivot_df.loc[insurer]
            if row.notna().any():
                col_idx = list(pivot_df.columns).index(row.idxmin())
                fig_heat.add_shape(
                    type="rect",
                    x0=col_idx - 0.5,
                    x1=col_idx + 0.5,
                    y0=row_idx - 0.5,
                    y1=row_idx + 0.5,
                    line=dict(color=NAVY, width=2),
                )

        style_fig(
            fig_heat,
            f"{metric_label} for every insurer and model",
            "",
            height=max(340, 36 * len(pivot_df) + 150),
        )
        fig_heat.update_xaxes(showgrid=False, side="top")
        fig_heat.update_yaxes(showgrid=False, autorange="reversed")

        show_chart(fig_heat, "fig_heat")

        chart_note(
            "Outlined cell = best model for that insurer. Models are ordered "
            "from best to worst average; greener cells mean lower error."
        )
else:
    st.info(
        "Choose **All insurers** in the filters to compare models across "
        "insurers in a heatmap."
    )


# ============================================================
# 3. BEST MODEL BY INSURER
# ============================================================

section_heading("3. Best model by insurer", PURPLE)

best_cols = ["Insurer", "Model", metric] + [m for m in METRICS if m != metric]

best_table = (
    insurer_best[best_cols]
    .sort_values(metric)
    .rename(columns={"Model": "Best Model", **METRIC_LABEL})
    .reset_index(drop=True)
)

with st.container(key="chart_best_table"):
    render_html(
        f'<div class="table-title">Lowest {escape(metric_label)} per insurer</div>'
    )
    show_table(best_table, list(METRIC_LABEL.values()))


# ============================================================
# 4. AVERAGE PERFORMANCE BY MODEL
# ============================================================

section_heading("4. Average performance by model", BLUE)

model_summary = view.groupby("Model").agg(
    **{
        "Insurers": ("Insurer", "nunique"),
        **{f"Average {METRIC_LABEL[m]}": (m, "mean") for m in METRICS},
    }
)
model_summary["Insurers won"] = (
    wins.reindex(model_summary.index).fillna(0).astype(int)
)
model_summary = (
    model_summary.sort_values(f"Average {metric_label}")
    .reset_index()
)

with st.container(key="chart_model_table"):
    render_html(
        f'<div class="table-title">Models ranked by average {escape(metric_label)}</div>'
    )
    show_table(model_summary, [f"Average {v}" for v in METRIC_LABEL.values()])


# ============================================================
# 5. DETAILED RESULTS
# ============================================================

section_heading("5. Detailed results", TEAL)

display_df = view.sort_values(["Insurer", metric]).reset_index(drop=True)

with st.container(key="chart_detail_table"):
    render_html(
        f'<div class="table-title">All results, ordered by {escape(metric_label)} within each insurer</div>'
    )
    show_table(display_df, METRICS)


# ============================================================
# DATA DETAILS
# ============================================================

with st.expander("Data details"):
    detail_col1, detail_col2 = st.columns(2, gap="small")

    with detail_col1:
        st.write(f"Source file: `{DATA_FILE}`")
        st.write(f"Raw records loaded: {load_info['raw_rows']:,}")
        st.write(f"Rows dropped (missing names or metrics): {load_info['dropped_rows']:,}")
        st.write(f"Repeated insurer-model rows averaged: {load_info['duplicates_merged']:,}")

    with detail_col2:
        st.write(f"Insurers in file: {len(insurers):,}")
        st.write(f"Models in file: {len(models):,}")
        st.write(f"Rows in current view: {len(view):,}")
        st.write(f"Columns: `{', '.join(load_info['columns'])}`")


# ============================================================
# DOWNLOAD
# ============================================================

section_heading("Export comparison data", TEAL)

csv_data = display_df.to_csv(index=False).encode("utf-8")

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
                    <div class="download-title">Download model comparison</div>
                    <div class="download-description">
                        Export the results for the insurers, models and
                        metric currently selected in the filters.
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
        file_name="model_comparison.csv",
        mime="text/csv",
        key="download_csv",
        **STRETCH,
    )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="analysis-footer">
        Life Insurance Renewal Analytics and Forecasting System
        · Model Comparison
    </div>
    """
)
