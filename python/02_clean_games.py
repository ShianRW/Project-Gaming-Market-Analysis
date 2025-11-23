"""
Script Name: 02_clean_games.py
Purpose:
    Clean and standardise games.csv for each platform and merge them into a
    unified master dataset. Tasks include:
        - parsing list-like fields (developers, publishers, genres, languages)
        - converting release_date to datetime
        - extracting year, month, quarter
        - deduplicating by gameid and platform
        - normalising missing values
        - saving per-platform and master cleaned files

Dataset:
    Input:   data_raw/<platform>/games.csv
    Output:  data_clean/games_clean_<platform>.csv
             data_clean/games_master.csv

Author: Shian Raveneau-Wright

Notes:
    - Ensures consistent schema across PS, Steam, and Xbox.
    - Provides the base table required for pricing, purchases, and SQL analysis.
"""


import os # file path handling.
import ast # safely convert strings that look like Python lists into real lists.
import pandas as pd # main data analysis library.
from datetime import datetime # dates/times parsing.

''' ===== CONFIGURING AND SETTING UP PATHS | Locating existing file paths and creating new ones ===== '''

# os.path.dirname(__file__) -> finds the directory for where the currnt python script is located.
# os. path.join -> combines the scripts directory with '..' [which means go up one level].
# absolute path to top-level directory of repository.

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..") 

# takes the REPO_ROOT (top level directory variable) and appends the file name to save the directory to a variable.
RAW_BASE = os.path.join(REPO_ROOT, "data_raw")
CLEAN_DIR = os.path.join(REPO_ROOT, "data_clean")

#'PLATFORMS' -> A python 'dictionary', which stores key value pairs to map the lowercase foldernames to capitalised display names.
PLATFORMS = {
    "playstation": "PlayStation",
    "steam": "Steam",
    "xbox": "Xbox"
}
# 'TABLE_NAME' -> String variable that holds the name of the specified file.
# cleaner than hard coding in the file path - as the file name can be swapped out easily if needed.
TABLE_NAME = "games.csv"

# 'os.makedirs(CLEAN_DIR)' -> attempts to create the directory specified by the 'CLEAN_DIR' varibale.
# 'exist_ok=True' -> "If the directory already exists, do nothing and don't throw an error"
os.makedirs(CLEAN_DIR, exist_ok=True)


''' ===== HELPER FUNCTIONS | Creating Functions to call later in the Main script ====== '''

''' Attempt to convert string like "['A','B']" into a Python list '''

# # If conversion fails or value is NaN/empty, return None.
#'def' -> marks the begining of a function
## 'safe_literal_eval' -> function - reusable block of code that performs a specific task.
def safe_literal_eval(val):
    if pd.isna(val): # Checks if the value is a Pandas Not a Number (NaN) value (i.e., missing data).
        return None # If it's missing, the function immediately returns None to indicate no data.
    if isinstance(val, list): # Checks if the value is already a list.
        return val # If the data is already clean, it's returned immediately without processing.
    if isinstance(val,str):
        val = val.strip() # Removes any leading or trailing whitespace from the string.
        if val == "" or val.lower() in ["nan", "none", "[]", "na", "n/a"]:
            return None # Checks for empty or missing string data (e.g."nan", "none", or "[]").
        
        try: # securely parses a string that contains a valid Python literal structure (e.g. a list)
            parsed = ast.literal_eval(val) #safer than python's eval() function - literal_eval only evaluates data structures & prevents execution of arbitrary / potentially malicious code.
            if isinstance(parsed, (str, int, float)):
                return [str(parsed)] # If 'parsed' is a single non-list value - it is wrapped in a list and converted to a string.
            if isinstance(parsed, (tuple, set)):
                return list(parsed) # If 'parsed' is a tuple or set (similar to lists), then convert to a standard python list.
            return parsed # If 'parsed' is a list or a dictionary, return as is.
        
        except Exception:
            # sometimes the list is like "['A', 'B']" but with unicode quotes or as a plain string
            # fallback: try to split on commas
            try:
                cleaned = val.strip("[] ") # removes any surrounding square brackets and any extra spaces.
                if cleaned == "":
                    return None
                # breaks the string into individual parts based on the comma delimiter.
                ## uses a list comprehension to iterate through those parts, removes lingering quotes & spaces / ensuring empty parts are skipped.
                parts = [p.strip().strip("'\" ") for p in cleaned.split(",") if p.strip() != ""]
                return parts if parts else None
            except Exception:
                return None
    return None

''' Apply safe_literal_eval and then join lists to a canonical string for CSV storage. '''

def normalize_list_field(series): #'series' -> pandas series - a single column from a data frame.
    # 'series.apply' -> Takes the function 'safe_literal_eval' as an argument and executes it on every single value in the series (column).
    return series.apply(safe_literal_eval)

"""Parse a date-like column into datetime; return original col if parsing fails."""

