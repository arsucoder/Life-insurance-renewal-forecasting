import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

input_file = (
    BASE_DIR
    / "data"
    / "raw"
    / "insurance_renewal_100k_IRDAI_calibrated.csv"
)

df = pd.read_csv(input_file)

print("Dataset loaded successfully")
print("Shape:", df.shape)
