# ================================================================
# FINAL INSURER FORECASTING
# ================================================================
# Purpose:
#   Retrain the selected final model for each insurer using all
#   available historical data and generate the next 12 months.
#
# Input:
#   data/processed/monthly_by_insurer.csv
#
# Outputs:
#   reports/final_insurer_forecasts.csv
#   reports/final_model_selection.csv
# ================================================================

import os
import warnings

import numpy as np
import pandas as pd

from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

warnings.filterwarnings("ignore")


# ================================================================
# CONFIGURATION
# ================================================================

INPUT_FILE = "./data/processed/monthly_by_insurer.csv"

FORECAST_FILE = "./reports/final_insurer_forecasts.csv"
MODEL_FILE = "./reports/final_model_selection.csv"

FORECAST_MONTHS = 12

TARGET = "renewed_premium"


# ================================================================
# FINAL MODEL SELECTION
# ================================================================
# Based on our completed all-model test comparison.

FINAL_MODELS = {
    "Aditya Birla Sun Life": "ARIMA",
    "Bajaj Allianz": "Naive",
    "HDFC Life": "ARIMA",
    "ICICI Prudential": "Seasonal Naive",
    "LIC": "Default Prophet",
    "Max Life": "Naive",
    "SBI Life": "Seasonal Naive",
    "Tata AIA": "Naive"
}


# ================================================================
# CREATE REPORTS DIRECTORY
# ================================================================

os.makedirs("./reports", exist_ok=True)


# ================================================================
# LOAD DATA
# ================================================================

print("=" * 80)
print("LOADING DATA")
print("=" * 80)

df = pd.read_csv(INPUT_FILE)

print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())


# ================================================================
# DATE PREPARATION
# ================================================================

df["collection_month"] = pd.to_datetime(
    df["collection_month"]
)

df = df.sort_values(
    ["insurer", "collection_month"]
)


# ================================================================
# CHECK INSURERS
# ================================================================

insurers = sorted(df["insurer"].unique())

print("\nInsurers:")
for insurer in insurers:
    print("-", insurer)


# ================================================================
# STORE RESULTS
# ================================================================

all_forecasts = []

model_selection = []


# ================================================================
# FORECAST FUNCTION
# ================================================================

def generate_forecast(series, model_name):

    series = series.astype(float)

    last_date = series.index.max()

    future_dates = pd.date_range(
        start=last_date + pd.offsets.MonthBegin(1),
        periods=FORECAST_MONTHS,
        freq="MS"
    )

    # ------------------------------------------------------------
    # NAIVE
    # ------------------------------------------------------------

    if model_name == "Naive":

        last_value = series.iloc[-1]

        predictions = np.repeat(
            last_value,
            FORECAST_MONTHS
        )

    # ------------------------------------------------------------
    # SEASONAL NAIVE
    # ------------------------------------------------------------

    elif model_name == "Seasonal Naive":

        if len(series) < 12:
            raise ValueError(
                "At least 12 observations are required "
                "for Seasonal Naive."
            )

        last_12 = series.iloc[-12:].values

        predictions = np.tile(
            last_12,
            int(np.ceil(FORECAST_MONTHS / 12))
        )[:FORECAST_MONTHS]

    # ------------------------------------------------------------
    # ARIMA
    # ------------------------------------------------------------

    elif model_name == "ARIMA":

        print("    Fitting ARIMA(1,1,1)...")

        model = ARIMA(
            series,
            order=(1, 1, 1)
        )

        fitted_model = model.fit()

        predictions = fitted_model.forecast(
            steps=FORECAST_MONTHS
        )

        predictions = np.asarray(predictions)

    # ------------------------------------------------------------
    # DEFAULT PROPHET
    # ------------------------------------------------------------

    elif model_name == "Default Prophet":

        print("    Fitting Default Prophet...")

        prophet_df = pd.DataFrame({
            "ds": series.index,
            "y": series.values
        })

        model = Prophet(
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10,
            seasonality_mode="additive",
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False
        )

        model.fit(prophet_df)

        future = model.make_future_dataframe(
            periods=FORECAST_MONTHS,
            freq="MS",
            include_history=False
        )

        forecast = model.predict(future)

        predictions = forecast["yhat"].values

    else:

        raise ValueError(
            f"Unknown model: {model_name}"
        )

    return future_dates, predictions


