import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dynamic Forecasting",
    page_icon="🔮",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.title("🔮 Dynamic Insurance Premium Forecasting")

st.markdown(
    """
    Select an insurer, choose how many future months you want
    to forecast, and generate a dynamic renewal-premium forecast.
    """
)

st.divider()

# ============================================================
# FILE PATHS
# ============================================================

MONTHLY_INSURER_FILE = "data/processed/monthly_by_insurer.csv"
MODEL_SELECTION_FILE = "reports/final_model_selection.csv"

# ============================================================
# CHECK FILES
# ============================================================

if not os.path.exists(MONTHLY_INSURER_FILE):
    st.error(
        f"""
        Monthly insurer dataset not found:

        `{MONTHLY_INSURER_FILE}`
        """
    )
    st.stop()

if not os.path.exists(MODEL_SELECTION_FILE):
    st.warning(
        f"""
        Model selection file not found:

        `{MODEL_SELECTION_FILE}`

        Auto model selection will not be available.
        """
    )

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(MONTHLY_INSURER_FILE)
df.columns = df.columns.str.strip()

required_columns = [
    "collection_month",
    "insurer",
    "renewed_premium"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

# ============================================================
# DATA CLEANING
# ============================================================

df["collection_month"] = pd.to_datetime(
    df["collection_month"],
    errors="coerce"
)

df["renewed_premium"] = pd.to_numeric(
    df["renewed_premium"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "collection_month",
        "insurer",
        "renewed_premium"
    ]
)

df = df.sort_values(
    ["insurer", "collection_month"]
)

# ============================================================
# LOAD MODEL SELECTION
# ============================================================

model_selection = None

if os.path.exists(MODEL_SELECTION_FILE):
    model_selection = pd.read_csv(MODEL_SELECTION_FILE)
    model_selection.columns = model_selection.columns.str.strip()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Forecast Settings")

insurers = sorted(df["insurer"].unique())

selected_insurer = st.sidebar.selectbox(
    "Select Insurer",
    insurers
)

# ============================================================
# INSURER DATA
# ============================================================

insurer_df = df[
    df["insurer"] == selected_insurer
].copy()

insurer_df = insurer_df.sort_values("collection_month")

ts = insurer_df.set_index(
    "collection_month"
)["renewed_premium"]

# ============================================================
# FORECAST HORIZON
# ============================================================

forecast_months = st.sidebar.selectbox(
    "Forecast Horizon",
    [3, 6, 12, 18, 24],
    index=2
)

# ============================================================
# MODEL OPTIONS
# ============================================================

model_options = [
    "Auto Select",
    "Naive",
    "Seasonal Naive",
    "ARIMA",
    "SARIMA",
    "Prophet"
]

selected_model = st.sidebar.selectbox(
    "Forecasting Model",
    model_options
)

# ============================================================
# HISTORICAL INFORMATION
# ============================================================

last_date = insurer_df["collection_month"].max()
first_date = insurer_df["collection_month"].min()

# ============================================================
# AUTO MODEL
# ============================================================

auto_model = None

if model_selection is not None:
    selection_columns = model_selection.columns.tolist()

    insurer_column = None
    for col in selection_columns:
        if col.lower() == "insurer":
            insurer_column = col
            break

    model_column = None
    possible_model_columns = [
        "final_model",
        "best_model",
        "model",
        "Final Model",
        "Best Model"
    ]

    for col in possible_model_columns:
        if col in selection_columns:
            model_column = col
            break

    if (
        insurer_column is not None
        and model_column is not None
    ):
        matching = model_selection[
            model_selection[insurer_column] == selected_insurer
        ]

        if not matching.empty:
            auto_model = matching.iloc[0][model_column]

# ============================================================
# DISPLAY MODEL
# ============================================================

if selected_model == "Auto Select":
    if auto_model is not None:
        actual_model = str(auto_model)
    else:
        actual_model = "Naive"
else:
    actual_model = selected_model

# final_model_selection.csv may contain names produced by the
# model-comparison workflow. The dynamic page currently implements
# generic SARIMA/Prophet forecasting, so these names are normalized
# to the corresponding executable model.
model_aliases = {
    "Default Prophet": "Prophet",
    "Tuned Prophet": "Prophet",
    "Tuned SARIMA": "SARIMA"
}

actual_model = model_aliases.get(
    actual_model,
    actual_model
)

# ============================================================
# CURRENT INFORMATION
# ============================================================

st.subheader("📊 Forecast Configuration")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Insurer", selected_insurer)

with col2:
    st.metric("Historical Months", len(insurer_df))

with col3:
    st.metric(
        "Last Historical Month",
        last_date.strftime("%b %Y")
    )

with col4:
    st.metric("Selected Model", actual_model)

st.info(
    f"""
    Forecasting **{selected_insurer}** for the next
    **{forecast_months} months** using **{actual_model}**.
    """
)

# ============================================================
# FORECAST FUNCTION
# ============================================================

def generate_forecast(series, model_name, periods):
    """Generate forecast plus 80% and 95% uncertainty intervals."""

    series = series.dropna()

    if len(series) < 2:
        raise ValueError("Not enough historical observations.")

    model_key = str(model_name).strip().lower()

    # All model branches return the same interval columns.
    lower_80 = None
    upper_80 = None
    lower_95 = None
    upper_95 = None

    # --------------------------------------------------------
    # NAIVE
    # --------------------------------------------------------

    if model_key == "naive":
        last_value = float(series.iloc[-1])

        forecast_values = np.repeat(
            last_value,
            periods
        )

        # Historical one-step-ahead errors provide empirical
        # forecast-error distributions for the intervals.
        errors = (
            series.iloc[1:].values
            - series.iloc[:-1].values
        )

        q10, q90 = np.quantile(errors, [0.10, 0.90])
        q025, q975 = np.quantile(errors, [0.025, 0.975])

        lower_80 = np.maximum(0, forecast_values + q10)
        upper_80 = np.maximum(0, forecast_values + q90)
        lower_95 = np.maximum(0, forecast_values + q025)
        upper_95 = np.maximum(0, forecast_values + q975)

    # --------------------------------------------------------
    # SEASONAL NAIVE
    # --------------------------------------------------------

    elif model_key == "seasonal naive":
        season_length = 12

        if len(series) < season_length:
            # Not enough observations for a 12-month seasonal pattern.
            # Use Naive-style forecasting and errors as fallback.
            last_value = float(series.iloc[-1])
            forecast_values = np.repeat(
                last_value,
                periods
            )

            errors = (
                series.iloc[1:].values
                - series.iloc[:-1].values
            )
        else:
            seasonal_values = (
                series.iloc[-season_length:].values
            )

            forecast_values = np.array([
                seasonal_values[i % season_length]
                for i in range(periods)
            ])

            # Historical 12-month seasonal forecast errors.
            errors = (
                series.iloc[season_length:].values
                - series.iloc[:-season_length].values
            )

        q10, q90 = np.quantile(errors, [0.10, 0.90])
        q025, q975 = np.quantile(errors, [0.025, 0.975])

        lower_80 = np.maximum(0, forecast_values + q10)
        upper_80 = np.maximum(0, forecast_values + q90)
        lower_95 = np.maximum(0, forecast_values + q025)
        upper_95 = np.maximum(0, forecast_values + q975)

    # --------------------------------------------------------
    # ARIMA
    # --------------------------------------------------------

    elif model_key == "arima":
        from statsmodels.tsa.arima.model import ARIMA

        model = ARIMA(
            series,
            order=(1, 1, 1)
        )

        fitted_model = model.fit()

        forecast_result = fitted_model.get_forecast(
            steps=periods
        )

        forecast_values = (
            forecast_result.predicted_mean.values
        )

        conf_80 = forecast_result.conf_int(alpha=0.20)
        conf_95 = forecast_result.conf_int(alpha=0.05)

        lower_80 = np.maximum(
            0, conf_80.iloc[:, 0].values
        )
        upper_80 = np.maximum(
            0, conf_80.iloc[:, 1].values
        )
        lower_95 = np.maximum(
            0, conf_95.iloc[:, 0].values
        )
        upper_95 = np.maximum(
            0, conf_95.iloc[:, 1].values
        )

    # --------------------------------------------------------
    # SARIMA
    # --------------------------------------------------------

    elif model_key == "sarima":
        from statsmodels.tsa.statespace.sarimax import SARIMAX

        model = SARIMAX(
            series,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 12),
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        fitted_model = model.fit(disp=False)

        forecast_result = fitted_model.get_forecast(
            steps=periods
        )

        forecast_values = (
            forecast_result.predicted_mean.values
        )

        conf_80 = forecast_result.conf_int(alpha=0.20)
        conf_95 = forecast_result.conf_int(alpha=0.05)

        lower_80 = np.maximum(
            0, conf_80.iloc[:, 0].values
        )
        upper_80 = np.maximum(
            0, conf_80.iloc[:, 1].values
        )
        lower_95 = np.maximum(
            0, conf_95.iloc[:, 0].values
        )
        upper_95 = np.maximum(
            0, conf_95.iloc[:, 1].values
        )

    # --------------------------------------------------------
    # PROPHET
    # --------------------------------------------------------

    elif model_key == "prophet":
        from prophet import Prophet

        prophet_df = pd.DataFrame({
            "ds": series.index,
            "y": series.values
        })

        # Prophet's interval_width controls the uncertainty interval.
        # Two fits are used so both requested interval levels come
        # directly from Prophet rather than being manually invented.
        model_80 = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            interval_width=0.80
        )

        model_80.fit(prophet_df)

        future = model_80.make_future_dataframe(
            periods=periods,
            freq="MS"
        )

        prediction_80 = model_80.predict(future)

        model_95 = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            interval_width=0.95
        )

        model_95.fit(prophet_df)
        prediction_95 = model_95.predict(future)

        forecast_values = (
            prediction_95["yhat"]
            .tail(periods)
            .values
        )

        lower_80 = np.maximum(
            0,
            prediction_80["yhat_lower"]
            .tail(periods)
            .values
        )
        upper_80 = np.maximum(
            0,
            prediction_80["yhat_upper"]
            .tail(periods)
            .values
        )
        lower_95 = np.maximum(
            0,
            prediction_95["yhat_lower"]
            .tail(periods)
            .values
        )
        upper_95 = np.maximum(
            0,
            prediction_95["yhat_upper"]
            .tail(periods)
            .values
        )

    else:
        raise ValueError(
            f"Unsupported model: {model_name}"
        )

    # --------------------------------------------------------
    # FUTURE DATES + OUTPUT
    # --------------------------------------------------------

    last_date = pd.to_datetime(series.index.max())

    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=periods,
        freq="MS"
    )

    forecast_df = pd.DataFrame({
        "month": future_dates,
        "forecast_renewed_premium": forecast_values,
        "lower_80": lower_80,
        "upper_80": upper_80,
        "lower_95": lower_95,
        "upper_95": upper_95
    })

    return forecast_df

