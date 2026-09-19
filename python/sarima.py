from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

MONTHLY_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "monthly_renewal_premium.csv"
)


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(
    MONTHLY_PATH,
    parse_dates=["collection_month"]
)

df = (
    df
    .sort_values("collection_month")
    .reset_index(drop=True)
)

TARGET = "renewed_premium"
SEASONAL_PERIOD = 12


# ============================================================
# 3. METRICS
# ============================================================

def calculate_metrics(actual, prediction):

    actual = np.asarray(actual, dtype=float)
    prediction = np.asarray(prediction, dtype=float)

    error = actual - prediction

    mae = np.mean(np.abs(error))

    rmse = np.sqrt(
        np.mean(error ** 2)
    )

    mape = (
        np.mean(
            np.abs(error / actual)
        )
        * 100
    )

    return mae, rmse, mape


# ============================================================
# 4. THREE-WAY SPLIT
# ============================================================

# 48 months total
#
# TRAIN      : 24 months
# VALIDATION : 12 months
# FINAL TEST : 12 months

train = df.iloc[:24].copy()

validation = df.iloc[24:36].copy()

final_test = df.iloc[36:].copy()

y_train = train[TARGET]

y_validation = validation[TARGET]

y_final_test = final_test[TARGET]


print("=" * 60)
print("SARIMA MODEL SELECTION")
print("=" * 60)

print("\nTraining:")
print(
    train["collection_month"].min(),
    "to",
    train["collection_month"].max()
)

print("Observations:", len(train))

print("\nValidation:")
print(
    validation["collection_month"].min(),
    "to",
    validation["collection_month"].max()
)

print("Observations:", len(validation))

print("\nFINAL TEST:")
print(
    final_test["collection_month"].min(),
    "to",
    final_test["collection_month"].max()
)

print("Observations:", len(final_test))


# ============================================================
# 5. SARIMA CONFIGURATIONS
# ============================================================

orders = [
    (0, 1, 1),
    (1, 1, 0),
    (1, 1, 1),
]

seasonal_orders = [
    (0, 0, 1, 12),
    (1, 0, 0, 12),
]


# ============================================================
# 6. MODEL SELECTION
# ============================================================

results = []

print("\n" + "=" * 60)
print("TESTING SARIMA CONFIGURATIONS")
print("=" * 60)

for order in orders:

    for seasonal_order in seasonal_orders:

        print(
            "\nTesting:",
            order,
            seasonal_order
        )

        try:

            model = SARIMAX(
                y_train,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )

            model_fit = model.fit(
                disp=False
            )

            validation_forecast = model_fit.forecast(
                steps=len(validation)
            )

            mae, rmse, mape = calculate_metrics(
                y_validation,
                validation_forecast
            )

            results.append({
                "order": order,
                "seasonal_order": seasonal_order,
                "MAE": mae,
                "RMSE": rmse,
                "MAPE": mape
            })

            print("MAE :", mae)
            print("RMSE:", rmse)
            print("MAPE:", mape)

        except Exception as e:

            print("FAILED:", e)


# ============================================================
# 7. VALIDATION RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "MAE"
).reset_index(drop=True)


print("\n" + "=" * 60)
print("SARIMA VALIDATION RESULTS")
print("=" * 60)

print(results_df.to_string(index=False))


# ============================================================
# 8. SELECT BEST MODEL
# ============================================================

best_order = results_df.iloc[0]["order"]

best_seasonal_order = (
    results_df.iloc[0]["seasonal_order"]
)

print("\n" + "=" * 60)
print("BEST SARIMA MODEL")
print("=" * 60)

print("\nOrder:", best_order)

print(
    "Seasonal order:",
    best_seasonal_order
)


# ============================================================
# 9. RETRAIN ON TRAIN + VALIDATION
# ============================================================

development_data = df.iloc[:36]

y_development = development_data[TARGET]


print("\nRetraining using:")
print(
    development_data["collection_month"].min(),
    "to",
    development_data["collection_month"].max()
)

print("Observations:", len(development_data))


final_model = SARIMAX(
    y_development,
    order=best_order,
    seasonal_order=best_seasonal_order,
    enforce_stationarity=False,
    enforce_invertibility=False
)

final_model_fit = final_model.fit(
    disp=False
)


# ============================================================
# 10. FINAL TEST FORECAST
# ============================================================

final_forecast = final_model_fit.forecast(
    steps=len(final_test)
)


# ============================================================
# 11. FINAL TEST EVALUATION
# ============================================================

mae, rmse, mape = calculate_metrics(
    y_final_test,
    final_forecast
)

final_results = pd.DataFrame({
    "month": final_test["collection_month"],
    "actual": y_final_test.to_numpy(),
    "prediction": np.asarray(final_forecast)
})


# ============================================================
# 12. FINAL RESULTS
# ============================================================

print("\n" + "=" * 60)
print("SARIMA FINAL TEST RESULTS")
print("=" * 60)

print("\nSelected order:", best_order)

print(
    "Selected seasonal order:",
    best_seasonal_order
)

print("\nMAE:", mae)

print("RMSE:", rmse)

print("MAPE:", mape, "%")

print("\nFinal predictions:")

print(final_results)


# ============================================================
# 13. COMPLETION
# ============================================================

print("\n" + "=" * 60)
print("SARIMA TUNING COMPLETED")
print("=" * 60)