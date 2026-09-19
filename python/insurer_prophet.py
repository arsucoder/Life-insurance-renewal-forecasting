import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/processed/monthly_by_insurer.csv"

INSURER = "LIC"
TARGET = "renewed_premium"

TRAIN_END = "2023-03-01"
VALIDATION_END = "2024-03-01"
TEST_START = "2024-04-01"


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

df["collection_month"] = pd.to_datetime(df["collection_month"])

df = df[df["insurer"] == INSURER].copy()

df = df.sort_values("collection_month")

print("=" * 70)
print("INSURER PROPHET FORECASTING")
print("=" * 70)

print("Insurer:", INSURER)
print("Target:", TARGET)
print("Observations:", len(df))
print(
    "Date range:",
    df["collection_month"].min(),
    "to",
    df["collection_month"].max()
)


# ============================================================
# PREPARE PROPHET DATA
# ============================================================

prophet_df = df[["collection_month", TARGET]].copy()

prophet_df.columns = ["ds", "y"]

prophet_df = prophet_df.dropna()

prophet_df = prophet_df.sort_values("ds")


# ============================================================
# TRAIN / VALIDATION / TEST SPLIT
# ============================================================

train = prophet_df[
    prophet_df["ds"] <= TRAIN_END
].copy()

validation = prophet_df[
    (prophet_df["ds"] > TRAIN_END)
    & (prophet_df["ds"] <= VALIDATION_END)
].copy()

test = prophet_df[
    prophet_df["ds"] >= TEST_START
].copy()


print("\n" + "=" * 70)
print("DATA SPLIT")
print("=" * 70)

print(
    "Training:",
    train["ds"].min(),
    "to",
    train["ds"].max()
)

print("Training observations:", len(train))

print(
    "Validation:",
    validation["ds"].min(),
    "to",
    validation["ds"].max()
)

print("Validation observations:", len(validation))

print(
    "Test:",
    test["ds"].min(),
    "to",
    test["ds"].max()
)

print("Test observations:", len(test))


# ============================================================
# METRICS FUNCTION
# ============================================================

def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    mape = np.mean(
        np.abs(
            (actual - predicted) / actual
        )
    ) * 100

    return mae, rmse, mape


# ============================================================
# PROPHET CONFIGURATIONS
# ============================================================

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


# ============================================================
# PROPHET MODEL FUNCTION
# ============================================================

def fit_prophet(config, training_data):

    model = Prophet(
        changepoint_prior_scale=config["changepoint_prior_scale"],
        seasonality_prior_scale=config["seasonality_prior_scale"],
        seasonality_mode=config["seasonality_mode"],
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )

    model.fit(training_data)

    return model


# ============================================================
# MODEL SELECTION
# ============================================================

print("\n" + "=" * 70)
print("PROPHET MODEL SELECTION")
print("=" * 70)

results = []

for name, config in configs.items():

    print("\nTesting:", name)

    model = fit_prophet(config, train)

    future = validation[["ds"]].copy()

    forecast = model.predict(future)

    predictions = forecast["yhat"].values

    actual = validation["y"].values

    mae, rmse, mape = calculate_metrics(
        actual,
        predictions
    )

    print("MAE :", mae)
    print("RMSE:", rmse)
    print("MAPE:", mape)

    results.append({

        "model": name,

        "changepoint_prior_scale":
            config["changepoint_prior_scale"],

        "seasonality_prior_scale":
            config["seasonality_prior_scale"],

        "seasonality_mode":
            config["seasonality_mode"],

        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape
    })


# ============================================================
# VALIDATION RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values("MAPE")

print("\n" + "=" * 70)
print("PROPHET VALIDATION RESULTS")
print("=" * 70)

print(results_df.to_string(index=False))


# ============================================================
# SELECT BEST MODEL
# ============================================================

best = results_df.iloc[0]

best_model_name = best["model"]

best_config = configs[best_model_name]


print("\n" + "=" * 70)
print("BEST PROPHET MODEL")
print("=" * 70)

print("Model:", best_model_name)

print(
    "Changepoint prior scale:",
    best_config["changepoint_prior_scale"]
)

print(
    "Seasonality prior scale:",
    best_config["seasonality_prior_scale"]
)

print(
    "Seasonality mode:",
    best_config["seasonality_mode"]
)


# ============================================================
# RETRAIN ON TRAIN + VALIDATION
# ============================================================

final_training_data = prophet_df[
    prophet_df["ds"] <= VALIDATION_END
].copy()


print("\nRetraining best Prophet model...")

final_model = fit_prophet(
    best_config,
    final_training_data
)

print("Best model fitted successfully.")


# ============================================================
# FINAL TEST FORECAST
# ============================================================

future_test = test[["ds"]].copy()

forecast = final_model.predict(future_test)

predictions = forecast["yhat"].values

actual = test["y"].values


# ============================================================
# FINAL METRICS
# ============================================================

mae, rmse, mape = calculate_metrics(
    actual,
    predictions
)


print("\n" + "=" * 70)
print("TUNED PROPHET FINAL TEST RESULTS")
print("=" * 70)

print("Selected model:", best_model_name)

print("MAE :", mae)
print("RMSE:", rmse)
print("MAPE:", mape)


# ============================================================
# PREDICTIONS TABLE
# ============================================================

prediction_df = pd.DataFrame({

    "month": test["ds"].values,

    "actual": actual,

    "prediction": predictions
})


print("\nPredictions:")

print(
    prediction_df.to_string(index=False)
)


# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    "reports/lic_prophet_validation_results.csv",
    index=False
)

prediction_df.to_csv(
    "reports/lic_tuned_prophet_predictions.csv",
    index=False
)


print("\n" + "=" * 70)
print("FILES SAVED")
print("=" * 70)

print(
    "reports/lic_prophet_validation_results.csv"
)

print(
    "reports/lic_tuned_prophet_predictions.csv"
)

print("\n" + "=" * 70)
print("LIC TUNED PROPHET COMPLETED")
print("=" * 70)