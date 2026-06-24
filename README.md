# 📊 Mutual Fund Analytics — India

> An end-to-end data analytics project on Indian mutual funds using real AMFI data.
> Covers NAV history, AUM trends, SIP inflows, investor behaviour, portfolio holdings,
> and benchmark index comparisons — built with Python, Pandas, and Jupyter.

---

## 📌 Project Overview

| Detail | Info |
|---|---|
| **Domain** | Indian Mutual Fund Industry |
| **Data Source** | AMFI (Association of Mutual Funds in India) + mfapi.in |
| **Time Period** | January 2022 – May 2026 (4.5 years) |
| **Fund Houses** | 10 (SBI, HDFC, ICICI Pru, Nippon, Kotak, Axis, ABSL, UTI, Mirae, DSP) |
| **Schemes Covered** | 40 mutual fund schemes |
| **Total Records** | 87,493 rows across 10 datasets |
| **Language** | Python 3.x |
| **Tools** | Pandas, NumPy, Matplotlib, Seaborn, Plotly, Jupyter |

---

## 📁 Project Structure

```
mf_analytics/
│
├── data/
│   ├── raw/                        # Original CSV files — never edit these
│   │   ├── 01_fund_master.csv
│   │   ├── 02_nav_history.csv
│   │   ├── 03_aum_by_fund_house.csv
│   │   ├── 04_monthly_sip_inflows.csv
│   │   ├── 05_category_inflows.csv
│   │   ├── 06_industry_folio_count.csv
│   │   ├── 07_scheme_performance.csv
│   │   ├── 08_investor_transactions.csv
│   │   ├── 09_portfolio_holdings.csv
│   │   ├── 10_benchmark_indices.csv
│   │   ├── live_nav_125497.csv     # Live NAV — HDFC Top 100
│   │   ├── live_nav_125497.json    # Raw JSON from mfapi.in
│   │   └── live_nav_5schemes.csv   # Live NAV — 5 large-cap schemes
│   │
│   └── processed/                  # Cleaned versions — use these for analysis
│       ├── 01_fund_master_clean.csv
│       ├── 02_nav_history_clean.csv
│       ├── 03_aum_by_fund_house_clean.csv
│       ├── 04_monthly_sip_inflows_clean.csv
│       ├── 05_category_inflows_clean.csv
│       ├── 06_industry_folio_count_clean.csv
│       ├── 07_scheme_performance_clean.csv
│       ├── 08_investor_transactions_clean.csv
│       ├── 09_portfolio_holdings_clean.csv
│       └── 10_benchmark_indices_clean.csv
│
├── notebooks/                      # Jupyter notebooks for EDA and charts
│
├── sql/                            # SQL queries and schema files
│
├── dashboard/                      # Plotly / Dash dashboard code
│
├── reports/                        # Reports and summaries
│   ├── anomaly_report.md           # Detailed anomaly findings for all 10 files
│   └── data_quality_summary.md     # AMFI code validation results
│
├── data_ingestion.py               # Day 1 — loads, inspects, validates all data
├── data_cleaning.py                # Day 2 — cleans all 10 files, saves to processed/
├── live_nav_fetch.py               # Day 1 — fetches live NAV from mfapi.in
├── requirements.txt                # All Python package dependencies
└── README.md                       # This file
```

---

## 🗂️ Datasets

| # | File | Rows | Cols | Description |
|---|---|---|---|---|
| 1 | 01_fund_master.csv | 40 | 15 | Scheme metadata — fund house, category, expense ratio, risk grade |
| 2 | 02_nav_history.csv | 46,000 | 3 | Daily NAV per scheme from Jan 2022 to May 2026 |
| 3 | 03_aum_by_fund_house.csv | 90 | 5 | Quarterly AUM (₹ Crore) per fund house |
| 4 | 04_monthly_sip_inflows.csv | 48 | 6 | Monthly SIP inflow amounts across industry |
| 5 | 05_category_inflows.csv | 144 | 3 | Net inflows by fund category per month |
| 6 | 06_industry_folio_count.csv | 21 | 6 | Quarterly investor folio count by type |
| 7 | 07_scheme_performance.csv | 40 | 19 | Risk-return metrics — Sharpe, Sortino, Alpha, Beta, Drawdown |
| 8 | 08_investor_transactions.csv | 32,778 | 13 | Investor buy/sell transactions with demographics |
| 9 | 09_portfolio_holdings.csv | 322 | 8 | Top stock holdings per scheme with weights |
| 10 | 10_benchmark_indices.csv | 8,050 | 3 | Daily close values for NIFTY50, NIFTY100, BSE Smallcap, etc. |

---

## ⚙️ Setup — Step by Step

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/mf_analytics.git
cd mf_analytics
```

### Step 2 — Create a virtual environment
```bash
# Create it
python -m venv .venv

