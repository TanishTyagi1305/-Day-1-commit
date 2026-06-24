"""
day2_queries.py
===============
Day 2 — Task 6
Runs all 10 analytical SQL queries against bluestock_mf.db
and prints formatted results to terminal.

Run:
    python day2_queries.py
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "bluestock_mf.db"
pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 120)
pd.set_option("display.float_format", "{:,.2f}".format)

DIVIDER = "=" * 70

def run(conn, sql, title, desc):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(f"  {desc}")
    print(DIVIDER)
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    print(f"\n  Rows returned: {len(df)}")
    return df

if __name__ == "__main__":
    print(f"\n{'█'*70}")
    print("  DAY 2 — RUNNING 10 ANALYTICAL SQL QUERIES")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'█'*70}")

    conn = sqlite3.connect(DB_PATH)

    # ── Q1 ───────────────────────────────────────────────────
    run(conn, """
        SELECT fund_house,
               aum_crore,
               aum_lakh_crore,
               num_schemes,
               RANK() OVER (ORDER BY aum_crore DESC) AS aum_rank
        FROM   fact_aum
        WHERE  date_id = (SELECT MAX(date_id) FROM fact_aum)
        ORDER  BY aum_crore DESC LIMIT 5
    """, "QUERY 1: Top 5 Fund Houses by AUM",
        "Which fund house manages the most money?")

    # ── Q2 ───────────────────────────────────────────────────
    run(conn, """
        SELECT strftime('%Y-%m', n.date_id) AS month,
               ROUND(AVG(n.nav), 2)         AS avg_nav,
               ROUND(MIN(n.nav), 2)         AS min_nav,
               ROUND(MAX(n.nav), 2)         AS max_nav,
               COUNT(DISTINCT n.amfi_code)  AS schemes_counted
        FROM   fact_nav n
        WHERE  n.date_id >= '2025-06-01'
        GROUP  BY strftime('%Y-%m', n.date_id)
        ORDER  BY month
    """, "QUERY 2: Average NAV Per Month (Last 12 Months)",
        "How is the overall NAV trending?")

    # ── Q3 ───────────────────────────────────────────────────
    run(conn, """
        SELECT t.amfi_code,
               SUBSTR(f.scheme_name,1,35)  AS scheme_name,
               t.year,
               COUNT(*)                    AS sip_count,
               ROUND(SUM(t.amount_inr)/100000.0,1) AS sip_total_lakh
        FROM   fact_transactions t
        JOIN   dim_fund f USING (amfi_code)
        WHERE  t.transaction_type = 'SIP'
        GROUP  BY t.amfi_code, t.year
        ORDER  BY t.amfi_code, t.year
        LIMIT  20
    """, "QUERY 3: SIP Growth by Scheme and Year",
        "Which schemes are attracting more SIP investments?")

    # ── Q4 ───────────────────────────────────────────────────
    run(conn, """
        SELECT state,
               COUNT(*)                              AS total_txn,
               SUM(CASE WHEN transaction_type='SIP'
                        THEN 1 ELSE 0 END)           AS sip_count,
               ROUND(SUM(amount_inr)/10000000.0,2)  AS total_crore,
               ROUND(AVG(amount_inr),0)              AS avg_amount
        FROM   fact_transactions
        GROUP  BY state
        ORDER  BY total_txn DESC
        LIMIT  10
    """, "QUERY 4: Transactions by State (Top 10)",
        "Which states have the highest investor activity?")

    # ── Q5 ───────────────────────────────────────────────────
    run(conn, """
        SELECT SUBSTR(f.scheme_name,1,40) AS scheme_name,
               f.plan,
               p.expense_ratio_pct,
               p.return_1yr_pct,
               p.return_3yr_pct,
               p.sharpe_ratio
        FROM   fact_performance p
        JOIN   dim_fund f USING (amfi_code)
        WHERE  p.expense_ratio_pct < 1.0
        ORDER  BY p.expense_ratio_pct
    """, "QUERY 5: Funds with Expense Ratio Below 1%",
        "Low-cost funds — typically Direct plans give better returns")

    # ── Q6 ───────────────────────────────────────────────────
    run(conn, """
        SELECT SUBSTR(f.scheme_name,1,38) AS scheme_name,
               f.sub_category,
               f.plan,
               p.return_1yr_pct,
               p.return_3yr_pct,
               p.sharpe_ratio,
               p.morningstar_rating        AS stars,
               RANK() OVER (ORDER BY p.return_1yr_pct DESC) AS rank_
        FROM   fact_performance p
        JOIN   dim_fund f USING (amfi_code)
        ORDER  BY p.return_1yr_pct DESC
        LIMIT  10
    """, "QUERY 6: Top 10 Best Performing Funds (1-Year Return)",
        "Which funds delivered the highest returns this year?")

    # ── Q7 ───────────────────────────────────────────────────
    run(conn, """
        SELECT strftime('%Y-%m', transaction_date)  AS month,
               COUNT(*)                             AS sip_count,
               ROUND(SUM(amount_inr)/10000000.0,2) AS sip_crore,
               ROUND(AVG(amount_inr),0)             AS avg_amount,
               COUNT(DISTINCT investor_id)          AS unique_investors
        FROM   fact_transactions
        WHERE  transaction_type = 'SIP'
        GROUP  BY strftime('%Y-%m', transaction_date)
        ORDER  BY month
        LIMIT  12
    """, "QUERY 7: Monthly SIP Trend",
        "How is SIP investment volume changing over time?")

    # ── Q8 ───────────────────────────────────────────────────
    run(conn, """
        SELECT age_group,
               gender,
               COUNT(*)                              AS transactions,
               COUNT(DISTINCT investor_id)           AS investors,
               ROUND(AVG(amount_inr),0)              AS avg_amount,
               ROUND(AVG(annual_income_lakh),1)      AS avg_income_lakh
        FROM   fact_transactions
        GROUP  BY age_group, gender
        ORDER  BY age_group, gender
    """, "QUERY 8: Investor Profile — Age Group and Gender",
        "Who are the investors and how much do they invest?")

    # ── Q9 ───────────────────────────────────────────────────
    run(conn, """
        WITH s AS (SELECT amfi_code, nav AS start_nav
                   FROM   fact_nav
                   WHERE  date_id = (SELECT MIN(date_id) FROM fact_nav)),
             e AS (SELECT amfi_code, nav AS end_nav
                   FROM   fact_nav
                   WHERE  date_id = (SELECT MAX(date_id) FROM fact_nav))
        SELECT SUBSTR(f.scheme_name,1,38)          AS scheme_name,
               f.plan,
               ROUND(s.start_nav,2)                AS nav_start,
               ROUND(e.end_nav,2)                  AS nav_end,
               ROUND((e.end_nav-s.start_nav)*100.0
                     /s.start_nav,1)               AS growth_pct
        FROM   s JOIN e USING(amfi_code)
                 JOIN dim_fund f USING(amfi_code)
        ORDER  BY growth_pct DESC
        LIMIT  10
    """, "QUERY 9: NAV Growth — Start vs End (Top 10)",
        "Which fund's price grew the most over the full 4.5-year period?")

    # ── Q10 ──────────────────────────────────────────────────
    run(conn, """
        SELECT f.sub_category,
               COUNT(DISTINCT p.amfi_code)        AS funds,
               ROUND(AVG(p.return_1yr_pct),2)     AS avg_1yr_return,
               ROUND(AVG(p.return_3yr_pct),2)     AS avg_3yr_return,
               ROUND(AVG(p.std_dev_ann_pct),2)    AS avg_volatility,
               ROUND(AVG(p.sharpe_ratio),2)        AS avg_sharpe,
               ROUND(AVG(p.expense_ratio_pct),2)  AS avg_expense_ratio,
               SUM(p.alpha_positive)               AS beat_benchmark
        FROM   fact_performance p
        JOIN   dim_fund f USING (amfi_code)
        GROUP  BY f.sub_category
        ORDER  BY avg_1yr_return DESC
    """, "QUERY 10: Risk vs Return by Fund Category",
        "Do higher-risk categories actually deliver higher returns?")

    conn.close()
    print(f"\n{'█'*70}")
    print("  ALL 10 QUERIES COMPLETED  ✓")
    print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'█'*70}\n")
