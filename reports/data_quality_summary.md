# Data Quality Summary — AMFI Code Validation
**Project:** Mutual Fund Analytics
**Date:** 23 June 2026
**Author:** Data Analyst
**Files Checked:** 01_fund_master.csv, 02_nav_history.csv

---

## 1. AMFI Code Validation Result

| Check | Result | Status |
|---|---|---|
| Total schemes in fund_master | 40 | — |
| Total schemes in nav_history | 40 | — |
| Codes matched in BOTH tables | 40 / 40 | ✅ PASS |
| Codes missing from nav_history | 0 | ✅ PASS |
| Extra codes in nav_history only | 0 | ✅ PASS |

**Verdict: 100% of AMFI codes in fund_master are present in nav_history. No orphan codes found.**

---

## 2. NAV History Quality

| Check | Result | Status |
|---|---|---|
| Total NAV rows | 46,000 | — |
| Rows per scheme | 1,150 each (perfectly even) | ✅ PASS |
| Null values in NAV column | 0 | ✅ PASS |
| Null values in date column | 0 | ✅ PASS |
| Duplicate (code + date) rows | 0 | ✅ PASS |
| Date range | 03 Jan 2022 – 29 May 2026 | ✅ ~4.5 years |

---

## 3. Fund Master Quality

| Check | Result | Status |
|---|---|---|
| Total schemes | 40 | — |
| Null values (any column) | 0 across all 15 columns | ✅ PASS |
| Duplicate AMFI codes | 0 | ✅ PASS |
| Fund houses covered | 10 | — |
| Categories | 2 (Equity, Debt) | — |
| Sub-categories | 12 | — |
| Risk grades | 5 (Low to Very High) | — |

---

## 4. NAV Range by Scheme (Sample)

| AMFI Code | Scheme Name | Min NAV (₹) | Max NAV (₹) |
|---|---|---|---|
| 119551 | SBI Bluechip – Regular | 50.03 | 151.44 |
| 120503 | ICICI Pru Bluechip – Regular | 55.40 | 118.87 |
| 118632 | Nippon Large Cap – Regular | 42.80 | 114.44 |
| 119092 | Axis Bluechip – Regular | 35.13 | 56.70 |
| 120841 | Kotak Bluechip – Regular | 246.66 | 484.63 |
| 125497 | HDFC Top 100 – Direct | 529.64 | 1,286.06 |

---

## 5. Overall Data Quality Score

| Dataset | Completeness | Accuracy | Consistency | Score |
|---|---|---|---|---|
| fund_master | 100% | ✅ | ✅ | **Excellent** |
| nav_history | 100% | ✅ | ✅ | **Excellent** |

**Overall: Data is clean, complete, and ready for analysis. No issues found.**

---

## 6. Key Observations

1. Every scheme in fund_master has exactly **1,150 NAV records** — perfectly uniform coverage.
2. Both Regular and Direct plans are included for major schemes (e.g. SBI Bluechip 119551 + 119552).
3. NAV history spans **4.5 years** (Jan 2022 to May 2026) — enough for meaningful trend analysis.
4. Kotak Liquid Fund (120844) has the highest NAV at ₹3,180–4,268 — expected for liquid funds.
5. Zero null values across both datasets — no imputation needed.