# Activate it — Windows
.venv\Scripts\activate

# Activate it — Mac / Linux
source .venv/bin/activate
```
> You will see `(.venv)` appear at the start of your terminal prompt.
> This means the environment is active.

### Step 3 — Install all dependencies
```bash
pip install -r requirements.txt
```
> This installs: pandas, numpy, matplotlib, seaborn, plotly,
> sqlalchemy, requests, scipy, jupyter

### Step 4 — Add your CSV files
Place all 10 raw CSV files inside `data/raw/`:
```
data/raw/01_fund_master.csv
data/raw/02_nav_history.csv
... (all 10 files)
```

### Step 5 — Run data ingestion (Day 1)
```bash
python data_ingestion.py
```
This will:
- Load all 10 CSV files
- Print shape, dtypes, and head for each
- Detect anomalies
- Explore the fund master (fund houses, categories, risk grades)
- Validate all AMFI codes against nav_history
- Save `data/processed/data_quality_report.txt`

### Step 6 — Fetch live NAV (requires internet)
```bash
python live_nav_fetch.py
```
This will:
- Call `https://api.mfapi.in/mf/125497` (HDFC Top 100 Direct)
- Fetch live NAV for 5 key large-cap schemes
- Save JSON and CSV to `data/raw/`

### Step 7 — Run data cleaning (Day 2)
```bash
python data_cleaning.py
```
This will:
- Fix all date columns (string → datetime)
- Handle missing values
- Normalise portfolio weights
- Add derived columns (fund age, year, quarter, etc.)
- Save 10 cleaned files to `data/processed/`

### Step 8 — Open Jupyter notebooks
```bash
jupyter notebook
```
Navigate to the `notebooks/` folder and open any `.ipynb` file.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| pandas | ≥ 2.0.0 | Data loading, cleaning, analysis |
| numpy | ≥ 1.24.0 | Numerical operations |
| matplotlib | ≥ 3.7.0 | Static charts and plots |
| seaborn | ≥ 0.12.0 | Statistical visualisations |
| plotly | ≥ 5.18.0 | Interactive charts and dashboard |
| sqlalchemy | ≥ 2.0.0 | Database connectivity |
| requests | ≥ 2.31.0 | Live NAV API calls |
| scipy | ≥ 1.11.0 | Statistical calculations |
| jupyter | ≥ 1.0.0 | Interactive notebooks |

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🔌 Live NAV API

