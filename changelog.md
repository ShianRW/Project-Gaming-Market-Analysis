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
<<<<<<< HEAD

## [v0.5] - SQL Database Construction
- Script: python/05_build_sql_database.py
- Actions:
  - Created database/ folder.
  - Designed SQL schemas for games, players, purchases, and prices tables.
  - Loaded cleaned CSVs into SQLite using pandas + sqlite3.
  - Committed games_analytics.db to GitHub.

## [v0.06] - SQL Framework Setup
- Created /sql directory and structured 6 category-based SQL files.
- Added professional SQL header template to each file.
- Verified SQLite database loads correctly in DB Browser.
- Tested basic SQL execution (SELECT COUNT(*) FROM games).
- Prepared environment for upcoming analytical SQL queries.

## [v0.07] - SQL Environment Validation & Market Penetration Setup
- Script: sql/01_market_penetration.sql
- Actions:
  - Verified SQLite database structure and table contents.
  - Ran initial SQL connection tests and row count checks.
  - Created the first multi-table join for market penetration analysis.
  - Added query scaffold to 01_market_penetration.sql.

## [v0.08] - Market Penetration SQL Queries Added
- Script: sql/01_market_penetration.sql
- Actions:
  - Extended 01_market_penetration.sql with core analytical queries.
  - Added country-level penetration metrics.
  - Added platform-by-country penetration analysis.
  - Created cross-platform penetration matrix.
  - Added top and low penetration market queries.
  - Added placeholder for population-normalised penetration

## [v0.09] - Population Data & Penetration Rates
- Added country_population.csv to data_external.
- Script: python/06_load_population_data.py.
- Actions:
  - Created population table inside SQLite.
  - Extended 01_market_penetration.sql with:
    - True market penetration rate query.
    - Platform-specific penetration rate query.
  - Completed the market penetration analysis framework.

## [v0.10] - External Population Data Preparation
- Script: python/06_prepare_population_data.py
- Actions:
    - Imported OWID population CSV (historical data up to 2023).
    - Filtered to year 2023 only.
    - Selected relevant columns: country, population.
    - Filtered to only countries represented in players tables.
    - Saved cleaned CSV to data_external/population_clean.csv for SQL integration.

## [v0.11] - Population Data Integration
- Script: python/07_load_population_into_sql.py
- Actions:
    - Created new population table in SQLite.
    - Imported cleaned OWID population data into database.
    - Updated market penetration SQL to calculate penetration % by country and platform.