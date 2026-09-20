import pandas as pd

from data_loader import df


# For time series forecasting, collection_date must be a proper date

df['collection_date'] = pd.to_datetime(
    df['collection_date'],
    errors='coerce'
)

print("collection_date dtype:")
print(df['collection_date'].dtype)

print(
    "Invalid collection dates:",
    df['collection_date'].isnull().sum()
)


# Convert numeric columns

numeric_columns = [
    'premium_amount',
    'policy_duration',
    'customer_age'
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors='coerce'
    )


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

print("\nData cleaning completed.")
