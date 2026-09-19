from data_loader import df
import pandas as pd


# ============================================================
# 1. DATA CLEANING
# ============================================================

# Convert collection_date to datetime
df['collection_date'] = pd.to_datetime(
    df['collection_date'],
    errors='coerce'
)

# Convert numeric columns
numeric_columns = [
    'premium_amount',
    'policy_duration',
    'customer_age'
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Clean categorical columns
categorical_columns = [
    'insurer',
    'payment_mode',
    'policy_type',
    'region',
    'renewal_status'
]

for col in categorical_columns:
    df[col] = df[col].astype('string').str.strip()


# ============================================================
# 2. DATA QUALITY / EDA CHECKS
# ============================================================

# Dataset information
df.info()

# Check duplicate policy IDs
print("Duplicate policy IDs:", df['policy_id'].duplicated().sum())

# Check duplicate complete rows
print("Duplicate complete rows:", df.duplicated().sum())


# ============================================================
# 3. CATEGORICAL DATA ANALYSIS
# ============================================================

print("INSURERS:")
print(df['insurer'].value_counts())

print("\nPAYMENT MODES:")
print(df['payment_mode'].value_counts())

print("\nPOLICY TYPES:")
print(df['policy_type'].value_counts())

print("\nREGIONS:")
print(df['region'].value_counts())

print("\nRENEWAL STATUS:")
print(df['renewal_status'].value_counts())


# ============================================================
# 4. NUMERICAL DATA ANALYSIS
# ============================================================

print("\nNumerical Summary:")
print(
    df[
        ['premium_amount',
         'policy_duration',
         'customer_age']
    ].describe()
)

print("\nAge range:")
print(
    df['customer_age'].min(),
    "to",
    df['customer_age'].max()
)

print("\nPolicy duration range:")
print(
    df['policy_duration'].min(),
    "to",
    df['policy_duration'].max()
)

print("\nPremium range:")
print(
    df['premium_amount'].min(),
    "to",
    df['premium_amount'].max()
)


# ============================================================
# 5. RENEWAL ANALYSIS
# ============================================================

renewal_proportion = (
    df['renewal_status']
    .value_counts(normalize=True) * 100
)

print("\nRenewal Status Percentage:")
print(renewal_proportion)


# ============================================================
# 6. INVALID VALUE CHECKS
# ============================================================

print(
    "Invalid premium values:",
    (df['premium_amount'] <= 0).sum()
)

print(
    "Invalid customer ages:",
    (
        (df['customer_age'] < 18) |
        (df['customer_age'] > 100)
    ).sum()
)

print(
    "Invalid policy durations:",
    (df['policy_duration'] <= 0).sum()
)
