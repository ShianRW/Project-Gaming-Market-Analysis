import sqlite3
import pandas as pd
from pathlib import Path

# === Define paths ===
BASE_DIR = Path(".")
EXTERNAL_DIR = BASE_DIR / "data_external"
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "games_analytics.db"

POP_CLEAN = EXTERNAL_DIR / "population_clean.csv"

# === Load cleaned population CSV ===
population_df = pd.read_csv(POP_CLEAN)

# === Connect to SQLite ===
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# === Create population table ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS population (
    country TEXT PRIMARY KEY,
    population INTEGER
);
""")

conn.commit()

# === Insert data ===
population_df.to_sql(
    "population",
    conn,
    if_exists="replace",   # replace ensures the table updates cleanly
    index=False
)

conn.close()
print("Population data successfully added to SQLite.")