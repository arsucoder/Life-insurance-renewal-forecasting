import os
import warnings
import numpy as np
import pandas as pd

from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet

from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/processed/monthly_by_insurer.csv"

OUTPUT_FILE = (
    "reports/insurer_all_models_comparison.csv"
)

DATE_COL = "collection_month"
INSURER_COL = "insurer"
TARGET_COL = "renewed_premium"

TRAIN_END = "2024-03-01"
TEST_START = "2024-04-01"

SEASONAL_PERIOD = 12


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(actual, predicted):

    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    mae = mean_absolute_error(
        actual,
        predicted
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted
        )
    )

    mask = actual != 0

    mape = np.mean(
        np.abs(
            (actual[mask] - predicted[mask])
            / actual[mask]
        )
    ) * 100

    return mae, rmse, mape


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("LOADING DATA")
print("=" * 80)

df = pd.read_csv(INPUT_FILE)

print("Original columns:")
print(df.columns.tolist())

# Convert YYYY-MM into monthly timestamp
df[DATE_COL] = pd.to_datetime(
    df[DATE_COL].astype(str),
    format="%Y-%m"
)

df = df.sort_values(
    [INSURER_COL, DATE_COL]
)

print("\nShape:", df.shape)

print(
    "Insurers:",
    df[INSURER_COL].unique()
)

print(
    "Date range:",
    df[DATE_COL].min(),
    "to",
    df[DATE_COL].max()
)


# ============================================================
# CREATE REPORT DIRECTORY
# ============================================================

os.makedirs(
    "reports",
    exist_ok=True
)


# ============================================================
# RESULTS
# ============================================================

results = []


# ============================================================
# INSURER LOOP
# ============================================================

