import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
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

st.title(" Dynamic Insurance Premium Forecasting")

st.divider()


# ============================================================
# FILE PATHS
# ============================================================

MONTHLY_INSURER_FILE = (
    "data/processed/monthly_by_insurer.csv"
)

MODEL_SELECTION_FILE = (
    "reports/final_model_selection.csv"
)


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

df = pd.read_csv(
    MONTHLY_INSURER_FILE
)

df.columns = (
    df.columns
    .str.strip()
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "collection_month",
    "insurer",
    "renewed_premium"
]


missing_columns = [
    col
    for col in required_columns
    if col not in df.columns
]


if missing_columns:

    st.error(
        f"Missing columns: {missing_columns}"
    )

    st.write(
        "Available columns:",
        df.columns.tolist()
    )

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
    [
        "insurer",
        "collection_month"
    ]
)


# ============================================================
# LOAD MODEL SELECTION
# ============================================================

model_selection = None

if os.path.exists(MODEL_SELECTION_FILE):

    model_selection = pd.read_csv(
        MODEL_SELECTION_FILE
    )

    model_selection.columns = (
        model_selection.columns
        .str.strip()
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(" Forecast Settings")


# ============================================================
# INSURER SELECTION
# ============================================================

insurers = sorted(
    df["insurer"].unique()
)


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

insurer_df = insurer_df.sort_values(
    "collection_month"
)


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

last_date = insurer_df[
    "collection_month"
].max()

first_date = insurer_df[
    "collection_month"
].min()


# ============================================================
# AUTO MODEL
# ============================================================

auto_model = None

if model_selection is not None:

    selection_columns = (
        model_selection.columns
        .tolist()
    )

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
            model_selection[
                insurer_column
            ] == selected_insurer
        ]

        if not matching.empty:

            auto_model = (
                matching.iloc[0][model_column]
            )


# ============================================================
# DISPLAY MODEL
# ============================================================

if selected_model == "Auto Select":

    if auto_model is not None:

        actual_model = str(
            auto_model
        )

    else:

        actual_model = "Naive"

else:

    actual_model = selected_model


# ============================================================
# CURRENT INFORMATION
# ============================================================

st.subheader("Forecast Configuration")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Insurer",
        selected_insurer
    )


with col2:

    st.metric(
        "Historical Months",
        len(insurer_df)
    )


with col3:

    st.metric(
        "Last Historical Month",
        last_date.strftime("%b %Y")
    )


with col4:

    st.metric(
        "Selected Model",
        actual_model
    )


# ============================================================
# FORECAST FUNCTION
# ============================================================

def generate_forecast(
    series,
    model_name,
    periods
):

    series = series.dropna()

    if len(series) < 2:

        raise ValueError(
            "Not enough historical observations."
        )


    # --------------------------------------------------------
    # NAIVE
    # --------------------------------------------------------

    if model_name.lower() == "naive":

        last_value = series.iloc[-1]

        forecast_values = np.repeat(
            last_value,
            periods
        )


    # --------------------------------------------------------
    # SEASONAL NAIVE
    # --------------------------------------------------------

    elif model_name.lower() == "seasonal naive":

        season_length = 12

        if len(series) < season_length:

            last_value = series.iloc[-1]

            forecast_values = np.repeat(
                last_value,
                periods
            )

        else:

            seasonal_values = (
                series.iloc[-season_length:]
                .values
            )

            forecast_values = np.array([
                seasonal_values[
                    i % season_length
                ]
                for i in range(periods)
            ])


    # --------------------------------------------------------
    # ARIMA
    # --------------------------------------------------------

    elif model_name.lower() == "arima":

        from statsmodels.tsa.arima.model import ARIMA

        model = ARIMA(
            series,
            order=(1, 1, 1)
        )

        fitted_model = model.fit()

        forecast_values = (
            fitted_model
            .forecast(
                steps=periods
            )
            .values
        )


    # --------------------------------------------------------
    # SARIMA
    # --------------------------------------------------------

    elif model_name.lower() == "sarima":

        from statsmodels.tsa.statespace.sarimax import SARIMAX

        model = SARIMAX(
            series,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 12),
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        fitted_model = model.fit(
            disp=False
        )

        forecast_values = (
            fitted_model
            .forecast(
                steps=periods
            )
            .values
        )


    # --------------------------------------------------------
    # PROPHET
    # --------------------------------------------------------

    elif model_name.lower() == "prophet":

        from prophet import Prophet

        prophet_df = pd.DataFrame({
            "ds": series.index,
            "y": series.values
        })

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False
        )

        model.fit(
            prophet_df
        )

        future = model.make_future_dataframe(
            periods=periods,
            freq="MS"
        )

        prediction = model.predict(
            future
        )

        forecast_values = (
            prediction["yhat"]
            .tail(periods)
            .values
        )


    else:

        raise ValueError(
            f"Unsupported model: {model_name}"
        )


    # --------------------------------------------------------
    # FUTURE DATES
    # --------------------------------------------------------

    future_dates = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=periods,
        freq="MS"
    )


    forecast_df = pd.DataFrame({
        "month": future_dates,
        "forecast_renewed_premium":
            forecast_values
    })


    return forecast_df


