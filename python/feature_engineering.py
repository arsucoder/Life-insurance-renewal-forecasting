import pandas as pd
from pathlib import Path

from data_cleaning import df


# Month column creation

df['collection_month'] = (
    df['collection_date']
    .dt.to_period('M')
    .astype(str)
)


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

print(
    "Premium outliers:",
    df['premium_outlier_flag'].sum()
)


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

print(
    "Age outliers:",
    df['age_outlier_flag'].sum()
)


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


# Create year feature

df['year'] = df['collection_date'].dt.year


# Sort data

df = df.sort_values(
    ['collection_date', 'policy_id']
).reset_index(drop=True)


# Final column order

final_cols = [
    'policy_id',
    'collection_date',
    'year',
    'insurer',
    'premium_amount',
    'payment_mode',
    'policy_duration',
    'policy_type',
    'customer_age',
    'region',
    'renewal_status',
    'collection_month',
    'premium_outlier_flag',
    'age_outlier_flag',
    'duration_bucket',
    'renewal_flag'
]

df = df[final_cols]


# Save preprocessed data

BASE_DIR = Path(__file__).resolve().parents[1]

output_file = (
    BASE_DIR
    / 'data'
    / 'processed'
    / 'Insurance_renewal_preprocessed.csv'
)

df.to_csv(
    output_file,
    index=False
)

print("Final shape:", df.shape)
print("\nMissing values:")
print(df.isna().sum())
print("\nSaved:", output_file)
