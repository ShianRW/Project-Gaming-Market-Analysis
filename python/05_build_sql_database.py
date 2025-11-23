import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(".")
CLEAN_DIR = BASE_DIR / "data_clean"
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "games_analytics.db"

games = pd.read_csv(CLEAN_DIR / "games_master.csv")
players = pd.read_csv(CLEAN_DIR / "players_master.csv")
purchases = pd.read_csv(CLEAN_DIR / "purchases_master.csv")
prices = pd.read_csv(CLEAN_DIR / "prices_master_latest.csv")

conn = sqlite3.connect(DB_PATH) # establishes the 'door' through which python writes data to SQL.

cursor = conn.cursor() # cursor -> essentially the 'tool' used to send SQL queries through the 'door' (conn) and retrieve results.

#the following uses SQL language which will be skipped over in python to avoid confusing the code.
cursor.execute("""
CREATE TABLE IF NOT EXISTS games (
    gameid INTEGER,
    platform TEXT,
    platform_raw TEXT,
    title TEXT,
    developers TEXT,
    publishers TEXT,
    genres TEXT,
    supported_languages TEXT,
    release_date TEXT,
    release_date_year INTEGER,
    release_date_month INTEGER,
    release_date_quarter INTEGER,
    PRIMARY KEY (gameid, platform)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    playerid INTEGER PRIMARY KEY,
    platform TEXT,
    nickname TEXT,
    country TEXT,
    created_date TEXT
);
""")
# FOREIGN KEY () REFERENCES _ -> constraint that links this table to the primary key columns in the players and games tables.
## This ensures that you cannot record a purchase for a gameid that doesn't actually exist in the games table.
cursor.execute("""
CREATE TABLE IF NOT EXISTS purchases (
    playerid INTEGER,
    gameid INTEGER,
    platform TEXT,
    FOREIGN KEY (playerid) REFERENCES players(playerid),
    FOREIGN KEY (gameid) REFERENCES games(gameid)
);
""")

# usd REAL -> Defines the columns for currency prices. In SQLite, REAL is used to store floats.
cursor.execute("""
CREATE TABLE IF NOT EXISTS prices (
    gameid INTEGER,
    platform TEXT,
    usd REAL,
    eur REAL,
    gbp REAL,
    jpy REAL,
    rub REAL,
    date_acquired TEXT,
    FOREIGN KEY (gameid) REFERENCES games(gameid)
);
""")

# Tells the database connection to finalize and save all the changes (the table creation commands) made by the cursor.
conn.commit()

games.to_sql("games", conn, if_exists="append", index=False) # inserts the data in the 'games' data frame into the 'games' table in the database.
players.to_sql("players", conn, if_exists="append", index=False)
purchases.to_sql("purchases", conn, if_exists="append", index=False)
prices.to_sql("prices", conn, if_exists="append", index=False)

# Terminates the connection to the SQLite database file.
conn.close()
