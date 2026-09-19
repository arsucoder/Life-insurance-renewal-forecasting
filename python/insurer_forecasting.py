from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "monthly_by_insurer.csv"
)


# ============================================================
# SETTINGS
# ============================================================

INSURER = "LIC"

TARGET = "renewed_premium"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["collection_month"]
)

df = df.sort_values(
    ["insurer", "collection_month"]
).reset_index(drop=True)


# ============================================================
# SELECT INSURER
# ============================================================

insurer_df = df[
    df["insurer"] == INSURER
].copy()

insurer_df = insurer_df.sort_values(
    "collection_month"
).reset_index(drop=True)


print("=" * 70)
print("INSURER FORECASTING")
print("=" * 70)

print("Insurer:", INSURER)
print("Target:", TARGET)

print(
    "Date range:",
    insurer_df["collection_month"].min(),
    "to",
    insurer_df["collection_month"].max()
)

print(
    "Observations:",
    len(insurer_df)
)


# ============================================================
# TIME SERIES
# ============================================================

y = insurer_df[TARGET].astype(float)

dates = insurer_df["collection_month"]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

# 36 months training
# 12 months final test

train = y.iloc[:36]
test = y.iloc[36:]

test_dates = dates.iloc[36:]


print("\n" + "=" * 70)
print("TRAIN / TEST SPLIT")
print("=" * 70)

print(
    "Training:",
    dates.iloc[0],
    "to",
    dates.iloc[35]
)

print(
    "Training observations:",
    len(train)
)

print(
    "Testing:",
    dates.iloc[36],
    "to",
    dates.iloc[-1]
)

print(
    "Testing observations:",
    len(test)
)


# ============================================================
# NAIVE BASELINE
# ============================================================

print("\n" + "=" * 70)
print("NAIVE BASELINE")
print("=" * 70)

naive_predictions = np.repeat(
    train.iloc[-1],
    len(test)
)

naive_mae = mean_absolute_error(
    test,
    naive_predictions
)

naive_rmse = np.sqrt(
    mean_squared_error(
        test,
        naive_predictions
    )
)

naive_mape = np.mean(
    np.abs(
        (test.values - naive_predictions)
        / test.values
    )
) * 100


print("MAE :", naive_mae)
print("RMSE:", naive_rmse)
print("MAPE:", naive_mape, "%")


# ============================================================
# ARIMA
# ============================================================

print("\n" + "=" * 70)
print("ARIMA")
print("=" * 70)

ARIMA_ORDER = (1, 1, 1)

model = ARIMA(
    train,
    order=ARIMA_ORDER
)

fitted_model = model.fit()

arima_predictions = fitted_model.forecast(
    steps=len(test)
)

arima_mae = mean_absolute_error(
    test,
    arima_predictions
)

arima_rmse = np.sqrt(
    mean_squared_error(
        test,
        arima_predictions
    )
)

arima_mape = np.mean(
    np.abs(
        (test.values - arima_predictions)
        / test.values
    )
) * 100


print("Order:", ARIMA_ORDER)

print("MAE :", arima_mae)
print("RMSE:", arima_rmse)
print("MAPE:", arima_mape, "%")


# ============================================================
# RESULTS TABLE
# ============================================================

results = pd.DataFrame(
    [
        {
            "Model": "Naive",
            "MAE": naive_mae,
            "RMSE": naive_rmse,
            "MAPE": naive_mape
        },
        {
            "Model": "ARIMA",
            "MAE": arima_mae,
            "RMSE": arima_rmse,
            "MAPE": arima_mape
        }
    ]
)


print("\n" + "=" * 70)
print("LIC FORECASTING RESULTS")
print("=" * 70)

print(
    results.to_string(index=False)
)


# ============================================================
# PREDICTIONS
# ============================================================

prediction_df = pd.DataFrame(
    {
        "month": test_dates.values,
        "actual": test.values,
        "naive_prediction": naive_predictions,
        "arima_prediction": arima_predictions
    }
)

print("\nPredictions:")

print(
    prediction_df.to_string(index=False)
)

