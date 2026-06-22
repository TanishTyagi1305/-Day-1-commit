"""
live_nav_fetch.py
=================
Day 1 - Mutual Fund Analytics Project
Fetch live NAV from mfapi.in for HDFC Top 100 Direct and 5 key schemes.
Saves raw JSON + processed CSV to data/raw/.

Usage:
    python live_nav_fetch.py
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL = "https://api.mfapi.in/mf/{code}"
RAW_DIR  = os.path.join(os.path.dirname(__file__), "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# Primary scheme (Task 4)
HDFC_TOP100_CODE = 125497

# Five key schemes (Task 5)
KEY_SCHEMES = {
    119551: "SBI Bluechip Fund",
    120503: "ICICI Bluechip Fund",
    118632: "Nippon Large Cap Fund",
    119092: "Axis Bluechip Fund",
    120841: "Kotak Bluechip Fund",
}

TIMEOUT_SEC = 10


# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_nav(amfi_code: int) -> dict:
    """
    GET https://api.mfapi.in/mf/<code>
    Returns the parsed JSON response dict or raises on failure.
    """
    url = BASE_URL.format(code=amfi_code)
    print(f"  Fetching  {url}")
    response = requests.get(url, timeout=TIMEOUT_SEC)
    response.raise_for_status()
    return response.json()


def latest_nav_record(data: dict, amfi_code: int) -> dict:
    """Extract latest NAV record from mfapi.in response."""
    meta    = data.get("meta", {})
    records = data.get("data", [])

    latest = records[0] if records else {}
    return {
        "amfi_code":   amfi_code,
        "scheme_name": meta.get("scheme_name", ""),
        "fund_house":  meta.get("fund_house", ""),
        "category":    meta.get("scheme_category", ""),
        "nav_date":    latest.get("date", ""),
        "nav":         float(latest.get("nav", 0)),
        "fetched_at":  datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


# ── Task 4: HDFC Top 100 Direct ──────────────────────────────────────────────
def fetch_hdfc_top100() -> pd.DataFrame:
    print("\n── Task 4: HDFC Top 100 Direct (125497) ──")
    data    = fetch_nav(HDFC_TOP100_CODE)
    record  = latest_nav_record(data, HDFC_TOP100_CODE)

    # Save raw JSON
    json_path = os.path.join(RAW_DIR, f"live_nav_{HDFC_TOP100_CODE}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  Raw JSON saved  → {json_path}")

    # Save processed CSV
    df        = pd.DataFrame([record])
    csv_path  = os.path.join(RAW_DIR, f"live_nav_{HDFC_TOP100_CODE}.csv")
    df.to_csv(csv_path, index=False)
    print(f"  CSV saved       → {csv_path}")
    print(f"  Latest NAV      : ₹{record['nav']:.4f}  ({record['nav_date']})")
    return df


# ── Task 5: Five Key Schemes ──────────────────────────────────────────────────
def fetch_five_schemes() -> pd.DataFrame:
    print("\n── Task 5: Five Key Large-Cap Schemes ──")
    records = []

    for code, friendly_name in KEY_SCHEMES.items():
        try:
            data   = fetch_nav(code)
            record = latest_nav_record(data, code)
            record["friendly_name"] = friendly_name
            records.append(record)
            print(f"  {friendly_name:<28}  ₹{record['nav']:>10.4f}  ({record['nav_date']})")
            time.sleep(0.3)   # be polite to the public API
        except Exception as exc:
            print(f"  ✗ {friendly_name} ({code}): {exc}")
            records.append({
                "amfi_code": code,
                "friendly_name": friendly_name,
                "nav": None,
                "error": str(exc),
            })

    df       = pd.DataFrame(records)
    csv_path = os.path.join(RAW_DIR, "live_nav_5schemes.csv")
    df.to_csv(csv_path, index=False)
    print(f"\n  5-scheme CSV saved → {csv_path}")
    return df


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 64)
    print("  LIVE NAV FETCH — mfapi.in")
    print(f"  Run at: {datetime.utcnow().isoformat(timespec='seconds')}Z")
    print("=" * 64)

    df_hdfc  = fetch_hdfc_top100()
    df_five  = fetch_five_schemes()

    print("\n── Combined Summary ──")
    print(df_five[["amfi_code", "friendly_name", "nav", "nav_date"]].to_string(index=False))
    print("\n✓ live_nav_fetch.py complete")