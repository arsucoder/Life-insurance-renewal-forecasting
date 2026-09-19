# ================================================================
# ALL INSURERS - DEFAULT PROPHET VS TUNED PROPHET
# ================================================================

import os
import warnings
import pandas as pd
import numpy as np

from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")


# ================================================================
# CONFIGURATION
# ================================================================

DATA_PATH = "data/processed/monthly_by_insurer.csv"

OUTPUT_DIR = "reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET = "renewed_premium"

INSURERS = [
    "Aditya Birla Sun Life",
    "Bajaj Allianz",
    "HDFC Life",
    "ICICI Prudential",
    "LIC",
    "Max Life",
    "SBI Life",
    "Tata AIA"
]


# ================================================================
# LOAD DATA
# ================================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

df = pd.read_csv(DATA_PATH)

df["collection_month"] = pd.to_datetime(df["collection_month"])

df = df.sort_values(["insurer", "collection_month"])

print("Shape:", df.shape)
print("Insurers:", df["insurer"].unique())


# ================================================================
# METRIC FUNCTION
# ================================================================

def calculate_metrics(actual, prediction):

    mae = mean_absolute_error(actual, prediction)

    rmse = np.sqrt(
        mean_squared_error(actual, prediction)
    )

    mape = np.mean(
        np.abs(
            (actual - prediction) / actual
        )
    ) * 100

    return mae, rmse, mape


# ================================================================
# PROPHET FORECAST FUNCTION
# ================================================================

def run_prophet(
    train_df,
    test_df,
    changepoint_prior_scale=0.05,
    seasonality_prior_scale=10,
    seasonality_mode="additive",
    yearly_seasonality=True
):

    prophet_train = train_df[
        ["collection_month", TARGET]
    ].copy()

    prophet_train = prophet_train.rename(
        columns={
            "collection_month": "ds",
            TARGET: "y"
        }
    )

    model = Prophet(
        changepoint_prior_scale=changepoint_prior_scale,
        seasonality_prior_scale=seasonality_prior_scale,
        seasonality_mode=seasonality_mode,
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=False,
        daily_seasonality=False
    )

    model.fit(prophet_train)

    future = test_df[
        ["collection_month"]
    ].copy()

    future = future.rename(
        columns={
            "collection_month": "ds"
        }
    )

    forecast = model.predict(future)

    prediction = forecast["yhat"].values

    return prediction


# ================================================================
# MAIN LOOP
# ================================================================

all_results = []

print()
print("=" * 70)
print("STARTING ALL INSURER PROPHET COMPARISON")
print("=" * 70)