# ============================================================
# SEASONAL NAIVE
# ============================================================

print("\n" + "=" * 70)
print("SEASONAL NAIVE")
print("=" * 70)

seasonal_predictions = train.iloc[-12:].values

seasonal_mae = mean_absolute_error(
    test,
    seasonal_predictions
)

seasonal_rmse = np.sqrt(
    mean_squared_error(
        test,
        seasonal_predictions
    )
)

seasonal_mape = np.mean(
    np.abs(
        (test.values - seasonal_predictions)
        / test.values
    )
) * 100


print("MAE :", seasonal_mae)
print("RMSE:", seasonal_rmse)
print("MAPE:", seasonal_mape, "%")


print("\nSeasonal predictions:")

seasonal_prediction_df = pd.DataFrame(
    {
        "month": test_dates.values,
        "actual": test.values,
        "prediction": seasonal_predictions
    }
)

print(
    seasonal_prediction_df.to_string(index=False)
)

# ============================================================
# SARIMA MODEL SELECTION FOR LIC
# ============================================================

print("\n" + "=" * 70)
print("LIC SARIMA MODEL SELECTION")
print("=" * 70)

# Development split:
# 24 months training
# 12 months validation
# Final 12 months remains untouched

sarima_train = y.iloc[:24]
sarima_validation = y.iloc[24:36]

print("\nTraining:")
print(dates.iloc[0], "to", dates.iloc[23])
print("Observations:", len(sarima_train))

print("\nValidation:")
print(dates.iloc[24], "to", dates.iloc[35])
print("Observations:", len(sarima_validation))


# Candidate configurations
sarima_configs = [
    ((0, 1, 1), (0, 0, 1, 12)),
    ((0, 1, 1), (1, 0, 0, 12)),
    ((1, 1, 0), (0, 0, 1, 12)),
    ((1, 1, 0), (1, 0, 0, 12)),
    ((1, 1, 1), (0, 0, 1, 12)),
    ((1, 1, 1), (1, 0, 0, 12)),
]


sarima_results = []


for order, seasonal_order in sarima_configs:

    print("\nTesting:", order, seasonal_order)

    try:

        model = ARIMA(
            sarima_train,
            order=order,
            seasonal_order=seasonal_order
        )

        fitted = model.fit()

        predictions = fitted.forecast(
            steps=len(sarima_validation)
        )

        mae = mean_absolute_error(
            sarima_validation,
            predictions
        )

        rmse = np.sqrt(
            mean_squared_error(
                sarima_validation,
                predictions
            )
        )

        mape = np.mean(
            np.abs(
                (
                    sarima_validation.values
                    - predictions.values
                )
                / sarima_validation.values
            )
        ) * 100

        print("MAE :", mae)
        print("RMSE:", rmse)
        print("MAPE:", mape)

        sarima_results.append(
            {
                "order": order,
                "seasonal_order": seasonal_order,
                "MAE": mae,
                "RMSE": rmse,
                "MAPE": mape
            }
        )

    except Exception as e:

        print("FAILED:", e)


# ============================================================
# VALIDATION RESULTS
# ============================================================

sarima_results_df = pd.DataFrame(
    sarima_results
)

sarima_results_df = sarima_results_df.sort_values(
    "MAPE"
).reset_index(drop=True)


print("\n" + "=" * 70)
print("LIC SARIMA VALIDATION RESULTS")
print("=" * 70)

print(
    sarima_results_df.to_string(index=False)
)


# ============================================================
# BEST SARIMA
# ============================================================

best_sarima = sarima_results_df.iloc[0]

best_order = best_sarima["order"]
best_seasonal_order = best_sarima["seasonal_order"]


print("\n" + "=" * 70)
print("BEST LIC SARIMA")
print("=" * 70)

print(
    "Order:",
    best_order
)

print(
    "Seasonal order:",
    best_seasonal_order
)


# ============================================================
# RETRAIN ON FULL 36-MONTH DEVELOPMENT DATA
# ============================================================

final_sarima = ARIMA(
    train,
    order=best_order,
    seasonal_order=best_seasonal_order
)

