import pandas as pd
import numpy as np
import os

RAW = "data/raw"
PROCESSED = "data/processed"
os.makedirs(PROCESSED, exist_ok=True)

# Load fund master
df = pd.read_csv(f"{RAW}/01_fund_master.csv")
print("Before cleaning:", df.shape)
print("Null values:\n", df.isnull().sum())
print("Duplicate rows:", df.duplicated().sum())
# Fix date columns — convert text to proper dates
nav = pd.read_csv(f"{RAW}/02_nav_history.csv")
nav['date'] = pd.to_datetime(nav['date'])

# Fix numeric types
nav['nav'] = pd.to_numeric(nav['nav'], errors='coerce')

# Drop rows where NAV is missing (can't use them)
nav = nav.dropna(subset=['nav'])

print("NAV history cleaned:", nav.shape)
print("Date range:", nav['date'].min(), "to", nav['date'].max())

# Save cleaned version
nav.to_csv(f"{PROCESSED}/02_nav_history_clean.csv", index=False)
print("Saved cleaned NAV history")