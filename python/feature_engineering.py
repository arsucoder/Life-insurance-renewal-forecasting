import pandas as pd
from pathlib import Path

from data_cleaning import df


BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "Insurance_renewal_preprocessed.csv"
)


def feature_engineering(df):
    df['collection_month'] = (
        df['collection_date']
        .dt.to_period('M')
        .astype(str)
    )

    df['year'] = df['collection_date'].dt.year

    def iqr_bounds(s):
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        return q1 - 1.5 * iqr, q3 + 1.5 * iqr

    p_lo, p_hi = iqr_bounds(df['premium_amount'])
    a_lo, a_hi = iqr_bounds(df['customer_age'])

    df['premium_outlier_flag'] = (
        (df['premium_amount'] < p_lo) |
        (df['premium_amount'] > p_hi)
    ).astype(int)

    df['age_outlier_flag'] = (
        (df['customer_age'] < a_lo) |
        (df['customer_age'] > a_hi)
    ).astype(int)

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

    df['renewal_flag'] = (
        df['renewal_status'].eq('Renewed')
    ).astype(int)

    df = df.sort_values(
        ['collection_date', 'policy_id']
    ).reset_index(drop=True)

    return df


def save_processed_data(df):
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    df = feature_engineering(df)
    save_processed_data(df)
