from data_cleaning import df
import pandas as pd


# Create collection month
df['collection_month'] = (
    df['collection_date']
    .dt.to_period('M')
    .astype(str)
)


# Create year feature
df['year'] = df['collection_date'].dt.year


# Create premium outlier flag using IQR
Q1 = df['premium_amount'].quantile(0.25)
Q3 = df['premium_amount'].quantile(0.75)

IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df['premium_outlier_flag'] = (
    (df['premium_amount'] < lower_bound) |
    (df['premium_amount'] > upper_bound)
).astype(int)


# Create age outlier flag using IQR
Q1_age = df['customer_age'].quantile(0.25)
Q3_age = df['customer_age'].quantile(0.75)

IQR_age = Q3_age - Q1_age

lower_age = Q1_age - 1.5 * IQR_age
upper_age = Q3_age + 1.5 * IQR_age

df['age_outlier_flag'] = (
    (df['customer_age'] < lower_age) |
    (df['customer_age'] > upper_age)
).astype(int)


# Create policy duration buckets
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


# Create binary renewal flag
df['renewal_flag'] = (
    df['renewal_status']
    .str.strip()
    .str.lower()
    .map({
        'renewed': 1,
        'lapsed': 0
    })
)
