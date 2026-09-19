from pathlib import Path

import numpy as np
import pandas as pd
from prophet import Prophet


# ============================================================
# 1. PROJECT PATH
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


# ============================================================
# 3. PROPHET FORMAT
# ============================================================

prophet_df = df[
    ["collection_month", "renewed_premium"]
].copy()

prophet_df.columns = ["ds", "y"]


# ============================================================
# 4. TRAIN / VALIDATION / FINAL TEST
# ============================================================

train = prophet_df.iloc[:24].copy()

validation = prophet_df.iloc[24:36].copy()

final_test = prophet_df.iloc[36:].copy()


print("=" * 60)
print("PROPHET MODEL TUNING")
print("=" * 60)

print("\nTRAIN:")
print(train["ds"].min(), "to", train["ds"].max())
print("Observations:", len(train))

print("\nVALIDATION:")
print(validation["ds"].min(), "to", validation["ds"].max())
print("Observations:", len(validation))

print("\nFINAL TEST:")
print(final_test["ds"].min(), "to", final_test["ds"].max())
print("Observations:", len(final_test))


# ============================================================
# 5. METRICS
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
# 6. HYPERPARAMETERS
# ============================================================

changepoint_prior_scales = [
    0.01,
    0.05,
    0.1,
    0.5
]

seasonality_prior_scales = [
    1.0,
    5.0,
    10.0
]

seasonality_modes = [
    "additive",
    "multiplicative"
]


# ============================================================
# 7. MODEL TUNING
# ============================================================

results = []

total_models = (
    len(changepoint_prior_scales)
    * len(seasonality_prior_scales)
    * len(seasonality_modes)
)

model_number = 0


print("\n" + "=" * 60)
print("TESTING PROPHET CONFIGURATIONS")
print("=" * 60)

for cps in changepoint_prior_scales:

    for sps in seasonality_prior_scales:

        for mode in seasonality_modes:

            model_number += 1

            print(
                f"\n[{model_number}/{total_models}] "
                f"changepoint_prior_scale={cps}, "
                f"seasonality_prior_scale={sps}, "
                f"mode={mode}"
            )

            try:

                model = Prophet(
                    yearly_seasonality=True,
                    weekly_seasonality=False,
                    daily_seasonality=False,

                    changepoint_prior_scale=cps,

                    seasonality_prior_scale=sps,

                    seasonality_mode=mode
                )

                model.fit(train)

                future = model.make_future_dataframe(
                    periods=len(validation),
                    freq="MS"
                )

                forecast = model.predict(future)

                validation_prediction = (
                    forecast["yhat"]
                    .tail(len(validation))
                    .reset_index(drop=True)
                )

                actual = (
                    validation["y"]
                    .reset_index(drop=True)
                )

                mae, rmse, mape = calculate_metrics(
                    actual,
                    validation_prediction
                )

                results.append({
                    "changepoint_prior_scale": cps,
                    "seasonality_prior_scale": sps,
                    "seasonality_mode": mode,
                    "MAE": mae,
                    "RMSE": rmse,
                    "MAPE": mape
                })

                print(
                    f"MAE={mae:,.2f} | "
                    f"RMSE={rmse:,.2f} | "
                    f"MAPE={mape:.4f}%"
                )

            except Exception as e:

                print("FAILED:", e)


# ============================================================
# 8. VALIDATION RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_df = (
    results_df
    .sort_values("MAPE")
    .reset_index(drop=True)
)


print("\n" + "=" * 60)
print("PROPHET VALIDATION RESULTS")
print("=" * 60)

print(
    results_df.to_string(index=False)
)


# ============================================================
# 9. BEST CONFIGURATION
# ============================================================

best = results_df.iloc[0]

best_cps = best[
    "changepoint_prior_scale"
]

best_sps = best[
    "seasonality_prior_scale"
]

best_mode = best[
    "seasonality_mode"
]


print("\n" + "=" * 60)
print("BEST PROPHET CONFIGURATION")
print("=" * 60)

print(
    "Changepoint prior scale:",
    best_cps
)

print(
    "Seasonality prior scale:",
    best_sps
)

print(
    "Seasonality mode:",
    best_mode
)

print(
    "\nValidation MAPE:",
    best["MAPE"],
    "%"
)


# ============================================================
# 10. RETRAIN ON TRAIN + VALIDATION
# ============================================================

development_data = prophet_df.iloc[:36].copy()


print("\n" + "=" * 60)
print("RETRAINING BEST PROPHET MODEL")
print("=" * 60)

print(
    development_data["ds"].min(),
    "to",
    development_data["ds"].max()
)

print(
    "Observations:",
    len(development_data)
)


final_model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,

    changepoint_prior_scale=best_cps,

    seasonality_prior_scale=best_sps,

    seasonality_mode=best_mode
)


final_model.fit(
    development_data
)


# ============================================================
# 11. FINAL TEST FORECAST
# ============================================================

future = final_model.make_future_dataframe(
    periods=len(final_test),
    freq="MS"
)

forecast = final_model.predict(
    future
)


final_prediction = (
    forecast["yhat"]
    .tail(len(final_test))
    .reset_index(drop=True)
)

actual = (
    final_test["y"]
    .reset_index(drop=True)
)

months = (
    final_test["ds"]
    .reset_index(drop=True)
)


# ============================================================
# 12. FINAL TEST METRICS
# ============================================================

mae, rmse, mape = calculate_metrics(
    actual,
    final_prediction
)


final_results = pd.DataFrame({
    "month": months,
    "actual": actual,
    "prediction": final_prediction
})


# ============================================================
# 13. FINAL RESULTS
# ============================================================

print("\n" + "=" * 60)
print("TUNED PROPHET FINAL TEST RESULTS")
print("=" * 60)

print(
    "\nSelected changepoint_prior_scale:",
    best_cps
)

print(
    "Selected seasonality_prior_scale:",
    best_sps
)

print(
    "Selected seasonality_mode:",
    best_mode
)

print("\nMAE:", mae)

print("RMSE:", rmse)

print("MAPE:", mape, "%")


print("\nFinal predictions:")

print(
    final_results.to_string(index=False)
)


# ============================================================
# 14. COMPLETED
# ============================================================

print("\n" + "=" * 60)
print("PROPHET TUNING COMPLETED")
print("=" * 60)