**Source:** [mfapi.in](https://mfapi.in) — Free, no API key needed

**Endpoint:**
```
GET https://api.mfapi.in/mf/{amfi_code}
```

**Schemes fetched in this project:**

| Scheme | AMFI Code | Category |
|---|---|---|
| HDFC Top 100 – Direct | 125497 | Large Cap |
| SBI Bluechip | 119551 | Large Cap |
| ICICI Prudential Bluechip | 120503 | Large Cap |
| Nippon India Large Cap | 118632 | Large Cap |
| Axis Bluechip | 119092 | Large Cap |
| Kotak Bluechip | 120841 | Large Cap |

---

## 🔍 Key Findings So Far

- **Best 1-year return** across all 40 schemes: **24.93%**
- **Worst 1-year return:** **4.26%**
- **AMFI Code Validation:** 40/40 codes matched perfectly between fund_master and nav_history
- **Data Quality:** Zero nulls after cleaning. Only 12 expected nulls in yoy_growth_pct (first year — no prior year to compare)
- **Largest fund house by scheme count:** ICICI Prudential (most diverse)
- **NAV history coverage:** 1,150 records per scheme — perfectly uniform

---

## ✅ Day-wise Progress

### Day 1 — Data Ingestion
- [x] Created project folder structure
- [x] Installed all 9 dependencies
- [x] Loaded all 10 CSV files with shape, dtypes, head
- [x] Fetched live NAV from mfapi.in (6 schemes)
- [x] Explored fund master — fund houses, categories, risk grades
- [x] Validated AMFI codes — 40/40 matched
- [x] Wrote anomaly report and data quality summary
- [x] Git commit: *"Day 1: Data ingestion complete"*

### Day 2 — Data Cleaning *(in progress)*
- [x] Fixed date columns across all 10 files
- [x] Handled 12 null values in SIP inflows
- [x] Normalised portfolio weights
- [x] Added derived columns (fund age, year, quarter, flow direction)
- [x] Saved 10 clean files to data/processed/
- [ ] EDA notebooks
- [ ] Visualisations and charts
- [ ] Git commit: *"Day 2: EDA and data cleaning complete"*

---

## 🤝 Contributing

This is a personal learning project. Feel free to fork and adapt it.

---

## 📄 Licence

This project is for educational purposes only.
Data sourced from AMFI India and mfapi.in (public domain).# 📊 Mutual Fund Analytics — India

> An end-to-end data analytics project on Indian mutual funds using real AMFI data.
> Covers NAV history, AUM trends, SIP inflows, investor behaviour, portfolio holdings,
> and benchmark index comparisons — built with Python, Pandas, and Jupyter.

---

## 📌 Project Overview

| Detail | Info |
|---|---|
| **Domain** | Indian Mutual Fund Industry |
| **Data Source** | AMFI (Association of Mutual Funds in India) + mfapi.in |
| **Time Period** | January 2022 – May 2026 (4.5 years) |
| **Fund Houses** | 10 (SBI, HDFC, ICICI Pru, Nippon, Kotak, Axis, ABSL, UTI, Mirae, DSP) |
| **Schemes Covered** | 40 mutual fund schemes |
| **Total Records** | 87,493 rows across 10 datasets |
| **Language** | Python 3.x |
| **Tools** | Pandas, NumPy, Matplotlib, Seaborn, Plotly, Jupyter |

---

## 📁 Project Structure

```
mf_analytics/
│
├── data/
│   ├── raw/                        # Original CSV files — never edit these
│   │   ├── 01_fund_master.csv
│   │   ├── 02_nav_history.csv
│   │   ├── 03_aum_by_fund_house.csv
│   │   ├── 04_monthly_sip_inflows.csv
│   │   ├── 05_category_inflows.csv
│   │   ├── 06_industry_folio_count.csv
│   │   ├── 07_scheme_performance.csv
│   │   ├── 08_investor_transactions.csv
│   │   ├── 09_portfolio_holdings.csv
│   │   ├── 10_benchmark_indices.csv
│   │   ├── live_nav_125497.csv     # Live NAV — HDFC Top 100
│   │   ├── live_nav_125497.json    # Raw JSON from mfapi.in
│   │   └── live_nav_5schemes.csv   # Live NAV — 5 large-cap schemes
│   │
│   └── processed/                  # Cleaned versions — use these for analysis
│       ├── 01_fund_master_clean.csv
│       ├── 02_nav_history_clean.csv
│       ├── 03_aum_by_fund_house_clean.csv
│       ├── 04_monthly_sip_inflows_clean.csv
│       ├── 05_category_inflows_clean.csv
│       ├── 06_industry_folio_count_clean.csv
│       ├── 07_scheme_performance_clean.csv
│       ├── 08_investor_transactions_clean.csv
│       ├── 09_portfolio_holdings_clean.csv
│       └── 10_benchmark_indices_clean.csv
│
├── notebooks/                      # Jupyter notebooks for EDA and charts
│
├── sql/                            # SQL queries and schema files
│
├── dashboard/                      # Plotly / Dash dashboard code
│
├── reports/                        # Reports and summaries
│   ├── anomaly_report.md           # Detailed anomaly findings for all 10 files
│   └── data_quality_summary.md     # AMFI code validation results
│
├── data_ingestion.py               # Day 1 — loads, inspects, validates all data
├── data_cleaning.py                # Day 2 — cleans all 10 files, saves to processed/
├── live_nav_fetch.py               # Day 1 — fetches live NAV from mfapi.in
├── requirements.txt                # All Python package dependencies
└── README.md                       # This file
```

---

## 🗂️ Datasets

| # | File | Rows | Cols | Description |
|---|---|---|---|---|
| 1 | 01_fund_master.csv | 40 | 15 | Scheme metadata — fund house, category, expense ratio, risk grade |
| 2 | 02_nav_history.csv | 46,000 | 3 | Daily NAV per scheme from Jan 2022 to May 2026 |
| 3 | 03_aum_by_fund_house.csv | 90 | 5 | Quarterly AUM (₹ Crore) per fund house |
| 4 | 04_monthly_sip_inflows.csv | 48 | 6 | Monthly SIP inflow amounts across industry |
| 5 | 05_category_inflows.csv | 144 | 3 | Net inflows by fund category per month |
| 6 | 06_industry_folio_count.csv | 21 | 6 | Quarterly investor folio count by type |
| 7 | 07_scheme_performance.csv | 40 | 19 | Risk-return metrics — Sharpe, Sortino, Alpha, Beta, Drawdown |
| 8 | 08_investor_transactions.csv | 32,778 | 13 | Investor buy/sell transactions with demographics |
| 9 | 09_portfolio_holdings.csv | 322 | 8 | Top stock holdings per scheme with weights |
| 10 | 10_benchmark_indices.csv | 8,050 | 3 | Daily close values for NIFTY50, NIFTY100, BSE Smallcap, etc. |

---

## ⚙️ Setup — Step by Step

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/mf_analytics.git
cd mf_analytics
```

### Step 2 — Create a virtual environment
```bash
# Create it
python -m venv .venv

# Activate it — Windows
.venv\Scripts\activate

# Activate it — Mac / Linux
source .venv/bin/activate
```
> You will see `(.venv)` appear at the start of your terminal prompt.
> This means the environment is active.

### Step 3 — Install all dependencies
```bash
pip install -r requirements.txt
```
> This installs: pandas, numpy, matplotlib, seaborn, plotly,
> sqlalchemy, requests, scipy, jupyter

### Step 4 — Add your CSV files
Place all 10 raw CSV files inside `data/raw/`:
```
data/raw/01_fund_master.csv
data/raw/02_nav_history.csv
... (all 10 files)
```

### Step 5 — Run data ingestion (Day 1)
```bash
python data_ingestion.py
```
This will:
- Load all 10 CSV files
- Print shape, dtypes, and head for each
- Detect anomalies
- Explore the fund master (fund houses, categories, risk grades)
- Validate all AMFI codes against nav_history
- Save `data/processed/data_quality_report.txt`

### Step 6 — Fetch live NAV (requires internet)
```bash
python live_nav_fetch.py
```
This will:
- Call `https://api.mfapi.in/mf/125497` (HDFC Top 100 Direct)
- Fetch live NAV for 5 key large-cap schemes
- Save JSON and CSV to `data/raw/`

### Step 7 — Run data cleaning (Day 2)
```bash
python data_cleaning.py
```
This will:
- Fix all date columns (string → datetime)
- Handle missing values
- Normalise portfolio weights
- Add derived columns (fund age, year, quarter, etc.)
- Save 10 cleaned files to `data/processed/`

### Step 8 — Open Jupyter notebooks
```bash
jupyter notebook
```
Navigate to the `notebooks/` folder and open any `.ipynb` file.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| pandas | ≥ 2.0.0 | Data loading, cleaning, analysis |
| numpy | ≥ 1.24.0 | Numerical operations |
| matplotlib | ≥ 3.7.0 | Static charts and plots |
| seaborn | ≥ 0.12.0 | Statistical visualisations |
| plotly | ≥ 5.18.0 | Interactive charts and dashboard |
| sqlalchemy | ≥ 2.0.0 | Database connectivity |
| requests | ≥ 2.31.0 | Live NAV API calls |
| scipy | ≥ 1.11.0 | Statistical calculations |
| jupyter | ≥ 1.0.0 | Interactive notebooks |

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🔌 Live NAV API

**Source:** [mfapi.in](https://mfapi.in) — Free, no API key needed

**Endpoint:**
```
GET https://api.mfapi.in/mf/{amfi_code}
```

**Schemes fetched in this project:**

| Scheme | AMFI Code | Category |
|---|---|---|
| HDFC Top 100 – Direct | 125497 | Large Cap |
| SBI Bluechip | 119551 | Large Cap |
| ICICI Prudential Bluechip | 120503 | Large Cap |
| Nippon India Large Cap | 118632 | Large Cap |
| Axis Bluechip | 119092 | Large Cap |
| Kotak Bluechip | 120841 | Large Cap |

---

## 🔍 Key Findings So Far

- **Best 1-year return** across all 40 schemes: **24.93%**
- **Worst 1-year return:** **4.26%**
- **AMFI Code Validation:** 40/40 codes matched perfectly between fund_master and nav_history
- **Data Quality:** Zero nulls after cleaning. Only 12 expected nulls in yoy_growth_pct (first year — no prior year to compare)
- **Largest fund house by scheme count:** ICICI Prudential (most diverse)
- **NAV history coverage:** 1,150 records per scheme — perfectly uniform

---

## ✅ Day-wise Progress

### Day 1 — Data Ingestion
- [x] Created project folder structure
- [x] Installed all 9 dependencies
- [x] Loaded all 10 CSV files with shape, dtypes, head
- [x] Fetched live NAV from mfapi.in (6 schemes)
- [x] Explored fund master — fund houses, categories, risk grades
- [x] Validated AMFI codes — 40/40 matched
- [x] Wrote anomaly report and data quality summary
- [x] Git commit: *"Day 1: Data ingestion complete"*

### Day 2 — Data Cleaning *(in progress)*
- [x] Fixed date columns across all 10 files
- [x] Handled 12 null values in SIP inflows
- [x] Normalised portfolio weights
- [x] Added derived columns (fund age, year, quarter, flow direction)
- [x] Saved 10 clean files to data/processed/
- [ ] EDA notebooks
- [ ] Visualisations and charts
- [ ] Git commit: *"Day 2: EDA and data cleaning complete"*

---

## 🤝 Contributing

This is a personal learning project. Feel free to fork and adapt it.

---

## 📄 Licence

This project is for educational purposes only.
Data sourced from AMFI India and mfapi.in (public domain).