for insurer in df[INSURER_COL].unique():

    print("\n")
    print("#" * 80)
    print("INSURER:", insurer)
    print("#" * 80)

    insurer_df = df[
        df[INSURER_COL] == insurer
    ].copy()

    insurer_df = insurer_df.sort_values(
        DATE_COL
    )

    # --------------------------------------------------------
    # Create time series
    # --------------------------------------------------------

    insurer_df = insurer_df[
        [DATE_COL, TARGET_COL]
    ].dropna()

    insurer_df = insurer_df.set_index(
        DATE_COL
    )

    insurer_df = insurer_df.asfreq(
        "MS"
    )

    y = insurer_df[TARGET_COL]

    print(
        "Observations:",
        len(y)
    )

    # ========================================================
    # TRAIN / TEST
    # ========================================================

    train = y[
        y.index <= TRAIN_END
    ]

    test = y[
        y.index >= TEST_START
    ]

    print(
        "Training:",
        train.index.min(),
        "to",
        train.index.max()
    )

    print(
        "Training observations:",
        len(train)
    )

    print(
        "Testing:",
        test.index.min(),
        "to",
        test.index.max()
    )

    print(
        "Testing observations:",
        len(test)
    )

    actual = test.values


    # ========================================================
    # 1. NAIVE
    # ========================================================

    print("\n" + "-" * 70)
    print("NAIVE")
    print("-" * 70)

    naive_predictions = np.repeat(
        train.iloc[-1],
        len(test)
    )

    mae, rmse, mape = calculate_metrics(
        actual,
        naive_predictions
    )

    print(
        f"MAE  : {mae:,.2f}"
    )

    print(
        f"RMSE : {rmse:,.2f}"
    )

    print(
        f"MAPE : {mape:.4f}%"
    )

    results.append({
        "Insurer": insurer,
        "Model": "Naive",
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape
    })


    # ========================================================
    # 2. SEASONAL NAIVE
    # ========================================================

    print("\n" + "-" * 70)
    print("SEASONAL NAIVE")
    print("-" * 70)

    seasonal_predictions = []

    for date in test.index:

        previous_year = (
            date - pd.DateOffset(months=12)
        )

        if previous_year in train.index:

            prediction = train.loc[
                previous_year
            ]

        else:

            prediction = train.iloc[-1]

        seasonal_predictions.append(
            prediction
        )

    seasonal_predictions = np.array(
        seasonal_predictions
    )

    mae, rmse, mape = calculate_metrics(
        actual,
        seasonal_predictions
    )

    print(
        f"MAE  : {mae:,.2f}"
    )

    print(
        f"RMSE : {rmse:,.2f}"
    )

    print(
        f"MAPE : {mape:.4f}%"
    )

    results.append({
        "Insurer": insurer,
        "Model": "Seasonal Naive",
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape
    })


    # ========================================================
    # 3. ARIMA
    # ========================================================

    print("\n" + "-" * 70)
    print("ARIMA (1,1,1)")
    print("-" * 70)

    try:

        arima_model = ARIMA(
            train,
            order=(1, 1, 1)
        )

        arima_fit = arima_model.fit()

        arima_predictions = (
            arima_fit.forecast(
                steps=len(test)
            )
        )

        mae, rmse, mape = calculate_metrics(
            actual,
            arima_predictions
        )

        print(
            f"MAE  : {mae:,.2f}"
        )

        print(
            f"RMSE : {rmse:,.2f}"
        )

        print(
            f"MAPE : {mape:.4f}%"
        )

        results.append({
            "Insurer": insurer,
            "Model": "ARIMA",
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape
        })

    except Exception as e:

        print(
            "ARIMA failed:",
            e
        )


    # ========================================================
    # 4. TUNED SARIMA
    # ========================================================

    print("\n" + "-" * 70)
    print("TUNED SARIMA")
    print("-" * 70)

    sarima_train = y[
        y.index < "2023-04-01"
    ]

    sarima_validation = y[
        (y.index >= "2023-04-01")
        &
        (y.index <= "2024-03-01")
    ]

    sarima_orders = [

        ((0, 1, 1), (0, 0, 1, 12)),

        ((0, 1, 1), (1, 0, 0, 12)),

        ((1, 1, 0), (0, 0, 1, 12)),

        ((1, 1, 0), (1, 0, 0, 12)),

        ((1, 1, 1), (0, 0, 1, 12)),

        ((1, 1, 1), (1, 0, 0, 12))
    ]

    sarima_results = []

    for order, seasonal_order in sarima_orders:

        try:

            model = SARIMAX(
                sarima_train,
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )

            fitted = model.fit(
                disp=False
            )

            validation_prediction = (
                fitted.forecast(
                    steps=len(
                        sarima_validation
                    )
                )
            )

            mae, rmse, mape = (
                calculate_metrics(
                    sarima_validation.values,
                    validation_prediction
                )
            )

            sarima_results.append({
                "order": order,
                "seasonal_order":
                    seasonal_order,
                "MAE": mae,
                "RMSE": rmse,
                "MAPE": mape
            })

            print(
                f"{order} {seasonal_order} "
                f"MAPE={mape:.4f}%"
            )

        except Exception as e:

            print(
                "SARIMA failed:",
                order,
                seasonal_order,
                e
            )


    if sarima_results:

        sarima_results_df = (
            pd.DataFrame(
                sarima_results
            )
        )

        best_sarima = (
            sarima_results_df
            .sort_values("MAPE")
            .iloc[0]
        )

        best_order = (
            best_sarima["order"]
        )

        best_seasonal_order = (
            best_sarima[
                "seasonal_order"
            ]
        )

        print(
            "\nBest SARIMA:",
            best_order,
            best_seasonal_order
        )

        final_sarima = SARIMAX(
            train,
            order=best_order,
            seasonal_order=
                best_seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )

        final_sarima_fit = (
            final_sarima.fit(
                disp=False
            )
        )

        sarima_predictions = (
            final_sarima_fit
            .forecast(
                steps=len(test)
            )
        )

        mae, rmse, mape = (
            calculate_metrics(
                actual,
                sarima_predictions
            )
        )

        print(
            f"FINAL SARIMA MAPE: "
            f"{mape:.4f}%"
        )

        results.append({
            "Insurer": insurer,
            "Model": "Tuned SARIMA",
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape
        })


    # ========================================================
    # 5. DEFAULT PROPHET
    # ========================================================

    print("\n" + "-" * 70)
    print("DEFAULT PROPHET")
    print("-" * 70)

    prophet_train = (
        train.reset_index()
    )

    prophet_train.columns = [
        "ds",
        "y"
    ]

    prophet_model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )

    prophet_model.fit(
        prophet_train
    )

    future = pd.DataFrame({
        "ds": test.index
    })

    forecast = (
        prophet_model.predict(
            future
        )
    )

    prophet_predictions = (
        forecast["yhat"].values
    )

    mae, rmse, mape = (
        calculate_metrics(
            actual,
            prophet_predictions
        )
    )

    print(
        f"MAE  : {mae:,.2f}"
    )

    print(
        f"RMSE : {rmse:,.2f}"
    )

    print(
        f"MAPE : {mape:.4f}%"
    )

    results.append({
        "Insurer": insurer,
        "Model": "Default Prophet",
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape
    })


    # ========================================================
    # 6. TUNED PROPHET
    # ========================================================

    print("\n" + "-" * 70)
    print("TUNED PROPHET")
    print("-" * 70)

    prophet_train_tuning = y[
        y.index < "2023-04-01"
    ]

    prophet_validation = y[
        (y.index >= "2023-04-01")
        &
        (y.index <= "2024-03-01")
    ]

    prophet_configs = [

        {
            "name": "Default",
            "changepoint_prior_scale": 0.05,
            "seasonality_prior_scale": 10,
            "seasonality_mode": "additive"
        },

        {
            "name": "Flexible Trend",
            "changepoint_prior_scale": 0.10,
            "seasonality_prior_scale": 10,
            "seasonality_mode": "additive"
        },

        {
            "name": "Strong Trend",
            "changepoint_prior_scale": 0.50,
            "seasonality_prior_scale": 10,
            "seasonality_mode": "additive"
        },

        {
            "name": "Flexible Seasonality",
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
            "name": "Flexible Multiplicative",
            "changepoint_prior_scale": 0.10,
            "seasonality_prior_scale": 20,
            "seasonality_mode": "multiplicative"
        }
    ]

    prophet_tuning_results = []

    tuning_data = (
        prophet_train_tuning
        .reset_index()
    )

    tuning_data.columns = [
        "ds",
        "y"
    ]

    for config in prophet_configs:

        print(
            "Testing:",
            config["name"]
        )

        try:

            model = Prophet(
                changepoint_prior_scale=
                    config[
                        "changepoint_prior_scale"
                    ],

                seasonality_prior_scale=
                    config[
                        "seasonality_prior_scale"
                    ],

                seasonality_mode=
                    config[
                        "seasonality_mode"
                    ],

                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False
            )

            model.fit(
                tuning_data
            )

            validation_future = pd.DataFrame({
                "ds":
                    prophet_validation.index
            })

            validation_forecast = (
                model.predict(
                    validation_future
                )
            )

            predictions = (
                validation_forecast[
                    "yhat"
                ].values
            )

            mae, rmse, mape = (
                calculate_metrics(
                    prophet_validation.values,
                    predictions
                )
            )

            prophet_tuning_results.append({
                "config": config,
                "MAE": mae,
                "RMSE": rmse,
                "MAPE": mape
            })

            print(
                f"MAPE: {mape:.4f}%"
            )

        except Exception as e:

            print(
                "Prophet failed:",
                e
            )


    if prophet_tuning_results:

        best_prophet = min(
            prophet_tuning_results,
            key=lambda x: x["MAPE"]
        )

        best_config = (
            best_prophet["config"]
        )

        print(
            "\nBest Prophet:",
            best_config["name"]
        )

        print(
            "Validation MAPE:",
            best_prophet["MAPE"]
        )

        # ----------------------------------------------------
        # RETRAIN BEST PROPHET
        # ----------------------------------------------------

        full_prophet_train = (
            train.reset_index()
        )

        full_prophet_train.columns = [
            "ds",
            "y"
        ]

        tuned_prophet = Prophet(
            changepoint_prior_scale=
                best_config[
                    "changepoint_prior_scale"
                ],

            seasonality_prior_scale=
                best_config[
                    "seasonality_prior_scale"
                ],

            seasonality_mode=
                best_config[
                    "seasonality_mode"
                ],

            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False
        )

        tuned_prophet.fit(
            full_prophet_train
        )

        tuned_future = pd.DataFrame({
            "ds": test.index
        })

        tuned_forecast = (
            tuned_prophet.predict(
                tuned_future
            )
        )

        tuned_predictions = (
            tuned_forecast[
                "yhat"
            ].values
        )

        mae, rmse, mape = (
            calculate_metrics(
                actual,
                tuned_predictions
            )
        )

        print(
            f"FINAL TUNED PROPHET | "
            f"MAE: {mae:,.2f} | "
            f"RMSE: {rmse:,.2f} | "
            f"MAPE: {mape:.4f}%"
        )

        results.append({
            "Insurer": insurer,
            "Model": "Tuned Prophet",
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape
        })


# ============================================================
# FINAL TABLE
# ============================================================

print("\n")
print("=" * 100)
print("ALL INSURERS - ALL FORECASTING MODELS")
print("=" * 100)

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    [
        "Insurer",
        "MAPE"
    ]
)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n")
print("=" * 100)
print("COMPLETED")
print("=" * 100)

print(
    "Saved comparison to:",
    OUTPUT_FILE
)