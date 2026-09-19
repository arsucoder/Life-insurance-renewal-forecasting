import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss


# Load monthly time-series data
file_path = "data/processed/monthly_renewal_premium.csv"

df = pd.read_csv(file_path)

# Convert month column to datetime
df["collection_month"] = pd.to_datetime(df["collection_month"])

# Sort chronologically
df = df.sort_values("collection_month")

# Set date as index
df = df.set_index("collection_month")

# Target time series
series = df["renewed_premium"]


# --------------------------------------------------
# ADF TEST
# --------------------------------------------------

adf_result = adfuller(series, autolag="AIC")

print("ADF Test")
print("ADF Statistic:", adf_result[0])
print("p-value:", adf_result[1])

if adf_result[1] < 0.05:
    print("ADF: Series is stationary")
else:
    print("ADF: Series is non-stationary")


# --------------------------------------------------
# KPSS TEST
# --------------------------------------------------

kpss_result = kpss(series, regression="c", nlags="auto")

print("\nKPSS Test")
print("KPSS Statistic:", kpss_result[0])
print("p-value:", kpss_result[1])

if kpss_result[1] > 0.05:
    print("KPSS: Series is stationary")
else:
    print("KPSS: Series is non-stationary")


# --------------------------------------------------
# FIRST DIFFERENCING
# --------------------------------------------------

if adf_result[1] >= 0.05:

    print("\nApplying first-order differencing...")

    series_diff = series.diff().dropna()

    # Check stationarity again
    adf_diff = adfuller(series_diff, autolag="AIC")

    print("\nADF Test After Differencing")
    print("ADF Statistic:", adf_diff[0])
    print("p-value:", adf_diff[1])

    if adf_diff[1] < 0.05:
        print("Differenced series is stationary.")
    else:
        print("Differenced series is still non-stationary.")

    # Save differenced series
    stationary_df = series_diff.reset_index()
    stationary_df.columns = ["collection_month", "renewed_premium_diff"]

    stationary_df.to_csv(
        "data/processed/monthly_renewal_premium_stationary.csv",
        index=False
    )

    print("\nStationary data saved successfully.")

else:
    print("\nOriginal series is already stationary.")