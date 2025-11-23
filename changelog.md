# Changelog

## [v0.1] - Initial Data Import
- Downloaded Kaggle dataset.
- Extracted raw CSV files.
- Organized data by platform into data_raw.
- Committed dataset to GitHub.

## [v0.2] - Initial Raw Data Inspection
- Created Python environment and installed pandas/numpy/matplotlib.
- Script: 01_preview_raw_data.py
- Actions:
    - Created script to inspect raw CSV files.
    - Verified structure of games, players, prices, purchased_games tables for all platforms.
    - Identified initial data quality issues for future cleaning (missing values, datatype inconsistencies, etc.).

## [v0.3] - Games Table Cleaning
- Script: python/02_clean_games.py
- Actions:
  - Converted release_date to datetime and extracted year/month/quarter.
  - Converted developers/publishers/genres/supported_languages from stringified lists to Python lists (stored as strings in cleaned CSVs).
  - Normalized missing list fields to empty lists.
  - Deduplicated games by gameid (fallback title+platform).
  - Added platform and platform_raw columns.
  - Saved cleaned per-platform files and games_master.csv in data_clean/.

## [v0.04] - Players & Purchases Table Cleaning
- Script: 03_clean_players_and_purchases.py
- Actions:
    - Implemented full pricing analysis module across PlayStation, Steam, and Xbox datasets.
    - Added code for loading, validating, cleaning, merging, and enriching multi-currency price data.
    - Added handling for missing prices, inconsistent currencies, and timestamp variations.
    - Ensured preview-data–aware design compatible with the project’s business question.

## [v0.05] - Prices Table Cleaning
- Script: python/04_clean_prices.py
- Actions:
  - Converted price columns (usd, eur, gbp, jpy, rub) to numeric (coerced invalid values to NaN).
  - Parsed date_acquired to datetime and added consistent date formatting.
  - Dropped rows missing gameid.
  - Saved cleaned per-platform price history files.
  - Saved per-platform latest snapshot files.
  - Created consolidated master tables: prices_master_history.csv and prices_master_latest.csv in data_clean/.
