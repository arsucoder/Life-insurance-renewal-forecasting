import os

import numpy as np
import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Insurance Renewal Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# HIDE STREAMLIT'S AUTOMATIC SIDEBAR PAGE LIST
# (this home page uses its own navigation instead)
# ============================================================

st.markdown(
    """
    <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FILE LOCATIONS
# ============================================================

INSURER_FILE = "data/processed/monthly_by_insurer.csv"

DATA_FILES = [
    "data/processed/monthly_by_insurer.csv",
    "data/processed/monthly_by_payment_mode.csv",
    "data/processed/monthly_by_policy_type.csv",
    "data/processed/monthly_by_region.csv",
    "data/processed/yearly_renewal_premium.csv",
    "data/processed/monthly_renewal_premium.csv",
    "reports/all_insurers_all_models_comparison.csv",
    "reports/business_insights.csv",
]


# ============================================================
# PAGE REGISTRY  (edit here if you rename a page file)
# ============================================================

PAGES = [
    {
        "file": "pages/01_Overview.py",
        "icon": "🏠",
        "title": "Overview",
        "desc": "High-level summary of renewal performance across the whole portfolio.",
        "category": "Descriptive Analysis",
        "keywords": "summary kpi portfolio dashboard overall",
    },
    {
        "file": "pages/2_Insurer_Analysis.py",
        "icon": "🏢",
        "title": "Insurer Analysis",
        "desc": "Drill into any insurer: renewal rate, premium and policy trends by month.",
        "category": "Descriptive Analysis",
        "keywords": "insurer company renewal rate premium",
    },
    {
        "file": "pages/3_Payment_Analysis.py",
        "icon": "💳",
        "title": "Payment Analysis",
        "desc": "Compare renewal behaviour across payment modes.",
        "category": "Descriptive Analysis",
        "keywords": "payment mode upi cash cheque online",
    },
    {
        "file": "pages/4_Policy_Type_Analysis.py",
        "icon": "📋",
        "title": "Policy Type Analysis",
        "desc": "See which policy types renew best and where premium is concentrated.",
        "category": "Descriptive Analysis",
        "keywords": "policy type product plan",
    },
    {
        "file": "pages/5_Region_Analysis.py",
        "icon": "🌍",
        "title": "Region Analysis",
        "desc": "Regional renewal performance, premium and policy trends.",
        "category": "Descriptive Analysis",
        "keywords": "region geography zone state",
    },
    {
        "file": "pages/6_Yearly_Analysis.py",
        "icon": "📅",
        "title": "Yearly Analysis",
        "desc": "Financial-year view with year-over-year growth and best/worst years.",
        "category": "Descriptive Analysis",
        "keywords": "year financial year growth yoy",
    },
    {
        "file": "pages/7_Time_Series_Analysis.py",
        "icon": "📈",
        "title": "Time Series Analysis",
        "desc": "Trend, seasonality, stationarity (ADF), ACF and PACF of renewed premium.",
        "category": "Forecasting",
        "keywords": "time series trend seasonality adf acf pacf stationarity",
    },
    {
        "file": "pages/8_Model_Comparison.py",
        "icon": "🤖",
        "title": "Model Comparison",
        "desc": "Compare Naive, Seasonal Naive, ARIMA, SARIMA and Prophet by MAPE, MAE and RMSE.",
        "category": "Forecasting",
        "keywords": "model arima sarima prophet naive mape mae rmse accuracy",
    },
    {
        "file": "pages/9_Dynamic_Forecasting.py",
        "icon": "🔮",
        "title": "Dynamic Forecasting",
        "desc": "Generate forecasts interactively and explore what the future may look like.",
        "category": "Forecasting",
        "keywords": "forecast predict future dynamic",
    },
    {
        "file": "pages/10_Business_Insights.py",
        "icon": "💡",
        "title": "Business Insights",
        "desc": "Automatic insights, growth outlook and insurer comparison from forecasts.",
        "category": "Business",
        "keywords": "insight recommendation outlook volatility growth",
    },
]

CATEGORIES = ["Descriptive Analysis", "Forecasting", "Business"]
CATEGORY_ICONS = {
    "Descriptive Analysis": "📊",
    "Forecasting": "🔮",
    "Business": "💼",
}

# Guided navigation: question -> page file
GUIDED = {
    "How is the overall business performing?": "pages/01_Overview.py",
    "Which insurer renews best?": "pages/2_Insurer_Analysis.py",
    "Which payment mode has the best renewal rate?": "pages/3_Payment_Analysis.py",
    "Which policy type renews best?": "pages/4_Policy_Type_Analysis.py",
    "Which region is strongest or weakest?": "pages/5_Region_Analysis.py",
    "How did each financial year perform?": "pages/6_Yearly_Analysis.py",
    "Is there a trend or seasonality in premium?": "pages/7_Time_Series_Analysis.py",
    "Which forecasting model is most accurate?": "pages/8_Model_Comparison.py",
    "What will renewed premium look like next?": "pages/9_Dynamic_Forecasting.py",
    "What should the business take away?": "pages/10_Business_Insights.py",
}

PAGE_BY_FILE = {p["file"]: p for p in PAGES}


# ============================================================
# HELPERS
# ============================================================

def page_exists(path):
    return os.path.exists(path)


@st.cache_data(show_spinner=False)
def load_insurer_data(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    df["collection_month"] = pd.to_datetime(
        df["collection_month"], errors="coerce"
    )

    for col in [
        "total_policies",
        "renewed_policies",
        "total_premium",
        "renewed_premium",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["collection_month"])


def safe_rate(numerator, denominator):
    return numerator / denominator * 100 if denominator > 0 else 0


def render_card(page):
    """One navigation card with an open button."""
    with st.container(border=True):
        st.markdown(f"### {page['icon']} {page['title']}")
        st.caption(page["desc"])

        if page_exists(page["file"]):
            st.page_link(
                page["file"],
                label="Open page",
                icon="➡️",
                use_container_width=True,
            )
        else:
            st.warning(f"File not found: `{page['file']}`")


def render_cards(pages, ncols=3):
    for i in range(0, len(pages), ncols):
        cols = st.columns(ncols)
        for col, page in zip(cols, pages[i:i + ncols]):
            with col:
                render_card(page)


# ============================================================
# HERO
# ============================================================

st.title("🛡️ Insurance Renewal Analytics & Forecasting")

st.markdown(
    """
    An interactive dashboard to **analyse renewal performance**, understand
    **trends and seasonality**, compare **forecasting models** and turn
    the results into **business insights**.
    """
)

st.divider()


# ============================================================
# LIVE SNAPSHOT (INTERACTIVE)
# ============================================================

st.subheader("⚡ Live Snapshot")

snapshot_ready = False

if not page_exists(INSURER_FILE):
    st.info(
        f"Snapshot unavailable — `{INSURER_FILE}` not found. "
        "The navigation below still works."
    )
else:
    try:
        data = load_insurer_data(INSURER_FILE)

        needed = {
            "collection_month",
            "insurer",
            "total_policies",
            "renewed_policies",
            "total_premium",
            "renewed_premium",
        }

        if not needed.issubset(data.columns):
            st.warning(
                f"Snapshot unavailable — missing columns: "
                f"{sorted(needed - set(data.columns))}"
            )
        elif data.empty:
            st.warning("Snapshot unavailable — the dataset is empty.")
        else:
            snapshot_ready = True

    except Exception as e:
        st.warning(f"Snapshot could not be loaded: {e}")


if snapshot_ready:

    # ---------------- Controls ----------------

    all_months = list(
        pd.to_datetime(sorted(data["collection_month"].unique()))
    )

    insurers = ["All Insurers"] + sorted(data["insurer"].dropna().unique())

    ctrl1, ctrl2, ctrl3 = st.columns([1.2, 1.2, 2])

    with ctrl1:
        snap_insurer = st.selectbox("Insurer", insurers, key="snap_insurer")

    with ctrl2:
        metric_choice = st.selectbox(
            "Metric",
            [
                "Renewal Rate (%)",
                "Renewed Premium (₹ Cr)",
                "Total Premium (₹ Cr)",
                "Renewed Policies",
                "Total Policies",
            ],
            key="snap_metric",
        )

    with ctrl3:
        if len(all_months) > 1:
            start_m, end_m = st.select_slider(
                "Period",
                options=all_months,
                value=(all_months[0], all_months[-1]),
                format_func=lambda d: d.strftime("%b %Y"),
                key="snap_period",
            )
        else:
            start_m, end_m = all_months[0], all_months[0]
            st.caption(f"Only one month available: {start_m.strftime('%b %Y')}")

    chart_type = st.radio(
        "Chart type",
        ["Line", "Bar", "Area"],
        horizontal=True,
        key="snap_chart_type",
    )

    # ---------------- Filter ----------------

    period_df = data[
        (data["collection_month"] >= start_m)
        & (data["collection_month"] <= end_m)
    ]

    if snap_insurer == "All Insurers":
        scope_df = period_df
    else:
        scope_df = period_df[period_df["insurer"] == snap_insurer]

    if scope_df.empty:
        st.warning("No data for the selected filters.")
    else:

        # ---------------- KPIs ----------------

        tp = scope_df["total_policies"].sum()
        rp = scope_df["renewed_policies"].sum()
        tprem = scope_df["total_premium"].sum()
        rprem = scope_df["renewed_premium"].sum()

        k1, k2, k3, k4, k5 = st.columns(5)

        k1.metric("Total Policies", f"{tp:,.0f}")
        k2.metric("Renewed Policies", f"{rp:,.0f}")
        k3.metric("Renewal Rate", f"{safe_rate(rp, tp):.2f}%")
        k4.metric("Total Premium", f"₹{tprem / 1e7:,.2f} Cr")
        k5.metric("Renewed Premium", f"₹{rprem / 1e7:,.2f} Cr")

        # ---------------- Trend chart ----------------

        monthly = (
            scope_df
            .groupby("collection_month")[
                [
                    "total_policies",
                    "renewed_policies",
                    "total_premium",
                    "renewed_premium",
                ]
            ]
            .sum()
            .sort_index()
        )

        monthly["renewal_rate"] = (
            monthly["renewed_policies"]
            / monthly["total_policies"].replace(0, np.nan)
            * 100
        )

        metric_map = {
            "Renewal Rate (%)": monthly["renewal_rate"],
            "Renewed Premium (₹ Cr)": monthly["renewed_premium"] / 1e7,
            "Total Premium (₹ Cr)": monthly["total_premium"] / 1e7,
            "Renewed Policies": monthly["renewed_policies"],
            "Total Policies": monthly["total_policies"],
        }

        series = metric_map[metric_choice].rename(metric_choice)

        st.markdown(
            f"**{metric_choice} — {snap_insurer}** "
            f"({start_m.strftime('%b %Y')} → {end_m.strftime('%b %Y')})"
        )

        if chart_type == "Line":
            st.line_chart(series)
        elif chart_type == "Bar":
            st.bar_chart(series)
        else:
            st.area_chart(series)

        # ---------------- Leaderboard ----------------

        with st.expander("🏆 Insurer leaderboard for this period", expanded=False):

            board = (
                period_df
                .groupby("insurer")
                .agg(
                    total_policies=("total_policies", "sum"),
                    renewed_policies=("renewed_policies", "sum"),
                    total_premium=("total_premium", "sum"),
                    renewed_premium=("renewed_premium", "sum"),
                )
                .reset_index()
            )

            board["renewal_rate"] = (
                board["renewed_policies"]
                / board["total_policies"].replace(0, np.nan)
                * 100
            )

            board = board.dropna(subset=["renewal_rate"]).sort_values(
                "renewal_rate", ascending=False
            )

            if board.empty:
                st.info("No leaderboard data available.")
            else:
                top = board.iloc[0]
                bottom = board.iloc[-1]

                b1, b2 = st.columns(2)

                with b1:
                    st.success(
                        f"**Best renewal rate:** {top['insurer']} "
                        f"({top['renewal_rate']:.2f}%)"
                    )

                with b2:
                    st.warning(
                        f"**Lowest renewal rate:** {bottom['insurer']} "
                        f"({bottom['renewal_rate']:.2f}%)"
                    )

                st.bar_chart(
                    board.set_index("insurer")["renewal_rate"]
                )

                show = board.copy()
                show["total_premium"] = show["total_premium"] / 1e7
                show["renewed_premium"] = show["renewed_premium"] / 1e7

                show = show.rename(
                    columns={
                        "insurer": "Insurer",
                        "total_policies": "Total Policies",
                        "renewed_policies": "Renewed Policies",
                        "total_premium": "Total Premium (₹ Cr)",
                        "renewed_premium": "Renewed Premium (₹ Cr)",
                        "renewal_rate": "Renewal Rate (%)",
                    }
                )

                st.dataframe(
                    show.round(2),
                    use_container_width=True,
                    hide_index=True,
                )

        # ---------------- Jump to insurer page ----------------

        if page_exists("pages/2_Insurer_Analysis.py"):
            st.page_link(
                "pages/2_Insurer_Analysis.py",
                label="Open detailed Insurer Analysis",
                icon="🏢",
            )

st.divider()


# ============================================================
# GUIDED NAVIGATION
# ============================================================

st.subheader("🧭 What do you want to find out?")

guided_col1, guided_col2 = st.columns([3, 1])

with guided_col1:
    question = st.selectbox(
        "Pick a question and I'll take you to the right page",
        list(GUIDED.keys()),
        key="guided_question",
    )

target_file = GUIDED[question]
target_page = PAGE_BY_FILE[target_file]

with guided_col2:
    st.write("")
    st.write("")
    if st.button(
        f"Go to {target_page['title']}",
        key="guided_go",
        use_container_width=True,
        type="primary",
    ):
        if page_exists(target_file):
            st.switch_page(target_file)
        else:
            st.error(f"File not found: `{target_file}`")

st.caption(f"{target_page['icon']} {target_page['desc']}")

st.divider()


# ============================================================
# PAGE EXPLORER (SEARCH + TABS)
# ============================================================

st.subheader("🗂️ Explore All Pages")

query = st.text_input(
    "Search pages",
    placeholder="e.g. forecast, region, MAPE, payment…",
    key="page_search",
).strip().lower()

if query:

    results = [
        p for p in PAGES
        if query in p["title"].lower()
        or query in p["desc"].lower()
        or query in p["keywords"].lower()
        or query in p["category"].lower()
    ]

    if results:
        st.caption(f"{len(results)} page(s) match “{query}”")
        render_cards(results)
    else:
        st.info("No pages match your search. Try another keyword.")

else:

    tabs = st.tabs(
        [f"{CATEGORY_ICONS[c]} {c}" for c in CATEGORIES]
    )

    for tab, category in zip(tabs, CATEGORIES):
        with tab:
            render_cards(
                [p for p in PAGES if p["category"] == category]
            )

st.divider()


# ============================================================
# WORKFLOW
# ============================================================

with st.expander("🔄 Suggested analysis workflow"):
    st.markdown(
        """
        1. **Overview** — understand the overall renewal picture.
        2. **Insurer / Payment / Policy Type / Region / Yearly** — find *where* renewals are strong or weak.
        3. **Time Series Analysis** — check trend, seasonality and stationarity.
        4. **Model Comparison** — see which forecasting model works best for each insurer.
        5. **Dynamic Forecasting** — generate forecasts with the chosen model.
        6. **Business Insights** — convert forecasts into actionable takeaways.
        """
    )


# ============================================================
# SYSTEM CHECK
# ============================================================

with st.expander("🛠️ System check (data & page files)"):

    left, right = st.columns(2)

    with left:
        st.markdown("**Data files**")
        for f in DATA_FILES:
            st.write(("✅ " if page_exists(f) else "❌ ") + f"`{f}`")

    with right:
        st.markdown("**Page files**")
        for p in PAGES:
            st.write(
                ("✅ " if page_exists(p["file"]) else "❌ ")
                + f"`{p['file']}`"
            )

