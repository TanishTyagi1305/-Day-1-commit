-- ============================================================
-- queries.sql
-- Mutual Fund Analytics — 10 Analytical SQL Queries
-- Database: bluestock_mf.db
-- ============================================================

-- HOW TO RUN:
--   python day2_queries.py
-- OR open DB Browser for SQLite and paste each query


-- ─────────────────────────────────────────────────────────
-- QUERY 1: Top 5 Fund Houses by Latest AUM
-- Shows which fund house manages the most money
-- ─────────────────────────────────────────────────────────
SELECT
    fund_house,
    aum_crore,
    aum_lakh_crore,
    num_schemes,
    RANK() OVER (ORDER BY aum_crore DESC) AS aum_rank
FROM fact_aum
WHERE date_id = (SELECT MAX(date_id) FROM fact_aum)
ORDER BY aum_crore DESC
LIMIT 5;


-- ─────────────────────────────────────────────────────────
-- QUERY 2: Average NAV Per Month (Last 12 Months)
-- Tracks overall market movement across all funds
-- ─────────────────────────────────────────────────────────
SELECT
    strftime('%Y-%m', n.date_id)   AS month,
    ROUND(AVG(n.nav), 2)           AS avg_nav,
    ROUND(MIN(n.nav), 2)           AS min_nav,
    ROUND(MAX(n.nav), 2)           AS max_nav,
    COUNT(DISTINCT n.amfi_code)    AS schemes_counted
FROM fact_nav n
WHERE n.date_id >= date('now', '-12 months')
GROUP BY strftime('%Y-%m', n.date_id)
ORDER BY month;


-- ─────────────────────────────────────────────────────────
-- QUERY 3: SIP Year-on-Year Growth by Scheme
-- Which schemes are getting more SIP investments over time?
-- ─────────────────────────────────────────────────────────
SELECT
    t.amfi_code,
    f.scheme_name,
    t.year,
    COUNT(*)                                  AS sip_count,
    SUM(t.amount_inr)                         AS total_sip_amount,
    ROUND(SUM(t.amount_inr) / 100000.0, 2)   AS total_sip_lakh,
    LAG(COUNT(*)) OVER (
        PARTITION BY t.amfi_code ORDER BY t.year
    )                                         AS prev_year_count,
    ROUND(
        (COUNT(*) - LAG(COUNT(*)) OVER (
            PARTITION BY t.amfi_code ORDER BY t.year
        )) * 100.0 /
        NULLIF(LAG(COUNT(*)) OVER (
            PARTITION BY t.amfi_code ORDER BY t.year
        ), 0)
    , 1)                                      AS yoy_growth_pct
FROM fact_transactions t
JOIN dim_fund f USING (amfi_code)
WHERE t.transaction_type = 'SIP'
GROUP BY t.amfi_code, f.scheme_name, t.year
ORDER BY t.amfi_code, t.year;


-- ─────────────────────────────────────────────────────────
-- QUERY 4: Total Transactions and Amount by State
-- Geographic distribution of investor activity
-- ─────────────────────────────────────────────────────────
SELECT
    state,
    COUNT(*)                                AS total_transactions,
    SUM(CASE WHEN transaction_type='SIP'        THEN 1 ELSE 0 END) AS sip_count,
    SUM(CASE WHEN transaction_type='Lumpsum'    THEN 1 ELSE 0 END) AS lumpsum_count,
    SUM(CASE WHEN transaction_type='Redemption' THEN 1 ELSE 0 END) AS redemption_count,
    ROUND(SUM(amount_inr) / 10000000.0, 2) AS total_amount_crore,
    ROUND(AVG(amount_inr), 0)              AS avg_transaction_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 5: Funds with Expense Ratio Below 1%
-- Low-cost funds — typically Direct plans
-- ─────────────────────────────────────────────────────────
SELECT
    p.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.plan,
    p.expense_ratio_pct,
    p.return_1yr_pct,
    p.return_3yr_pct,
    p.sharpe_ratio,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f USING (amfi_code)
WHERE p.expense_ratio_pct < 1.0
ORDER BY p.expense_ratio_pct ASC;