for insurer in INSURERS:

    print()
    print("#" * 70)
    print(f"INSURER: {insurer}")
    print("#" * 70)

    # ------------------------------------------------------------
    # FILTER INSURER
    # ------------------------------------------------------------

    insurer_df = df[
        df["insurer"] == insurer
    ].copy()

    insurer_df = insurer_df.sort_values(
        "collection_month"
    ).reset_index(drop=True)

    print("Observations:", len(insurer_df))

    # ------------------------------------------------------------
    # SAFETY CHECK
    # ------------------------------------------------------------

    if len(insurer_df) < 48:

        print(
            f"Skipping {insurer}: "
            f"expected 48 observations."
        )

        continue

    # ------------------------------------------------------------
    # TRAIN / VALIDATION / TEST
    # ------------------------------------------------------------

    train = insurer_df.iloc[:24].copy()

    validation = insurer_df.iloc[24:36].copy()

    test = insurer_df.iloc[36:48].copy()

    print(
        "Training:",
        train["collection_month"].min(),
        "to",
        train["collection_month"].max()
    )

    print(
        "Validation:",
        validation["collection_month"].min(),
        "to",
        validation["collection_month"].max()
    )

    print(
        "Test:",
        test["collection_month"].min(),
        "to",
        test["collection_month"].max()
    )

    # ============================================================
    # DEFAULT PROPHET
    # ============================================================

    print()
    print("-" * 70)
    print("DEFAULT PROPHET")
    print("-" * 70)

    default_prediction = run_prophet(
        train_df=train,
        test_df=test,
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10,
        seasonality_mode="additive",
        yearly_seasonality=False
    )

    default_mae, default_rmse, default_mape = calculate_metrics(
        test[TARGET].values,
        default_prediction
    )

    print("MAE :", default_mae)
    print("RMSE:", default_rmse)
    print("MAPE:", default_mape)

    # ============================================================
    # PROPHET TUNING
    # ============================================================

    print()
    print("-" * 70)
    print("TUNING PROPHET")
    print("-" * 70)

    configurations = [

        {
            "name": "Default",
            "changepoint_prior_scale": 0.05,
            "seasonality_prior_scale": 10,
            "seasonality_mode": "additive"
        },

        {
            "name": "Flexible_Trend",
            "changepoint_prior_scale": 0.10,
            "seasonality_prior_scale": 10,
            "seasonality_mode": "additive"
        },

        {
            "name": "Strong_Trend",
            "changepoint_prior_scale": 0.50,
            "seasonality_prior_scale": 10,
            "seasonality_mode": "additive"
        },

        {
            "name": "Flexible_Seasonality",
            "changepoint_prior_scale": 0.05,
            "seasonality_prior_scale": 20,
            "seasonality_mode": "additive"
        },

        {
            "name": "Multiplicative",
            "changepoint_prior_scale": 0.05,
            "seasonality_prior_scale": 10,
            "seasonality_mode": "multiplicative"
        },

        {
            "name": "Flexible_Multiplicative",
            "changepoint_prior_scale": 0.10,
            "seasonality_prior_scale": 20,
            "seasonality_mode": "multiplicative"
        }
    ]

    validation_results = []

    # ------------------------------------------------------------
    # VALIDATION LOOP
    # ------------------------------------------------------------

    for config in configurations:

        print(
            f"\nTesting: {config['name']}"
        )

        validation_prediction = run_prophet(
            train_df=train,
            test_df=validation,
            changepoint_prior_scale=
                config["changepoint_prior_scale"],
            seasonality_prior_scale=
                config["seasonality_prior_scale"],
            seasonality_mode=
                config["seasonality_mode"],
            yearly_seasonality=False
        )

        mae, rmse, mape = calculate_metrics(
            validation[TARGET].values,
            validation_prediction
        )

        print("MAE :", mae)
        print("RMSE:", rmse)
        print("MAPE:", mape)

        validation_results.append({

            "insurer": insurer,

            "model": config["name"],

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
    # SELECT BEST MODEL
    # ============================================================

    validation_df = pd.DataFrame(
        validation_results
    )

    validation_df = validation_df.sort_values(
        "MAPE"
    ).reset_index(drop=True)

    best_model = validation_df.iloc[0]

    print()
    print("-" * 70)
    print("BEST TUNED MODEL")
    print("-" * 70)

    print(
        "Model:",
        best_model["model"]
    )

    print(
        "Changepoint:",
        best_model["changepoint_prior_scale"]
    )

    print(
        "Seasonality:",
        best_model["seasonality_prior_scale"]
    )

    print(
        "Mode:",
        best_model["seasonality_mode"]
    )

    print(
        "Validation MAPE:",
        best_model["MAPE"]
    )

    # ============================================================
    # RETRAIN BEST MODEL ON 36 MONTHS
    # ============================================================

    print()
    print("-" * 70)
    print("RETRAINING BEST MODEL ON 36 MONTHS")
    print("-" * 70)

    full_train = insurer_df.iloc[:36].copy()

    tuned_prediction = run_prophet(
        train_df=full_train,
        test_df=test,

        changepoint_prior_scale=
            best_model["changepoint_prior_scale"],

        seasonality_prior_scale=
            best_model["seasonality_prior_scale"],

        seasonality_mode=
            best_model["seasonality_mode"],

        yearly_seasonality=False
    )

    tuned_mae, tuned_rmse, tuned_mape = calculate_metrics(
        test[TARGET].values,
        tuned_prediction
    )

    print()
    print("FINAL TEST RESULTS")

    print("MAE :", tuned_mae)
    print("RMSE:", tuned_rmse)
    print("MAPE:", tuned_mape)

    # ============================================================
    # SAVE INSURER RESULT
    # ============================================================

    all_results.append({

        "Insurer": insurer,

        "Default Prophet MAE":
            default_mae,

        "Default Prophet RMSE":
            default_rmse,

        "Default Prophet MAPE":
            default_mape,

        "Tuned Prophet MAE":
            tuned_mae,

        "Tuned Prophet RMSE":
            tuned_rmse,

        "Tuned Prophet MAPE":
            tuned_mape,

        "Best Changepoint Prior Scale":
            best_model["changepoint_prior_scale"],

        "Best Seasonality Prior Scale":
            best_model["seasonality_prior_scale"],

        "Best Seasonality Mode":
            best_model["seasonality_mode"]
    })


# ================================================================
# FINAL COMPARISON TABLE
# ================================================================

results_df = pd.DataFrame(all_results)

results_df = results_df.sort_values(
    "Tuned Prophet MAPE"
).reset_index(drop=True)


print()
print()
print("=" * 90)
print("ALL INSURERS - PROPHET MODEL COMPARISON")
print("=" * 90)

print(
    results_df[
        [
            "Insurer",
            "Default Prophet MAE",
            "Tuned Prophet MAE",
            "Default Prophet MAPE",
            "Tuned Prophet MAPE"
        ]
    ].to_string(index=False)
)


# ================================================================
# SAVE RESULTS
# ================================================================

output_file = os.path.join(
    OUTPUT_DIR,
    "all_insurers_prophet_comparison.csv"
)

results_df.to_csv(
    output_file,
    index=False
)


print()
print("=" * 90)
print("COMPLETED")
print("=" * 90)

print(
    f"Saved comparison to: {output_file}"
)