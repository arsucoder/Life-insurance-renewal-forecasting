from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

MONTHLY_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "monthly_renewal_premium.csv"
)

FIGURES_DIR = BASE_DIR / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(
    MONTHLY_PATH,
    parse_dates=["collection_month"]
)

df = df.sort_values("collection_month").reset_index(drop=True)


# ============================================================
# 3. BASIC DATA INFORMATION
# ============================================================

print("Dataset shape:", df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nLast 5 rows:")
print(df.tail())

print("\nMissing values:")
print(df.isnull().sum())

print("\nStatistical Summary:")
print(df.describe(include="number"))


# ============================================================
# 4. MONTHLY RENEWED PREMIUM TREND
# ============================================================

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    df["collection_month"],
    df["renewed_premium"] / 1e9,
    marker="o"
)

ax.set_title("Monthly Renewed Premium Trend")
ax.set_xlabel("Collection Month")
ax.set_ylabel("Renewed Premium (₹ Billion)")
ax.tick_params(axis="x", rotation=45)
ax.grid(alpha=0.3)

fig.tight_layout()

premium_path = FIGURES_DIR / "monthly_renewed_premium_trend.png"

fig.savefig(
    premium_path,
    dpi=150,
    bbox_inches="tight"
)

plt.close(fig)

print("\nSaved:", premium_path)


# ============================================================
# 5. MONTHLY RENEWAL RATE TREND
# ============================================================

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    df["collection_month"],
    df["renewal_rate"],
    marker="o"
)

ax.set_title("Monthly Renewal Rate Trend")
ax.set_xlabel("Collection Month")
ax.set_ylabel("Renewal Rate (%)")
ax.tick_params(axis="x", rotation=45)
ax.grid(alpha=0.3)

fig.tight_layout()

renewal_rate_path = FIGURES_DIR / "monthly_renewal_rate_trend.png"

fig.savefig(
    renewal_rate_path,
    dpi=150,
    bbox_inches="tight"
)

plt.close(fig)

print("Saved:", renewal_rate_path)


# ============================================================
# 6. MONTHLY SEASONALITY DATA
# ============================================================

df["month"] = df["collection_month"].dt.month

df["month_name"] = df["collection_month"].dt.strftime("%B")

print("\nMonthly seasonality data:")

print(
    df[
        [
            "collection_month",
            "month",
            "month_name",
            "renewed_premium"
        ]
    ].head(12)
)


# ============================================================
# 7. COMPLETION MESSAGE
# ============================================================

print("\nEDA completed successfully.")



# ============================================================
# 8. SEASONALITY ANALYSIS
# ============================================================

seasonality = (
    df.groupby(["month", "month_name"])["renewed_premium"]
    .agg(["mean", "min", "max"])
    .reset_index()
)

# Sort by calendar month
seasonality = seasonality.sort_values("month")

print("\nSeasonality Analysis:")
print(seasonality)


# ============================================================
# 9. YEAR-OVER-YEAR MONTHLY ANALYSIS
# ============================================================

df["year"] = df["collection_month"].dt.year

year_month = df.pivot(
    index="month_name",
    columns="year",
    values="renewed_premium"
)

# Arrange months in calendar order
month_order = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

year_month = year_month.reindex(month_order)

print("\nYear-over-Year Monthly Renewed Premium:")
print(year_month)


# ============================================================
# 10. AVERAGE MONTHLY SEASONALITY
# ============================================================

seasonality_plot = (
    df.groupby(["month", "month_name"])["renewed_premium"]
    .mean()
    .reset_index()
    .sort_values("month")
)

plt.figure(figsize=(12, 5))

plt.bar(
    seasonality_plot["month_name"],
    seasonality_plot["renewed_premium"] / 1e9
)

plt.title("Average Renewed Premium by Calendar Month")
plt.xlabel("Month")
plt.ylabel("Average Renewed Premium (₹ Billion)")
plt.xticks(rotation=45)
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

seasonality_path = (
    FIGURES_DIR / "average_monthly_seasonality.png"
)

