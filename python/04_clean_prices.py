"""
Script Name: 04_clean_prices.py
Purpose:
    Clean and merge prices.csv across all platforms to create a unified,
    latest-acquired price table. Tasks include:
        - merging PlayStation, Steam, and Xbox price data
        - removing invalid rows (missing gameid, no currency values)
        - converting date_acquired to timestamp
        - selecting the most recent price per game/platform
        - normalising currency formats
        - saving final cleaned prices dataset

Dataset:
    Input:   data_raw/<platform>/prices.csv
    Output:  data_clean/prices_master_latest.csv

Author: Shian Raveneau-Wright

Notes:
    - Provides currency data required for pricing, supply, and behaviour analysis.
    - Designed to be beginner-friendly while maintaining analytical accuracy.
"""


import os
import pandas as pd
from datetime import datetime

''' ===== CONFIG ===== '''

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW_BASE = os.path.join(REPO_ROOT, "data_raw")
CLEAN_DIR = os.path.join(REPO_ROOT, "data_clean")
os.makedirs(CLEAN_DIR, exist_ok=True)

PLATFORMS = {
    "playstation": "PlayStation",
    "steam": "Steam",
    "xbox": "Xbox"
}

PRICE_COLS = ["usd", "eur", "gbp", "jpy", "rub"]  # expected numeric price columns
INPUT_NAME = "prices.csv"

''' ===== HELPER FUNCTION: Parse and Coerce price table ====='''

def clean_price_df(df, platform_pretty):
    """
    - Coerce price columns to numeric (NaN where missing / invalid)
    - Parse date_acquired => datetime
    - Drop rows missing gameid
    - Keep full cleaned history (returned)
    - Also returns a 'latest' price per gameid (most recent date_acquired)
    """
    # Standardize column names
    df.columns = [c.strip() for c in df.columns]

    # Ensure gameid exists
    if "gameid" not in df.columns:
        raise ValueError("prices.csv missing 'gameid' column")

    # Coerce price columns to numeric (if present)
    for pc in PRICE_COLS:
        if pc in df.columns:
            df[pc] = pd.to_numeric(df[pc], errors="coerce")

    # Parse date_acquired
    if "date_acquired" in df.columns:
        df["date_acquired"] = pd.to_datetime(df["date_acquired"], errors="coerce")
    else:
        df["date_acquired"] = pd.NaT

    # Drop rows with missing gameid and convert gameid to whole number
    df = df[df["gameid"].notna()].copy()
    df["gameid"] = df["gameid"].astype("Int64")

    # Add platform column
    df["platform"] = platform_pretty

    # Sort by gameid and date (so latest is last)
    df = df.sort_values(["gameid", "date_acquired"])

    # Latest price per gameid (keep the latest non-null record per currency ideally)
    # We'll group and take the last row for each gameid (most recent date_acquired)
    latest = df.groupby("gameid", as_index=False).last()

    return df, latest

''' ===== MAIN: process each platform, save outputs, and build masters ===== '''

def main():
    history_tables = []
    latest_tables = []

    for key, pretty in PLATFORMS.items():
        path = os.path.join(RAW_BASE, key, INPUT_NAME)
        print(f"Processing prices for: {pretty} — {path}")
        if not os.path.exists(path):
            print(f"  WARNING: file not found: {path}  (skipping)")
            continue

        df = pd.read_csv(path)
        df_clean_history, df_latest = clean_price_df(df, pretty)

        # Save per-platform cleaned history
        out_hist = os.path.join(CLEAN_DIR, f"prices_{key}_clean.csv")
        df_clean_history.to_csv(out_hist, index=False)
        print(f"  Saved cleaned history: {out_hist} ({len(df_clean_history)} rows)")

        # Save per-platform latest
        out_latest = os.path.join(CLEAN_DIR, f"prices_{key}_latest.csv")
        df_latest.to_csv(out_latest, index=False)
        print(f"  Saved latest snapshot: {out_latest} ({len(df_latest)} rows)")

        history_tables.append(df_clean_history)
        latest_tables.append(df_latest)

    # Build master history and latest
    if history_tables:
        master_history = pd.concat(history_tables, ignore_index=True, sort=False)
        master_history.to_csv(os.path.join(CLEAN_DIR, "prices_master_history.csv"), index=False)
        print("Saved prices_master_history.csv")

    if latest_tables:
        master_latest = pd.concat(latest_tables, ignore_index=True, sort=False)
        # Optional: ensure unique by (gameid, platform) after concatenation
        master_latest = master_latest.drop_duplicates(subset=["gameid", "platform"], keep="last")
        master_latest.to_csv(os.path.join(CLEAN_DIR, "prices_master_latest.csv"), index=False)
        print("Saved prices_master_latest.csv")

    print("\nPrice cleaning complete.")

if __name__ == "__main__":
    main()
