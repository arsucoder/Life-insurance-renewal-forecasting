import pandas as pd

from data_loader import df


def validate_data(df):
    print("Shape:", df.shape)
    print("\nFirst 5 rows:")
    print(df.head())

    print("\nData information:")
    df.info()

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nDuplicate policy IDs:")
    print(df['policy_id'].duplicated().sum())

    return df


if __name__ == "__main__":
    validate_data(df)