plt.savefig(
    seasonality_path,
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("\nSaved:", seasonality_path)

# ============================================================
# 11. SEASONAL DECOMPOSITION
# ============================================================

from statsmodels.tsa.seasonal import seasonal_decompose

ts = df.set_index("collection_month")["renewed_premium"]

decomposition = seasonal_decompose(
    ts,
    model="additive",
    period=12
)

decomposition.plot()
plt.tight_layout()

decomposition_path = FIGURES_DIR / "renewed_premium_decomposition.png"

plt.savefig(
    decomposition_path,
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("\nSaved:", decomposition_path)








# ============================================================
# 12. OUTLIER ANALYSIS
# ============================================================
# Purpose:
# Identify unusually high premium values and assess whether
# they could materially influence aggregate premium forecasting.
#
# The outlier flags were created during feature engineering.
# We reuse the existing flag instead of redefining the threshold.

PREPROCESSED_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "Insurance_renewal_preprocessed.csv"
)

policy_df = pd.read_csv(PREPROCESSED_PATH)

# Compare renewal behaviour of outlier and non-outlier policies
outlier_renewal = pd.crosstab(
    policy_df["premium_outlier_flag"],
    policy_df["renewal_status"],
    normalize="index"
) * 100

print("\nOutlier Renewal Status Distribution (%):")
print(outlier_renewal.round(2))

# Summarize premium contribution
outlier_summary = (
    policy_df
    .groupby("premium_outlier_flag")["premium_amount"]
    .agg(["count", "sum", "mean"])
)

print("\nOutlier Premium Summary:")
print(outlier_summary)

# Calculate the share of total premium contributed by outliers
outlier_premium_share = (
    policy_df.loc[
        policy_df["premium_outlier_flag"] == 1,
        "premium_amount"
    ].sum()
    / policy_df["premium_amount"].sum()
    * 100
)

print(
    f"\nPremium contribution from outlier policies: "
    f"{outlier_premium_share:.2f}%"
)

# Visualize premium distribution
fig, ax = plt.subplots(figsize=(12, 5))

ax.hist(
    policy_df["premium_amount"] / 1e6,
    bins=50
)

ax.set_title("Distribution of Policy Premium Amounts")
ax.set_xlabel("Premium Amount (₹ Million)")
ax.set_ylabel("Number of Policies")
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()

outlier_path = FIGURES_DIR / "premium_distribution.png"

fig.savefig(
    outlier_path,
    dpi=150,
    bbox_inches="tight"
)

plt.close(fig)

print("\nSaved:", outlier_path)

print(
    "\nOutlier analysis implication: "
    "Flagged premium values are retained because they may represent "
    "genuine high-value policies and can influence aggregate premium "
    "forecasting."
)



# ============================================================
# 13. DIMENSION-WISE ANALYSIS
# ============================================================
# Purpose:
# Analyse how different portfolio dimensions contribute to
# renewed premium and renewal behaviour.
#
# These analyses help identify whether differences in aggregate
# renewed premium are driven by renewal rates, portfolio size,
# or premium contribution across dimensions.


# ------------------------------------------------------------
# 13.1 INSURER-WISE ANALYSIS
# ------------------------------------------------------------

INSURER_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "monthly_by_insurer.csv"
)

insurer_df = pd.read_csv(INSURER_PATH)

insurer_summary = (
    insurer_df
    .groupby("insurer")
    .agg(
        policies=("total_policies", "sum"),
        renewed_policies=("renewed_policies", "sum"),
        total_premium=("total_premium", "sum"),
        renewed_premium=("renewed_premium", "sum")
    )
)

insurer_summary["renewal_rate"] = (
    insurer_summary["renewed_policies"]
    / insurer_summary["policies"]
    * 100
)

insurer_summary["premium_mix_pct"] = (
    insurer_summary["total_premium"]
    / insurer_summary["total_premium"].sum()
    * 100
)

insurer_summary["renewed_premium_mix_pct"] = (
    insurer_summary["renewed_premium"]
    / insurer_summary["renewed_premium"].sum()
    * 100
)

insurer_summary = insurer_summary.sort_values(
    "renewed_premium",
    ascending=False
)

print("\nInsurer-wise Analysis:")
print(insurer_summary.round(2))

insurer_summary.to_csv(
    FIGURES_DIR.parent / "insurer_analysis.csv"
)


# ------------------------------------------------------------
# 13.2 POLICY TYPE-WISE ANALYSIS
# ------------------------------------------------------------

POLICY_TYPE_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "monthly_by_policy_type.csv"
)

policy_type_df = pd.read_csv(POLICY_TYPE_PATH)

policy_type_summary = (
    policy_type_df
    .groupby("policy_type")
    .agg(
        policies=("total_policies", "sum"),
        renewed_policies=("renewed_policies", "sum"),
        total_premium=("total_premium", "sum"),
        renewed_premium=("renewed_premium", "sum")
    )
)

policy_type_summary["renewal_rate"] = (
    policy_type_summary["renewed_policies"]
    / policy_type_summary["policies"]
    * 100
)

