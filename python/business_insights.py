import pandas as pd
import os


# ============================================================
# PATHS
# ============================================================

MONTHLY_DATA = "./data/processed/monthly_by_insurer.csv"
FORECAST_DATA = "./reports/final_insurer_forecasts.csv"
MODEL_DATA = "./reports/final_model_selection.csv"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    monthly = pd.read_csv(MONTHLY_DATA)
    forecast = pd.read_csv(FORECAST_DATA)
    model = pd.read_csv(MODEL_DATA)

    monthly["collection_month"] = pd.to_datetime(
        monthly["collection_month"]
    )

    forecast["month"] = pd.to_datetime(
        forecast["month"]
    )

    return monthly, forecast, model


# ============================================================
# FORMAT MONEY
# ============================================================

def format_crore(value):

    crore = value / 10_000_000

    return f"₹{crore:,.2f} Cr"


# ============================================================
# INSURER BUSINESS INSIGHTS
# ============================================================

def generate_insurer_insight(insurer, monthly, forecast, model):

    hist = monthly[
        monthly["insurer"] == insurer
    ].copy()

    fc = forecast[
        forecast["insurer"] == insurer
    ].copy()

    mdl = model[
        model["insurer"] == insurer
    ].copy()

    if hist.empty:
        return None

    # --------------------------------------------------------
    # HISTORICAL METRICS
    # --------------------------------------------------------

    avg_historical = hist["renewed_premium"].mean()

    max_historical = hist["renewed_premium"].max()

    min_historical = hist["renewed_premium"].min()

    max_month = hist.loc[
        hist["renewed_premium"].idxmax(),
        "collection_month"
    ]

    min_month = hist.loc[
        hist["renewed_premium"].idxmin(),
        "collection_month"
    ]

    first_value = hist.iloc[0]["renewed_premium"]

    last_value = hist.iloc[-1]["renewed_premium"]

    historical_growth = (
        (last_value - first_value)
        / first_value
    ) * 100

    # --------------------------------------------------------
    # FORECAST METRICS
    # --------------------------------------------------------

    total_forecast = fc[
        "forecast_renewed_premium"
    ].sum()

    avg_forecast = fc[
        "forecast_renewed_premium"
    ].mean()

    max_forecast = fc[
        "forecast_renewed_premium"
    ].max()

    min_forecast = fc[
        "forecast_renewed_premium"
    ].min()

    max_forecast_month = fc.loc[
        fc["forecast_renewed_premium"].idxmax(),
        "month"
    ]

    min_forecast_month = fc.loc[
        fc["forecast_renewed_premium"].idxmin(),
        "month"
    ]

    # --------------------------------------------------------
    # FORECAST VS HISTORICAL
    # --------------------------------------------------------

    forecast_vs_history = (
        (avg_forecast - avg_historical)
        / avg_historical
    ) * 100

    # --------------------------------------------------------
    # FORECAST VOLATILITY
    # --------------------------------------------------------

    forecast_std = fc[
        "forecast_renewed_premium"
    ].std()

    forecast_cv = (
        forecast_std / avg_forecast
    ) * 100

    # --------------------------------------------------------
    # SELECTED MODEL
    # --------------------------------------------------------

    if not mdl.empty:

        final_model = mdl.iloc[0].get(
            "final_model",
            "Unknown"
        )

        test_mape = mdl.iloc[0].get(
            "test_mape",
            None
        )

    else:

        final_model = "Unknown"
        test_mape = None

    # --------------------------------------------------------
    # INSIGHTS
    # --------------------------------------------------------

    insights = []

    insights.append(
        f"{insurer} has an average historical "
        f"monthly renewed premium of "
        f"{format_crore(avg_historical)}."
    )

    insights.append(
        f"The highest historical renewed premium "
        f"was {format_crore(max_historical)} "
        f"in {max_month.strftime('%b %Y')}."
    )

    insights.append(
        f"The lowest historical renewed premium "
        f"was {format_crore(min_historical)} "
        f"in {min_month.strftime('%b %Y')}."
    )

    if historical_growth > 0:

        insights.append(
            f"Historical renewed premium increased by "
            f"{historical_growth:.2f}% "
            f"between the beginning and end of the "
            f"available historical period."
        )

    else:

        insights.append(
            f"Historical renewed premium decreased by "
            f"{abs(historical_growth):.2f}% "
            f"between the beginning and end of the "
            f"available historical period."
        )

    insights.append(
        f"The selected forecasting model is "
        f"{final_model}."
    )

    insights.append(
        f"The model forecasts total renewed premium "
        f"of {format_crore(total_forecast)} "
        f"over the next 12 months."
    )

    insights.append(
        f"Average monthly forecast is "
        f"{format_crore(avg_forecast)}."
    )

    if forecast_vs_history > 0:

        insights.append(
            f"The average forecast is "
            f"{forecast_vs_history:.2f}% higher than "
            f"the historical monthly average."
        )

    else:

        insights.append(
            f"The average forecast is "
            f"{abs(forecast_vs_history):.2f}% lower than "
            f"the historical monthly average."
        )

    insights.append(
        f"The highest forecast is "
        f"{format_crore(max_forecast)} "
        f"in {max_forecast_month.strftime('%b %Y')}."
    )

    insights.append(
        f"The lowest forecast is "
        f"{format_crore(min_forecast)} "
        f"in {min_forecast_month.strftime('%b %Y')}."
    )

    insights.append(
        f"Forecast variation, measured using the "
        f"coefficient of variation, is "
        f"{forecast_cv:.2f}%."
    )

    if test_mape is not None:

        insights.append(
            f"The selected model's test MAPE is "
            f"{float(test_mape):.2f}%."
        )

    # --------------------------------------------------------
    # RETURN EVERYTHING
    # --------------------------------------------------------

    return {

        "insurer": insurer,

        "final_model": final_model,

        "test_mape": test_mape,

        "historical_average":
            avg_historical,

        "historical_max":
            max_historical,

        "historical_min":
            min_historical,

        "historical_max_month":
            max_month,

        "historical_min_month":
            min_month,

        "historical_growth":
            historical_growth,

        "total_forecast":
            total_forecast,

        "average_forecast":
            avg_forecast,

        "minimum_forecast":
            min_forecast,

        "maximum_forecast":
            max_forecast,

        "forecast_vs_history":
            forecast_vs_history,

        "forecast_volatility":
            forecast_cv,

        "insights":
            insights
    }


