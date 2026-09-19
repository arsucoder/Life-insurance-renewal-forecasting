# ================================================================
# ALL INSURERS - ALL FORECASTING MODELS
# Fair 24 / 12 / 12 evaluation
#
# Models:
#   1. Naive
#   2. Seasonal Naive
#   3. ARIMA
#   4. Tuned SARIMA
#   5. Default Prophet
#   6. Tuned Prophet
#
# Data:
#   data/processed/monthly_by_insurer.csv
#
# Target:
#   renewed_premium
# ================================================================

import os
import warnings
import numpy as np
import pandas as pd

from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet

warnings.filterwarnings("ignore")


# ================================================================
# CONFIGURATION
# ================================================================

DATA_PATH = "./data/processed/monthly_by_insurer.csv"

REPORT_DIR = "./reports"

RAW_RESULTS_PATH = (
    "./reports/all_insurers_all_models_comparison.csv"
)

WIDE_RESULTS_PATH = (
    "./reports/all_insurers_model_comparison_wide.csv"
)

TARGET = "renewed_premium"

SEASONAL_PERIOD = 12


# ================================================================
# METRICS
# ================================================================

def calculate_metrics(actual, predicted):

    actual = np.array(actual, dtype=float)
    predicted = np.array(predicted, dtype=float)

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    # Avoid division by zero
    non_zero = actual != 0

    if np.any(non_zero):
        mape = np.mean(
            np.abs(
                (actual[non_zero] - predicted[non_zero])
                / actual[non_zero]
            )
        ) * 100
    else:
        mape = np.nan

    return mae, rmse, mape


# ================================================================
# PREPARE DATA
# ================================================================

def prepare_data(df, insurer):

    data = df[df["insurer"] == insurer].copy()

    data["collection_month"] = pd.to_datetime(
        data["collection_month"]
    )

    data = data.sort_values("collection_month")

    # Keep only required columns
    data = data[
        ["collection_month", TARGET]
    ].copy()

    data[TARGET] = pd.to_numeric(
        data[TARGET],
        errors="coerce"
    )

    data = data.dropna()

    # Monthly frequency
    data = data.set_index("collection_month")

    data = data.asfreq("MS")

    return data


# ================================================================
# NAIVE
# ================================================================

def naive_forecast(train, test):

    last_value = train.iloc[-1]

    predictions = np.repeat(
        last_value,
        len(test)
    )

    return predictions


# ================================================================
# SEASONAL NAIVE
# ================================================================

def seasonal_naive_forecast(
    train,
    test,
    seasonal_period=12
):

    predictions = []

    for i in range(len(test)):

        if len(train) >= seasonal_period:

            prediction = train.iloc[
                -seasonal_period + (i % seasonal_period)
            ]

        else:

            prediction = train.iloc[-1]

        predictions.append(prediction)

    return np.array(predictions)


# ================================================================
# ARIMA
# ================================================================

def arima_forecast(
    train,
    test,
    order=(1, 1, 1)
):

    model = ARIMA(
        train,
        order=order
    )

    fitted_model = model.fit()

    forecast = fitted_model.forecast(
        steps=len(test)
    )

    return np.array(forecast)


# ================================================================
# SARIMA
# ================================================================