policy_type_summary["premium_mix_pct"] = (
    policy_type_summary["total_premium"]
    / policy_type_summary["total_premium"].sum()
    * 100
)

policy_type_summary["renewed_premium_mix_pct"] = (
    policy_type_summary["renewed_premium"]
    / policy_type_summary["renewed_premium"].sum()
    * 100
)

policy_type_summary = policy_type_summary.sort_values(
    "renewed_premium",
    ascending=False
)

print("\nPolicy Type-wise Analysis:")
print(policy_type_summary.round(2))

policy_type_summary.to_csv(
    FIGURES_DIR.parent / "policy_type_analysis.csv"
)


# ------------------------------------------------------------
# 13.3 PAYMENT MODE-WISE ANALYSIS
# ------------------------------------------------------------

PAYMENT_MODE_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "monthly_by_payment_mode.csv"
)

payment_mode_df = pd.read_csv(PAYMENT_MODE_PATH)

payment_mode_summary = (
    payment_mode_df
    .groupby("payment_mode")
    .agg(
        policies=("total_policies", "sum"),
        renewed_policies=("renewed_policies", "sum"),
        total_premium=("total_premium", "sum"),
        renewed_premium=("renewed_premium", "sum")
    )
)

payment_mode_summary["renewal_rate"] = (
    payment_mode_summary["renewed_policies"]
    / payment_mode_summary["policies"]
    * 100
)

payment_mode_summary["premium_mix_pct"] = (
    payment_mode_summary["total_premium"]
    / payment_mode_summary["total_premium"].sum()
    * 100
)

payment_mode_summary["renewed_premium_mix_pct"] = (
    payment_mode_summary["renewed_premium"]
    / payment_mode_summary["renewed_premium"].sum()
    * 100
)

payment_mode_summary = payment_mode_summary.sort_values(
    "renewed_premium",
    ascending=False
)

print("\nPayment Mode-wise Analysis:")
print(payment_mode_summary.round(2))

payment_mode_summary.to_csv(
    FIGURES_DIR.parent / "payment_mode_analysis.csv"
)


# ------------------------------------------------------------
# 13.4 REGION-WISE ANALYSIS
# ------------------------------------------------------------

REGION_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "monthly_by_region.csv"
)

region_df = pd.read_csv(REGION_PATH)

region_summary = (
    region_df
    .groupby("region")
    .agg(
        policies=("total_policies", "sum"),
        renewed_policies=("renewed_policies", "sum"),
        total_premium=("total_premium", "sum"),
        renewed_premium=("renewed_premium", "sum")
    )
)

region_summary["renewal_rate"] = (
    region_summary["renewed_policies"]
    / region_summary["policies"]
    * 100
)

region_summary["premium_mix_pct"] = (
    region_summary["total_premium"]
    / region_summary["total_premium"].sum()
    * 100
)

region_summary["renewed_premium_mix_pct"] = (
    region_summary["renewed_premium"]
    / region_summary["renewed_premium"].sum()
    * 100
)

region_summary = region_summary.sort_values(
    "renewed_premium",
    ascending=False
)

print("\nRegion-wise Analysis:")
print(region_summary.round(2))

region_summary.to_csv(
    FIGURES_DIR.parent / "region_analysis.csv"
)


# ------------------------------------------------------------
# 13.5 POLICY DURATION-WISE ANALYSIS
# ------------------------------------------------------------

policy_df["renewed_premium"] = policy_df["premium_amount"].where(
    policy_df["renewal_status"] == "Renewed",
    0
)

duration_summary = (
    policy_df
    .groupby("policy_duration")
    .agg(
        policies=("policy_id", "count"),
        renewed_policies=("renewal_flag", "sum"),
        total_premium=("premium_amount", "sum"),
        renewed_premium=("renewed_premium", "sum")
    )
)

duration_summary["renewal_rate"] = (
    duration_summary["renewed_policies"]
    / duration_summary["policies"]
    * 100
)

duration_summary["premium_mix_pct"] = (
    duration_summary["total_premium"]
    / duration_summary["total_premium"].sum()
    * 100
)

duration_summary["renewed_premium_mix_pct"] = (
    duration_summary["renewed_premium"]
    / duration_summary["renewed_premium"].sum()
    * 100
)

duration_summary = duration_summary.sort_index()

print("\nPolicy Duration-wise Analysis:")
print(duration_summary.round(2))

duration_summary.to_csv(
    FIGURES_DIR.parent / "duration_analysis.csv"
)


# ============================================================
# 14. EDA COMPLETION
# ============================================================

print("\nEDA completed successfully.")
