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