-- ─────────────────────────────────────────────────────────
-- QUERY 6: Best Performing Funds by 1-Year Return
-- Top 10 funds ranked by 1-year return
-- ─────────────────────────────────────────────────────────
SELECT
    p.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    f.plan,
    p.return_1yr_pct,
    p.return_3yr_pct,
    p.return_5yr_pct,
    p.sharpe_ratio,
    p.expense_ratio_pct,
    p.morningstar_rating,
    RANK() OVER (ORDER BY p.return_1yr_pct DESC) AS return_rank
FROM fact_performance p
JOIN dim_fund f USING (amfi_code)
ORDER BY p.return_1yr_pct DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────
-- QUERY 7: Monthly SIP Transaction Trend
-- How are SIP amounts trending month by month?
-- ─────────────────────────────────────────────────────────
SELECT
    strftime('%Y-%m', transaction_date)   AS month,
    COUNT(*)                              AS sip_count,
    ROUND(SUM(amount_inr)/10000000.0, 2) AS total_sip_crore,
    ROUND(AVG(amount_inr), 0)            AS avg_sip_amount,
    COUNT(DISTINCT investor_id)           AS unique_investors
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY strftime('%Y-%m', transaction_date)
ORDER BY month;


-- ─────────────────────────────────────────────────────────
-- QUERY 8: Investor Profile — Age Group and Gender Analysis
-- Who is investing and how much?
-- ─────────────────────────────────────────────────────────
SELECT
    age_group,
    gender,
    COUNT(*)                                AS transactions,
    COUNT(DISTINCT investor_id)             AS unique_investors,
    ROUND(AVG(amount_inr), 0)              AS avg_amount_inr,
    ROUND(SUM(amount_inr)/10000000.0, 2)  AS total_amount_crore,
    ROUND(AVG(annual_income_lakh), 1)      AS avg_income_lakh
FROM fact_transactions
GROUP BY age_group, gender
ORDER BY age_group, gender;


-- ─────────────────────────────────────────────────────────
-- QUERY 9: NAV Growth Analysis — Start vs End NAV
-- Which fund gave the best price growth over the full period?
-- ─────────────────────────────────────────────────────────
WITH nav_start AS (
    SELECT amfi_code, nav AS start_nav
    FROM fact_nav
    WHERE date_id = (SELECT MIN(date_id) FROM fact_nav)
),
nav_end AS (
    SELECT amfi_code, nav AS end_nav
    FROM fact_nav
    WHERE date_id = (SELECT MAX(date_id) FROM fact_nav)
)
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    f.plan,
    ROUND(s.start_nav, 2)                              AS nav_jan2022,
    ROUND(e.end_nav, 2)                                AS nav_may2026,
    ROUND(e.end_nav - s.start_nav, 2)                  AS nav_growth_inr,
    ROUND((e.end_nav - s.start_nav) * 100.0
          / s.start_nav, 2)                            AS nav_growth_pct
FROM nav_start s
JOIN nav_end e   USING (amfi_code)
JOIN dim_fund f  USING (amfi_code)
ORDER BY nav_growth_pct DESC;


-- ─────────────────────────────────────────────────────────
-- QUERY 10: Risk vs Return Summary by Category
-- Are higher-risk categories actually giving higher returns?
-- ─────────────────────────────────────────────────────────
SELECT
    f.sub_category,
    COUNT(DISTINCT p.amfi_code)                AS scheme_count,
    ROUND(AVG(p.return_1yr_pct), 2)           AS avg_return_1yr,
    ROUND(AVG(p.return_3yr_pct), 2)           AS avg_return_3yr,
    ROUND(AVG(p.std_dev_ann_pct), 2)          AS avg_volatility,
    ROUND(AVG(p.sharpe_ratio), 2)             AS avg_sharpe,
    ROUND(AVG(p.max_drawdown_abs), 2)         AS avg_max_drawdown,
    ROUND(AVG(p.expense_ratio_pct), 2)        AS avg_expense_ratio,
    SUM(p.alpha_positive)                     AS funds_beating_benchmark
FROM fact_performance p
JOIN dim_fund f USING (amfi_code)
GROUP BY f.sub_category
ORDER BY avg_return_1yr DESC;
