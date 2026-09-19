import pandas as pd
import numpy as np


# Load dataset
df = pd.read_csv('../data/raw/insurance_renewal_100k_IRDAI_calibrated.csv')


# For time series forecasting, collection_date must be a proper date
df['collection_date'] = pd.to_datetime(
    df['collection_date'],
    errors='coerce'
)


# Month column creation
df['collection_month'] = (
    df['collection_date']
    .dt.to_period('M')
    .astype(str)
)


# Separate column only for year
df['year'] = df['collection_date'].dt.year


# Convert numerical columns
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


# Creation of premium outlier flag
Q1 = df['premium_amount'].quantile(0.25)
Q3 = df['premium_amount'].quantile(0.75)

IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df['premium_outlier_flag'] = (
    (df['premium_amount'] < lower_bound) |
    (df['premium_amount'] > upper_bound)
).astype(int)


# Creation of age outlier flag
Q1_age = df['customer_age'].quantile(0.25)
Q3_age = df['customer_age'].quantile(0.75)

IQR_age = Q3_age - Q1_age

lower_age = Q1_age - 1.5 * IQR_age
upper_age = Q3_age + 1.5 * IQR_age

df['age_outlier_flag'] = (
    (df['customer_age'] < lower_age) |
    (df['customer_age'] > upper_age)
).astype(int)


# Creation of duration buckets
bins = [0, 10, 15, 20, 25]
labels = [
    '5-10 Years',
    '11-15 Years',
    '16-20 Years',
    '21-25 Years'
]

df['duration_bucket'] = pd.cut(
    df['policy_duration'],
    bins=bins,
    labels=labels,
    include_lowest=True
)


# Creation of renewal flag
df['renewal_flag'] = (
    df['renewal_status']
    .str.strip()
    .str.lower()
    .map({
        'renewed': 1,
        'lapsed': 0
    })
)


# Sort by collection date
df = df.sort_values(
    'collection_date'
).reset_index(drop=True)


# Save processed dataset
output_file = '../data/processed/Insurance_renewal_preprocessed.csv'

df.to_csv(
    output_file,
    index=False
)
