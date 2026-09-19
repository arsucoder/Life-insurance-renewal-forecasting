from pathlib import Path

import numpy as np
import pandas as pd


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

df = df.sort_values("collection_month").reset_index(drop=True)

TARGET = "renewed_premium"


# ============================================================
# 3. EVALUATION METRICS
# ============================================================

def calculate_metrics(actual, prediction):

    actual = np.asarray(actual, dtype=float)
    prediction = np.asarray(prediction, dtype=float)

    error = actual - prediction

    mae = np.mean(np.abs(error))

    rmse = np.sqrt(np.mean(error ** 2))

    mape = np.mean(
        np.abs(error / actual)
    ) * 100

    return mae, rmse, mape


# ============================================================
# 4. ONE-MONTH-AHEAD NAIVE BASELINE
# ============================================================

print("=" * 60)
print("ONE-MONTH-AHEAD NAIVE BASELINE")
print("=" * 60)

INITIAL_TRAIN_SIZE = 24

one_step_predictions = []

for i in range(INITIAL_TRAIN_SIZE, len(df)):

    train = df.iloc[:i]

    test = df.iloc[i]

    prediction = train[TARGET].iloc[-1]

    one_step_predictions.append({
        "month": test["collection_month"],
        "actual": test[TARGET],
        "prediction": prediction
    })

one_step_df = pd.DataFrame(one_step_predictions)

mae, rmse, mape = calculate_metrics(
    one_step_df["actual"],
    one_step_df["prediction"]
)

print("\nNumber of forecasts:", len(one_step_df))

print("\nMAE:", mae)
print("RMSE:", rmse)
print("MAPE:", mape, "%")

print("\nFirst 5 predictions:")
print(one_step_df.head())

print("\nLast 5 predictions:")
print(one_step_df.tail())


# ============================================================
# 5. 12-MONTH NAIVE BASELINE
# ============================================================

print("\n" + "=" * 60)
print("12-MONTH NAIVE BASELINE")
print("=" * 60)

TEST_SIZE = 12

train_12m = df.iloc[:-TEST_SIZE].copy()
test_12m = df.iloc[-TEST_SIZE:].copy()

last_training_value = train_12m[TARGET].iloc[-1]

test_12m["prediction"] = last_training_value

mae, rmse, mape = calculate_metrics(
    test_12m[TARGET],
    test_12m["prediction"]
)

print("\nTraining last value:", last_training_value)

print("\nNumber of forecasts:", len(test_12m))

print("\nMAE:", mae)
print("RMSE:", rmse)
print("MAPE:", mape, "%")

print("\n12-month predictions:")
print(
    test_12m[
        [
            "collection_month",
            TARGET,
            "prediction"
        ]
    ]
)


# ============================================================
# 6. SEASONAL NAIVE BASELINE
# ============================================================

print("\n" + "=" * 60)
print("SEASONAL NAIVE BASELINE")
print("=" * 60)

# Use the same calendar month from the previous year.

train_seasonal = df.iloc[:-TEST_SIZE].copy()
test_seasonal = df.iloc[-TEST_SIZE:].copy()

train_seasonal["month"] = (
    train_seasonal["collection_month"].dt.month
)

test_seasonal["month"] = (
    test_seasonal["collection_month"].dt.month
)

seasonal_lookup = (
    train_seasonal
    .groupby("month")[TARGET]
    .last()
)

test_seasonal["prediction"] = (
    test_seasonal["month"]
    .map(seasonal_lookup)
)

print("\nMissing seasonal predictions:")
print(test_seasonal["prediction"].isna().sum())

mae, rmse, mape = calculate_metrics(
    test_seasonal[TARGET],
    test_seasonal["prediction"]
)

print("\nNumber of forecasts:", len(test_seasonal))

print("\nMAE:", mae)
print("RMSE:", rmse)
print("MAPE:", mape, "%")

print("\nSeasonal naive predictions:")

print(
    test_seasonal[
        [
            "collection_month",
            TARGET,
            "prediction"
        ]
    ]
)


# ============================================================
# 7. ONE-MONTH-AHEAD SEASONAL NAIVE
# ============================================================

print("\n" + "=" * 60)
print("ONE-MONTH-AHEAD SEASONAL NAIVE BASELINE")
print("=" * 60)

seasonal_one_step = []

for i in range(INITIAL_TRAIN_SIZE, len(df)):

    train = df.iloc[:i].copy()

    test = df.iloc[i]

    train["month"] = (
        train["collection_month"].dt.month
    )

    test_month = test["collection_month"].month

    historical_values = train.loc[
        train["month"] == test_month,
        TARGET
    ]

    prediction = historical_values.iloc[-1]

    seasonal_one_step.append({
        "month": test["collection_month"],
        "actual": test[TARGET],
        "prediction": prediction
    })

seasonal_one_step_df = pd.DataFrame(
    seasonal_one_step
)

mae, rmse, mape = calculate_metrics(
    seasonal_one_step_df["actual"],
    seasonal_one_step_df["prediction"]
)

print("\nNumber of forecasts:",
      len(seasonal_one_step_df))

print("\nMAE:", mae)
print("RMSE:", rmse)
print("MAPE:", mape, "%")

print("\nFirst 5 predictions:")
print(seasonal_one_step_df.head())

print("\nLast 5 predictions:")
print(seasonal_one_step_df.tail())


# ============================================================
# 8. COMPLETION
# ============================================================

print("\n" + "=" * 60)
print("BASELINE COMPLETED")
print("=" * 60)