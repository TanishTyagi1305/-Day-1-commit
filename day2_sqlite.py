"""
day2_sqlite.py
==============
Day 2 — Tasks 4 & 5
Task 4 : Create SQLite star schema (dim_fund, dim_date,
         fact_nav, fact_transactions, fact_performance, fact_aum)
Task 5 : Load all cleaned datasets into SQLite, verify row counts

Run:
    python day2_sqlite.py
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, date

# ── Paths ────────────────────────────────────────────────────
RAW       = "data/raw"
PROCESSED = "data/processed"
DB_PATH   = "bluestock_mf.db"
SCHEMA    = "sql/schema.sql"

DIVIDER = "=" * 60


# ── Helper ───────────────────────────────────────────────────
def connect():
    """Return a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def row_count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

def verify(conn, table, expected, label=""):
    actual = row_count(conn, table)
    status = "✓" if actual == expected else "✗ MISMATCH"
    print(f"  {table:<30} expected={expected:>8,}  actual={actual:>8,}  {status}  {label}")
    return actual == expected


# ════════════════════════════════════════════════════════════
# TASK 4 — Create star schema
# ════════════════════════════════════════════════════════════
def create_schema(conn):
    print(f"\n{DIVIDER}")
    print("  TASK 4 — Creating SQLite Star Schema")
    print(DIVIDER)

    with open(SCHEMA, "r") as f:
        sql = f.read()

    # Remove comment-only lines and use executescript for full DDL
    conn.executescript(sql)
    conn.commit()

    # Verify tables created
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print(f"  Tables created:")
    for t in tables:
        print(f"    • {t[0]}")
    print(f"\n  Schema created successfully  ✓")


# ════════════════════════════════════════════════════════════
# dim_fund
# ════════════════════════════════════════════════════════════
def load_dim_fund(conn):
    print(f"\n{DIVIDER}")
    print("  Loading → dim_fund")
    print(DIVIDER)

    df = pd.read_csv(f"{RAW}/01_fund_master.csv")
    df['launch_date'] = pd.to_datetime(df['launch_date']).dt.strftime('%Y-%m-%d')

    df.to_sql("dim_fund", conn, if_exists="replace", index=False)
    count = row_count(conn, "dim_fund")
    print(f"  Loaded {count} rows into dim_fund  ✓")
    return count


# ════════════════════════════════════════════════════════════
# dim_date
# ════════════════════════════════════════════════════════════
def load_dim_date(conn):
    print(f"\n{DIVIDER}")
    print("  Loading → dim_date")
    print(DIVIDER)

    # Build a complete date dimension from 2022-01-01 to 2026-12-31
    dates = pd.date_range("2022-01-01", "2026-12-31", freq="D")
    df = pd.DataFrame({
        "date_id":     dates.strftime("%Y-%m-%d"),
        "year":        dates.year,
        "month":       dates.month,
        "quarter":     dates.quarter,
        "month_name":  dates.strftime("%B"),
        "day_of_week": dates.strftime("%A"),
        "is_weekend":  (dates.weekday >= 5).astype(int),
        "week_number": dates.isocalendar().week.values,
    })

    df.to_sql("dim_date", conn, if_exists="replace", index=False)
    count = row_count(conn, "dim_date")
    print(f"  Loaded {count} rows into dim_date  ✓")
    print(f"  Date range: 2022-01-01 → 2026-12-31")
    return count


# ════════════════════════════════════════════════════════════
# fact_nav
# ════════════════════════════════════════════════════════════
def load_fact_nav(conn):
    print(f"\n{DIVIDER}")
    print("  Loading → fact_nav")
    print(DIVIDER)

    # Use cleaned file if available, else raw
    path = (f"{PROCESSED}/02_nav_history_clean.csv"
            if os.path.exists(f"{PROCESSED}/02_nav_history_clean.csv")
            else f"{RAW}/02_nav_history.csv")

    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    df['date_id'] = df['date'].dt.strftime('%Y-%m-%d')

    # Select only columns that match the schema
    keep = ['amfi_code', 'date_id', 'nav']
    if 'year' in df.columns:   keep.append('year')
    if 'month' in df.columns:  keep.append('month')
    if 'weekday' in df.columns: keep.append('weekday')

    df = df[keep].copy()

    source_count = len(df)
    df.to_sql("fact_nav", conn, if_exists="replace", index=False)
    count = row_count(conn, "fact_nav")
    print(f"  Source rows : {source_count:>10,}")
    print(f"  Loaded rows : {count:>10,}  ✓")
    return count


