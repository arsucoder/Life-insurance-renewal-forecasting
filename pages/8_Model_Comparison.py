import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Model Comparison",
    page_icon="",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("Forecasting Model Comparison")

st.divider()


# ============================================================
# DATA PATH
# ============================================================

DATA_FILE = "reports/all_insurers_all_models_comparison.csv"


if not os.path.exists(DATA_FILE):

    st.error(
        f"Model comparison file not found:\n\n`{DATA_FILE}`"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_FILE)

df.columns = df.columns.str.strip()


# ============================================================
# SHOW COLUMNS
# ============================================================

required_columns = [
    "Insurer",
    "Model",
    "MAE",
    "RMSE",
    "MAPE"
]


missing = [
    col
    for col in required_columns
    if col not in df.columns
]


if missing:

    st.error(
        f"Missing columns: {missing}"
    )

    st.write(
        "Available columns:",
        df.columns.tolist()
    )

    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

for col in ["MAE", "RMSE", "MAPE"]:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


df = df.dropna(
    subset=["MAPE"]
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Comparison Filters")


insurers = sorted(
    df["Insurer"].dropna().unique()
)


selected_insurer = st.sidebar.selectbox(
    "Select Insurer",
    ["All Insurers"] + insurers
)


models = sorted(
    df["Model"].dropna().unique()
)


selected_models = st.sidebar.multiselect(
    "Select Models",
    models,
    default=models
)


metric = st.sidebar.selectbox(
    "Performance Metric",
    ["MAPE", "MAE", "RMSE"]
)


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df.copy()


if selected_insurer != "All Insurers":

    filtered_df = filtered_df[
        filtered_df["Insurer"]
        == selected_insurer
    ]


if selected_models:

    filtered_df = filtered_df[
        filtered_df["Model"].isin(
            selected_models
        )
    ]


if filtered_df.empty:

    st.warning(
        "No data available for the selected filters."
    )

    st.stop()


# ============================================================
# KPI SECTION
# ============================================================

st.subheader("Model Performance Overview")


col1, col2, col3, col4 = st.columns(4)


best_row = filtered_df.loc[
    filtered_df[metric].idxmin()
]


with col1:

    st.metric(
        "Models Compared",
        filtered_df["Model"].nunique()
    )


with col2:

    st.metric(
        "Insurers Compared",
        filtered_df["Insurer"].nunique()
    )


with col3:

    st.metric(
        f"Lowest {metric}",
        f"{best_row[metric]:.2f}"
    )


with col4:

    st.metric(
        "Best Model",
        best_row["Model"]
    )


st.divider()


# ============================================================
# INSURER-WISE COMPARISON
# ============================================================

st.subheader(
    f"{metric} Comparison by Insurer"
)


pivot_df = filtered_df.pivot_table(
    index="Insurer",
    columns="Model",
    values=metric,
    aggfunc="mean"
)


st.line_chart(
    pivot_df
)


# ============================================================
# BAR CHART
# ============================================================

st.subheader(
    f"{metric} by Model"
)


if selected_insurer != "All Insurers":

    chart_df = filtered_df[
        ["Model", metric]
    ].set_index("Model")

    st.bar_chart(
        chart_df
    )

else:

    model_avg = (
        filtered_df
        .groupby("Model")[metric]
        .mean()
        .sort_values()
    )

    st.bar_chart(
        model_avg
    )


# ============================================================
# MAPE COMPARISON
# ============================================================

st.subheader("MAPE Comparison")

mape_df = filtered_df.pivot_table(
    index="Insurer",
    columns="Model",
    values="MAPE",
    aggfunc="mean"
)


st.bar_chart(
    mape_df
)


# ============================================================
# BEST MODEL PER INSURER
# ============================================================

st.subheader("Best Model by Insurer")


best_models = (
    df.loc[
        df.groupby("Insurer")["MAPE"]
        .idxmin()
    ]
    [
        [
            "Insurer",
            "Model",
            "MAPE",
            "MAE",
            "RMSE"
        ]
    ]
    .sort_values("MAPE")
)


best_models = best_models.rename(
    columns={
        "Insurer": "Insurer",
        "Model": "Best Model",
        "MAPE": "Test MAPE (%)",
        "MAE": "MAE",
        "RMSE": "RMSE"
    }
)


st.dataframe(
    best_models,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# MODEL-WISE AVERAGE
# ============================================================

st.subheader("Average Performance by Model")


model_summary = (
    df.groupby("Model")
    .agg(
        Average_MAE=("MAE", "mean"),
        Average_RMSE=("RMSE", "mean"),
        Average_MAPE=("MAPE", "mean")
    )
    .sort_values("Average_MAPE")
)


model_summary = model_summary.rename(
    columns={
        "Average_MAE": "Average MAE",
        "Average_RMSE": "Average RMSE",
        "Average_MAPE": "Average MAPE (%)"
    }
)


st.dataframe(
    model_summary.round(4),
    use_container_width=True
)


# ============================================================
# MODEL MAPE CHART
# ============================================================

st.subheader("Average MAPE by Model")


avg_mape = (
    df.groupby("Model")["MAPE"]
    .mean()
    .sort_values()
)


st.bar_chart(
    avg_mape
)


# ============================================================
# DETAILED RESULTS
# ============================================================

st.divider()

st.subheader(" Detailed Model Results")


display_df = filtered_df.copy()


display_df = display_df.sort_values(
    ["Insurer", "MAPE"]
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD
# ============================================================

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Model Comparison",
    data=csv_data,
    file_name="model_comparison.csv",
    mime="text/csv"
)