# ============================================================
# GENERATE BUTTON
# ============================================================

generate = st.button(
    " Generate Forecast",
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



        # ====================================================
        # FORECAST KPIs
        # ====================================================

        st.subheader(" Forecast Summary")


        total_forecast = (
            forecast_df[
                "forecast_renewed_premium"
            ].sum()
        )


        average_forecast = (
            forecast_df[
                "forecast_renewed_premium"
            ].mean()
        )


        minimum_forecast = (
            forecast_df[
                "forecast_renewed_premium"
            ].min()
        )


        maximum_forecast = (
            forecast_df[
                "forecast_renewed_premium"
            ].max()
        )


        c1, c2, c3, c4 = st.columns(4)


        with c1:

            st.metric(
                "Total Forecast",
                f"₹{total_forecast/1e7:.2f} Cr"
            )


        with c2:

            st.metric(
                "Average / Month",
                f"₹{average_forecast/1e7:.2f} Cr"
            )


        with c3:

            st.metric(
                "Minimum",
                f"₹{minimum_forecast/1e7:.2f} Cr"
            )


        with c4:

            st.metric(
                "Maximum",
                f"₹{maximum_forecast/1e7:.2f} Cr"
            )


        # ====================================================
        # HISTORICAL + FORECAST CHART
        # ====================================================

        st.subheader(
            " Historical vs Future Forecast"
        )


        fig, ax = plt.subplots(
            figsize=(14, 6)
        )


        # Historical

        ax.plot(
            ts.index,
            ts.values,
            label="Historical"
        )


        # Forecast

        ax.plot(
            forecast_df["month"],
            forecast_df[
                "forecast_renewed_premium"
            ],
            linestyle="--",
            marker="o",
            label="Forecast"
        )


        # Forecast starting line

        ax.axvline(
            last_date,
            linestyle=":"
        )


        ax.set_title(
            f"{selected_insurer} — "
            f"{actual_model} Forecast"
        )

        ax.set_xlabel(
            "Month"
        )

        ax.set_ylabel(
            "Renewed Premium"
        )

        ax.legend()

        ax.grid(
            alpha=0.3
        )


        st.pyplot(
            fig,
            clear_figure=True
        )


        # ====================================================
        # FORECAST TABLE
        # ====================================================

        st.subheader(
            " Monthly Forecast"
        )


        display_forecast = (
            forecast_df.copy()
        )


        display_forecast[
            "Forecast Premium (₹ Cr)"
        ] = (
            display_forecast[
                "forecast_renewed_premium"
            ] / 1e7
        ).round(2)


        display_forecast = (
            display_forecast[
                [
                    "month",
                    "Forecast Premium (₹ Cr)"
                ]
            ]
        )


        display_forecast[
            "month"
        ] = display_forecast[
            "month"
        ].dt.strftime(
            "%b %Y"
        )


        st.dataframe(
            display_forecast,
            use_container_width=True,
            hide_index=True
        )


        # ====================================================
        # MONTHLY FORECAST BAR CHART
        # ====================================================

        st.subheader(
            "Monthly Forecast"
        )


        bar_df = forecast_df.copy()

        bar_df["month"] = (
            bar_df["month"]
            .dt.strftime("%b %Y")
        )


        bar_df = bar_df.set_index(
            "month"
        )


        bar_df[
            "forecast_renewed_premium"
        ] = (
            bar_df[
                "forecast_renewed_premium"
            ] / 1e7
        )


        st.bar_chart(
            bar_df[
                "forecast_renewed_premium"
            ]
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

        st.error(
            "Forecast generation failed."
        )

        st.exception(e)