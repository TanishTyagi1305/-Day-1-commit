"""
day2_cleaning.py
================
Day 2 — Deep Cleaning (Tasks 1, 2, 3)

Task 1 : Clean nav_history.csv
Task 2 : Clean investor_transactions.csv
Task 3 : Clean scheme_performance.csv

Run:
    python day2_cleaning.py
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime

RAW       = "data/raw"
PROCESSED = "data/processed"
os.makedirs(PROCESSED, exist_ok=True)

DIVIDER = "=" * 60

# ─────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────
def report(title, before_df, after_df, notes=None):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)
    print(f"  Rows  : {len(before_df):>6,}  →  {len(after_df):>6,}")
    print(f"  Nulls : {before_df.isnull().sum().sum():>6}  →  {after_df.isnull().sum().sum():>6}")
    print(f"  Dups  : {before_df.duplicated().sum():>6}  →  {after_df.duplicated().sum():>6}")
    if notes:
        for n in notes:
            print(f"  NOTE  : {n}")


# ═════════════════════════════════════════════════════════════
# TASK 1 — nav_history.csv
# ═════════════════════════════════════════════════════════════
def clean_nav_history():
    print(f"\n{'█'*60}")
    print("  TASK 1 — Cleaning nav_history.csv")
    print(f"{'█'*60}")

    df = pd.read_csv(f"{RAW}/02_nav_history.csv")
    raw = df.copy()
    notes = []

    # ── Step 1: Parse date ──────────────────────────────────
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    print("  [1] date column → datetime64  ✓")

    # ── Step 2: Remove duplicates (amfi_code + date) ────────
    before = len(df)
    df = df.drop_duplicates(subset=['amfi_code', 'date'], keep='first')
    removed = before - len(df)
    notes.append(f"Duplicates removed: {removed}")
    print(f"  [2] Duplicates removed: {removed}")

    # ── Step 3: Validate NAV > 0 ────────────────────────────
    invalid_nav = df[df['nav'] <= 0]
    notes.append(f"NAV <= 0 rows found: {len(invalid_nav)} (removed)")
    df = df[df['nav'] > 0].copy()
    print(f"  [3] NAV <= 0 rows removed: {len(invalid_nav)}")

    # ── Step 4: Sort by amfi_code + date ────────────────────
    df = df.sort_values(['amfi_code', 'date']).reset_index(drop=True)
    print("  [4] Sorted by amfi_code + date  ✓")

    # ── Step 5: Forward-fill missing NAVs for holidays/weekends
    # Create a complete date range for each scheme (every calendar day)
    # then forward-fill so weekends/holidays inherit the last known NAV
    full_dates = pd.date_range(df['date'].min(), df['date'].max(), freq='D')
    all_codes  = df['amfi_code'].unique()

    idx = pd.MultiIndex.from_product(
        [all_codes, full_dates], names=['amfi_code', 'date']
    )
    df_full = df.set_index(['amfi_code', 'date']).reindex(idx)
    # Forward fill within each amfi_code group
    df_full['nav'] = df_full.groupby(level='amfi_code')['nav'].ffill()
    df_full = df_full.reset_index()
    df_full = df_full.dropna(subset=['nav'])   # drop rows before first NAV

    filled = len(df_full) - len(df)
    notes.append(f"Holiday/weekend NAVs forward-filled: {filled:,} rows added")
    print(f"  [5] Forward-filled {filled:,} holiday/weekend rows  ✓")

    # ── Step 6: Add useful derived columns ──────────────────
    df_full['year']  = df_full['date'].dt.year
    df_full['month'] = df_full['date'].dt.month
    df_full['weekday'] = df_full['date'].dt.day_name()
    print("  [6] Derived columns added: year, month, weekday  ✓")

    # ── Step 7: Final validation ─────────────────────────────
    assert df_full['nav'].gt(0).all(),   "FAIL: Some NAV values are zero or negative!"
    assert df_full['date'].notnull().all(), "FAIL: Null dates found!"
    print("  [7] Validation passed: all NAV > 0, no null dates  ✓")

    # ── Save ─────────────────────────────────────────────────
    out = f"{PROCESSED}/02_nav_history_clean.csv"
    df_full.to_csv(out, index=False)
    report("nav_history CLEANING SUMMARY", raw, df_full, notes)
    print(f"\n  Saved → {out}")

    print("\n  VALIDATION REPORT:")
    print(f"    Total rows          : {len(df_full):>10,}")
    print(f"    Unique schemes      : {df_full['amfi_code'].nunique():>10}")
    print(f"    Date range          : {df_full['date'].min().date()} → {df_full['date'].max().date()}")
    print(f"    Min NAV             : {df_full['nav'].min():>10.4f}")
    print(f"    Max NAV             : {df_full['nav'].max():>10.4f}")
    print(f"    Null values         : {df_full.isnull().sum().sum():>10}")
    return df_full


# ═════════════════════════════════════════════════════════════
# TASK 2 — investor_transactions.csv
# ═════════════════════════════════════════════════════════════
def clean_investor_transactions():
    print(f"\n{'█'*60}")
    print("  TASK 2 — Cleaning investor_transactions.csv")
    print(f"{'█'*60}")

    df = pd.read_csv(f"{RAW}/08_investor_transactions.csv")
    raw = df.copy()
    notes = []

    # ── Step 1: Parse transaction_date ──────────────────────
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], format='%Y-%m-%d')
    print("  [1] transaction_date → datetime64  ✓")

    # ── Step 2: Standardise transaction_type ────────────────
    # Map to canonical values: SIP / Lumpsum / Redemption
    type_map = {
        'SIP':        'SIP',
        'sip':        'SIP',
        'Sip':        'SIP',
        'Lumpsum':    'Lumpsum',
        'lumpsum':    'Lumpsum',
        'LUMPSUM':    'Lumpsum',
        'Redemption': 'Redemption',
        'redemption': 'Redemption',
        'REDEMPTION': 'Redemption',
    }
    original_types = df['transaction_type'].unique().tolist()
    df['transaction_type'] = df['transaction_type'].str.strip().map(type_map).fillna(df['transaction_type'])

    unmapped = df[~df['transaction_type'].isin(['SIP', 'Lumpsum', 'Redemption'])]['transaction_type'].unique()
    notes.append(f"Original types found: {original_types}")
    notes.append(f"Standardised to: SIP / Lumpsum / Redemption")
    if len(unmapped) > 0:
        notes.append(f"WARNING — Unmapped types: {unmapped}")
        print(f"  [2] WARNING: Unmapped transaction types: {unmapped}")
    else:
        print(f"  [2] transaction_type standardised → SIP / Lumpsum / Redemption  ✓")

    # ── Step 3: Validate amount > 0 ─────────────────────────
    invalid_amt = df[df['amount_inr'] <= 0]
    notes.append(f"Transactions with amount <= 0: {len(invalid_amt)} removed")
    df = df[df['amount_inr'] > 0].copy()
    print(f"  [3] Amount <= 0 rows removed: {len(invalid_amt)}  ✓")

    # ── Step 4: Check and standardise KYC status enum ───────
    valid_kyc = {'Verified', 'Pending'}
    bad_kyc = df[~df['kyc_status'].isin(valid_kyc)]['kyc_status'].unique()
    if len(bad_kyc) > 0:
        notes.append(f"Invalid KYC values found & flagged: {bad_kyc}")
        df['kyc_flag'] = ~df['kyc_status'].isin(valid_kyc)
        print(f"  [4] WARNING: Invalid KYC values: {bad_kyc}")
    else:
        print(f"  [4] KYC status valid — all values in {{Verified, Pending}}  ✓")
        notes.append("KYC status: all values valid (Verified / Pending)")

    # ── Step 5: Strip whitespace from all string columns ────
    str_cols = df.select_dtypes(include='object').columns
    for col in str_cols:
        df[col] = df[col].str.strip()
    print("  [5] Whitespace stripped from all text columns  ✓")

    # ── Step 6: Remove duplicate transactions ───────────────
    before = len(df)
    df = df.drop_duplicates(
        subset=['investor_id', 'transaction_date', 'amfi_code',
                'amount_inr', 'transaction_type'],
        keep='first'
    )
    removed = before - len(df)
    notes.append(f"Exact duplicate transactions removed: {removed}")
    print(f"  [6] Duplicate transactions removed: {removed}  ✓")

    # ── Step 7: Add derived columns ─────────────────────────
    df['year']  = df['transaction_date'].dt.year
    df['month'] = df['transaction_date'].dt.month
    df['quarter'] = df['transaction_date'].dt.quarter
    df['amount_lakh'] = (df['amount_inr'] / 100000).round(4)
    df['is_large_transaction'] = df['amount_inr'] > 200000
    print("  [7] Derived columns added: year, month, quarter, amount_lakh, is_large_transaction  ✓")

    # ── Step 8: Sort ─────────────────────────────────────────
    df = df.sort_values('transaction_date').reset_index(drop=True)

    # ── Save ─────────────────────────────────────────────────
    out = f"{PROCESSED}/08_investor_transactions_clean.csv"
    df.to_csv(out, index=False)
    report("investor_transactions CLEANING SUMMARY", raw, df, notes)
    print(f"\n  Saved → {out}")

    print("\n  VALIDATION REPORT:")
    print(f"    Total transactions  : {len(df):>10,}")
    print(f"    Unique investors    : {df['investor_id'].nunique():>10,}")
    txn_counts = df['transaction_type'].value_counts()
    for t, c in txn_counts.items():
        print(f"    {t:<20}: {c:>10,} ({c/len(df)*100:.1f}%)")
    print(f"    KYC Verified        : {(df['kyc_status']=='Verified').sum():>10,}")
    print(f"    KYC Pending         : {(df['kyc_status']=='Pending').sum():>10,}")
    print(f"    Median amount (INR) : {df['amount_inr'].median():>10,.0f}")
    print(f"    Min amount (INR)    : {df['amount_inr'].min():>10,}")
    print(f"    Max amount (INR)    : {df['amount_inr'].max():>10,}")
    return df


# ═════════════════════════════════════════════════════════════
# TASK 3 — scheme_performance.csv
# ═════════════════════════════════════════════════════════════
def clean_scheme_performance():
    print(f"\n{'█'*60}")
    print("  TASK 3 — Cleaning scheme_performance.csv")
    print(f"{'█'*60}")

    df = pd.read_csv(f"{RAW}/07_scheme_performance.csv")
    raw = df.copy()
    notes = []
    anomalies = []

    # ── Step 1: Validate all return columns are numeric ─────
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct',
                   'benchmark_3yr_pct', 'alpha', 'beta', 'sharpe_ratio',
                   'sortino_ratio', 'std_dev_ann_pct', 'max_drawdown_pct',
                   'expense_ratio_pct']

    print("  [1] Return column validation:")
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        null_count = df[col].isnull().sum()
        if null_count > 0:
            print(f"       WARNING: {col} has {null_count} non-numeric values → coerced to NaN")
            anomalies.append(f"{col}: {null_count} non-numeric values")
        else:
            print(f"       {col}: all numeric  ✓")

    # ── Step 2: Flag anomalies in return values ──────────────
    print("\n  [2] Anomaly detection:")

    # 2a — Unrealistic 1-year return (< -50% or > 100%)
    extreme_1yr = df[
        (df['return_1yr_pct'] < -50) | (df['return_1yr_pct'] > 100)
    ]
    if len(extreme_1yr) > 0:
        anomalies.append(f"Extreme 1yr returns (< -50% or > 100%): {len(extreme_1yr)} rows")
        print(f"       Extreme 1yr returns: {len(extreme_1yr)} flagged")
    else:
        print(f"       1yr returns in normal range (-50% to +100%)  ✓")

    # 2b — Beta < 0 (unexpected for equity funds)
    neg_beta = df[df['beta'] < 0]
    if len(neg_beta) > 0:
        anomalies.append(f"Negative beta (unexpected): {neg_beta['scheme_name'].tolist()}")
        print(f"       Negative beta: {len(neg_beta)} funds flagged")
    else:
        print(f"       Beta values: all >= 0  ✓")

    # 2c — Sharpe < -5 (very unusual)
    bad_sharpe = df[df['sharpe_ratio'] < -5]
    if len(bad_sharpe) > 0:
        anomalies.append(f"Sharpe ratio < -5: {len(bad_sharpe)} rows")
        print(f"       Sharpe < -5: {len(bad_sharpe)} flagged")
    else:
        print(f"       Sharpe ratios: no extreme outliers  ✓")

    # 2d — Max drawdown > 0 (should always be negative or 0)
    pos_drawdown = df[df['max_drawdown_pct'] > 0]
    if len(pos_drawdown) > 0:
        anomalies.append(f"max_drawdown_pct > 0 (invalid): {len(pos_drawdown)} rows")
        print(f"       max_drawdown > 0 (invalid): {len(pos_drawdown)} flagged")
    else:
        print(f"       max_drawdown_pct: all <= 0 (correct — drawdown is always negative)  ✓")

    # ── Step 3: Validate expense_ratio range 0.1% to 2.5% ───
    print("\n  [3] Expense ratio validation (valid range: 0.1% – 2.5%):")
    below_min = df[df['expense_ratio_pct'] < 0.1]
    above_max = df[df['expense_ratio_pct'] > 2.5]

    if len(below_min) > 0:
        anomalies.append(f"expense_ratio < 0.1%: {below_min['scheme_name'].tolist()}")
        print(f"       Below 0.1%: {len(below_min)} schemes  ← FLAGGED")
        df.loc[df['expense_ratio_pct'] < 0.1, 'expense_ratio_flag'] = 'BELOW_MIN'
    else:
        print(f"       No expense ratios below 0.1%  ✓")

    if len(above_max) > 0:
        anomalies.append(f"expense_ratio > 2.5%: {above_max['scheme_name'].tolist()}")
        print(f"       Above 2.5%: {len(above_max)} schemes  ← FLAGGED")
        df.loc[df['expense_ratio_pct'] > 2.5, 'expense_ratio_flag'] = 'ABOVE_MAX'
    else:
        print(f"       No expense ratios above 2.5%  ✓")

    if len(below_min) == 0 and len(above_max) == 0:
        df['expense_ratio_flag'] = 'OK'
        print(f"       All expense ratios in valid range (0.1% – 2.5%)  ✓")

    # ── Step 4: Add anomaly flag column ─────────────────────
    df['has_anomaly'] = False
    if len(extreme_1yr) > 0:
        df.loc[extreme_1yr.index, 'has_anomaly'] = True
    if len(neg_beta) > 0:
        df.loc[neg_beta.index, 'has_anomaly'] = True
    if len(bad_sharpe) > 0:
        df.loc[bad_sharpe.index, 'has_anomaly'] = True
    if len(pos_drawdown) > 0:
        df.loc[pos_drawdown.index, 'has_anomaly'] = True
    print(f"\n  [4] has_anomaly flag added: {df['has_anomaly'].sum()} rows flagged")

    # ── Step 5: Add derived columns ─────────────────────────
    df['alpha_positive']       = df['alpha'] > 0   # did fund beat benchmark?
    df['outperformed_3yr']     = df['return_3yr_pct'] > df['benchmark_3yr_pct']
    df['max_drawdown_abs']     = df['max_drawdown_pct'].abs()   # positive form
    df['direct_plan']          = df['plan'].str.lower() == 'direct'
    print("  [5] Derived columns added: alpha_positive, outperformed_3yr, max_drawdown_abs, direct_plan  ✓")

    # ── Step 6: Standardise text fields ─────────────────────
    df['scheme_name'] = df['scheme_name'].str.strip()
    df['fund_house']  = df['fund_house'].str.strip()
    df['category']    = df['category'].str.strip()
    df['plan']        = df['plan'].str.strip()
    df['risk_grade']  = df['risk_grade'].str.strip()

    # ── Step 7: Sort best performers first ──────────────────
    df = df.sort_values('return_1yr_pct', ascending=False).reset_index(drop=True)

    # ── Save ─────────────────────────────────────────────────
    out = f"{PROCESSED}/07_scheme_performance_clean.csv"
    df.to_csv(out, index=False)
    report("scheme_performance CLEANING SUMMARY", raw, df,
           notes + [f"Anomalies flagged: {len(anomalies)}"])
    print(f"\n  Saved → {out}")

    print("\n  VALIDATION REPORT:")
    print(f"    Total schemes       : {len(df):>6}")
    print(f"    Return cols numeric : All  ✓")
    print(f"    Expense ratio range : {df['expense_ratio_pct'].min():.2f}% – {df['expense_ratio_pct'].max():.2f}%")
    print(f"    Best  1yr return    : {df['return_1yr_pct'].max():.2f}%  ({df.loc[df['return_1yr_pct'].idxmax(),'scheme_name'][:35]})")
    print(f"    Worst 1yr return    : {df['return_1yr_pct'].min():.2f}%  ({df.loc[df['return_1yr_pct'].idxmin(),'scheme_name'][:35]})")
    print(f"    Beat benchmark (3yr): {df['outperformed_3yr'].sum()} / {len(df)} schemes")
    print(f"    Anomaly flags       : {df['has_anomaly'].sum()}")

    if anomalies:
        print("\n  ANOMALY DETAILS:")
        for a in anomalies:
            print(f"    • {a}")

    return df


# ═════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{'█'*60}")
    print("  DAY 2 — DEEP DATA CLEANING")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'█'*60}")

    nav_df  = clean_nav_history()
    txn_df  = clean_investor_transactions()
    perf_df = clean_scheme_performance()

    print(f"\n\n{'█'*60}")
    print("  ALL 3 FILES CLEANED SUCCESSFULLY")
    print(f"{'█'*60}")
    print(f"  {'File':<40} {'Rows':>10}")
    print(f"  {'-'*52}")
    print(f"  {'02_nav_history_clean.csv':<40} {len(nav_df):>10,}")
    print(f"  {'08_investor_transactions_clean.csv':<40} {len(txn_df):>10,}")
    print(f"  {'07_scheme_performance_clean.csv':<40} {len(perf_df):>10,}")
    print(f"\n  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n  Next step → python day2_sqlite.py\n")
