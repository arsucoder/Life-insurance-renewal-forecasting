"""
Central evaluation metrics for the life-insurance renewal forecasting pipeline.

Existing project metric:
    MAPE

Required hackathon metrics:
    WAPE, MAE, RMSE, Bias
"""

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calculate_metrics(actual, predicted):
    """
    Calculate forecasting evaluation metrics.

    Returns:
        MAE
        RMSE
        WAPE
        Bias
        MAPE

    Bias definition:
        predicted - actual

        Positive Bias -> over-forecasting
        Negative Bias -> under-forecasting
    """

    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    if actual.shape != predicted.shape:
        raise ValueError(
            "actual and predicted must have the same shape"
        )

    if actual.size == 0:
        raise ValueError(
            "actual and predicted cannot be empty"
        )

    # ------------------------------------------------------------
    # Errors
    # ------------------------------------------------------------

    errors = predicted - actual

    # ------------------------------------------------------------
    # MAE
    # ------------------------------------------------------------

    mae = mean_absolute_error(
        actual,
        predicted
    )

    # ------------------------------------------------------------
    # RMSE
    # ------------------------------------------------------------

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted
        )
    )

    # ------------------------------------------------------------
    # WAPE
    # ------------------------------------------------------------

    denominator = np.sum(
        np.abs(actual)
    )

    if denominator == 0:
        wape = np.nan
    else:
        wape = (
            np.sum(np.abs(errors))
            / denominator
            * 100
        )

    # ------------------------------------------------------------
    # Bias
    # ------------------------------------------------------------

    bias = np.mean(
        errors
    )

    # ------------------------------------------------------------
    # MAPE
    # ------------------------------------------------------------
    # Keep MAPE because it already exists in the project.
    # Ignore zero actual values to avoid division by zero.
    # ------------------------------------------------------------

    non_zero = actual != 0

    if np.any(non_zero):

        mape = (
            np.mean(
                np.abs(
                    (
                        actual[non_zero]
                        - predicted[non_zero]
                    )
                    / actual[non_zero]
                )
            )
            * 100
        )

    else:

        mape = np.nan

    # ------------------------------------------------------------
    # Return all metrics
    # ------------------------------------------------------------

    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "WAPE": float(wape)
        if not np.isnan(wape)
        else np.nan,
        "Bias": float(bias),
        "MAPE": float(mape)
        if not np.isnan(mape)
        else np.nan
    }


def evaluate_predictions(actual, predicted):
    """
    Alias for calculate_metrics().
    """

    return calculate_metrics(
        actual,
        predicted
    )


# ================================================================
# OPTIONAL SMOKE TEST
# ================================================================

if __name__ == "__main__":

    actual = np.array([
        100.0,
        120.0,
        80.0
    ])

    predicted = np.array([
        110.0,
        100.0,
        90.0
    ])

    print(
        calculate_metrics(
            actual,
            predicted
        )
    )