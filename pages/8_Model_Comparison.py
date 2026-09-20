import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Model Comparison",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title(
    "🤖 Forecasting Model Comparison"
)

st.markdown(
    """
    Compare the forecasting performance of different
    time-series models across insurers using MAPE,
    WAPE, MAE, RMSE and Bias.
    """
)

st.divider()


# ============================================================
# DATA PATH
# ============================================================

DATA_FILE = (
    "reports/"
    "all_insurers_all_models_comparison.csv"
)


if not os.path.exists(DATA_FILE):

    st.error(
        f"Model comparison file not found:\n\n"
        f"`{DATA_FILE}`"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    DATA_FILE
)

df.columns = (
    df.columns
    .str.strip()
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [

    "Insurer",

    "Model",

    "MAE",

    "RMSE",

    "WAPE",

    "Bias",

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

for col in [

    "MAE",

    "RMSE",

    "WAPE",

    "Bias",

    "MAPE"

]:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


df = df.dropna(
    subset=[
        "WAPE",
        "MAE",
        "RMSE",
        "Bias"
    ]
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "🔎 Comparison Filters"
)


insurers = sorted(
    df["Insurer"]
    .dropna()
    .unique()
)


selected_insurer = (
    st.sidebar.selectbox(
        "Select Insurer",
        ["All Insurers"] + insurers
    )
)


models = sorted(
    df["Model"]
    .dropna()
    .unique()
)


selected_models = (
    st.sidebar.multiselect(
        "Select Models",
        models,
        default=models
    )
)


metric = st.sidebar.selectbox(
    "Performance Metric",
    [
        "MAPE",
        "WAPE",
        "MAE",
        "RMSE",
        "Bias"
    ]
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

st.subheader(
    "📊 Model Performance Overview"
)


col1, col2, col3, col4 = (
    st.columns(4)
)


if metric == "Bias":
    best_row = filtered_df.loc[
        filtered_df["Bias"].abs().idxmin()
    ]
    metric_label = "Closest Bias to Zero"
else:
    best_row = filtered_df.loc[
        filtered_df[metric].idxmin()
    ]
    metric_label = f"Lowest {metric}"


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
        metric_label,
        f"{best_row[metric]:.2f}"
    )


with col4:

    st.metric(
        "Best Model",
        best_row["Model"]
    )


st.divider()

# ============================================================
# BACKTESTING METHODOLOGY
# ============================================================

st.subheader(
    "🧪 Time-Ordered Backtesting"
)

st.markdown(
    """
    The forecasting models are evaluated using a
    **time-ordered 24 / 12 / 12 split**.

    Historical observations are kept in chronological order.
    No random train-test shuffling is used.
    """
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Training Period",
        "24 Months"
    )

    st.caption(
        "Used to train the forecasting model."
    )


with col2:

    st.metric(
        "Validation Period",
        "12 Months"
    )

    st.caption(
        "Used for model / hyperparameter selection."
    )


with col3:

    st.metric(
        "Test Period",
        "12 Months"
    )

    st.caption(
        "Held-out period used for final evaluation."
    )


st.info(
    """
    **Evaluation flow**

    Historical Data → 24-month Training
    → 12-month Validation
    → 12-month Test
    → Forecast Test Period
    → Compare Actual vs Predicted
    → Calculate MAE, RMSE, WAPE, Bias and MAPE.
    """
)


st.markdown(
    """
    ### Why time-ordered validation?

    For time-series forecasting, future observations should
    not be used to train a model before they occur.

    Therefore, the project keeps earlier months for training
    and later months for validation and testing.
    """
)


st.divider()

# ============================================================
# INSURER-WISE COMPARISON
# ============================================================

st.subheader(
    f"📈 {metric} Comparison by Insurer"
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
    f"📊 {metric} by Model"
)


if selected_insurer != "All Insurers":

    chart_df = (
        filtered_df[
            ["Model", metric]
        ]
        .set_index("Model")
    )

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
# WAPE COMPARISON
# ============================================================

st.subheader(
    "📊 WAPE Comparison"
)


wape_df = filtered_df.pivot_table(

    index="Insurer",

    columns="Model",

    values="WAPE",

    aggfunc="mean"
)


st.bar_chart(
    wape_df
)


# ============================================================
# MAPE COMPARISON
# ============================================================

st.subheader(
    "📊 MAPE Comparison"
)


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

st.subheader(
    "🏆 Best Model by Insurer"
)


# Keep the project's existing MAPE-based
# model-selection methodology here.

best_models = (
    df.loc[
        df.groupby("Insurer")["MAPE"]
        .idxmin()
    ][
        [
            "Insurer",
            "Model",
            "MAPE",
            "WAPE",
            "Bias",
            "MAE",
            "RMSE"
        ]
    ]
    .sort_values("MAPE")
)


best_models = best_models.rename(
    columns={

        "Model":
            "Best Model",

        "MAPE":
            "Test MAPE (%)",

        "WAPE":
            "Test WAPE (%)"
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

st.subheader(
    "📊 Average Performance by Model"
)


model_summary = (

    df.groupby("Model")

    .agg(

        Average_MAE=(
            "MAE",
            "mean"
        ),

        Average_RMSE=(
            "RMSE",
            "mean"
        ),

        Average_WAPE=(
            "WAPE",
            "mean"
        ),

        Average_Bias=(
            "Bias",
            "mean"
        ),

        Average_MAPE=(
            "MAPE",
            "mean"
        )
    )

    .sort_values(
        "Average_MAPE"
    )
)


model_summary = model_summary.rename(
    columns={

        "Average_MAE":
            "Average MAE",

        "Average_RMSE":
            "Average RMSE",

        "Average_WAPE":
            "Average WAPE (%)",

        "Average_Bias":
            "Average Bias",

        "Average_MAPE":
            "Average MAPE (%)"
    }
)


st.dataframe(
    model_summary.round(4),
    use_container_width=True
)


# ============================================================
# AVERAGE WAPE
# ============================================================

st.subheader(
    "📉 Average WAPE by Model"
)


avg_wape = (

    df.groupby("Model")["WAPE"]

    .mean()

    .sort_values()
)


st.bar_chart(
    avg_wape
)


# ============================================================
# AVERAGE MAPE
# ============================================================

st.subheader(
    "📉 Average MAPE by Model"
)


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


st.subheader(
    "📄 Detailed Model Results"
)


display_df = filtered_df.copy()


display_df = display_df.sort_values(
    [
        "Insurer",
        "MAPE"
    ]
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD
# ============================================================

csv_data = (
    filtered_df
    .to_csv(index=False)
    .encode("utf-8")
)


st.download_button(

    label="⬇️ Download Model Comparison",

    data=csv_data,

    file_name="model_comparison.csv",

    mime="text/csv"
)


# ============================================================
# EXPLANATION
# ============================================================

st.divider()


st.subheader(
    "🧠 How to Read This Page"
)


st.markdown(
    """
    ### MAPE

    **Mean Absolute Percentage Error**

    Measures average percentage error.
    Lower values indicate smaller percentage errors.

    ### WAPE

    **Weighted Absolute Percentage Error**

    Measures total absolute forecasting error
    relative to total actual values.

    ### MAE

    **Mean Absolute Error**

    Measures the average absolute forecasting error.

    ### RMSE

    **Root Mean Squared Error**

    Gives greater importance to larger forecasting errors.

    ### Bias

    Measures the average signed forecasting error.

    Positive Bias indicates over-forecasting.
    Negative Bias indicates under-forecasting.

    ### Models

    - **Naive** — uses the latest observed value.
    - **Seasonal Naive** — uses the corresponding value
      from the previous seasonal cycle.
    - **ARIMA** — models autoregression, differencing
      and moving-average behavior.
    - **SARIMA** — extends ARIMA with seasonal components.
    - **Prophet** — models trend and seasonality using
      a decomposable forecasting approach.

    The project compares models separately for each
    insurer because different insurers can have
    different time-series behavior.
    """
)