final_sarima_fit = final_sarima.fit()

sarima_predictions = final_sarima_fit.forecast(
    steps=len(test)
)


# ============================================================
# FINAL SARIMA TEST METRICS
# ============================================================

sarima_mae = mean_absolute_error(
    test,
    sarima_predictions
)

sarima_rmse = np.sqrt(
    mean_squared_error(
        test,
        sarima_predictions
    )
)

sarima_mape = np.mean(
    np.abs(
        (
            test.values
            - sarima_predictions.values
        )
        / test.values
    )
) * 100


print("\n" + "=" * 70)
print("LIC SARIMA FINAL TEST RESULTS")
print("=" * 70)

print("MAE :", sarima_mae)
print("RMSE:", sarima_rmse)
print("MAPE:", sarima_mape, "%")


print("\nPredictions:")

print(
    pd.DataFrame(
        {
            "month": test_dates.values,
            "actual": test.values,
            "prediction": sarima_predictions.values
        }
    ).to_string(index=False)
)

# ============================================================
# LIC PROPHET FORECASTING
# ============================================================

print("\n" + "=" * 70)
print("LIC PROPHET FORECASTING")
print("=" * 70)

from prophet import Prophet

# ------------------------------------------------------------
# PREPARE DATA FOR PROPHET
# ------------------------------------------------------------

prophet_train = pd.DataFrame({
    "ds": dates.iloc[:36].values,
    "y": train.values
})

prophet_test = pd.DataFrame({
    "ds": dates.iloc[36:].values,
    "actual": test.values
})

print("\nTraining period:")
print(prophet_train["ds"].min(), "to", prophet_train["ds"].max())
print("Training observations:", len(prophet_train))

print("\nTesting period:")
print(prophet_test["ds"].min(), "to", prophet_test["ds"].max())
print("Testing observations:", len(prophet_test))


# ------------------------------------------------------------
# FIT PROPHET
# ------------------------------------------------------------

print("\nFitting Prophet model...")

prophet_model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False
)

prophet_model.fit(prophet_train)

print("Prophet model fitted successfully.")


# ------------------------------------------------------------
# CREATE FUTURE DATAFRAME
# ------------------------------------------------------------

future = prophet_model.make_future_dataframe(
    periods=12,
    freq="MS"
)

print("\nFuture dataframe:")
print(
    future.tail(12).to_string(index=False)
)


# ------------------------------------------------------------
# GENERATE FORECAST
# ------------------------------------------------------------

print("\nGenerating forecast...")

forecast = prophet_model.predict(future)

print("Forecast generated successfully.")


# ------------------------------------------------------------
# EXTRACT TEST PREDICTIONS
# ------------------------------------------------------------

prophet_predictions = forecast[
    forecast["ds"].isin(prophet_test["ds"])
]["yhat"].values


# ------------------------------------------------------------
# CALCULATE METRICS
# ------------------------------------------------------------

prophet_mae = mean_absolute_error(
    prophet_test["actual"],
    prophet_predictions
)

prophet_rmse = np.sqrt(
    mean_squared_error(
        prophet_test["actual"],
        prophet_predictions
    )
)

prophet_mape = np.mean(
    np.abs(
        (
            prophet_test["actual"].values
            - prophet_predictions
        )
        / prophet_test["actual"].values
    )
) * 100


# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("LIC PROPHET RESULTS")
print("=" * 70)

print("MAE :", prophet_mae)
print("RMSE:", prophet_rmse)
print("MAPE:", prophet_mape, "%")


# ------------------------------------------------------------
# PREDICTION TABLE
# ------------------------------------------------------------

prophet_results = pd.DataFrame({
    "month": prophet_test["ds"].values,
    "actual": prophet_test["actual"].values,
    "prediction": prophet_predictions
})

print("\nPredictions:")
print(
    prophet_results.to_string(index=False)
)


# ------------------------------------------------------------
# ADD TO MODEL COMPARISON
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("LIC MODEL COMPARISON")
print("=" * 70)

