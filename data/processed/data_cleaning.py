"""
data_cleaning.py
================
Mutual Fund Analytics Project — Day 2
Cleans all 10 raw CSV files and saves polished versions to data/processed/.

What this script does for each file:
  - Fixes date columns (string → proper datetime)
  - Fixes wrong data types
  - Handles missing/null values
  - Removes duplicates
  - Adds useful derived columns
  - Saves cleaned file to data/processed/

Usage:
    python data_cleaning.py
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime

# ── Folder paths ──────────────────────────────────────────────────────────────
RAW       = "data/raw"
PROCESSED = "data/processed"
os.makedirs(PROCESSED, exist_ok=True)

# ── Helper: print a before/after summary ─────────────────────────────────────
def summary(name, before, after):
    print(f"\n{'='*55}")
    print(f"  {name}")
    print(f"{'='*55}")
    print(f"  Rows  : {before.shape[0]:>6}  →  {after.shape[0]:>6}")
    print(f"  Cols  : {before.shape[1]:>6}  →  {after.shape[1]:>6}")
    nulls_before = int(before.isnull().sum().sum())
    nulls_after  = int(after.isnull().sum().sum())
    print(f"  Nulls : {nulls_before:>6}  →  {nulls_after:>6}")
    dups_before  = int(before.duplicated().sum())
    dups_after   = int(after.duplicated().sum())
    print(f"  Dups  : {dups_before:>6}  →  {dups_after:>6}")
    print(f"  Status: ✓ Saved to {PROCESSED}/{name}")


# ══════════════════════════════════════════════════════════════════════════════
# FILE 1 — 01_fund_master.csv
# Issues: launch_date is a string, not a proper date
# ══════════════════════════════════════════════════════════════════════════════
def clean_fund_master():
    df = pd.read_csv(f"{RAW}/01_fund_master.csv")
    raw = df.copy()

    # Fix 1 — convert launch_date from string to proper date
    df['launch_date'] = pd.to_datetime(df['launch_date'], format='%Y-%m-%d')

    # Fix 2 — add a useful derived column: fund age in years
    today = pd.Timestamp.today()
    df['fund_age_years'] = ((today - df['launch_date']).dt.days / 365.25).round(1)

    # Fix 3 — standardise text columns (strip extra spaces, consistent case)
    text_cols = ['fund_house', 'scheme_name', 'category', 'sub_category',
                 'plan', 'benchmark', 'fund_manager', 'risk_category']
    for col in text_cols:
        df[col] = df[col].str.strip()

    # Fix 4 — sort by amfi_code for clean ordering
    df = df.sort_values('amfi_code').reset_index(drop=True)

    df.to_csv(f"{PROCESSED}/01_fund_master_clean.csv", index=False)
    summary("01_fund_master_clean.csv", raw, df)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FILE 2 — 02_nav_history.csv
# Issues: date is a string, not a proper date
# ══════════════════════════════════════════════════════════════════════════════
def clean_nav_history():
    df = pd.read_csv(f"{RAW}/02_nav_history.csv")
    raw = df.copy()

    # Fix 1 — convert date from string to proper date
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    # Fix 2 — nav should be float (already is, but force to be sure)
    df['nav'] = pd.to_numeric(df['nav'], errors='coerce')

    # Fix 3 — drop any row where NAV is null or zero (invalid price)
    df = df[df['nav'] > 0].copy()

    # Fix 4 — remove duplicate (amfi_code + date) pairs if any
    df = df.drop_duplicates(subset=['amfi_code', 'date'])

    # Fix 5 — sort by amfi_code then date (important for time-series work)
    df = df.sort_values(['amfi_code', 'date']).reset_index(drop=True)

    # Add derived column: year and month (useful for grouping later)
    df['year']  = df['date'].dt.year
    df['month'] = df['date'].dt.month

    df.to_csv(f"{PROCESSED}/02_nav_history_clean.csv", index=False)
    summary("02_nav_history_clean.csv", raw, df)
    print(f"  Date range: {df['date'].min().date()} → {df['date'].max().date()}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FILE 3 — 03_aum_by_fund_house.csv
# Issues: date is a string
# ══════════════════════════════════════════════════════════════════════════════
def clean_aum_by_fund_house():
    df = pd.read_csv(f"{RAW}/03_aum_by_fund_house.csv")
    raw = df.copy()

    # Fix 1 — convert date from string to proper date
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    # Fix 2 — standardise fund_house text
    df['fund_house'] = df['fund_house'].str.strip()

    # Fix 3 — aum_crore should be numeric (already int, but force)
    df['aum_crore']       = pd.to_numeric(df['aum_crore'],       errors='coerce')
    df['aum_lakh_crore']  = pd.to_numeric(df['aum_lakh_crore'],  errors='coerce')
    df['num_schemes']     = pd.to_numeric(df['num_schemes'],      errors='coerce').astype('Int64')

    # Fix 4 — add year and quarter columns (useful for quarterly analysis)
    df['year']    = df['date'].dt.year
    df['quarter'] = df['date'].dt.quarter

    # Fix 5 — sort by date then fund_house
    df = df.sort_values(['date', 'fund_house']).reset_index(drop=True)

    df.to_csv(f"{PROCESSED}/03_aum_by_fund_house_clean.csv", index=False)
    summary("03_aum_by_fund_house_clean.csv", raw, df)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FILE 4 — 04_monthly_sip_inflows.csv
# Issues: month is string, 12 nulls in yoy_growth_pct (first year, expected)
# ══════════════════════════════════════════════════════════════════════════════
def clean_monthly_sip_inflows():
    df = pd.read_csv(f"{RAW}/04_monthly_sip_inflows.csv")
    raw = df.copy()

    # Fix 1 — convert month from string to proper date (first day of month)
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')

    # Fix 2 — fill the 12 null yoy_growth_pct values with 0
    # (these are Jan-Dec 2022 — no prior year data exists, so 0 is correct)
    null_count = df['yoy_growth_pct'].isnull().sum()
    df['yoy_growth_pct'] = df['yoy_growth_pct'].fillna(0)
    print(f"\n  NOTE: Filled {null_count} null yoy_growth_pct values with 0")
    print(f"        (These are 2022 rows — no prior year to compare)")

    # Fix 3 — ensure all numeric columns are proper floats
    numeric_cols = ['sip_inflow_crore', 'active_sip_accounts_crore',
                    'new_sip_accounts_lakh', 'sip_aum_lakh_crore', 'yoy_growth_pct']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fix 4 — add year and month_num for easy grouping
    df['year']      = df['month'].dt.year
    df['month_num'] = df['month'].dt.month

    # Fix 5 — sort by month
    df = df.sort_values('month').reset_index(drop=True)

    df.to_csv(f"{PROCESSED}/04_monthly_sip_inflows_clean.csv", index=False)
    summary("04_monthly_sip_inflows_clean.csv", raw, df)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FILE 5 — 05_category_inflows.csv
# Issues: month is string; net_inflow_crore can be negative (valid — outflows)
# ══════════════════════════════════════════════════════════════════════════════
def clean_category_inflows():
    df = pd.read_csv(f"{RAW}/05_category_inflows.csv")
    raw = df.copy()

    # Fix 1 — convert month from string to proper date
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')

    # Fix 2 — standardise category text
    df['category'] = df['category'].str.strip()

    # Fix 3 — ensure net_inflow_crore is float
    df['net_inflow_crore'] = pd.to_numeric(df['net_inflow_crore'], errors='coerce')

    # Fix 4 — add a flag column: is this month an inflow or outflow?
    df['flow_direction'] = df['net_inflow_crore'].apply(
        lambda x: 'Inflow' if x >= 0 else 'Outflow'
    )

    # Fix 5 — add year column
    df['year'] = df['month'].dt.year

    # Fix 6 — sort by month then category
    df = df.sort_values(['month', 'category']).reset_index(drop=True)

    df.to_csv(f"{PROCESSED}/05_category_inflows_clean.csv", index=False)
    summary("05_category_inflows_clean.csv", raw, df)
    outflows = (df['net_inflow_crore'] < 0).sum()
    print(f"  NOTE: {outflows} rows have negative inflow (money flowing OUT) — this is valid")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FILE 6 — 06_industry_folio_count.csv
# Issues: month is string; tiny rounding in totals (expected)
# ══════════════════════════════════════════════════════════════════════════════
def clean_industry_folio_count():
    df = pd.read_csv(f"{RAW}/06_industry_folio_count.csv")
    raw = df.copy()

    # Fix 1 — convert month from string to proper date
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')

    # Fix 2 — ensure all numeric columns are float
    numeric_cols = ['total_folios_crore', 'equity_folios_crore',
                    'debt_folios_crore', 'hybrid_folios_crore', 'others_folios_crore']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fix 3 — add a verification column: sum of parts vs total
    # (tiny rounding differences are expected — max ~0.01)
    df['computed_total'] = (
        df['equity_folios_crore'] +
        df['debt_folios_crore']   +
        df['hybrid_folios_crore'] +
        df['others_folios_crore']
    ).round(2)
    df['rounding_diff'] = (df['total_folios_crore'] - df['computed_total']).abs().round(4)

    # Fix 4 — add year column
    df['year'] = df['month'].dt.year

    # Fix 5 — sort by month
    df = df.sort_values('month').reset_index(drop=True)

    df.to_csv(f"{PROCESSED}/06_industry_folio_count_clean.csv", index=False)
    summary("06_industry_folio_count_clean.csv", raw, df)
    max_diff = df['rounding_diff'].max()
    print(f"  NOTE: Max rounding difference in totals = {max_diff} (safe to ignore)")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FILE 7 — 07_scheme_performance.csv
# Issues: no date columns, but standardise text and add risk labels
# Note: max_drawdown_pct is negative by financial definition — do NOT fix
# ══════════════════════════════════════════════════════════════════════════════
def clean_scheme_performance():
    df = pd.read_csv(f"{RAW}/07_scheme_performance.csv")
    raw = df.copy()

    # Fix 1 — standardise text columns
    text_cols = ['scheme_name', 'fund_house', 'category', 'plan', 'risk_grade']
    for col in text_cols:
        df[col] = df[col].str.strip()

    # Fix 2 — all return/ratio columns should be float
    float_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct',
                  'benchmark_3yr_pct', 'alpha', 'beta', 'sharpe_ratio',
                  'sortino_ratio', 'std_dev_ann_pct', 'max_drawdown_pct',
                  'expense_ratio_pct']
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fix 3 — morningstar_rating should be int (1–5)
    df['morningstar_rating'] = pd.to_numeric(df['morningstar_rating'],
                                              errors='coerce').astype('Int64')

    # Fix 4 — add a useful derived column: alpha_vs_benchmark
    # Positive alpha = fund beat its benchmark
    df['outperformed_benchmark'] = df['alpha'] > 0

    # Fix 5 — add absolute drawdown column (easier to read as positive number)
    df['max_drawdown_abs'] = df['max_drawdown_pct'].abs()

    # Fix 6 — sort by return_1yr_pct descending (best performers first)
    df = df.sort_values('return_1yr_pct', ascending=False).reset_index(drop=True)

    df.to_csv(f"{PROCESSED}/07_scheme_performance_clean.csv", index=False)
    summary("07_scheme_performance_clean.csv", raw, df)
    print(f"  NOTE: max_drawdown_pct is negative by definition (measures a fall)")
    print(f"        Best 1yr return : {df['return_1yr_pct'].max():.2f}%")
    print(f"        Worst 1yr return: {df['return_1yr_pct'].min():.2f}%")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FILE 8 — 08_investor_transactions.csv
# Issues: transaction_date is string; large outlier amounts (valid HNI data)
# ══════════════════════════════════════════════════════════════════════════════
def clean_investor_transactions():
    df = pd.read_csv(f"{RAW}/08_investor_transactions.csv")
    raw = df.copy()

    # Fix 1 — convert transaction_date from string to proper date
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], format='%Y-%m-%d')

    # Fix 2 — ensure amount_inr is numeric
    df['amount_inr'] = pd.to_numeric(df['amount_inr'], errors='coerce')

    # Fix 3 — standardise all text/category columns
    text_cols = ['transaction_type', 'state', 'city', 'city_tier',
                 'age_group', 'gender', 'payment_mode', 'kyc_status']
    for col in text_cols:
        df[col] = df[col].str.strip()

    # Fix 4 — annual_income_lakh should be float
    df['annual_income_lakh'] = pd.to_numeric(df['annual_income_lakh'], errors='coerce')

    # Fix 5 — remove duplicate transactions (same investor, same date, same amount)
    before_dedup = len(df)
    df = df.drop_duplicates(subset=['investor_id', 'transaction_date',
                                    'amfi_code', 'amount_inr', 'transaction_type'])
    removed = before_dedup - len(df)
    if removed > 0:
        print(f"\n  Removed {removed} duplicate transaction rows")

    # Fix 6 — add useful derived columns
    df['year']  = df['transaction_date'].dt.year
    df['month'] = df['transaction_date'].dt.month

    # Flag large transactions (> ₹2,00,000) for easy filtering
    df['is_large_transaction'] = df['amount_inr'] > 200000

    # Fix 7 — sort by transaction_date
    df = df.sort_values('transaction_date').reset_index(drop=True)

    df.to_csv(f"{PROCESSED}/08_investor_transactions_clean.csv", index=False)
    summary("08_investor_transactions_clean.csv", raw, df)
    large = df['is_large_transaction'].sum()
    print(f"  Large transactions (>₹2L): {large:,} ({large/len(df)*100:.1f}%)")
    print(f"  Median amount: ₹{df['amount_inr'].median():,.0f}")
    print(f"  Mean amount  : ₹{df['amount_inr'].mean():,.0f}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FILE 9 — 09_portfolio_holdings.csv
# Issues: portfolio_date is string; weight >100% in some schemes (rounding)
# ══════════════════════════════════════════════════════════════════════════════
def clean_portfolio_holdings():
    df = pd.read_csv(f"{RAW}/09_portfolio_holdings.csv")
    raw = df.copy()

    # Fix 1 — convert portfolio_date from string to proper date
    df['portfolio_date'] = pd.to_datetime(df['portfolio_date'], format='%Y-%m-%d')

    # Fix 2 — ensure numeric columns are float
    float_cols = ['weight_pct', 'market_value_cr', 'current_price_inr']
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fix 3 — standardise text columns
    text_cols = ['stock_symbol', 'stock_name', 'sector']
    for col in text_cols:
        df[col] = df[col].str.strip()

    # Fix 4 — add normalised weight (fixes the >100% rounding issue)
    # Divide each holding's weight by the total weight of that scheme
    # so weights for each scheme always sum to exactly 100%
    total_weight = df.groupby('amfi_code')['weight_pct'].transform('sum')
    df['weight_pct_normalised'] = (df['weight_pct'] / total_weight * 100).round(4)

    # Fix 5 — sort by amfi_code then weight (largest holding first)
    df = df.sort_values(['amfi_code', 'weight_pct'],
                        ascending=[True, False]).reset_index(drop=True)

    df.to_csv(f"{PROCESSED}/09_portfolio_holdings_clean.csv", index=False)
    summary("09_portfolio_holdings_clean.csv", raw, df)
    over100 = df.groupby('amfi_code')['weight_pct'].sum()
    print(f"  Schemes with raw weight >100% : {(over100 > 100).sum()} (fixed by normalisation)")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# FILE 10 — 10_benchmark_indices.csv
# Issues: date is string; very different value scales across indices (expected)
# ══════════════════════════════════════════════════════════════════════════════
def clean_benchmark_indices():
    df = pd.read_csv(f"{RAW}/10_benchmark_indices.csv")
    raw = df.copy()

    # Fix 1 — convert date from string to proper date
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    # Fix 2 — ensure close_value is float
    df['close_value'] = pd.to_numeric(df['close_value'], errors='coerce')

    # Fix 3 — drop rows where close_value is null or zero
    df = df[df['close_value'] > 0].copy()

    # Fix 4 — standardise index_name text
    df['index_name'] = df['index_name'].str.strip()

    # Fix 5 — add year and month columns
    df['year']  = df['date'].dt.year
    df['month'] = df['date'].dt.month

    # Fix 6 — remove duplicate (index_name + date) pairs
    df = df.drop_duplicates(subset=['index_name', 'date'])

    # Fix 7 — sort by index_name then date
    df = df.sort_values(['index_name', 'date']).reset_index(drop=True)

    df.to_csv(f"{PROCESSED}/10_benchmark_indices_clean.csv", index=False)
    summary("10_benchmark_indices_clean.csv", raw, df)
    print(f"  Unique indices: {df['index_name'].nunique()}")
    for idx in df['index_name'].unique():
        sub = df[df['index_name'] == idx]
        print(f"    {idx:<25} range: {sub['close_value'].min():>9.2f} "
              f"→ {sub['close_value'].max():>9.2f}")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — run all 10 cleaning functions
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":

    print("\n" + "█"*55)
    print("  MUTUAL FUND ANALYTICS — Data Cleaning")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("█"*55)

    cleaned = {}
    cleaned['fund_master']           = clean_fund_master()
    cleaned['nav_history']           = clean_nav_history()
    cleaned['aum_by_fund_house']     = clean_aum_by_fund_house()
    cleaned['monthly_sip_inflows']   = clean_monthly_sip_inflows()
    cleaned['category_inflows']      = clean_category_inflows()
    cleaned['industry_folio_count']  = clean_industry_folio_count()
    cleaned['scheme_performance']    = clean_scheme_performance()
    cleaned['investor_transactions'] = clean_investor_transactions()
    cleaned['portfolio_holdings']    = clean_portfolio_holdings()
    cleaned['benchmark_indices']     = clean_benchmark_indices()

    # ── Final summary ─────────────────────────────────────────────────────────
    print("\n\n" + "█"*55)
    print("  CLEANING COMPLETE — FILES SAVED TO data/processed/")
    print("█"*55)
    print(f"\n  {'File':<40} {'Rows':>8}  {'Cols':>5}  {'Nulls':>6}")
    print(f"  {'-'*62}")
    for name, df in cleaned.items():
        nulls = int(df.isnull().sum().sum())
        print(f"  {name:<40} {len(df):>8,}  {df.shape[1]:>5}  {nulls:>6}")

    print(f"\n  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n  Next step → commit to GitHub:")
    print("  git add . && git commit -m 'Day 2: Data cleaning complete' && git push\n")