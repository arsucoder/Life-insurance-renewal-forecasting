import pandas as pd

from data_loader import df
from data_validation import validate_data


def clean_data(df):
    df['policy_id'] = df['policy_id'].astype(str).str.strip()

    df['collection_date'] = pd.to_datetime(
        df['collection_date'],
        errors='coerce'
    )

    numeric_cols = [
        'premium_amount',
        'policy_duration',
        'customer_age'
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors='coerce'
        )

    categorical_cols = [
        'insurer',
        'payment_mode',
        'policy_type',
        'region',
        'renewal_status'
    ]

    for col in categorical_cols:
        df[col] = df[col].astype(str).str.strip()

    df['renewal_status'] = df['renewal_status'].str.title()

    return df


if __name__ == "__main__":
    df = clean_data(df)
    validate_data(df)
