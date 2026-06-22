"""
data_ingestion.py
=================
Day 1 - Mutual Fund Analytics Project
Load all 10 CSV datasets, print diagnostics, validate AMFI codes, and
write a data-quality summary.

Usage:
    python data_ingestion.py
"""

import os
import pandas as pd
import numpy as np


# ── Paths ────────────────────────────────────────────────────────────────────
RAW_DIR       = os.path.join(os.path.dirname(__file__), "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

CSV_FILES = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]


# ── 1. Load & Inspect ────────────────────────────────────────────────────────
def load_all_datasets() -> dict[str, pd.DataFrame]:
    """Load every CSV and print shape / dtypes / head. Return {name: df}."""
    datasets: dict[str, pd.DataFrame] = {}

    for fname in CSV_FILES:
        path = os.path.join(RAW_DIR, fname)
        df   = pd.read_csv(path)
        datasets[fname] = df

        print(f"\n{'='*64}")
        print(f"FILE : {fname}")
        print(f"Shape: {df.shape}  ({df.shape[0]:,} rows × {df.shape[1]} cols)")
        print(f"\nDtypes:\n{df.dtypes.to_string()}")
        print(f"\nHead (3 rows):\n{df.head(3).to_string()}")

    return datasets


# ── 2. Anomaly Detection ─────────────────────────────────────────────────────
def detect_anomalies(datasets: dict[str, pd.DataFrame]) -> dict[str, list[str]]:
    """Return a dict of {filename: [issue, ...]} for every dataset."""
    report: dict[str, list[str]] = {}

    for fname, df in datasets.items():
        issues: list[str] = []

        # Missing values
        null_counts = df.isnull().sum()
        nulls = null_counts[null_counts > 0]
        if not nulls.empty:
            issues.append(f"Null values — {dict(nulls)}")

        # Duplicate rows
        dups = int(df.duplicated().sum())
        if dups:
            issues.append(f"{dups:,} duplicate rows")

        # Negative numerics (unexpected)
        num_cols = df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            neg = int((df[col] < 0).sum())
            if neg and col not in ("max_drawdown_pct", "alpha", "net_inflow_crore"):
                issues.append(f"Column '{col}' has {neg} negative values")

        report[fname] = issues if issues else ["✓ No anomalies detected"]

    return report


# ── 3. Fund-Master Deep Dive ─────────────────────────────────────────────────
def explore_fund_master(df: pd.DataFrame) -> None:
    """Print unique fund houses, categories, sub-categories, risk grades."""
    print("\n" + "="*64)
    print("FUND MASTER — UNIQUE VALUES")
    print("="*64)

    for col in ("fund_house", "category", "sub_category", "risk_category", "sebi_category_code"):
        vals = df[col].unique()
        print(f"\n{col.upper()}  ({len(vals)} unique):")
        for v in sorted(vals):
            print(f"    {v}")

    print(f"\nAMFI code range: {df['amfi_code'].min()} – {df['amfi_code'].max()}")
    print(f"Total schemes  : {len(df)}")


# ── 4. AMFI Code Validation ───────────────────────────────────────────────────
def validate_amfi_codes(
    fund_master: pd.DataFrame,
    nav_history: pd.DataFrame,
) -> str:
    """Validate every AMFI code in fund_master exists in nav_history."""
    master_codes = set(fund_master["amfi_code"].unique())
    nav_codes    = set(nav_history["amfi_code"].unique())

    missing_in_nav   = master_codes - nav_codes          # codes we expect but can't find
    extra_in_nav     = nav_codes    - master_codes        # extra codes (no metadata)
    matched          = master_codes & nav_codes

    lines = [
        "",
        "="*64,
        "DATA QUALITY SUMMARY — AMFI CODE VALIDATION",
        "="*64,
        f"fund_master unique AMFI codes : {len(master_codes):>5}",
        f"nav_history unique AMFI codes : {len(nav_codes):>5}",
        f"Codes matched (both tables)   : {len(matched):>5}",
        f"Missing in nav_history        : {len(missing_in_nav):>5}"
        + (f" {sorted(missing_in_nav)}" if missing_in_nav else "  ← None ✓"),
        f"Extra in nav_history only     : {len(extra_in_nav):>5}"
        + (f" {sorted(extra_in_nav)[:5]}…" if extra_in_nav else "  ← None ✓"),
        "",
        "NAV HISTORY COVERAGE",
        "-"*40,
    ]

    for code in sorted(master_codes):
        name = fund_master.loc[fund_master["amfi_code"] == code, "scheme_name"].values[0]
        rows = int((nav_history["amfi_code"] == code).sum())
        status = "✓" if rows > 0 else "✗ MISSING"
        lines.append(f"  {code}  {rows:>5} rows  {status}  {name[:55]}")

    summary = "\n".join(lines)
    print(summary)
    return summary


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 64)
    print("  MUTUAL FUND ANALYTICS — Day 1: Data Ingestion")
    print("=" * 64)

    # Step 1 — load
    datasets = load_all_datasets()

    # Step 2 — anomalies
    anomalies = detect_anomalies(datasets)
    print("\n\n" + "="*64)
    print("ANOMALY REPORT")
    print("="*64)
    for fname, issues in anomalies.items():
        print(f"\n{fname}:")
        for issue in issues:
            print(f"    {issue}")

    # Step 3 — fund master exploration
    explore_fund_master(datasets["01_fund_master.csv"])

    # Step 4 — AMFI validation
    quality_summary = validate_amfi_codes(
        datasets["01_fund_master.csv"],
        datasets["02_nav_history.csv"],
    )

    # Save summary report
    report_path = os.path.join(PROCESSED_DIR, "data_quality_report.txt")
    with open(report_path, "w") as f:
        f.write(quality_summary)
    print(f"\nData quality report saved → {report_path}")

    print("\n✓ data_ingestion.py complete")