import pandas as pd
import numpy as np

from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet


def load_data():

    df = pd.read_csv(
        "./data/processed/monthly_by_insurer.csv"
    )

    df["collection_month"] = pd.to_datetime(
        df["collection_month"]
    )

    return df


def forecast_insurer(
    insurer,
    months=12,
    model_name="Auto Select"
):

    df = load_data()

    # -----------------------------
    # Filter insurer
    # -----------------------------

    data = df[df["insurer"] == insurer].copy()

    data = data.sort_values("collection_month")

    if len(data) == 0:
        raise ValueError(
            f"No data found for {insurer}"
        )

    # -----------------------------
    # Time series
    # -----------------------------

    ts = data[
        ["collection_month", "renewed_premium"]
    ].copy()

    ts = ts.rename(
        columns={
            "collection_month": "ds",
            "renewed_premium": "y"
        }
    )

    ts = ts.sort_values("ds")

    # -----------------------------
    # Auto model selection
    # -----------------------------

    if model_name == "Auto Select":

        # Your final model selection
        # from previous model comparison

        final_models = {

            "Aditya Birla Sun Life": "ARIMA",

            "Bajaj Allianz": "Naive",

            "HDFC Life": "ARIMA",

            "ICICI Prudential": "Seasonal Naive",

            "LIC": "Default Prophet",

            "Max Life": "Naive",

            "SBI Life": "Seasonal Naive",

            "Tata AIA": "Naive"
        }

        model_name = final_models.get(
            insurer,
            "Naive"
        )

    # -----------------------------
    # Forecast
    # -----------------------------

    if model_name == "Naive":

        last_value = ts["y"].iloc[-1]

        future_dates = pd.date_range(
            start=ts["ds"].iloc[-1]
            + pd.offsets.MonthBegin(1),
            periods=months,
            freq="MS"
        )

        forecast_values = [
            last_value
        ] * months

    elif model_name == "Seasonal Naive":

        future_dates = pd.date_range(
            start=ts["ds"].iloc[-1]
            + pd.offsets.MonthBegin(1),
            periods=months,
            freq="MS"
        )

        values = ts["y"].values

        forecast_values = []

        for i in range(months):

            index = len(values) - 12 + (i % 12)

            forecast_values.append(
                values[index]
            )

    elif model_name == "ARIMA":

        model = ARIMA(
            ts["y"],
            order=(1, 1, 1)
        )

        fitted_model = model.fit()

        forecast_values = fitted_model.forecast(
            steps=months
        )

        future_dates = pd.date_range(
            start=ts["ds"].iloc[-1]
            + pd.offsets.MonthBegin(1),
            periods=months,
            freq="MS"
        )

    elif model_name == "Default Prophet":

        prophet_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False
        )

        prophet_model.fit(ts)

        future = prophet_model.make_future_dataframe(
            periods=months,
            freq="MS"
        )

        prediction = prophet_model.predict(
            future
        )

        forecast = prediction.tail(months)

        future_dates = forecast["ds"]

        forecast_values = forecast["yhat"].values

    else:

        raise ValueError(
            f"Model '{model_name}' "
            "is not implemented yet."
        )

    # -----------------------------
    # Create forecast dataframe
    # -----------------------------

    forecast_df = pd.DataFrame({

        "month": future_dates,

        "insurer": insurer,

        "model": model_name,

        "forecast_renewed_premium":
            forecast_values
    })

    return forecast_df