import pandas as pd


# --------------------------------------------------
# 1. Load preprocessed data
# --------------------------------------------------

input_file = "data/processed/Insurance_renewal_preprocessed.csv"
df = pd.read_csv(input_file)

print("Preprocessed data loaded successfully.")
print("Shape:", df.shape)


# --------------------------------------------------
# 2. Convert date columns
# --------------------------------------------------

df["collection_date"] = pd.to_datetime(df["collection_date"])
df["collection_month"] = pd.to_datetime(df["collection_month"])


# --------------------------------------------------
# 3. Create Renewed-only premium column
# --------------------------------------------------

df["renewed_premium"] = df["premium_amount"].where(
    df["renewal_status"] == "Renewed",
    0
)


# --------------------------------------------------
# 4. Create duration bucket
# --------------------------------------------------

# The raw data contains 5, 10, 15, 20 and 25 year durations.
df["duration_bucket"] = (
    df["policy_duration"].astype(int).astype(str) + " years"
)


# --------------------------------------------------
# 5. OVERALL MONTHLY AGGREGATION
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

monthly["renewal_rate"] = (
    monthly["renewed_policies"]
    / monthly["total_policies"]
    * 100
)

monthly = monthly.sort_values("collection_month")

monthly_output = "data/processed/monthly_renewal_premium.csv"
monthly.to_csv(monthly_output, index=False)

print("\nOverall monthly aggregation completed.")
print("Monthly shape:", monthly.shape)
print(monthly.head().to_string())


# --------------------------------------------------
# 6. MONTHLY AGGREGATION BY INSURER + DURATION
# --------------------------------------------------

insurer_duration = (
    df.groupby(
        ["collection_month", "insurer", "duration_bucket"]
    )
    .agg(
        total_policies=("policy_id", "count"),
        renewed_policies=("renewal_flag", "sum"),
        total_premium=("premium_amount", "sum"),
        renewed_premium=("renewed_premium", "sum")
    )
    .reset_index()
)

insurer_duration["renewal_rate"] = (
    insurer_duration["renewed_policies"]
    / insurer_duration["total_policies"]
    * 100
)

insurer_duration = insurer_duration.sort_values(
    ["collection_month", "insurer", "duration_bucket"]
)

insurer_duration_output = (
    "data/processed/monthly_renewal_by_insurer_duration.csv"
)

insurer_duration.to_csv(
    insurer_duration_output,
    index=False
)

print("\nInsurer + duration aggregation completed.")
print("Shape:", insurer_duration.shape)
print(insurer_duration.head(10).to_string())


# --------------------------------------------------
# 7. MONTHLY PAYMENT-MODE MIX
# --------------------------------------------------

payment_mode = (
    df.groupby(
        ["collection_month", "insurer", "payment_mode"]
    )
    .agg(
        total_policies=("policy_id", "count"),
        renewed_policies=("renewal_flag", "sum"),
        total_premium=("premium_amount", "sum"),
        renewed_premium=("renewed_premium", "sum")
    )
    .reset_index()
)

payment_mode["renewal_rate"] = (
    payment_mode["renewed_policies"]
    / payment_mode["total_policies"]
    * 100
)

payment_mode = payment_mode.sort_values(
    ["collection_month", "insurer", "payment_mode"]
)

payment_mode_output = "data/processed/monthly_payment_mode_mix.csv"
payment_mode.to_csv(payment_mode_output, index=False)

print("\nPayment-mode aggregation completed.")
print("Shape:", payment_mode.shape)
print(payment_mode.head(10).to_string())


# --------------------------------------------------
# 8. CREATE FINANCIAL YEAR
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
# 9. YEARLY FINANCIAL-YEAR AGGREGATION
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

yearly["renewal_rate"] = (
    yearly["renewed_policies"]
    / yearly["total_policies"]
    * 100
)

yearly = yearly.sort_values("financial_year")

yearly_output = "data/processed/yearly_renewal_premium.csv"
yearly.to_csv(yearly_output, index=False)

print("\nFinancial-year aggregation completed.")
print("Yearly shape:", yearly.shape)
print(yearly.to_string())


# --------------------------------------------------
# 10. VALIDATION SUMMARY
# --------------------------------------------------

print("\n============================================================")
print("AGGREGATION SUMMARY")
print("============================================================")
print("Insurers:", df["insurer"].nunique())
print("Insurer names:", sorted(df["insurer"].dropna().unique()))
print("Duration buckets:", sorted(df["duration_bucket"].dropna().unique()))
print("Payment modes:", sorted(df["payment_mode"].dropna().unique()))
print("Monthly observations:", monthly.shape[0])
print("Insurer-duration rows:", insurer_duration.shape[0])
print("Payment-mode rows:", payment_mode.shape[0])
print("\nFiles created:")
print(monthly_output)
print(insurer_duration_output)
print(payment_mode_output)
print(yearly_output)

print("\nAggregation completed successfully.")