def parse_dates(df, col): 
    
    if col not in df.columns: # checks if the specified column name actually exists in the data frame.
        return df # If the column is missing, the function immediately returns the original DataFrame without doing anything.
    
    # 'pd.to_datetime()' -> Pandas function for converting a Series (column) into the datetime data type.
    ## errors='coerce' -> If the function encounters a value that cannot be parsed into a valid date, replaces with NaT (Not a Time/Date)
    ### 'utc=False' -> function does not convert the times to Coordinated Universal Time (UTC).
    df[col] = pd.to_datetime(df[col], errors='coerce', utc=False) 
    # Add convenience columns if parsing succeeded
    df[f"{col}_year"] = df[col].dt.year # Creates a new column ('release_date'_year) containing only the year.
    df[f"{col}_month"] = df[col].dt.month # Creates a new column ('release_date'_month) containing only the month number.
    df[f"{col}_quarter"] = df[col].dt.to_period("Q").astype(str) # Creates a new column ('release_date'_quarter) containing the quarter.
    return df # Returns the modified data frame, which now has the date column corrected and new feature columns added.

'''Deduplicate by gameid if available, otherwise by title+platform'''

def deduplicate_games(df):
   
    if "gameid" in df.columns: #checks if a column called 'gameid' exists in the data frame.
        before = len(df) # stores the number of rows in the data frame before deduplication as 'before' to help track data quality changes
        # sorts data frame by release date in descending order tehn drops duplicates - keeps the most recent instance of the gameid.
        df = df.sort_values(by=["release_date"], ascending=False) \
               .drop_duplicates(subset=["gameid"], keep="first")
        after = len(df) # stores the number of rows in the data frame after duplicatoin as 'after'.
        print(f"Deduplicated by gameid: {before} -> {after}")
    else:
        before = len(df)
        df = df.sort_values(by=["release_date"], ascending=False) \
               .drop_duplicates(subset=["title", "platform"], keep="first")
        after = len(df)
        print(f"Deduplicated by title+platform: {before} -> {after}")
    return df


''' ===== MAIN PROCESS ====== '''


MASTER_DFS = [] # list which temporarily holdes the cleaned data frame created for each gaming platform before they are combined
# 'key' -> variable name assigned to the Key Name in the dictionary (the original string; e.g. 'playstation')
## 'pretty' -> the variable name assigned to the Value Name in the dictionary (the string new string; e.g. 'PlayStation')

for key, pretty in PLATFORMS.items(): 
    raw_path = os.path.join(RAW_BASE, key, TABLE_NAME) #  creates a path to the raw data file, then the platform, then the file name (which was all set above)
    print(f"\nProcessing platform: {pretty} — file: {raw_path}")
    if not os.path.exists(raw_path): # checks if the file exists.
        print(f"  WARNING: file not found: {raw_path} — skipping platform.") # If the file is missing, prints a warning.
        continue # Immediatley skips to the next platform in the loop and skips processing any more of the steps below.

     # Load
    df = pd.read_csv(raw_path) # data is in the 'raw-path' location is loaded from the .csv into a pandas data frame (df).
    print(f"  Loaded {len(df)} rows, columns: {list(df.columns)}") # Prints the number of rows loaded and the list of column names.

     # Standardize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns] # removes any leading or trailing whitespace from all column names - ensures consistency.

     # Add platform identifier
    df["platform_raw"] = key # stores the short / raw name.
    df["platform"] = pretty # stores the 'pretty' / new / user facing name.

     # Parse release_date
    df = parse_dates(df, "release_date") # calls the parse_dates helper function created to attempt to convert the specified column to datetime format.

     # Convert list-like string fields into python lists
    for col in ["developers", "publishers", "genres", "supported_languages"]:
        if col in df.columns:
            df[col] = normalize_list_field(df[col]) # calls the normalize_list_field helper function to convert data to python lists
        else:
            df[col] = None # if one of the specified columns is missing - adds a column and fills it with 'None' to keep structure consistent accross all platforms.

      # Normalize text fields: title -> strip whitespace
    if "title" in df.columns:
        df["title"] = df["title"].astype(str).str.strip() # ensures the 'title' column is treated as a string and removes extra spaces.
        # '.astype(str)' -> converts every single value in the column into a string.
        ## '.str' -> speccial pandas accessor that tells the program to apply standard python string method to every entry in the column.
        ### .strip() -> text operation that removes any leading or trailing whitespaces from the text.
        #### df["title"] = -> assigns the cleaned result back into the original "title" column of the data frame overwriting the messy data.

        # Fill missing textual fields with 'Unknown' where appropriate
    for col in ["developers", "publishers", "genres", "supported_languages"]: # initiates a loop - the value of 'col' = each item in turn.
        # keep None for lists; we will represent None as empty lists for consistency
        df[col] = df[col].apply(lambda x: x if x is not None else []) 
        # lambda -> takes a single input, performs a simple calcuation, then returns a result.
        ##  lambda x -> defintes the input variable 'x'. When appl() runs, x will be the value of a single cell (e.g.the cell with list of developer names for a single title)
        ### x if x is not None -> if the cell value (x) is not None (e.g. already contains a list, even an empty one), return the value (x) as it is.
        #### else [] -> if the cell value (x) is None (meaning it was a missing value), return an empty list ([]).
    
     # Ensure gameid exists and is integer (coerce)
    if "gameid" in df.columns: # does the current data frame have a column with the exact name 'game_id'?
        df["gameid"] = pd.to_numeric(df["gameid"], errors="coerce").astype("Int64")
        # df["gameid"] = -> replaces the entire columns data with the results of the script
        ## pd.to_numeric() -> pandas function designed to convert data into a numeric type (like an int or float).
        ### errors="coerce" -> if value that can't be converted to number - coerce that number into a missing value (NaN/NaT).
        #### .astype("Int64") - > after the data has been converted to numners, changes the column type to Int64 (pandas).

     # Deduplicate
    df = deduplicate_games(df)   # calls the deduplicate helper function above to remove duplicate game entries.

     # Save cleaned per-platform CSV (lists stored as JSON-like strings to keep readability)
    out_path = os.path.join(CLEAN_DIR, f"games_{key}_clean.csv")
    # out_path = -> Variable name
    ## os.path.join(...) -> (operating system) od module's 'join' function - combine folder names to create a pathway.
    ### (CLEAN_DIR, f"games_{key}_clean.csv") -> CLEAN_DIR = pathway set at config to the clean data folder, key = current platform in the loop's short name.
     
     # Convert lists to JSON-like strings for storage so Excel/SQLite imports can parse if needed
    df_to_save = df.copy() # new data frame (df_to_save) is created as a copy of the main, cleaned data frame (df).
    for col in ["developers", "publishers", "genres", "supported_languages"]: # loops through the columns that contain lists.
        df_to_save[col] = df_to_save[col].apply(lambda lst: f"{lst}" if lst is not None else "[]")
        # lambda function - process every list (1st) in the column. IF value is a list (or anything else), and IS NOT 'None', convert that list into a string using an f-string (f"{lst}").
        ## else [] - if it IS 'None', ensures that the value is the string '[]'.
    df_to_save.to_csv(out_path, index=False) # saves the data frame to the file path created earlier - index=False, ensures internal row numbers (data frame index numbers) are not saved as an extra column.
    print(f"  Saved cleaned file to: {out_path} ({len(df_to_save)} rows)") # Reports total no. of rows saved in the new deduplicated file.

    # Select canonical columns for master table
    canonical_cols = ["gameid", "platform", "platform_raw", "title", # creates a list (canonical_cols) with standardised list of column names.
                      "developers", "publishers", "genres", "supported_languages",
                      "release_date", "release_date_year", "release_date_month", "release_date_quarter"]
    # Some platforms may not have gameid — keep what's available
    existing = [c for c in canonical_cols if c in df.columns] # creates a new list (existing) containing only the columns that are currently present in the data frame.
    master = df[existing].copy() # creates a new data frame copy which only uses the columns listed in 'existing'.
    MASTER_DFS.append(master) # adds the newly created 'master' data frame to the MASTER_DFS list - stores all the individual platform tables before they are combined.

