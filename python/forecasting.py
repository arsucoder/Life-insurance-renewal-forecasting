from pathlib import Path

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
# 2. LOAD MONTHLY DATA
# ============================================================

df = pd.read_csv(
    MONTHLY_PATH,
    parse_dates=["collection_month"]
)

df = df.sort_values("collection_month").reset_index(drop=True)

TARGET = "renewed_premium"


print("=" * 60)
print("FORECASTING DATA PREPARATION")
print("=" * 60)

print("\nTotal observations:", len(df))
print("Start:", df["collection_month"].min())
print("End:", df["collection_month"].max())
print("Target:", TARGET)


# ============================================================
# 3. ONE-MONTH-AHEAD FORECASTING
# ============================================================

print("\n" + "=" * 60)
print("ONE-MONTH-AHEAD FORECASTING")
print("=" * 60)

INITIAL_TRAIN_SIZE = 24

one_step_results = []

for i in range(INITIAL_TRAIN_SIZE, len(df)):

    train = df.iloc[:i]

    test = df.iloc[i]

    one_step_results.append({
        "train_start": train["collection_month"].iloc[0],
        "train_end": train["collection_month"].iloc[-1],
        "test_month": test["collection_month"],
        "actual": test[TARGET]
    })

one_step_df = pd.DataFrame(one_step_results)

print("Initial training observations:", INITIAL_TRAIN_SIZE)
print("One-step forecast periods:", len(one_step_df))

print("\nFirst 5 one-step forecast periods:")
print(one_step_df.head())

print("\nLast 5 one-step forecast periods:")
print(one_step_df.tail())


# ============================================================
# 4. 12-MONTH-AHEAD FORECASTING
# ============================================================

print("\n" + "=" * 60)
print("12-MONTH-AHEAD FORECASTING")
print("=" * 60)

TEST_SIZE = 12

train_12m = df.iloc[:-TEST_SIZE].copy()
test_12m = df.iloc[-TEST_SIZE:].copy()

print("\nTraining data:")
print("Start:", train_12m["collection_month"].min())
print("End:", train_12m["collection_month"].max())
print("Observations:", len(train_12m))

print("\nTest data:")
print("Start:", test_12m["collection_month"].min())
print("End:", test_12m["collection_month"].max())
print("Observations:", len(test_12m))


# ============================================================
# 5. TARGET SERIES
# ============================================================

y_train_12m = train_12m[TARGET]
y_test_12m = test_12m[TARGET]

print("\nTraining target shape:", y_train_12m.shape)
print("Test target shape:", y_test_12m.shape)


# ============================================================
# 6. COMPLETION
# ============================================================

print("\n" + "=" * 60)
print("FORECASTING DATA PREPARATION COMPLETED")
print("=" * 60)