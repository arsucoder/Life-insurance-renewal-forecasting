import json
import urllib.request

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Region Analysis",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = "data/processed/monthly_by_region.csv"
GEOJSON_URL = "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson"

# ----------------------------------------------------------------
# PALETTE
# ----------------------------------------------------------------
NAVY_DARK = "#0B1B3A"
NAVY_MID = "#142B52"
BLUE = "#2563EB"
PURPLE = "#7C3AED"
GREEN = "#16A34A"
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

        /* ---------- HERO BANNER (compact) ---------- */
        .hero {
            background: linear-gradient(135deg, #0B1B3A 0%, #142B52 55%, #0F2247 100%);
            border-radius: 16px;
            padding: 16px 26px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            color: #CBD5E1;
            font-size: 0.68rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 999px;
            margin-bottom: 6px;
        }
        .hero-badge-dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: #38BDF8; display: inline-block;
        }
        .hero-title {
            color: #F8FAFC;
            font-size: 1.5rem;
            font-weight: 800;
            line-height: 1.1;
            margin: 0;
        }
        .hero-spark { opacity: 0.9; }

        /* ---------- SECTION LABEL ---------- */
        .section-label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            color: #1E293B;
            margin: 2px 0 6px 0;
        }
        .section-label .bar {
            width: 4px; height: 13px;
            background: #2563EB;
            border-radius: 2px;
            display: inline-block;
        }

        /* ---------- CARD WRAPPER ---------- */
        .kcard {
            background: #F8FAFC;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 10px 14px 6px 14px;
        }
        .kcard-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: #1E293B;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 2px;
        }
        .kcard-title .dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .kcard-hint {
            font-size: 0.72rem;
            font-weight: 500;
            color: #94A3B8;
            margin-left: auto;
        }

        /* ---------- METRIC (KPI) STYLING ---------- */
        div[data-testid="stMetric"] {
            background: #F8FAFC;            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 10px 14px 8px 14px;
        }
        div[data-testid="stMetricLabel"] { font-size: 0.74rem; color: #64748B; font-weight: 600; }
        div[data-testid="stMetricValue"] { font-size: 1.3rem; font-weight: 800; color: #0F172A; }

        div[data-testid="element-container"] { margin-bottom: 0.1rem; }

        /* ---------- FILTER LABELS ---------- */
        .filter-label {
            font-size: 0.72rem;
            font-weight: 600;
            color: #64748B;
            margin-bottom: 2px;
        }

        /* ---------- DATE INPUT FIX ----------
           Default Streamlit date-range widget can get squeezed
           inside a narrow column, which clips/wraps the two dates.
           Give it a fixed readable size and let it size to content
           instead of being force-shrunk by the column. */
        div[data-testid="stDateInput"] {
            width: 100%;
        }
        div[data-testid="stDateInput"] > div {
            min-width: 100%;
        }
        div[data-testid="stDateInput"] input {
            font-size: 0.82rem;
            padding: 6px 8px;
            min-width: 105px;
        }

        /* ---------- EXPANDER (detailed tables) ---------- */
        div[data-testid="stExpander"] {
            background: #F8FAFC;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            margin-top: 6px;
        }

        /* ---------- HIGHLIGHTS ---------- */
        .hl {
            font-size: 0.78rem;
            color: #475569;
            line-height: 1.55;
        }
        .hl b { color: #0F172A; }
        .hl .dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# HERO BANNER
# ----------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div>
            <div class="hero-badge">
                <span class="hero-badge-dot"></span> Regional performance
            </div>
            <div class="hero-title">Region Analysis</div>
        </div>
        <svg class="hero-spark" width="140" height="46" viewBox="0 0 170 70" xmlns="http://www.w3.org/2000/svg">
            <polyline points="0,55 25,42 50,48 75,22 100,30 125,14 150,18 170,6"
                      fill="none" stroke="#38BDF8" stroke-width="2.5"
                      stroke-linecap="round" stroke-linejoin="round" />
            <polyline points="100,30 125,14 150,18 170,6"
                      fill="none" stroke="#22D3EE" stroke-width="2.5"
                      stroke-dasharray="4,4"
                      stroke-linecap="round" stroke-linejoin="round" />
            <circle cx="100" cy="30" r="4" fill="#F8FAFC" stroke="#38BDF8" stroke-width="2"/>
        </svg>
    </div>
    """,
    unsafe_allow_html=True,
)


def _norm(s):
    """Lowercase, '&' -> 'and', collapse whitespace."""
    return " ".join(str(s).strip().lower().replace("&", "and").split())


def _canon_region_name(s):
    """Strip filler words so 'North Zone' -> 'north', 'North-East Region' -> 'north-east'."""
    n = _norm(s).replace(" zone", "").replace(" region", "").strip()
    return n


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()

    required_columns = [
        "collection_month",
        "region",
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

    return df.sort_values(["region", "collection_month"]).reset_index(drop=True)


@st.cache_data
def load_india_geojson():
    req = urllib.request.Request(GEOJSON_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


try:
    df = load_data()
except FileNotFoundError:
    st.error(f"Dataset not found: `{DATA_PATH}` — make sure it is inside data/processed/")
    st.stop()

regions = sorted(df["region"].dropna().unique())

# ----------------------------------------------------------------
# STATE -> REGION MAPPING (drives the clickable map)
# ----------------------------------------------------------------
# Canonical zone for every Indian state/UT (normalised keys).
_CANON_ZONES = {
    "north": [
        "Jammu and Kashmir", "Ladakh", "Himachal Pradesh", "Punjab",
        "Chandigarh", "Uttarakhand", "Uttaranchal", "Haryana", "Delhi",
        "NCT of Delhi", "Uttar Pradesh", "Rajasthan",
    ],
    "south": [
        "Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu", "Kerala",
        "Puducherry", "Pondicherry", "Lakshadweep",
        "Andaman and Nicobar", "Andaman and Nicobar Islands",
    ],
    "east": [
        "Bihar", "Jharkhand", "West Bengal", "Odisha", "Orissa",
    ],
    "west": [
        "Gujarat", "Maharashtra", "Goa",
        "Dadra and Nagar Haveli", "Daman and Diu",
        "Dadra and Nagar Haveli and Daman and Diu",
    ],
    # Overrides below win when the dataset actually has these regions;
    # otherwise their states fall back to west / east respectively.
    "central": ["Madhya Pradesh", "Chhattisgarh", "Chhatisgarh"],
    "northeast": [
        "Sikkim", "Assam", "Arunachal Pradesh", "Manipur", "Meghalaya",
        "Mizoram", "Nagaland", "Tripura",
    ],
}
STATE_CANON = {_norm(s): z for z, states in _CANON_ZONES.items() for s in states}

ZONE_ALIASES = {
    "north": ["north", "northern"],
    "south": ["south", "southern"],
    "east": ["east", "eastern"],
    "west": ["west", "western"],
    "central": ["central"],
    "northeast": ["north east", "north-east", "northeast", "north eastern", "ne"],
}
ZONE_COLORS = {
    "north": BLUE,
    "south": GREEN,
    "east": PURPLE,
    "west": "#F59E0B",
    "central": "#0EA5E9",
    "northeast": "#EC4899",
}

_canon_lookup = {_canon_region_name(r): r for r in regions}


def _match_zone(canon):
    for alias in ZONE_ALIASES[canon]:
        if alias in _canon_lookup:
            return _canon_lookup[alias]
    return None


zone_actual = {z: _match_zone(z) for z in _CANON_ZONES}
zone_actual = {z: a for z, a in zone_actual.items() if a}

state_to_region = {}
for s_norm, canon in STATE_CANON.items():
    if canon == "central" and "central" not in zone_actual:
        canon = "west"                      # fall back when no Central region in data
    if canon == "northeast" and "northeast" not in zone_actual:
        canon = "east"                      # fall back when no North-East region in data
    actual = zone_actual.get(canon)
    if actual:
        state_to_region[s_norm] = actual


def _sync_map_focus():
    """Keep the map highlight in step when the Region dropdown is changed manually."""
    st.session_state["_map_focus"] = st.session_state.get("selected_region")
    # Remount the map so any stale Plotly click-highlight is wiped and the
    # whole newly selected region glows; also forget the last click signature
    # so clicking the same state again is treated as a fresh click.
    st.session_state["_map_key_n"] = st.session_state.get("_map_key_n", 0) + 1
    st.session_state.pop("_last_map_click", None)


def _clicked_region(pt, fig):
    """Resolve which region a clicked map point belongs to.

    Streamlit/Plotly versions differ in what a choropleth click carries, so
    try several shapes in order: customdata (the true region, embedded per
    state), a state name, the trace index (every trace is exactly one true
    region, in every map mode), then trace + point index -> state -> region.
    """
    # 1) customdata carries the true region directly
    try:
        cd = pt.get("customdata")
        if isinstance(cd, (list, tuple)) and cd:
            cand = str(cd[0])
            if cand in regions:
                return cand
    except Exception:        pass

    # 2) state name directly, if the payload includes it
    loc = pt.get("location") or pt.get("text")
    if loc:
        r = state_to_region.get(_norm(loc))
        if r in regions:
            return r

    def _num(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    cn = pt.get("curve_number", pt.get("curveNumber"))
    pn = pt.get("point_number", pt.get("pointNumber", pt.get("point_index", pt.get("pointIndex"))))
    cn, pn = _num(cn), _num(pn)
    # Guard against negative indices: Python would wrap them around and
    # resolve the wrong trace/state instead of failing cleanly.
    if cn is not None and cn < 0:
        cn = None
    if pn is not None and pn < 0:
        pn = None

    if cn is not None:
        try:
            trace = fig.data[cn]
            # 3) each trace is one true region -> the trace name IS the region
            if trace.name in regions:
                return trace.name
            # 4) trace + point index -> state name -> region
            if pn is not None:
                state_name = trace.locations[pn]
                r = state_to_region.get(_norm(str(state_name)))
                if r in regions:
                    return r
        except (IndexError, AttributeError, TypeError):
            pass
    return None

# ----------------------------------------------------------------
# INTERACTIVE INDIA MAP — click a state to select its region
# ----------------------------------------------------------------
st.markdown('<div class="section-label"><span class="bar"></span>Select Region</div>', unsafe_allow_html=True)

try:
    india_geojson = load_india_geojson()
except Exception:
    india_geojson = None

if india_geojson is None:
    st.info("Map could not be loaded (needs internet once) — use the Region dropdown below instead.")
else:
    if "_map_key_n" not in st.session_state:
        st.session_state["_map_key_n"] = 0

    state_keys = [f["properties"]["NAME_1"] for f in india_geojson["features"]]
    map_df = pd.DataFrame({"name_key": state_keys})
    map_df["true_region"] = map_df["name_key"].apply(
        lambda n: state_to_region.get(_norm(n), "Other")
    )

    # Focus mode: once a region is picked (map click or dropdown), the whole
    # region stays coloured and the rest fade — instead of Plotly's default
    # single-state click highlight. Every map mode keeps one trace per TRUE
    # region (non-focused regions are just greyed out via the color map), so
    # a click's trace index always maps straight back to its region.
    focus = st.session_state.get("_map_focus")
    if focus not in regions:
        focus = None

    map_df["region"] = map_df["true_region"]
    if focus:
        focus_canon = next((c for c, a in zone_actual.items() if a == focus), None)
        focus_color = ZONE_COLORS.get(focus_canon, BLUE)
        region_colors = {
            r: (focus_color if r == focus else "#E2E8F0")
            for r in map_df["region"].unique()
        }
    else:
        region_colors = {actual: ZONE_COLORS[canon] for canon, actual in zone_actual.items()}
    if "Other" in map_df["region"].values and "Other" not in region_colors:
        region_colors["Other"] = "#CBD5E1"

    fig_map = px.choropleth(
        map_df,
        geojson=india_geojson,
        locations="name_key",
        featureidkey="properties.NAME_1",
        color="region",
        color_discrete_map=region_colors,
        custom_data=["true_region"],
    )
    fig_map.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig_map.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=-0.06, font=dict(size=10)),
        dragmode=False,  # disable mouse drag pan / zoom on the map (clicks + hover still work)
    )
    fig_map.update_traces(
        marker_line_width=0.8,
        marker_line_color="#FFFFFF",
        hovertemplate="<b>%{customdata[0]}</b><extra></extra>",
    )

    st.markdown(
        '<div class="kcard"><div class="kcard-title">'
        f'<span class="dot" style="background:{BLUE};"></span>'
        'India Map<span class="kcard-hint">click a state to load its region below</span></div>',
        unsafe_allow_html=True,
    )

    # on_select needs Streamlit >= 1.35; older versions just show the map.
    try:
        map_event = st.plotly_chart(
            fig_map,            use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False},
            on_select="rerun",
            selection_mode="points",
            key=f"india_map_{st.session_state['_map_key_n']}",
        )
    except TypeError:
        st.plotly_chart(
            fig_map,
            use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False},
            key=f"india_map_{st.session_state['_map_key_n']}",
        )
        map_event = None
        st.warning(
            f"Map click needs Streamlit ≥ 1.35 (you have {st.__version__}) — "
            "upgrade with `pip install -U streamlit`, or use the Region dropdown below."
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Consume the click: the selection persists across reruns, so only act
    # on a *new* point signature to avoid stale clicks overriding the dropdown.
    points = []
    try:
        sel = (map_event or {}).get("selection") or {}
        points = sel.get("points") or []
    except Exception:
        points = []

    if points:
        pt = points[0]
        cn = pt.get("curve_number", pt.get("curveNumber"))
        pn = pt.get("point_number", pt.get("pointNumber", pt.get("point_index", pt.get("pointIndex"))))
        sig = (cn, pn)
        if sig != st.session_state.get("_last_map_click"):
            st.session_state["_last_map_click"] = sig
            clicked_region = _clicked_region(pt, fig_map)
            if clicked_region and clicked_region in regions:
                st.session_state["selected_region"] = clicked_region
                st.session_state["_map_focus"] = clicked_region
                # Remount the chart with a fresh key so Plotly's single-state
                # click highlight is wiped, then rerun immediately — the map
                # renders before this handler, so without this it would lag
                # one click behind and never show the whole region glowing.
                st.session_state["_map_key_n"] += 1
                st.rerun()

# -----------------------------
# FILTERS
# -----------------------------
# Date range gets more room than the region dropdown so the two
# date boxes inside it never get squeezed/wrapped.
col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown('<div class="filter-label">Region</div>', unsafe_allow_html=True)
    if "selected_region" not in st.session_state:
        st.session_state["selected_region"] = regions[0]
    selected_region = st.selectbox(
        "Select Region",
        regions,
        label_visibility="collapsed",
        key="selected_region",
        on_change=_sync_map_focus,
    )

region_df = df[df["region"] == selected_region].copy()

min_date = region_df["collection_month"].min().date()
max_date = region_df["collection_month"].max().date()

with col2:
    st.markdown('<div class="filter-label">Date Range</div>', unsafe_allow_html=True)
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed",
    )

# While the user has only picked the start date, date_range is a
# single-element tuple — fall back to the full range instead of
# erroring, and only apply the filter once both ends are picked.
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = region_df[
        (region_df["collection_month"].dt.date >= start_date)
        & (region_df["collection_month"].dt.date <= end_date)
    ].copy()
else:
    filtered_df = region_df.copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_policies = filtered_df["total_policies"].sum()
renewed_policies = filtered_df["renewed_policies"].sum()

total_premium = filtered_df["total_premium"].sum()
renewed_premium = filtered_df["renewed_premium"].sum()

renewal_rate = (
    renewed_policies / total_policies * 100 if total_policies > 0 else 0
)

average_premium = (
    total_premium / total_policies if total_policies > 0 else 0
)

# -----------------------------
# KPI CARDS
# -----------------------------
st.markdown('<div class="section-label"><span class="bar"></span>Overview</div>', unsafe_allow_html=True)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Total Policies", f"{total_policies:,.0f}")

with kpi2:
    st.metric("Renewal Rate", f"{renewal_rate:.2f}%")

with kpi3:
    st.metric("Renewed Premium", f"₹{renewed_premium / 1e7:.2f} Cr")

with kpi4:
    st.metric("Avg Premium / Policy", f"₹{average_premium:,.0f}")

# -----------------------------
# CHART DATA
# -----------------------------
monthly_df = filtered_df.sort_values("collection_month").copy()

st.markdown('<div class="section-label"><span class="bar"></span>Trends</div>', unsafe_allow_html=True)

# -----------------------------
# CHART ROW — Monthly Renewal Rate + Premium Mix
# -----------------------------
chart1, chart2 = st.columns(2)

with chart1:
    st.markdown(
        '<div class="kcard"><div class="kcard-title">'
        f'<span class="dot" style="background:{BLUE};"></span>'
        'Monthly Renewal Rate</div>',
        unsafe_allow_html=True,
    )

    fig_renewal = px.line(
        monthly_df,
        x="collection_month",
        y="renewal_rate",
        markers=True,
        color_discrete_sequence=[BLUE],
    )

    fig_renewal.update_layout(
        height=165,
        margin=dict(l=8, r=8, t=4, b=8),
        xaxis_title="",
        yaxis_title="",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_renewal.update_yaxes(ticksuffix="%", gridcolor="#EEF2F7")
    fig_renewal.update_xaxes(showgrid=False)
    fig_renewal.update_traces(
        line_width=2.5,
        marker_size=6,
        hovertemplate="<b>%{x|%b %Y}</b><br>Renewal Rate: %{y:.2f}%<extra></extra>",
    )

    st.plotly_chart(fig_renewal, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with chart2:
    st.markdown(
        '<div class="kcard"><div class="kcard-title">'
        f'<span class="dot" style="background:{PURPLE};"></span>'
        'Premium Mix</div>',
        unsafe_allow_html=True,
    )

    non_renewed_premium = max(total_premium - renewed_premium, 0)

    premium_df = pd.DataFrame({
        "Premium Type": ["Renewed Premium", "Non-Renewed Premium"],
        "Premium": [renewed_premium, non_renewed_premium],
    })

    fig_premium = px.pie(
        premium_df,
        names="Premium Type",
        values="Premium",
        hole=0.6,
        color="Premium Type",
        color_discrete_map={
            "Renewed Premium": GREEN,
            "Non-Renewed Premium": NON_RENEWED,
        },
    )

    fig_premium.update_traces(
        textinfo="percent",
        textfont_size=11,
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Premium: ₹%{value:,.0f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
    )

    fig_premium.update_layout(
        height=165,
        margin=dict(l=8, r=8, t=4, b=8),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.18, font=dict(size=10)),
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig_premium, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# CHART ROW — Premium Trend + Policy Trend
# -----------------------------
chart3, chart4 = st.columns(2)

with chart3:
    st.markdown(
        '<div class="kcard"><div class="kcard-title">'
        f'<span class="dot" style="background:{GREEN};"></span>'        'Monthly Premium Trend</div>',
        unsafe_allow_html=True,
    )

    prem_trend = monthly_df[["collection_month", "total_premium", "renewed_premium"]].copy()
    prem_trend["total_premium"] = prem_trend["total_premium"] / 1e7
    prem_trend["renewed_premium"] = prem_trend["renewed_premium"] / 1e7
    prem_melt = prem_trend.melt(
        id_vars="collection_month", var_name="Series", value_name="Premium"
    )
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

    fig_prem_trend.update_layout(
        height=160,
        margin=dict(l=8, r=8, t=22, b=8),
        xaxis_title="",
        yaxis_title="",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
    )
    fig_prem_trend.update_yaxes(ticksuffix=" Cr", gridcolor="#EEF2F7")
    fig_prem_trend.update_xaxes(showgrid=False)
    fig_prem_trend.update_traces(
        line_width=2.5,
        marker_size=5,
        hovertemplate="<b>%{x|%b %Y}</b><br>%{fullData.name}: ₹%{y:.2f} Cr<extra></extra>",
    )

    st.plotly_chart(fig_prem_trend, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with chart4:
    st.markdown(
        '<div class="kcard"><div class="kcard-title">'
        f'<span class="dot" style="background:{PURPLE};"></span>'
        'Monthly Policy Trend</div>',
        unsafe_allow_html=True,
    )

    pol_trend = monthly_df[["collection_month", "total_policies", "renewed_policies"]].copy()
    pol_melt = pol_trend.melt(
        id_vars="collection_month", var_name="Series", value_name="Policies"
    )
    pol_melt["Series"] = pol_melt["Series"].map(
        {"total_policies": "Total Policies", "renewed_policies": "Renewed Policies"}
    )

    fig_pol_trend = px.line(
        pol_melt,
        x="collection_month",
        y="Policies",
        color="Series",
        markers=True,
        color_discrete_map={"Total Policies": BLUE, "Renewed Policies": GREEN},
    )

    fig_pol_trend.update_layout(
        height=160,
        margin=dict(l=8, r=8, t=22, b=8),
        xaxis_title="",
        yaxis_title="",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
    )
    fig_pol_trend.update_yaxes(gridcolor="#EEF2F7")
    fig_pol_trend.update_xaxes(showgrid=False)
    fig_pol_trend.update_traces(
        line_width=2.5,
        marker_size=5,
        hovertemplate="<b>%{x|%b %Y}</b><br>%{fullData.name}: %{y:,.0f}<extra></extra>",
    )

    st.plotly_chart(fig_pol_trend, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# CHART ROW — Region Comparison + Highlights
# -----------------------------
chart5, chart6 = st.columns(2)

with chart5:
    st.markdown(
        '<div class="kcard"><div class="kcard-title">'
        f'<span class="dot" style="background:{BLUE};"></span>'
        'Renewal Rate by Region</div>',
        unsafe_allow_html=True,
    )

    comparison = (
        df.groupby("region")
        .agg(
            total_policies=("total_policies", "sum"),
            renewed_policies=("renewed_policies", "sum"),
            total_premium=("total_premium", "sum"),
            renewed_premium=("renewed_premium", "sum"),
        )
        .reset_index()
    )
    comparison["renewal_rate"] = (
        comparison["renewed_policies"] / comparison["total_policies"] * 100
    )
    comparison["premium_renewal_rate"] = (
        comparison["renewed_premium"] / comparison["total_premium"] * 100    )
    comparison = comparison.sort_values("renewal_rate", ascending=False)

    fig_comp = px.bar(
        comparison,
        x="region",
        y="renewal_rate",
        color_discrete_sequence=[BLUE],
    )

    fig_comp.update_layout(
        height=150,
        margin=dict(l=8, r=8, t=4, b=8),
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_comp.update_yaxes(ticksuffix="%", gridcolor="#EEF2F7")
    fig_comp.update_xaxes(showgrid=False)
    fig_comp.update_traces(
        hovertemplate="<b>%{x}</b><br>Renewal Rate: %{y:.2f}%<extra></extra>",
    )

    st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with chart6:
    st.markdown(
        '<div class="kcard"><div class="kcard-title">'
        f'<span class="dot" style="background:{GREEN};"></span>'
        'Highlights</div>',
        unsafe_allow_html=True,
    )

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
            f'<div class="hl"><span class="dot" style="background:{GREEN};"></span>'
            f"<b>Best month</b><br>{best_label}<br>{best_rate} · {best_pol} renewed</div>",
            unsafe_allow_html=True,
        )

    with h2:
        st.markdown(
            '<div class="hl"><span class="dot" style="background:#F59E0B;"></span>'
            f"<b>Lowest month</b><br>{worst_label}<br>{worst_rate} · {worst_pol} renewed</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# DETAILED TABLES (collapsed — keeps everything on one screen)
# -----------------------------
with st.expander("Detailed tables"):
    st.markdown(
        '<div class="section-label"><span class="bar"></span>Region Comparison</div>',
        unsafe_allow_html=True,
    )

    display_comparison = comparison.copy()
    display_comparison["total_premium"] = display_comparison["total_premium"] / 1e7
    display_comparison["renewed_premium"] = display_comparison["renewed_premium"] / 1e7
    display_comparison = display_comparison.rename(
        columns={
            "region": "Region",
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
        '<div class="section-label"><span class="bar"></span>Monthly Data</div>',
        unsafe_allow_html=True,
    )

    display_df = filtered_df.copy()
    display_df["total_premium"] = display_df["total_premium"] / 1e7
    display_df["renewed_premium"] = display_df["renewed_premium"] / 1e7
    display_df = display_df.rename(
        columns={
            "collection_month": "Month",
            "region": "Region",
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
        label="Download Regional Data",
        data=csv_data,
        file_name=f"{selected_region}_monthly_analysis.csv",
        mime="text/csv",    )