# Concatenate master table
if MASTER_DFS: # if the MASTER_DFS list contains any data frames then...
    games_master = pd.concat(MASTER_DFS, ignore_index=True, sort=False) 
    # games_master = pd.concat -> concatenate's all of the data frames into one data frame called 'games_master'.
    ## ignore_index=True -> This tells pandas to create a brand new, continuous set of row numbers (the index) for the new combined table.
    ### sort=False -> tells pandas not to sort the data alphabetically to speed up the processing time.
    
    # Ensure consistent columns exist
    for col in ["gameid", "platform", "title"]: # iterates through the absolute essential identifiers:(gameid), (platform), (title).
        if col not in games_master.columns: # Checks that the critical column exists in the combined master table.
            games_master[col] = pd.NA # If the column is missing, creates that column in the master table and fills every row with pd.NA (pandas for 'not available').

    # Optionally reorder columns
    col_order = ["gameid", "platform", "platform_raw", "title", # list that represents the ideal final order of columns.
                 "developers", "publishers", "genres", "supported_languages",
                 "release_date", "release_date_year", "release_date_month", "release_date_quarter"]
    existing_order = [c for c in col_order if c in games_master.columns] # creates an ordered list which contains only the columns that actually exist in the data frame.
    games_master = games_master[existing_order] # uses the 'existing order' list to select the columns to passed to the data frame in the order specified.

    master_out = os.path.join(CLEAN_DIR, "games_master.csv") # creates the full file path for the final master file.
    # store list columns as strings for CSV
    for col in ["developers", "publishers", "genres", "supported_languages"]: # iterates through the list-containing columns.
        if col in games_master.columns: # ensures the columnn exists in the master table before attempting to modify it.
            games_master[col] = games_master[col].apply(lambda lst: f"{lst}" if lst is not None else "[]")
            #lambda function applised to every value in the column: 
            # # converts the Python list object back into its string representation (necessary because CSV can only store plain text).
    games_master.to_csv(master_out, index=False) # final, cleaned, and reordered DataFrame to the CSV file - prevents internal row numbering.
    print(f"\nMaster games table saved to: {master_out} — rows: {len(games_master)}") # provides feedback to the user confirming the path and final row count.

else:
    print("No platform data processed — master table not created.")
    # Informs the user that the script finished, but no master file could be created because no data was available to process.