# ================================================================
# PROCESS EACH INSURER
# ================================================================

print("\n" + "=" * 80)
print("STARTING FINAL 12-MONTH FORECAST")
print("=" * 80)


for insurer in insurers:

    print("\n" + "#" * 70)
    print("INSURER:", insurer)
    print("#" * 70)

    insurer_df = df[
        df["insurer"] == insurer
    ].copy()

    insurer_df = insurer_df.sort_values(
        "collection_month"
    )

    # ------------------------------------------------------------
    # CREATE TIME SERIES
    # ------------------------------------------------------------

    series = insurer_df.set_index(
        "collection_month"
    )[TARGET]

    series = series.asfreq("MS")

    # ------------------------------------------------------------
    # CHECK MISSING VALUES
    # ------------------------------------------------------------

    if series.isna().any():

        print(
            "WARNING: Missing values found. "
            "Interpolating..."
        )

        series = series.interpolate(
            method="linear"
        )

    # ------------------------------------------------------------
    # MODEL
    # ------------------------------------------------------------

    model_name = FINAL_MODELS.get(insurer)

    if model_name is None:

        print(
            "WARNING: No final model configured."
        )

        continue

    print("Observations:", len(series))
    print("Historical period:")
    print(series.index.min(), "to", series.index.max())

    print("Selected final model:", model_name)

    # ------------------------------------------------------------
    # GENERATE FORECAST
    # ------------------------------------------------------------

    future_dates, predictions = generate_forecast(
        series,
        model_name
    )

    # ------------------------------------------------------------
    # CREATE OUTPUT
    # ------------------------------------------------------------

    forecast_df = pd.DataFrame({

        "month": future_dates,

        "insurer": insurer,

        "model": model_name,

        "forecast_renewed_premium": predictions

    })

    # Avoid negative premium forecasts

    forecast_df[
        "forecast_renewed_premium"
    ] = forecast_df[
        "forecast_renewed_premium"
    ].clip(lower=0)

    # ------------------------------------------------------------
    # ADD TO MASTER RESULT
    # ------------------------------------------------------------

    all_forecasts.append(
        forecast_df
    )

    # ------------------------------------------------------------
    # MODEL INFORMATION
    # ------------------------------------------------------------

    model_selection.append({

        "insurer": insurer,

        "final_model": model_name,

        "historical_start":
            series.index.min(),

        "historical_end":
            series.index.max(),

        "historical_observations":
            len(series),

        "forecast_months":
            FORECAST_MONTHS

    })

    print("\nForecast generated:")
    print(forecast_df.to_string(index=False))


# ================================================================
# COMBINE ALL FORECASTS
# ================================================================

final_forecasts = pd.concat(
    all_forecasts,
    ignore_index=True
)

final_model_df = pd.DataFrame(
    model_selection
)


# ================================================================
# FORMAT DATES
# ================================================================

final_forecasts["month"] = pd.to_datetime(
    final_forecasts["month"]
).dt.strftime("%Y-%m-%d")


# ================================================================
# SAVE FILES
# ================================================================

final_forecasts.to_csv(
    FORECAST_FILE,
    index=False
)

final_model_df.to_csv(
    MODEL_FILE,
    index=False
)


# ================================================================
# DISPLAY SUMMARY
# ================================================================

print("\n")
print("=" * 80)
print("FINAL FORECAST SUMMARY")
print("=" * 80)

print(
    final_model_df[
        [
            "insurer",
            "final_model",
            "historical_observations",
            "forecast_months"
        ]
    ].to_string(index=False)
)


# ================================================================
# FORECAST SUMMARY BY INSURER
# ================================================================

print("\n")
print("=" * 80)
print("12-MONTH FORECAST SUMMARY")
print("=" * 80)

summary = (
    final_forecasts
    .groupby("insurer")
    ["forecast_renewed_premium"]
    .agg(
        total_forecast="sum",
        average_monthly_forecast="mean",
        minimum_forecast="min",
        maximum_forecast="max"
    )
    .reset_index()
)

print(
    summary.to_string(index=False)
)


# ================================================================
# COMPLETED
# ================================================================

print("\n")
print("=" * 80)
print("FINAL FORECASTING COMPLETED")
print("=" * 80)

print("\nFiles saved:")

print(
    FORECAST_FILE
)

print(
    MODEL_FILE
)