lic_model_comparison = pd.DataFrame([
    {
        "Model": "Naive",
        "MAE": naive_mae,
        "RMSE": naive_rmse,
        "MAPE": naive_mape
    },
    {
        "Model": "ARIMA",
        "MAE": arima_mae,
        "RMSE": arima_rmse,
        "MAPE": arima_mape
    },
    {
        "Model": "Seasonal Naive",
        "MAE": seasonal_mae,
        "RMSE": seasonal_rmse,
        "MAPE": seasonal_mape
    },
    {
        "Model": "Tuned SARIMA",
        "MAE": sarima_mae,
        "RMSE": sarima_rmse,
        "MAPE": sarima_mape
    },
    {
        "Model": "Prophet",
        "MAE": prophet_mae,
        "RMSE": prophet_rmse,
        "MAPE": prophet_mape
    }
])

print(
    lic_model_comparison
    .sort_values("MAPE")
    .to_string(index=False)
)

print("\n" + "=" * 70)
print("LIC PROPHET COMPLETED")
print("=" * 70)

# ============================================================
# LIC PROPHET TUNING
# ============================================================

import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv("data/processed/monthly_by_insurer.csv")

df["collection_month"] = pd.to_datetime(df["collection_month"])

# Select LIC
lic = df[df["insurer"] == "LIC"].copy()

lic = lic.sort_values("collection_month")

# Prophet requires:
# ds = date
# y  = target

prophet_df = lic[[
    "collection_month",
    "renewed_premium"
]].rename(columns={
    "collection_month": "ds",
    "renewed_premium": "y"
})

print("=" * 70)
print("LIC PROPHET TUNING")
print("=" * 70)

print("Total observations:", len(prophet_df))
print("Start:", prophet_df["ds"].min())
print("End:", prophet_df["ds"].max())


# ------------------------------------------------------------
# 2. TRAIN / VALIDATION / TEST SPLIT
# ------------------------------------------------------------

train = prophet_df.iloc[:24].copy()
validation = prophet_df.iloc[24:36].copy()
test = prophet_df.iloc[36:48].copy()

print("\nTraining:")
print(train["ds"].min(), "to", train["ds"].max())
print("Observations:", len(train))

print("\nValidation:")
print(validation["ds"].min(), "to", validation["ds"].max())
print("Observations:", len(validation))

print("\nFinal Test:")
print(test["ds"].min(), "to", test["ds"].max())
print("Observations:", len(test))


# ------------------------------------------------------------
# 3. METRIC FUNCTION
# ------------------------------------------------------------

def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    mape = np.mean(
        np.abs((actual - predicted) / actual)
    ) * 100

    return mae, rmse, mape


# ------------------------------------------------------------
# 4. PROPHET CONFIGURATIONS
# ------------------------------------------------------------

configs = {

    "Prophet_Default": {
        "changepoint_prior_scale": 0.05,
        "seasonality_prior_scale": 10,
        "seasonality_mode": "additive"
    },

    "Prophet_Trend_Flexible": {
        "changepoint_prior_scale": 0.10,
        "seasonality_prior_scale": 10,
        "seasonality_mode": "additive"
    },

    "Prophet_Trend_Strong": {
        "changepoint_prior_scale": 0.50,
        "seasonality_prior_scale": 10,
        "seasonality_mode": "additive"
    },

    "Prophet_Seasonality_Flexible": {
        "changepoint_prior_scale": 0.05,
        "seasonality_prior_scale": 20,
        "seasonality_mode": "additive"
    },

    "Prophet_Multiplicative": {
        "changepoint_prior_scale": 0.05,
        "seasonality_prior_scale": 10,
        "seasonality_mode": "multiplicative"
    },

    "Prophet_Flexible_Multiplicative": {
        "changepoint_prior_scale": 0.10,
        "seasonality_prior_scale": 20,
        "seasonality_mode": "multiplicative"
    }
}


# ------------------------------------------------------------
# 5. VALIDATION
# ------------------------------------------------------------

results = []

print("\n" + "=" * 70)
print("TESTING PROPHET CONFIGURATIONS")
print("=" * 70)

