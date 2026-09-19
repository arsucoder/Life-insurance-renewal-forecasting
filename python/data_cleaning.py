from data_loader import df
import pandas as pd

df['collection_date'] = pd.to_datetime(
    df['collection_date'],
    errors='coerce'
)

numeric_columns = [
    'premium_amount',
    'policy_duration',
    'customer_age'
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

categorical_columns = [
    'insurer',
    'payment_mode',
    'policy_type',
    'region',
    'renewal_status'
]

for col in categorical_columns:
    df[col] = df[col].astype('string').str.strip()

df.isnull().sum()

df.info()

df['policy_id'].duplicated().sum()

df.duplicated().sum()

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

df['policy_id'].duplicated().sum()

df.duplicated().sum()

print("Duplicate policy IDs:", df['policy_id'].duplicated().sum())
print("Duplicate complete rows:", df.duplicated().sum())

df[['premium_amount', 'policy_duration', 'customer_age']].describe()

print("Age range:")
print(df['customer_age'].min(), "to", df['customer_age'].max())

print("\nPolicy duration range:")
print(df['policy_duration'].min(), "to", df['policy_duration'].max())

print("\nPremium range:")
print(df['premium_amount'].min(), "to", df['premium_amount'].max())

df['renewal_status'].value_counts(normalize=True) * 100

print("Invalid premium values:", (df['premium_amount'] <= 0).sum())
print("Invalid customer ages:", ((df['customer_age'] < 18) | (df['customer_age'] > 100)).sum())
print("Invalid policy durations:", (df['policy_duration'] <= 0).sum())

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

print("Premium outliers:", df['premium_outlier_flag'].sum())

Q1_age = df['customer_age'].quantile(0.25)
Q3_age = df['customer_age'].quantile(0.75)

IQR_age = Q3_age - Q1_age

lower_age = Q1_age - 1.5 * IQR_age
upper_age = Q3_age + 1.5 * IQR_age

df['age_outlier_flag'] = (
    (df['customer_age'] < lower_age) |
    (df['customer_age'] > upper_age)
).astype(int)

print("Age outliers:", df['age_outlier_flag'].sum())

df['age_outlier_flag'].value_counts()

print("Lower age boundary:", lower_age)
print("Upper age boundary:", upper_age)

# Creation of duration buckets

bins = [0, 10, 15, 20, 25]
labels = ['5-10 Years', '11-15 Years', '16-20 Years', '21-25 Years']

df['duration_bucket'] = pd.cut(
    df['policy_duration'],
    bins=bins,
    labels=labels,
    include_lowest=True
)

df['duration_bucket'].value_counts().sort_index()

df['renewal_flag'] = (
    df['renewal_status']
    .str.strip()
    .str.lower()
    .map({
        'renewed': 1,
        'lapsed': 0
    })
)

df['renewal_flag'].value_counts()

df = df.sort_values('collection_date').reset_index(drop=True)
