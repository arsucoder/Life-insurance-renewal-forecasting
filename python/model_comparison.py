from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "monthly_renewal_premium.csv"
)

REPORTS_DIR = BASE_DIR / "reports"

FIGURES_DIR = REPORTS_DIR / "figures"

FIGURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. FINAL TEST DATA
# ============================================================

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["collection_month"]
)

df = (
    df
    .sort_values("collection_month")
    .reset_index(drop=True)
)

test = df.iloc[36:].copy()

test_months = test["collection_month"]

actual = test["renewed_premium"].values


# ============================================================
# 3. MODEL RESULTS
# ============================================================

# These are the FINAL TEST metrics from our completed models.

model_results = [
    {
        "Model": "Naive",
        "MAE": 14874481983.333334,
        "RMSE": 19101806791.039055,
        "MAPE": 4.436415856336238
    },
    {
        "Model": "12-Month Naive",
        "MAE": 25416396125.0,
        "RMSE": 27496626047.755417,
        "MAPE": 7.163009837744476
    },
    {
        "Model": "Seasonal Naive",
        "MAE": 28553218350.0,
        "RMSE": 31421093693.343124,
        "MAPE": 8.039646810485142
    },
    {
        "Model": "ARIMA",
        "MAE": 25509739203.273468,
        "RMSE": 27599001636.399776,
        "MAPE": 7.189009325524126
    },
    {
        "Model": "Tuned SARIMA",
        "MAE": 18415493599.875217,
        "RMSE": 20760307849.919262,
        "MAPE": 5.22712298573433
    },
    {
        "Model": "Prophet",
        "MAE": 13281770658.367975,
        "RMSE": 15563594847.849695,
        "MAPE": 3.8548898245912824
    },
    {
        "Model": "Tuned Prophet",
        "MAE": 8768972209.849472,
        "RMSE": 11319236161.220144,
        "MAPE": 2.4809796931947052
    }
]

comparison_df = pd.DataFrame(model_results)


# ============================================================
# 4. PRINT COMPARISON
# ============================================================

print("=" * 70)
print("FINAL MODEL COMPARISON")
print("=" * 70)

print(
    comparison_df.to_string(index=False)
)


# ============================================================
# 5. BEST MODEL BY EACH METRIC
# ============================================================

print("\n" + "=" * 70)
print("METRIC COMPARISON")
print("=" * 70)

best_mae = comparison_df.loc[
    comparison_df["MAE"].idxmin()
]

best_rmse = comparison_df.loc[
    comparison_df["RMSE"].idxmin()
]

best_mape = comparison_df.loc[
    comparison_df["MAPE"].idxmin()
]

print(
    "\nLowest MAE:",
    best_mae["Model"]
)

print(
    "MAE:",
    best_mae["MAE"]
)

print(
    "\nLowest RMSE:",
    best_rmse["Model"]
)

print(
    "RMSE:",
    best_rmse["RMSE"]
)

print(
    "\nLowest MAPE:",
    best_mape["Model"]
)

print(
    "MAPE:",
    best_mape["MAPE"],
    "%"
)


# ============================================================
# 6. SAVE COMPARISON TABLE
# ============================================================

comparison_path = (
    REPORTS_DIR
    / "forecast_model_comparison.csv"
)

comparison_df.to_csv(
    comparison_path,
    index=False
)

print(
    "\nComparison saved to:",
    comparison_path
)


# ============================================================
# 7. ACTUAL VS TUNED PROPHET
# ============================================================

# Final tuned Prophet predictions

tuned_prophet_prediction = np.array([
    3.409047e11,
    3.546151e11,
    3.441822e11,
    3.423622e11,
    3.697285e11,
    3.450346e11,
    3.370884e11,
    3.360977e11,
    3.602943e11,
    3.536593e11,
    3.160966e11,
    3.480402e11
])


plt.figure(figsize=(12, 6))

plt.plot(
    test_months,
    actual,
    marker="o",
    label="Actual"
)

plt.plot(
    test_months,
    tuned_prophet_prediction,
    marker="o",
    label="Tuned Prophet"
)

plt.title(
    "Actual vs Tuned Prophet - Renewed Premium"
)

plt.xlabel("Month")

plt.ylabel("Renewed Premium")

plt.xticks(
    rotation=45
)

plt.legend()

plt.tight_layout()


prophet_plot_path = (
    FIGURES_DIR
    / "actual_vs_tuned_prophet.png"
)

plt.savefig(
    prophet_plot_path,
    dpi=300
)

plt.close()

print(
    "Saved:",
    prophet_plot_path
)


# ============================================================
# 8. MODEL MAPE COMPARISON
# ============================================================

plt.figure(figsize=(12, 6))

plt.bar(
    comparison_df["Model"],
    comparison_df["MAPE"]
)

plt.title(
    "Forecasting Model Comparison - MAPE"
)

plt.xlabel("Model")

plt.ylabel("MAPE (%)")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()


mape_plot_path = (
    FIGURES_DIR
    / "forecast_model_mape_comparison.png"
)

plt.savefig(
    mape_plot_path,
    dpi=300
)

plt.close()

print(
    "Saved:",
    mape_plot_path
)


# ============================================================
# 9. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("MODEL COMPARISON COMPLETED")
print("=" * 70)