"""
Script Name: 03_clean_players_and_purchases.py
Purpose:
    Clean and merge players.csv and purchased_games.csv across platforms.
    Tasks include:
        - validating player IDs
        - normalising country fields
        - expanding purchase lists into 1 row per purchase
        - tagging records with platform
        - building unified players_master and purchases_master datasets

Dataset:
    Input:   data_raw/<platform>/players.csv
             data_raw/<platform>/purchased_games.csv
    Output:  data_clean/players_master.csv
             data_clean/purchases_master.csv

Author: Shian Raveneau-Wright

Notes:
    - Creates clean relational tables ready for SQL foreign keys.
    - Ensures consistent schemas across platforms.
    - Purchase expansion supports accurate player value analysis.
"""


import os
import ast
import pandas as pd
from datetime import datetime


''' ===== PATH SETUP ===== '''

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW_BASE = os.path.join(REPO_ROOT, "data_raw")
CLEAN_DIR = os.path.join(REPO_ROOT, "data_clean")
os.makedirs(CLEAN_DIR, exist_ok=True) # if the folder already exists - move on and don't produce an error message.

PLATFORMS = ["playstation", "steam", "xbox"]


''' ===== SAFE PARSER FOR LIST FIELDS ===== '''

def safe_literal_eval(value):
# Convert a string like "[1, 2, 3]" into a real Python list.
#Handles None, empty strings, invalid formats.

    if value is None:
        return []
    if isinstance(value, list):
        return value
    if not isinstance(value, str):
        return []
    val = value.replace("“", "\"").replace("”", "\"").replace("'", "\"")
    try:
        return ast.literal_eval(val)
    except:
        return []

''' ===== CLEAN PLAYERS FOR ONE PLATFORM ===== '''

def clean_players(platform):
    raw_path = os.path.join(RAW_BASE, platform, "players.csv")
    df = pd.read_csv(raw_path)

    if platform == "playstation":
        df["platform"] = "PlayStation"
        df["created_date"] = None

    elif platform == "steam":
        df["platform"] = "Steam"
        df["created_date"] = pd.to_datetime(df["created"], errors="coerce")
        df.drop(columns=["created"], inplace=True)
        df["nickname"] = None

    elif platform == "xbox":
        df["platform"] = "Xbox"
        df["country"] = None
        df["created_date"] = None

    df = df[["playerid", "platform", "nickname", "country", "created_date"]]

    # Deduplicate if needed
    df = df.drop_duplicates(subset=["playerid", "platform"], keep="first")

    # Save cleaned player table
    out_path = os.path.join(CLEAN_DIR, f"players_{platform}.csv")
    df.to_csv(out_path, index=False)
    print(f"  ✔ saved players_{platform}.csv")
    return df

''' ===== CLEAN PURCHASED GAMES FOR ONE PLATFORM ===== '''

def clean_purchases(platform):
    raw_path = os.path.join(RAW_BASE, platform, "purchased_games.csv")
    df = pd.read_csv(raw_path)

    # Normalize library field
    df["library"] = df["library"].apply(safe_literal_eval)

    # EXPLODE: one row per purchased game
    df_exploded = df.explode("library") # explode - takes a single cell with a list/array and seperates each list member as a seperate cell.
    df_exploded = df_exploded.rename(columns={"library": "gameid"}) # replaces old column name 'library' with 'gameid'.

    # Remove rows where gameid is missing
    df_exploded = df_exploded[df_exploded["gameid"].notna()]
    # checks every item in the gameid column and returns a bool value of true if the value is NOT A NaN and drops any that are false.

    df_exploded["platform"] = platform.capitalize() # capitalises the first letter of the text in the cell.

    # Ensure gameid is integer
    df_exploded["gameid"] = df_exploded["gameid"].astype("Int64")

    # Final order
    df_exploded = df_exploded[["playerid", "gameid", "platform"]]

    out_path = os.path.join(CLEAN_DIR, f"purchases_{platform}.csv")
    df_exploded.to_csv(out_path, index=False)
    print(f"  ✔ saved purchases_{platform}.csv")

    return df_exploded


''' ===== MAIN EXECUTION ===== '''

def main():
    all_players = []
    all_purchases = []

    print("\nCleaning PLAYERS and PURCHASES...")

    for plat in PLATFORMS:
        print(f"\n--- Platform: {plat} ---")

        players_df = clean_players(plat)
        purchases_df = clean_purchases(plat)

        all_players.append(players_df)
        all_purchases.append(purchases_df)

    # Combine per-platform CSVs into master tables
    players_master = pd.concat(all_players, ignore_index=True)
    purchases_master = pd.concat(all_purchases, ignore_index=True)

    players_master.to_csv(os.path.join(CLEAN_DIR, "players_master.csv"), index=False)
    purchases_master.to_csv(os.path.join(CLEAN_DIR, "purchases_master.csv"), index=False)

    print("\n✔ Master tables created:")
    print("  players_master.csv")
    print("  purchases_master.csv")

if __name__ == "__main__":
    main()