# ════════════════════════════════════════════════════════════
# fact_transactions
# ════════════════════════════════════════════════════════════
def load_fact_transactions(conn):
    print(f"\n{DIVIDER}")
    print("  Loading → fact_transactions")
    print(DIVIDER)

    path = (f"{PROCESSED}/08_investor_transactions_clean.csv"
            if os.path.exists(f"{PROCESSED}/08_investor_transactions_clean.csv")
            else f"{RAW}/08_investor_transactions.csv")

    df = pd.read_csv(path)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['date_id'] = df['transaction_date'].dt.strftime('%Y-%m-%d')
    df['transaction_date'] = df['transaction_date'].dt.strftime('%Y-%m-%d')

    # Add derived cols if not already present
    if 'year' not in df.columns:
        df['year'] = pd.to_datetime(df['transaction_date']).dt.year
    if 'month' not in df.columns:
        df['month'] = pd.to_datetime(df['transaction_date']).dt.month
    if 'quarter' not in df.columns:
        df['quarter'] = pd.to_datetime(df['transaction_date']).dt.quarter
    if 'amount_lakh' not in df.columns:
        df['amount_lakh'] = (df['amount_inr'] / 100000).round(4)
    if 'is_large_transaction' not in df.columns:
        df['is_large_transaction'] = (df['amount_inr'] > 200000).astype(int)
    else:
        df['is_large_transaction'] = df['is_large_transaction'].astype(int)

    # Drop columns not in schema
    keep = ['investor_id', 'transaction_date', 'date_id', 'amfi_code',
            'transaction_type', 'amount_inr', 'amount_lakh', 'state',
            'city', 'city_tier', 'age_group', 'gender',
            'annual_income_lakh', 'payment_mode', 'kyc_status',
            'year', 'month', 'quarter', 'is_large_transaction']
    df = df[[c for c in keep if c in df.columns]]

    source_count = len(df)
    df.to_sql("fact_transactions", conn, if_exists="replace", index=False)
    count = row_count(conn, "fact_transactions")
    print(f"  Source rows : {source_count:>10,}")
    print(f"  Loaded rows : {count:>10,}  ✓")
    return count


# ════════════════════════════════════════════════════════════
# fact_performance
# ════════════════════════════════════════════════════════════
def load_fact_performance(conn):
    print(f"\n{DIVIDER}")
    print("  Loading → fact_performance")
    print(DIVIDER)

    path = (f"{PROCESSED}/07_scheme_performance_clean.csv"
            if os.path.exists(f"{PROCESSED}/07_scheme_performance_clean.csv")
            else f"{RAW}/07_scheme_performance.csv")

    df = pd.read_csv(path)

    # Add bool columns as int for SQLite
    for col in ['alpha_positive', 'outperformed_3yr', 'direct_plan', 'has_anomaly']:
        if col in df.columns:
            df[col] = df[col].astype(int)

    if 'max_drawdown_abs' not in df.columns:
        df['max_drawdown_abs'] = df['max_drawdown_pct'].abs()
    if 'expense_ratio_flag' not in df.columns:
        df['expense_ratio_flag'] = 'OK'

    source_count = len(df)
    df.to_sql("fact_performance", conn, if_exists="replace", index=False)
    count = row_count(conn, "fact_performance")
    print(f"  Source rows : {source_count:>10,}")
    print(f"  Loaded rows : {count:>10,}  ✓")
    return count