# ============================================================
# GENERATE BUTTON
# ============================================================

generate = st.button(
    "🚀 Generate Forecast",
    type="primary",
    use_container_width=True
)

# ============================================================
# FORECAST
# ============================================================

if generate:
    try:
        with st.spinner(
            "Training model and generating forecast..."
        ):
            forecast_df = generate_forecast(
                ts,
                actual_model,
                forecast_months
            )

        st.success(
            f"""
            Forecast successfully generated for
            **{selected_insurer}**.
            """
        )

        # ====================================================
        # FORECAST KPIs
        # ====================================================

        st.subheader("📈 Forecast Summary")

        total_forecast = forecast_df[
            "forecast_renewed_premium"
        ].sum()

        average_forecast = forecast_df[
            "forecast_renewed_premium"
        ].mean()

        minimum_forecast = forecast_df[
            "forecast_renewed_premium"
        ].min()

        maximum_forecast = forecast_df[
            "forecast_renewed_premium"
        ].max()

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Total Forecast",
                f"₹{total_forecast / 1e7:.2f} Cr"
            )

        with c2:
            st.metric(
                "Average / Month",
                f"₹{average_forecast / 1e7:.2f} Cr"
            )

        with c3:
            st.metric(
                "Minimum",
                f"₹{minimum_forecast / 1e7:.2f} Cr"
            )

        with c4:
            st.metric(
                "Maximum",
                f"₹{maximum_forecast / 1e7:.2f} Cr"
            )

        # ====================================================
        # HISTORICAL + FORECAST CHART
        # ====================================================

        st.subheader("📉 Historical vs Future Forecast")

        fig, ax = plt.subplots(figsize=(14, 6))

        # Historical
        ax.plot(
            ts.index,
            ts.values,
            label="Historical"
        )

        # Forecast
        ax.plot(
            forecast_df["month"],
            forecast_df["forecast_renewed_premium"],
            linestyle="--",
            marker="o",
            label="Forecast"
        )

        # 95% uncertainty interval
        ax.fill_between(
            forecast_df["month"],
            forecast_df["lower_95"],
            forecast_df["upper_95"],
            alpha=0.12,
            label="95% Interval"
        )

        # 80% uncertainty interval
        ax.fill_between(
            forecast_df["month"],
            forecast_df["lower_80"],
            forecast_df["upper_80"],
            alpha=0.22,
            label="80% Interval"
        )

        # Forecast starting line
        ax.axvline(
            last_date,
            linestyle=":"
        )

        ax.set_title(
            f"{selected_insurer} — {actual_model} Forecast"
        )

        ax.set_xlabel("Month")
        ax.set_ylabel("Renewed Premium")
        ax.legend()
        ax.grid(alpha=0.3)

        st.pyplot(
            fig,
            clear_figure=True
        )

        # ====================================================
        # FORECAST TABLE
        # ====================================================

        st.subheader("📋 Monthly Forecast")

        display_forecast = forecast_df.copy()

        display_forecast[
            "Forecast Premium (₹ Cr)"
        ] = (
            display_forecast["forecast_renewed_premium"] / 1e7
        ).round(2)

        display_forecast[
            "80% Lower (₹ Cr)"
        ] = (
            display_forecast["lower_80"] / 1e7
        ).round(2)

        display_forecast[
            "80% Upper (₹ Cr)"
        ] = (
            display_forecast["upper_80"] / 1e7
        ).round(2)

        display_forecast[
            "95% Lower (₹ Cr)"
        ] = (
            display_forecast["lower_95"] / 1e7
        ).round(2)

        display_forecast[
            "95% Upper (₹ Cr)"
        ] = (
            display_forecast["upper_95"] / 1e7
        ).round(2)

        display_forecast = display_forecast[
            [
                "month",
                "Forecast Premium (₹ Cr)",
                "80% Lower (₹ Cr)",
                "80% Upper (₹ Cr)",
                "95% Lower (₹ Cr)",
                "95% Upper (₹ Cr)"
            ]
        ]

        display_forecast["month"] = (
            display_forecast["month"].dt.strftime("%b %Y")
        )

        st.dataframe(
            display_forecast,
            use_container_width=True,
            hide_index=True
        )

        # ====================================================
        # MONTHLY FORECAST BAR CHART
        # ====================================================

        st.subheader("📊 Monthly Forecast")

        bar_df = forecast_df.copy()
        bar_df["month"] = bar_df["month"].dt.strftime("%b %Y")
        bar_df = bar_df.set_index("month")
        bar_df["forecast_renewed_premium"] = (
            bar_df["forecast_renewed_premium"] / 1e7
        )

        st.bar_chart(
            bar_df["forecast_renewed_premium"]
        )

        # ====================================================
        # DOWNLOAD
        # ====================================================

        csv_data = forecast_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇️ Download Forecast CSV",
            data=csv_data,
            file_name=(
                f"{selected_insurer}_"
                f"{forecast_months}_month_forecast.csv"
            ),
            mime="text/csv"
        )

    except Exception as e:
        st.error("Forecast generation failed.")
        st.exception(e)
