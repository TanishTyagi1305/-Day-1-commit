# Data Dictionary — Mutual Fund Analytics
**Project:** Bluestock Mutual Fund Analytics  
**Database:** bluestock_mf.db (SQLite)  
**Last Updated:** June 2026  
**Author:** Data Analytics Team

---

## Table of Contents
1. [dim_fund](#1-dim_fund)
2. [dim_date](#2-dim_date)
3. [fact_nav](#3-fact_nav)
4. [fact_transactions](#4-fact_transactions)
5. [fact_performance](#5-fact_performance)
6. [fact_aum](#6-fact_aum)
7. [Business Glossary](#7-business-glossary)

---

## 1. dim_fund

**Source file:** `data/raw/01_fund_master.csv`  
**Rows:** 40  
**Description:** Master reference table for all 40 mutual fund schemes. One row per scheme. This is the primary dimension that all fact tables join to.

| Column | Data Type | Nullable | Example | Business Definition |
|--------|-----------|----------|---------|---------------------|
| `amfi_code` | INTEGER | NO (PK) | 119551 | Unique 6-digit code assigned by AMFI (Association of Mutual Funds in India) to every scheme. This is the primary key used to join all tables. |
| `fund_house` | TEXT | NO | SBI Mutual Fund | The Asset Management Company (AMC) that manages the fund. Also called fund house or AMC name. |
| `scheme_name` | TEXT | NO | SBI Bluechip Fund - Regular Plan - Growth | Full official SEBI-registered name of the scheme including plan and option. |
| `category` | TEXT | NO | Equity | Broad SEBI classification — Equity or Debt. Equity funds invest in stocks; Debt funds invest in bonds. |
| `sub_category` | TEXT | YES | Large Cap | SEBI-defined sub-category e.g. Large Cap, Mid Cap, Small Cap, Flexi Cap, ELSS, Liquid, Gilt, Index. |
| `plan` | TEXT | YES | Regular | Regular = sold via distributor (higher expense); Direct = bought directly from AMC (lower expense). |
| `launch_date` | TEXT | YES | 2006-02-14 | Date when the scheme was launched and made available to investors. Format: YYYY-MM-DD. |
| `benchmark` | TEXT | YES | NIFTY 100 TRI | The index that the fund's performance is measured against. TRI = Total Return Index (includes dividends). |
| `expense_ratio_pct` | REAL | YES | 1.54 | Annual fee charged by the fund house to manage the fund, expressed as % of AUM. Valid range: 0.1% – 2.5%. |
| `exit_load_pct` | REAL | YES | 1.0 | Penalty charged when you sell (redeem) your units before a specified holding period. Usually 1% if redeemed within 1 year. |
| `min_sip_amount` | INTEGER | YES | 500 | Minimum amount in INR you can invest via SIP (monthly). |
| `min_lumpsum_amount` | INTEGER | YES | 1000 | Minimum one-time investment amount in INR. |
| `fund_manager` | TEXT | YES | Sohini Andani | Name of the fund manager responsible for investment decisions. |
| `risk_category` | TEXT | YES | Moderate | SEBI-mandated risk label. Values: Low / Moderate / Moderately High / High / Very High. |
| `sebi_category_code` | TEXT | YES | EC01 | SEBI internal classification code. EC = Equity, DC = Debt, EI = Equity Index. |

---

## 2. dim_date

**Source:** Generated programmatically  
**Rows:** 1,826 (2022-01-01 to 2026-12-31)  
**Description:** Calendar dimension table. One row per calendar day. Used to join all fact tables on date and enable time-based analysis.

| Column | Data Type | Nullable | Example | Business Definition |
|--------|-----------|----------|---------|---------------------|
| `date_id` | TEXT | NO (PK) | 2024-03-15 | Calendar date in YYYY-MM-DD format. Primary key. Used as foreign key in all fact tables. |
| `year` | INTEGER | NO | 2024 | Calendar year (2022–2026). |
| `month` | INTEGER | NO | 3 | Month number (1=January to 12=December). |
| `quarter` | INTEGER | NO | 1 | Quarter number (1–4). Q1=Jan-Mar, Q2=Apr-Jun, Q3=Jul-Sep, Q4=Oct-Dec. |
| `month_name` | TEXT | NO | March | Full month name (January, February, etc.). Useful for display in reports. |
| `day_of_week` | TEXT | NO | Friday | Full weekday name (Monday to Sunday). |
| `is_weekend` | INTEGER | NO | 0 | 1 = Saturday or Sunday (market closed); 0 = weekday (market open). |
| `week_number` | INTEGER | YES | 11 | ISO 8601 week number (1–53). |

---

## 3. fact_nav

**Source file:** `data/processed/02_nav_history_clean.csv`  
**Rows:** 64,320 (includes forward-filled weekends/holidays)  
**Original rows:** 46,000  
**Description:** Daily NAV (Net Asset Value) price for each fund scheme. This is the main time-series fact table. After cleaning, weekend and holiday NAVs are forward-filled from the previous trading day.

| Column | Data Type | Nullable | Example | Business Definition |
|--------|-----------|----------|---------|---------------------|
| `nav_id` | INTEGER | NO (PK) | 1 | Auto-incrementing surrogate primary key. |
| `amfi_code` | INTEGER | NO (FK) | 119551 | Foreign key → dim_fund.amfi_code. Identifies which scheme this NAV belongs to. |
| `date_id` | TEXT | NO (FK) | 2024-03-15 | Foreign key → dim_date.date_id. The date of this NAV value. |
| `nav` | REAL | NO | 95.4823 | Net Asset Value in Indian Rupees (INR). The price per unit of the fund on that date. Must be > 0. |
| `year` | INTEGER | YES | 2024 | Derived from date. Useful for year-based aggregations without joining dim_date. |
| `month` | INTEGER | YES | 3 | Derived from date. Month number 1–12. |
| `weekday` | TEXT | YES | Friday | Day of week. Forward-filled values will show the weekend/holiday day name. |

**Notes:**
- NAV is published by AMFI every business day after 9 PM
- Weekend and holiday NAVs are forward-filled (carry the last known price)
- NAV must always be > 0; zero or negative values were removed in cleaning

---

## 4. fact_transactions

**Source file:** `data/processed/08_investor_transactions_clean.csv`  
**Rows:** 32,778  
**Description:** Individual investor buy and sell transactions. One row per transaction. Contains investor demographics and transaction details.

| Column | Data Type | Nullable | Example | Business Definition |
|--------|-----------|----------|---------|---------------------|
| `txn_id` | INTEGER | NO (PK) | 1 | Auto-incrementing surrogate primary key. |
| `investor_id` | TEXT | NO | INV003054 | Unique anonymous investor identifier. Format: INV + 6 digits. |
| `transaction_date` | TEXT | NO | 2024-01-01 | Date of the transaction in YYYY-MM-DD format. |
| `date_id` | TEXT | NO (FK) | 2024-01-01 | Foreign key → dim_date.date_id. |
| `amfi_code` | INTEGER | NO (FK) | 119092 | Foreign key → dim_fund.amfi_code. Which fund was transacted. |
| `transaction_type` | TEXT | NO | SIP | Standardised transaction type. Values: SIP / Lumpsum / Redemption. |
| `amount_inr` | INTEGER | NO | 1834 | Transaction amount in Indian Rupees. Must be > 0. |
| `amount_lakh` | REAL | YES | 0.0183 | Amount in lakhs (1 lakh = 100,000). Derived: amount_inr ÷ 100,000. |
| `state` | TEXT | YES | Telangana | Indian state where the investor is registered. |
| `city` | TEXT | YES | Hyderabad | City of the investor. |
| `city_tier` | TEXT | YES | T30 | T30 = Top 30 cities (metro); B30 = Beyond Top 30 (smaller towns). SEBI classification. |
| `age_group` | TEXT | YES | 56+ | Age bracket of the investor: 18-25 / 26-35 / 36-45 / 46-55 / 56+. |
| `gender` | TEXT | YES | Female | Investor gender: Male / Female. |
| `annual_income_lakh` | REAL | YES | 77.1 | Self-declared annual income in lakhs. |
| `payment_mode` | TEXT | YES | UPI | Payment method: UPI / Net Banking / Cheque / NEFT / NACH. |
| `kyc_status` | TEXT | YES | Verified | KYC (Know Your Customer) status. Values: Verified / Pending. Unverified investors cannot invest. |
| `year` | INTEGER | YES | 2024 | Derived from transaction_date. |
| `month` | INTEGER | YES | 1 | Derived from transaction_date. Month number 1–12. |
| `quarter` | INTEGER | YES | 1 | Derived from transaction_date. Quarter number 1–4. |
| `is_large_transaction` | INTEGER | YES | 0 | 1 if amount_inr > ₹2,00,000; 0 otherwise. Derived flag for high-value transaction analysis. |

---

## 5. fact_performance

**Source file:** `data/processed/07_scheme_performance_clean.csv`  
**Rows:** 40  
**Description:** Risk and return metrics for each scheme. One row per scheme. This is a snapshot table — metrics calculated at a point in time.

| Column | Data Type | Nullable | Example | Business Definition |
|--------|-----------|----------|---------|---------------------|
| `perf_id` | INTEGER | NO (PK) | 1 | Auto-incrementing surrogate primary key. |
| `amfi_code` | INTEGER | NO (FK) | 119551 | Foreign key → dim_fund.amfi_code. |
| `scheme_name` | TEXT | YES | SBI Bluechip Fund... | Full scheme name. Denormalized from dim_fund for convenience. |
| `fund_house` | TEXT | YES | SBI Mutual Fund | Fund house name. Denormalized from dim_fund. |
| `category` | TEXT | YES | Equity | Equity or Debt. |
| `plan` | TEXT | YES | Regular | Regular or Direct. |
| `return_1yr_pct` | REAL | YES | 12.42 | Absolute return generated over the past 1 year, as a percentage. |
| `return_3yr_pct` | REAL | YES | 12.36 | CAGR (Compounded Annual Growth Rate) over the past 3 years. More reliable than 1-year. |
| `return_5yr_pct` | REAL | YES | 14.45 | CAGR over the past 5 years. Best indicator of long-term performance. |
| `benchmark_3yr_pct` | REAL | YES | 11.49 | 3-year CAGR of the fund's benchmark index (e.g. NIFTY 100). Used to calculate alpha. |
| `alpha` | REAL | YES | 0.87 | Excess return over benchmark. Positive alpha = fund outperformed. Negative = underperformed. |
| `beta` | REAL | YES | 0.89 | Market sensitivity. Beta=1 means fund moves exactly with market. Beta<1 means less volatile. |
| `sharpe_ratio` | REAL | YES | 0.88 | Return per unit of total risk. Higher is better. Formula: (Return - Risk-free rate) ÷ Std Dev. |
| `sortino_ratio` | REAL | YES | 1.29 | Like Sharpe but only penalises downside risk. Higher is better than Sharpe for comparison. |
| `std_dev_ann_pct` | REAL | YES | 14.0 | Annual standard deviation of returns. Measures volatility. Higher = more volatile = higher risk. |
| `max_drawdown_pct` | REAL | YES | -21.70 | Worst peak-to-trough fall ever experienced by the fund. Always negative or zero. -21.7% means fund fell 21.7% from its peak at worst. |
| `max_drawdown_abs` | REAL | YES | 21.70 | Absolute value of max_drawdown_pct. Positive number — easier to read in comparisons. Derived column. |
| `aum_crore` | INTEGER | YES | 14288 | Assets Under Management in crores (₹). 1 crore = ₹1,00,00,000. |
| `expense_ratio_pct` | REAL | YES | 1.54 | Annual management fee as % of AUM. Valid range: 0.1% – 2.5%. |
| `expense_ratio_flag` | TEXT | YES | OK | Validation flag: OK = in valid range; BELOW_MIN = below 0.1%; ABOVE_MAX = above 2.5%. |
| `morningstar_rating` | INTEGER | YES | 4 | 1 to 5 star rating by Morningstar. 5 = best historical risk-adjusted performance. |
| `risk_grade` | TEXT | YES | Moderate | SEBI risk label: Low / Moderate / Moderately High / High / Very High. |
| `alpha_positive` | INTEGER | YES | 1 | 1 if alpha > 0 (fund beat benchmark); 0 if underperformed. Derived column. |
| `outperformed_3yr` | INTEGER | YES | 1 | 1 if return_3yr_pct > benchmark_3yr_pct. Derived. |
| `direct_plan` | INTEGER | YES | 0 | 1 if plan = Direct; 0 if Regular. Derived. |
| `has_anomaly` | INTEGER | YES | 0 | 1 if any metric was flagged as anomalous during cleaning. 0 = clean data. |

---

## 6. fact_aum

**Source file:** `data/raw/03_aum_by_fund_house.csv`  
**Rows:** 90  
**Description:** Quarterly AUM (Assets Under Management) per fund house. One row per fund house per quarter. Tracks how the total money managed by each AMC changes over time.

| Column | Data Type | Nullable | Example | Business Definition |
|--------|-----------|----------|---------|---------------------|
| `aum_id` | INTEGER | NO (PK) | 1 | Auto-incrementing surrogate primary key. |
| `date_id` | TEXT | NO (FK) | 2022-03-31 | Foreign key → dim_date.date_id. Quarter-end date. |
| `fund_house` | TEXT | NO | SBI Mutual Fund | Name of the Asset Management Company. |
| `aum_lakh_crore` | REAL | YES | 6.05 | AUM in lakh crore (₹). 1 lakh crore = ₹1,000,00,00,00,000. Useful for industry-level view. |
| `aum_crore` | INTEGER | YES | 605000 | AUM in crore (₹). 1 crore = ₹1,00,00,000. Standard unit used in the industry. |
| `num_schemes` | INTEGER | YES | 186 | Total number of schemes offered by this fund house at this date. |

---

## 7. Business Glossary

| Term | Full Form | Definition |
|------|-----------|------------|
| **AMFI** | Association of Mutual Funds in India | Industry body that regulates and promotes mutual funds in India. Assigns unique AMFI codes to all schemes. |
| **NAV** | Net Asset Value | Price per unit of a mutual fund. Calculated as (Total Assets − Liabilities) ÷ Total Units. Published daily after market close. |
| **AUM** | Assets Under Management | Total market value of investments managed by a fund or fund house. |
| **SIP** | Systematic Investment Plan | A method to invest a fixed amount every month in a fund. Like an EMI for investing. |
| **KYC** | Know Your Customer | Mandatory identity verification (Aadhaar/PAN) required before investing in mutual funds. |
| **AMC** | Asset Management Company | The company that manages mutual funds. Also called Fund House (e.g. SBI Mutual Fund, HDFC Mutual Fund). |
| **SEBI** | Securities and Exchange Board of India | Market regulator that governs mutual funds in India. |
| **CAGR** | Compounded Annual Growth Rate | The smoothed annual return rate over multiple years. Better than simple average for comparing investments. |
| **Alpha** | — | Excess return generated by a fund manager over the benchmark. Positive alpha = skilled management. |
| **Beta** | — | Sensitivity of a fund to market movements. Beta=1 means same movement as market. |
| **Sharpe Ratio** | — | Risk-adjusted return. Higher = better return per unit of risk taken. |
| **Drawdown** | Maximum Drawdown | The worst fall in NAV from a peak to the next trough. Always expressed as a negative percentage. |
| **Expense Ratio** | — | Annual fee charged to manage the fund, expressed as % of AUM. Deducted daily from NAV. |
| **Direct Plan** | — | Fund bought directly from AMC without a broker. Lower expense ratio than Regular plan. |
| **Regular Plan** | — | Fund bought through a distributor/broker. Higher expense ratio as distributor commission is included. |
| **T30** | Top 30 Cities | SEBI classification for the 30 largest Indian cities. Investors from T30 have easier access to mutual funds. |
| **B30** | Beyond Top 30 | SEBI classification for cities outside the top 30. SEBI gives incentives to grow mutual fund penetration in B30. |
| **ELSS** | Equity Linked Savings Scheme | A tax-saving mutual fund under Section 80C. 3-year lock-in period. Also called Tax Saver fund. |
| **TRI** | Total Return Index | Benchmark index that includes dividend reinvestment (not just price). More accurate for performance comparison. |
| **Exit Load** | — | Fee charged when you sell (redeem) units before a specified period. Deducted from redemption proceeds. |
| **Folio** | — | An investor's account with a fund house. One investor can have multiple folios. |
| **Lumpsum** | — | A one-time large investment in a mutual fund, as opposed to monthly SIP. |
| **Redemption** | — | Selling (withdrawing) your mutual fund units back to the fund house. |

---

## Schema Diagram

```
dim_fund (amfi_code PK)
    │
    ├──── fact_nav (amfi_code FK, date_id FK)
    ├──── fact_transactions (amfi_code FK, date_id FK)
    ├──── fact_performance (amfi_code FK)
    │
dim_date (date_id PK)
    │
    ├──── fact_nav (date_id FK)
    ├──── fact_transactions (date_id FK)
    └──── fact_aum (date_id FK)
```

---

## Data Quality Notes

| Table | Issue | Resolution |
|-------|-------|------------|
| fact_nav | date column stored as string | Converted to datetime in cleaning |
| fact_nav | Weekends/holidays had no NAV | Forward-filled from previous trading day — added 18,320 rows |
| fact_transactions | transaction_date stored as string | Converted to datetime in cleaning |
| fact_performance | max_drawdown_pct all negative | Expected — drawdown is always negative by definition |
| dim_fund | launch_date stored as string | Converted to datetime in cleaning |
| fact_aum | date stored as string | Converted and stored as date_id in SQLite |
