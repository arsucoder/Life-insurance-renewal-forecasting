"""
Central evaluation metrics for the life-insurance renewal forecasting pipeline.

Required hackathon metrics:
    WAPE, MAE, RMSE, Bias

MAPE is retained as an additional diagnostic metric because the existing
project already reports it in several places.
"""

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calculate_metrics(actual, predicted):
    """Return the common forecasting metrics as a dictionary.

    Bias is defined as mean(predicted - actual):
        positive -> over-forecasting
        negative -> under-forecasting

    WAPE is:
        sum(abs(actual - predicted)) / sum(abs(actual)) * 100
    """
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    if actual.shape != predicted.shape:
        raise ValueError("actual and predicted must have the same shape")

    if actual.size == 0:
        raise ValueError("actual and predicted cannot be empty")

    errors = predicted - actual

    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))

    denominator = np.sum(np.abs(actual))
    if denominator == 0:
        wape = np.nan
    else:
        wape = np.sum(np.abs(errors)) / denominator * 100

    bias = np.mean(errors)

    non_zero = actual != 0
    if np.any(non_zero):
        mape = (
            np.mean(
                np.abs(
                    (actual[non_zero] - predicted[non_zero])
                    / actual[non_zero]
                )
            )
            * 100
        )
    else:
        mape = np.nan

    return {
        "WAPE": float(wape),
        "MAE": float(mae),
        "RMSE": float(rmse),
        "Bias": float(bias),
        "MAPE": float(mape) if not np.isnan(mape) else np.nan,
    }


def evaluate_predictions(actual, predicted):
    """Alias for callers that want an explicit evaluation function."""
    return calculate_metrics(actual, predicted)


if __name__ == "__main__":
    # Small smoke test only. It does not use project data.
    actual = np.array([100.0, 120.0, 80.0])
    predicted = np.array([110.0, 100.0, 90.0])
    print(calculate_metrics(actual, predicted))
