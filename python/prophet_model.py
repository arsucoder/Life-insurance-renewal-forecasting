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

df = df.sort_values("collection_month").reset_index(drop=True)


# ============================================================
# 3. PREPARE PROPHET DATA
# ============================================================

prophet_df = df[
    ["collection_month", "renewed_premium"]
].copy()

prophet_df.columns = ["ds", "y"]


# ============================================================
# 4. TRAIN / TEST SPLIT
# ============================================================

train = prophet_df.iloc[:36].copy()
test = prophet_df.iloc[36:].copy()


print("=" * 60)
print("PROPHET FORECASTING")
print("=" * 60)

print("\nTraining period:")
print(train["ds"].min(), "to", train["ds"].max())
print("Training observations:", len(train))

print("\nTesting period:")
print(test["ds"].min(), "to", test["ds"].max())
print("Testing observations:", len(test))


# ============================================================
# 5. CREATE MODEL
# ============================================================

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    seasonality_mode="additive"
)


# ============================================================
# 6. TRAIN MODEL
# ============================================================

print("\nFitting Prophet model...")

model.fit(train)

print("Prophet model fitted successfully.")


# ============================================================
# 7. CREATE FUTURE DATES
# ============================================================

future = model.make_future_dataframe(
    periods=12,
    freq="MS"
)

print("\nFuture dataframe:")
print(future.tail(12))


# ============================================================
# 8. GENERATE FORECAST
# ============================================================

print("\nGenerating forecast...")

forecast = model.predict(future)

print("Forecast generated successfully.")


# ============================================================
# 9. EXTRACT FINAL 12 MONTHS
# ============================================================

forecast_test = forecast[
    ["ds", "yhat"]
].tail(12).reset_index(drop=True)

actual = test[
    "y"
].reset_index(drop=True)

months = test[
    "ds"
].reset_index(drop=True)


# ============================================================
# 10. CALCULATE METRICS
# ============================================================

prediction = forecast_test["yhat"]

error = actual - prediction

mae = np.mean(
    np.abs(error)
)

rmse = np.sqrt(
    np.mean(error ** 2)
)

mape = (
    np.mean(
        np.abs(error / actual)
    )
    * 100
)


# ============================================================
# 11. CREATE RESULTS TABLE
# ============================================================

results = pd.DataFrame({
    "month": months,
    "actual": actual,
    "prediction": prediction
})


# ============================================================
# 12. PRINT RESULTS
# ============================================================

print("\n" + "=" * 60)
print("PROPHET RESULTS")
print("=" * 60)

print("\nMAE:", mae)

print("RMSE:", rmse)

print("MAPE:", mape, "%")

print("\nPredictions:")

print(results.to_string(index=False))


# ============================================================
# 13. COMPLETED
# ============================================================

print("\n" + "=" * 60)
print("PROPHET COMPLETED")
print("=" * 60)