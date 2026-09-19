from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


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


# ============================================================
# 3. TRAIN / TEST SPLIT
# ============================================================

TEST_SIZE = 12

train = df.iloc[:-TEST_SIZE].copy()
test = df.iloc[-TEST_SIZE:].copy()

y_train = train[TARGET]
y_test = test[TARGET]


print("=" * 60)
print("ARIMA FORECASTING")
print("=" * 60)

print("\nTraining period:")
print(train["collection_month"].min(), "to",
      train["collection_month"].max())

print("Training observations:", len(train))

print("\nTesting period:")
print(test["collection_month"].min(), "to",
      test["collection_month"].max())

print("Testing observations:", len(test))


# ============================================================
# 4. FIT ARIMA MODEL
# ============================================================

# Start with a simple ARIMA(1,1,1)

ORDER = (1, 1, 1)

print("\nARIMA order:", ORDER)

model = ARIMA(
    y_train,
    order=ORDER
)

model_fit = model.fit()


# ============================================================
# 5. FORECAST
# ============================================================

forecast = model_fit.forecast(
    steps=len(test)
)


# ============================================================
# 6. EVALUATION
# ============================================================

actual = y_test.to_numpy()
prediction = np.asarray(forecast)

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


# ============================================================
# 7. RESULTS
# ============================================================

results = pd.DataFrame({
    "month": test["collection_month"],
    "actual": actual,
    "prediction": prediction
})

print("\n" + "=" * 60)
print("ARIMA RESULTS")
print("=" * 60)

print("\nMAE:", mae)
print("RMSE:", rmse)
print("MAPE:", mape, "%")

print("\nPredictions:")
print(results)


# ============================================================
# 8. COMPLETION
# ============================================================

print("\n" + "=" * 60)
print("ARIMA COMPLETED")
print("=" * 60)