def sarima_forecast(
    train,
    test,
    order,
    seasonal_order
):

    model = SARIMAX(
        train,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    fitted_model = model.fit(
        disp=False
    )

    forecast = fitted_model.forecast(
        steps=len(test)
    )

    return np.array(forecast)


# ================================================================
# TUNED SARIMA
# ================================================================

def tune_sarima(
    train,
    validation
):

    candidates = [

        ((0, 1, 1), (0, 0, 1, 12)),

        ((0, 1, 1), (1, 0, 0, 12)),

        ((1, 1, 0), (0, 0, 1, 12)),

        ((1, 1, 0), (1, 0, 0, 12)),

        ((1, 1, 1), (0, 0, 1, 12)),

        ((1, 1, 1), (1, 0, 0, 12)),
    ]

    results = []

    for order, seasonal_order in candidates:

        try:

            prediction = sarima_forecast(
                train,
                validation,
                order,
                seasonal_order
            )

            mae, rmse, mape = calculate_metrics(
                validation,
                prediction
            )

            results.append({
                "order": order,
                "seasonal_order": seasonal_order,
                "MAE": mae,
                "RMSE": rmse,
                "MAPE": mape
            })

        except Exception as e:

            print(
                f"SARIMA failed: "
                f"{order} {seasonal_order}"
            )

    results_df = pd.DataFrame(results)

    if results_df.empty:
        return (1, 1, 1), (1, 0, 0, 12)

    results_df = results_df.sort_values(
        "MAPE"
    )

    best = results_df.iloc[0]

    return (
        best["order"],
        best["seasonal_order"]
    )


# ================================================================
# DEFAULT PROPHET
# ================================================================

def prophet_forecast(
    train,
    test,
    changepoint_prior_scale=0.05,
    seasonality_prior_scale=10,
    seasonality_mode="additive"
):

    prophet_train = pd.DataFrame({
        "ds": train.index,
        "y": train.values
    })

    model = Prophet(
        changepoint_prior_scale=changepoint_prior_scale,
        seasonality_prior_scale=seasonality_prior_scale,
        seasonality_mode=seasonality_mode,
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )

    model.fit(
        prophet_train
    )

    future = pd.DataFrame({
        "ds": test.index
    })

    forecast = model.predict(
        future
    )

    return forecast["yhat"].values


# ================================================================
# TUNED PROPHET
# ================================================================

def tune_prophet(
    train,
    validation
):

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

    results = []

    for config in configurations:

        print(
            f"Testing Prophet: "
            f"{config['name']}"
        )

        try:

            prediction = prophet_forecast(
                train,
                validation,
                config[
                    "changepoint_prior_scale"
                ],
                config[
                    "seasonality_prior_scale"
                ],
                config[
                    "seasonality_mode"
                ]
            )

            mae, rmse, mape = calculate_metrics(
                validation,
                prediction
            )

            results.append({
                "name": config["name"],
                "changepoint_prior_scale":
                    config[
                        "changepoint_prior_scale"
                    ],
                "seasonality_prior_scale":
                    config[
                        "seasonality_prior_scale"
                    ],
                "seasonality_mode":
                    config[
                        "seasonality_mode"
                    ],
                "MAE": mae,
                "RMSE": rmse,
                "MAPE": mape
            })

        except Exception as e:

            print(
                "Prophet failed:",
                e
            )

    results_df = pd.DataFrame(results)

    if results_df.empty:

        return configurations[0]

    results_df = results_df.sort_values(
        "MAPE"
    )

    best = results_df.iloc[0]

    return {
        "name": best["name"],
        "changepoint_prior_scale":
            best[
                "changepoint_prior_scale"
            ],
        "seasonality_prior_scale":
            best[
                "seasonality_prior_scale"
            ],
        "seasonality_mode":
            best[
                "seasonality_mode"
            ]
    }


# ================================================================
# MAIN
# ================================================================

def main():

    print("=" * 80)
    print("ALL INSURERS - ALL FORECASTING MODELS")
    print("=" * 80)

    # ------------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------------

    print("\nLoading data...")

    df = pd.read_csv(
        DATA_PATH
    )

    print(
        "Shape:",
        df.shape
    )

    print(
        "Columns:",
        df.columns.tolist()
    )

    insurers = df[
        "insurer"
    ].unique()

    print(
        "\nInsurers:",
        insurers
    )

    all_results = []

    # ============================================================
    # EACH INSURER
    # ============================================================

    for insurer in insurers:

        print("\n")
        print("#" * 80)
        print(
            f"INSURER: {insurer}"
        )
        print("#" * 80)

        data = prepare_data(
            df,
            insurer
        )

        print(
            "Observations:",
            len(data)
        )

        if len(data) < 48:

            print(
                "WARNING: Expected 48 observations."
            )

        # --------------------------------------------------------
        # 24 / 12 / 12 SPLIT
        # --------------------------------------------------------

        train = data.iloc[:24][TARGET]

        validation = data.iloc[24:36][TARGET]

        test = data.iloc[36:48][TARGET]

        print(
            "\nTrain:",
            train.index.min(),
            "to",
            train.index.max()
        )

        print(
            "Validation:",
            validation.index.min(),
            "to",
            validation.index.max()
        )

        print(
            "Test:",
            test.index.min(),
            "to",
            test.index.max()
        )

        # ========================================================
        # 1. NAIVE
        # ========================================================

        print("\nNaive...")

        # Tune nothing.
        # Retrain on train + validation.
        train_36 = pd.concat(
            [train, validation]
        )

        naive_prediction = naive_forecast(
            train_36,
            test
        )

        mae, rmse, mape = calculate_metrics(
            test,
            naive_prediction
        )

        all_results.append({
            "Insurer": insurer,
            "Model": "Naive",
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape
        })

        # ========================================================
        # 2. SEASONAL NAIVE
        # ========================================================

        print(
            "Seasonal Naive..."
        )

        seasonal_prediction = (
            seasonal_naive_forecast(
                train_36,
                test,
                12
            )
        )

        mae, rmse, mape = calculate_metrics(
            test,
            seasonal_prediction
        )

        all_results.append({
            "Insurer": insurer,
            "Model": "Seasonal Naive",
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape
        })

        # ========================================================
        # 3. ARIMA
        # ========================================================

        print(
            "ARIMA..."
        )

        arima_prediction = arima_forecast(
            train_36,
            test,
            (1, 1, 1)
        )

        mae, rmse, mape = calculate_metrics(
            test,
            arima_prediction
        )

        all_results.append({
            "Insurer": insurer,
            "Model": "ARIMA",
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape
        })

        # ========================================================
        # 4. TUNED SARIMA
        # ========================================================

        print(
            "\nTuning SARIMA..."
        )

        best_order, best_seasonal_order = (
            tune_sarima(
                train,
                validation
            )
        )

        print(
            "Best SARIMA:",
            best_order,
            best_seasonal_order
        )

        tuned_sarima_prediction = (
            sarima_forecast(
                train_36,
                test,
                best_order,
                best_seasonal_order
            )
        )

        mae, rmse, mape = calculate_metrics(
            test,
            tuned_sarima_prediction
        )

        all_results.append({
            "Insurer": insurer,
            "Model": "Tuned SARIMA",
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape
        })

        # ========================================================
        # 5. DEFAULT PROPHET
        # ========================================================

        print(
            "\nDefault Prophet..."
        )

        default_prophet_prediction = (
            prophet_forecast(
                train_36,
                test,
                0.05,
                10,
                "additive"
            )
        )

        mae, rmse, mape = calculate_metrics(
            test,
            default_prophet_prediction
        )

        all_results.append({
            "Insurer": insurer,
            "Model": "Default Prophet",
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape
        })

        # ========================================================
        # 6. TUNED PROPHET
        # ========================================================

        print(
            "\nTuning Prophet..."
        )

        best_prophet = tune_prophet(
            train,
            validation
        )

        print(
            "\nBest Prophet:",
            best_prophet
        )

        tuned_prophet_prediction = (
            prophet_forecast(
                train_36,
                test,
                best_prophet[
                    "changepoint_prior_scale"
                ],
                best_prophet[
                    "seasonality_prior_scale"
                ],
                best_prophet[
                    "seasonality_mode"
                ]
            )
        )

        mae, rmse, mape = calculate_metrics(
            test,
            tuned_prophet_prediction
        )

        all_results.append({
            "Insurer": insurer,
            "Model": "Tuned Prophet",
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape
        })

        print(
            f"\nCompleted: {insurer}"
        )

    # ============================================================
    # CREATE RESULTS DATAFRAME
    # ============================================================

    results_df = pd.DataFrame(
        all_results
    )

    # Sort insurer + MAPE
    results_df = results_df.sort_values(
        ["Insurer", "MAPE"]
    )

    # ============================================================
    # SAVE RAW LONG FORMAT
    # ============================================================

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    results_df.to_csv(
        RAW_RESULTS_PATH,
        index=False
    )

    # ============================================================
    # CREATE WIDE TABLE
    # ============================================================

    wide = results_df.pivot(
        index="Insurer",
        columns="Model",
        values="MAPE"
    )

    # ------------------------------------------------------------
    # Rename columns
    # ------------------------------------------------------------

    wide = wide.rename(
        columns={
            "Naive": "Naive MAPE",
            "Seasonal Naive":
                "Seasonal Naive MAPE",
            "ARIMA":
                "ARIMA MAPE",
            "Tuned SARIMA":
                "Tuned SARIMA MAPE",
            "Default Prophet":
                "Default Prophet MAPE",
            "Tuned Prophet":
                "Tuned Prophet MAPE"
        }
    )

    # ------------------------------------------------------------
    # Find best model based on test MAPE
    # ------------------------------------------------------------

    model_columns = [
        "Naive MAPE",
        "Seasonal Naive MAPE",
        "ARIMA MAPE",
        "Tuned SARIMA MAPE",
        "Default Prophet MAPE",
        "Tuned Prophet MAPE"
    ]

    wide["Best Model"] = wide[
        model_columns
    ].idxmin(axis=1)

    wide["Best Model"] = (
        wide["Best Model"]
        .str.replace(
            " MAPE",
            "",
            regex=False
        )
    )

    wide["Best Test MAPE"] = wide[
        model_columns
    ].min(axis=1)

    # Put Best Model first
    wide = wide[
        [
            "Best Model",
            "Best Test MAPE"
        ] + model_columns
    ]

    wide = wide.sort_values(
        "Best Test MAPE"
    )

    # Save
    wide.to_csv(
        WIDE_RESULTS_PATH
    )

    # ============================================================
    # DISPLAY FINAL RESULTS
    # ============================================================

    print("\n")
    print("=" * 100)
    print(
        "ALL INSURERS - ALL FORECASTING MODELS"
    )
    print("=" * 100)

    display_df = results_df.copy()

    display_df["MAE"] = (
        display_df["MAE"]
        .round(2)
    )

    display_df["RMSE"] = (
        display_df["RMSE"]
        .round(2)
    )

    display_df["MAPE"] = (
        display_df["MAPE"]
        .round(4)
    )

    print(
        display_df.to_string(
            index=False
        )
    )

    print("\n")
    print("=" * 100)
    print(
        "INSURER-WISE MODEL COMPARISON"
    )
    print("=" * 100)

    print(
        wide.round(4).to_string()
    )

    print("\n")
    print("=" * 100)
    print("FILES SAVED")
    print("=" * 100)

    print(
        RAW_RESULTS_PATH
    )

    print(
        WIDE_RESULTS_PATH
    )

    print("\nDONE.")


# ================================================================
# RUN
# ================================================================

if __name__ == "__main__":
    main()