# ============================================================
# ALL INSURERS
# ============================================================

def generate_all_insights():

    monthly, forecast, model = load_data()

    insurers = sorted(
        monthly["insurer"].unique()
    )

    results = []

    for insurer in insurers:

        result = generate_insurer_insight(
            insurer,
            monthly,
            forecast,
            model
        )

        if result:

            results.append(result)

    return results


# ============================================================
# SAVE BUSINESS INSIGHTS
# ============================================================

def save_insights():

    results = generate_all_insights()

    rows = []

    for result in results:

        rows.append({

            "Insurer":
                result["insurer"],

            "Final Model":
                result["final_model"],

            "Test MAPE":
                result["test_mape"],

            "Historical Avg Premium":
                result["historical_average"],

            "Historical Max Premium":
                result["historical_max"],

            "Historical Min Premium":
                result["historical_min"],

            "Historical Growth %":
                result["historical_growth"],

            "12 Month Forecast":
                result["total_forecast"],

            "Average Forecast":
                result["average_forecast"],

            "Minimum Forecast":
                result["minimum_forecast"],

            "Maximum Forecast":
                result["maximum_forecast"],

            "Forecast vs Historical %":
                result["forecast_vs_history"],

            "Forecast Volatility %":
                result["forecast_volatility"]
        })

    df = pd.DataFrame(rows)

    output_path = "./reports/business_insights.csv"

    df.to_csv(
        output_path,
        index=False
    )

    print("=" * 80)

    print("BUSINESS INSIGHTS GENERATED")

    print("=" * 80)

    print(df.to_string(index=False))

    print()

    print(
        f"Saved to: {output_path}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    save_insights()