for name, params in configs.items():

    print("\nTesting:", name)

    model = Prophet(
        changepoint_prior_scale=params["changepoint_prior_scale"],
        seasonality_prior_scale=params["seasonality_prior_scale"],
        seasonality_mode=params["seasonality_mode"],
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False
    )

    # Monthly data → explicitly add yearly seasonality
    model.add_seasonality(
        name="yearly",
        period=365.25,
        fourier_order=5
    )

    model.fit(train)

    future = validation[["ds"]]

    forecast = model.predict(future)

    predictions = forecast["yhat"].values

    mae, rmse, mape = calculate_metrics(
        validation["y"].values,
        predictions
    )

    print("MAE :", mae)
    print("RMSE:", rmse)
    print("MAPE:", mape)

    results.append({
        "model": name,
        "changepoint_prior_scale":
            params["changepoint_prior_scale"],
        "seasonality_prior_scale":
            params["seasonality_prior_scale"],
        "seasonality_mode":
            params["seasonality_mode"],
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape
    })


# ------------------------------------------------------------
# 6. VALIDATION RESULTS
# ------------------------------------------------------------

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "MAPE"
).reset_index(drop=True)

print("\n" + "=" * 70)
print("LIC PROPHET VALIDATION RESULTS")
print("=" * 70)

print(results_df.to_string(index=False))


# ------------------------------------------------------------
# 7. SELECT BEST MODEL
# ------------------------------------------------------------

best = results_df.iloc[0]

print("\n" + "=" * 70)
print("BEST LIC PROPHET MODEL")
print("=" * 70)

print("Model:", best["model"])
print(
    "Changepoint prior scale:",
    best["changepoint_prior_scale"]
)
print(
    "Seasonality prior scale:",
    best["seasonality_prior_scale"]
)
print(
    "Seasonality mode:",
    best["seasonality_mode"]
)


# ------------------------------------------------------------
# 8. RETRAIN ON TRAIN + VALIDATION
# ------------------------------------------------------------

final_train = pd.concat(
    [train, validation]
).reset_index(drop=True)

best_model = Prophet(
    changepoint_prior_scale=best["changepoint_prior_scale"],
    seasonality_prior_scale=best["seasonality_prior_scale"],
    seasonality_mode=best["seasonality_mode"],
    yearly_seasonality=False,
    weekly_seasonality=False,
    daily_seasonality=False
)

best_model.add_seasonality(
    name="yearly",
    period=365.25,
    fourier_order=5
)

print("\nRetraining best Prophet model...")

best_model.fit(final_train)

print("Best model fitted successfully.")


# ------------------------------------------------------------
# 9. FINAL TEST FORECAST
# ------------------------------------------------------------

future_test = test[["ds"]]

forecast_test = best_model.predict(
    future_test
)

predictions = forecast_test["yhat"].values

mae, rmse, mape = calculate_metrics(
    test["y"].values,
    predictions
)


# ------------------------------------------------------------
# 10. FINAL RESULTS
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("LIC TUNED PROPHET FINAL TEST RESULTS")
print("=" * 70)

print("Selected model:", best["model"])
print("MAE :", mae)
print("RMSE:", rmse)
print("MAPE:", mape)


# ------------------------------------------------------------
# 11. PREDICTION TABLE
# ------------------------------------------------------------

prediction_df = pd.DataFrame({
    "month": test["ds"].values,
    "actual": test["y"].values,
    "prediction": predictions
})

print("\nPredictions:")
print(prediction_df.to_string(index=False))


# ------------------------------------------------------------
# 12. SAVE RESULTS
# ------------------------------------------------------------

results_df.to_csv(
    "reports/lic_prophet_validation_results.csv",
    index=False
)

prediction_df.to_csv(
    "reports/lic_tuned_prophet_predictions.csv",
    index=False
)

print("\nSaved:")
print("reports/lic_prophet_validation_results.csv")
print("reports/lic_tuned_prophet_predictions.csv")

print("\n" + "=" * 70)
print("LIC TUNED PROPHET COMPLETED")
print("=" * 70)