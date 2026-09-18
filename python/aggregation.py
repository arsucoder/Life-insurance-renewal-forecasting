import pandas as pd


# --------------------------------------------------
# 1. Load preprocessed data
# --------------------------------------------------

input_file = "data/processed/Insurance_renewal_preprocessed.csv"

df = pd.read_csv(input_file)

print("Preprocessed data loaded successfully.")
print("Shape:", df.shape)


# --------------------------------------------------
# 2. Convert collection_date to datetime
# --------------------------------------------------

df["collection_date"] = pd.to_datetime(df["collection_date"])


# --------------------------------------------------
# 3. Create Renewed-only premium column
# --------------------------------------------------

df["renewed_premium"] = df["premium_amount"].where(
    df["renewal_status"] == "Renewed",
    0
)


# --------------------------------------------------
# 4. Monthly aggregation
# --------------------------------------------------

monthly = (
    df.groupby("collection_month")
    .agg(
        total_policies=("policy_id", "count"),
        renewed_policies=("renewal_flag", "sum"),
        total_premium=("premium_amount", "sum"),
        renewed_premium=("renewed_premium", "sum")
    )
    .reset_index()
)


# Calculate monthly renewal rate
monthly["renewal_rate"] = (
    monthly["renewed_policies"] / monthly["total_policies"] * 100
)


# Sort chronologically
monthly = monthly.sort_values("collection_month")


# Save monthly dataset
monthly_output = "data/processed/monthly_renewal_premium.csv"

monthly.to_csv(monthly_output, index=False)

print("\nMonthly aggregation completed.")
print("Monthly shape:", monthly.shape)
print(monthly.head().to_string())


# --------------------------------------------------
# 5. Create financial year
# --------------------------------------------------

df["year"] = df["collection_date"].dt.year
df["month"] = df["collection_date"].dt.month

df["financial_year"] = df["year"].where(
    df["month"] >= 4,
    df["year"] - 1
)

df["financial_year"] = (
    df["financial_year"].astype(str)
    + "-"
    + (df["financial_year"] + 1).astype(str).str[-2:]
)


# --------------------------------------------------
# 6. Yearly financial-year aggregation
# --------------------------------------------------

yearly = (
    df.groupby("financial_year")
    .agg(
        total_policies=("policy_id", "count"),
        renewed_policies=("renewal_flag", "sum"),
        total_premium=("premium_amount", "sum"),
        renewed_premium=("renewed_premium", "sum")
    )
    .reset_index()
)


# Calculate yearly renewal rate
yearly["renewal_rate"] = (
    yearly["renewed_policies"] / yearly["total_policies"] * 100
)


# Sort chronologically
yearly = yearly.sort_values("financial_year")


# Save yearly dataset
yearly_output = "data/processed/yearly_renewal_premium.csv"

yearly.to_csv(yearly_output, index=False)

print("\nFinancial-year aggregation completed.")
print("Yearly shape:", yearly.shape)
print(yearly.to_string())


print("\nAggregation completed successfully.")