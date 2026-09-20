from data_loader import df

print("Shape:")
print(df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nData information:")
df.info()

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate complete rows:")
print(df.duplicated().sum())

print("\nColumns:")
print(df.columns)

print("\nCategorical value checking")

print("\nInsurers:")
print(df['insurer'].unique())

print("\nPayment modes:")
print(df['payment_mode'].unique())

print("\nPolicy types:")
print(df['policy_type'].unique())

print("\nRegions:")
print(df['region'].unique())

print("\nRenewal status:")
print(df['renewal_status'].unique())

print("\nAge range:")
print(df['customer_age'].min(), "to", df['customer_age'].max())

print("\nPolicy duration range:")
print(df['policy_duration'].min(), "to", df['policy_duration'].max())

print("\nPremium range:")
print(df['premium_amount'].min(), "to", df['premium_amount'].max())

print("\nRenewal status percentage:")
print(df['renewal_status'].value_counts(normalize=True) * 100)

print(
    "Invalid premium values:",
    (df['premium_amount'] <= 0).sum()
)

print(
    "Invalid customer ages:",
    ((df['customer_age'] < 18) | (df['customer_age'] > 100)).sum()
)

print(
    "Invalid policy durations:",
    (df['policy_duration'] <= 0).sum()
)
