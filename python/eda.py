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