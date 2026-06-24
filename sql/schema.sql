-- ============================================================
-- schema.sql
-- Mutual Fund Analytics — SQLite Star Schema
-- ============================================================
-- Star schema structure:
--   Dimension tables : dim_fund, dim_date
--   Fact tables      : fact_nav, fact_transactions,
--                      fact_performance, fact_aum
-- ============================================================

PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────────
-- DIMENSION 1 — dim_fund
-- One row per mutual fund scheme
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           INTEGER PRIMARY KEY,   -- AMFI unique scheme code
    fund_house          TEXT    NOT NULL,       -- e.g. SBI Mutual Fund
    scheme_name         TEXT    NOT NULL,       -- Full scheme name
    category            TEXT    NOT NULL,       -- Equity / Debt
    sub_category        TEXT,                  -- Large Cap, Mid Cap, etc.
    plan                TEXT,                  -- Regular / Direct
    launch_date         TEXT,                  -- YYYY-MM-DD
    benchmark           TEXT,                  -- Benchmark index name
    expense_ratio_pct   REAL,                  -- Annual expense ratio %
    exit_load_pct       REAL,                  -- Exit load %
    min_sip_amount      INTEGER,               -- Minimum SIP amount INR
    min_lumpsum_amount  INTEGER,               -- Minimum lumpsum INR
    fund_manager        TEXT,                  -- Fund manager name
    risk_category       TEXT,                  -- Low/Moderate/High/etc.
    sebi_category_code  TEXT,                  -- SEBI category code e.g. EC01
    created_at          TEXT DEFAULT (datetime('now'))
);

-- ─────────────────────────────────────────────
-- DIMENSION 2 — dim_date
-- Calendar dimension — one row per calendar day
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_date (
    date_id     TEXT    PRIMARY KEY,  -- YYYY-MM-DD (natural key)
    year        INTEGER NOT NULL,
    month       INTEGER NOT NULL,     -- 1-12
    quarter     INTEGER NOT NULL,     -- 1-4
    month_name  TEXT    NOT NULL,     -- January, February, etc.
    day_of_week TEXT    NOT NULL,     -- Monday, Tuesday, etc.
    is_weekend  INTEGER NOT NULL,     -- 1 = weekend, 0 = weekday
    week_number INTEGER               -- ISO week number
);

-- ─────────────────────────────────────────────
-- FACT 1 — fact_nav
-- Daily NAV price for each scheme
-- Grain: one row per amfi_code + date
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code   INTEGER NOT NULL,
    date_id     TEXT    NOT NULL,
    nav         REAL    NOT NULL,     -- NAV price in INR
    year        INTEGER,
    month       INTEGER,
    weekday     TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_nav_amfi ON fact_nav(amfi_code);
CREATE INDEX IF NOT EXISTS idx_fact_nav_date ON fact_nav(date_id);

-- ─────────────────────────────────────────────
-- FACT 2 — fact_transactions
-- Individual investor buy/sell transactions
-- Grain: one row per transaction
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id          TEXT    NOT NULL,
    transaction_date     TEXT    NOT NULL,
    date_id              TEXT    NOT NULL,
    amfi_code            INTEGER NOT NULL,
    transaction_type     TEXT    NOT NULL,  -- SIP / Lumpsum / Redemption
    amount_inr           INTEGER NOT NULL,
    amount_lakh          REAL,
    state                TEXT,
    city                 TEXT,
    city_tier            TEXT,              -- T30 / B30
    age_group            TEXT,
    gender               TEXT,
    annual_income_lakh   REAL,
    payment_mode         TEXT,
    kyc_status           TEXT,              -- Verified / Pending
    year                 INTEGER,
    month                INTEGER,
    quarter              INTEGER,
    is_large_transaction INTEGER,           -- 1 if amount > 2,00,000
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);

CREATE INDEX IF NOT EXISTS idx_txn_amfi  ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_txn_date  ON fact_transactions(date_id);
CREATE INDEX IF NOT EXISTS idx_txn_state ON fact_transactions(state);
CREATE INDEX IF NOT EXISTS idx_txn_type  ON fact_transactions(transaction_type);

-- ─────────────────────────────────────────────
-- FACT 3 — fact_performance
-- Scheme-level risk/return metrics
-- Grain: one row per scheme (snapshot)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code            INTEGER NOT NULL,
    scheme_name          TEXT,
    fund_house           TEXT,
    category             TEXT,
    plan                 TEXT,
    return_1yr_pct       REAL,
    return_3yr_pct       REAL,
    return_5yr_pct       REAL,
    benchmark_3yr_pct    REAL,
    alpha                REAL,    -- Excess return vs benchmark
    beta                 REAL,    -- Market sensitivity (1 = moves with market)
    sharpe_ratio         REAL,    -- Return per unit of risk
    sortino_ratio        REAL,    -- Return per unit of downside risk
    std_dev_ann_pct      REAL,    -- Annual volatility %
    max_drawdown_pct     REAL,    -- Worst peak-to-trough fall (always negative)
    max_drawdown_abs     REAL,    -- Absolute value of drawdown
    aum_crore            INTEGER,
    expense_ratio_pct    REAL,
    expense_ratio_flag   TEXT,    -- OK / BELOW_MIN / ABOVE_MAX
    morningstar_rating   INTEGER, -- 1-5 stars
    risk_grade           TEXT,
    alpha_positive       INTEGER, -- 1 if fund beat benchmark
    outperformed_3yr     INTEGER, -- 1 if 3yr return > benchmark
    direct_plan          INTEGER, -- 1 if Direct plan
    has_anomaly          INTEGER, -- 1 if any metric flagged
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- ─────────────────────────────────────────────
-- FACT 4 — fact_aum
-- Quarterly AUM per fund house
-- Grain: one row per fund_house + date
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id         TEXT    NOT NULL,
    fund_house      TEXT    NOT NULL,
    aum_lakh_crore  REAL,
    aum_crore       INTEGER,
    num_schemes     INTEGER,
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id)
);

CREATE INDEX IF NOT EXISTS idx_aum_date      ON fact_aum(date_id);
CREATE INDEX IF NOT EXISTS idx_aum_fundhouse ON fact_aum(fund_house);