# ════════════════════════════════════════════════════════════
# fact_aum
# ════════════════════════════════════════════════════════════
def load_fact_aum(conn):
    print(f"\n{DIVIDER}")
    print("  Loading → fact_aum")
    print(DIVIDER)

    df = pd.read_csv(f"{RAW}/03_aum_by_fund_house.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['date_id'] = df['date'].dt.strftime('%Y-%m-%d')
    df = df.drop(columns=['date'])

    source_count = len(df)
    df.to_sql("fact_aum", conn, if_exists="replace", index=False)
    count = row_count(conn, "fact_aum")
    print(f"  Source rows : {source_count:>10,}")
    print(f"  Loaded rows : {count:>10,}  ✓")
    return count


# ════════════════════════════════════════════════════════════
# VERIFICATION — row counts match source CSVs
# ════════════════════════════════════════════════════════════
def verify_all(conn):
    print(f"\n{DIVIDER}")
    print("  TASK 5 — VERIFICATION: Row Counts Match Source CSVs")
    print(DIVIDER)

    all_pass = True

    # dim tables
    src_fund = len(pd.read_csv(f"{RAW}/01_fund_master.csv"))
    all_pass &= verify(conn, "dim_fund", src_fund, "← fund_master.csv")

    # fact tables
    nav_path = (f"{PROCESSED}/02_nav_history_clean.csv"
                if os.path.exists(f"{PROCESSED}/02_nav_history_clean.csv")
                else f"{RAW}/02_nav_history.csv")
    src_nav = len(pd.read_csv(nav_path))
    all_pass &= verify(conn, "fact_nav", src_nav, "← nav_history_clean.csv")

    txn_path = (f"{PROCESSED}/08_investor_transactions_clean.csv"
                if os.path.exists(f"{PROCESSED}/08_investor_transactions_clean.csv")
                else f"{RAW}/08_investor_transactions.csv")
    src_txn = len(pd.read_csv(txn_path))
    all_pass &= verify(conn, "fact_transactions", src_txn, "← investor_transactions_clean.csv")

    perf_path = (f"{PROCESSED}/07_scheme_performance_clean.csv"
                 if os.path.exists(f"{PROCESSED}/07_scheme_performance_clean.csv")
                 else f"{RAW}/07_scheme_performance.csv")
    src_perf = len(pd.read_csv(perf_path))
    all_pass &= verify(conn, "fact_performance", src_perf, "← scheme_performance_clean.csv")

    src_aum = len(pd.read_csv(f"{RAW}/03_aum_by_fund_house.csv"))
    all_pass &= verify(conn, "fact_aum", src_aum, "← aum_by_fund_house.csv")

    print(f"\n  dim_date: {row_count(conn,'dim_date'):,} rows (2022-01-01 to 2026-12-31)  ✓")
    print(f"\n  {'OVERALL RESULT':}")
    if all_pass:
        print("  ALL ROW COUNTS MATCH  ✓  Database is consistent with source CSVs")
    else:
        print("  MISMATCH FOUND  ✗  Check the flagged tables above")

    # Print table summary
    print(f"\n  {'Table':<30} {'Rows':>10}  {'Purpose'}")
    print(f"  {'-'*65}")
    tables_info = [
        ("dim_fund",          "Dimension — scheme metadata"),
        ("dim_date",          "Dimension — calendar dates"),
        ("fact_nav",          "Fact — daily NAV prices"),
        ("fact_transactions", "Fact — investor transactions"),
        ("fact_performance",  "Fact — risk/return metrics"),
        ("fact_aum",          "Fact — quarterly AUM"),
    ]
    for t, desc in tables_info:
        c = row_count(conn, t)
        print(f"  {t:<30} {c:>10,}  {desc}")

    return all_pass


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{'█'*60}")
    print("  DAY 2 — SQLITE STAR SCHEMA + DATA LOAD")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'█'*60}")

    # Remove old DB so we start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"\n  Removed existing {DB_PATH}")

    conn = connect()
    print(f"  Connected to: {DB_PATH}")

    create_schema(conn)
    load_dim_fund(conn)
    load_dim_date(conn)
    load_fact_nav(conn)
    load_fact_transactions(conn)
    load_fact_performance(conn)
    load_fact_aum(conn)

    all_ok = verify_all(conn)
    conn.close()

    db_size = os.path.getsize(DB_PATH) / (1024*1024)
    print(f"\n{'█'*60}")
    print(f"  COMPLETE")
    print(f"{'█'*60}")
    print(f"  Database file : {DB_PATH}")
    print(f"  File size     : {db_size:.1f} MB")
    print(f"  All checks    : {'PASSED ✓' if all_ok else 'FAILED ✗'}")
    print(f"  Finished      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n  Next step → python day2_queries.py\n")
