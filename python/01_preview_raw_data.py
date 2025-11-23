"""
Script Name: 01_preview_raw_data.py
Purpose:
    Inspect raw CSV files for PlayStation, Steam, and Xbox datasets.
    Preview structure, column types, row counts, and initial data quality issues.
    Establishes the foundation for subsequent data cleaning modules.

Dataset:
    data_raw/ (folder containing raw platform CSVs)

Author: Shian Raveneau-Wright

Notes:
    - Outputs summary prints for each table.
    - Does not modify or save any data.
    - Intended as an initial exploration step to understand dataset shape.
"""


import pandas as pd

# Creates file paths (relative to the project folder)
platforms = ["playstation", "steam", "xbox"]
tables = ["games", "players", "prices", "purchased_games"]
base_path = "./data_raw/"

#Loops through each string in the 'platforms' list and assigns it to the temp. variable 'platform'
#Actions the code below it then reassigns the value of 'platform' to the next string in the list until there are none left 
for platform in platforms:
    print(f"\n===== PLATFORM: {platform.upper()} =====") #'f-string' - used for formatting | '\n' - new line
    # generates a file path - 'f' instructs python to use the actual values stored in the {} in the string
    #takes the string in variable 'platform' and converts all charactesr to upper case

    for table in tables:
        file_path = f"{base_path}{platform}/{table}.csv"
        # the value of the variable 'file_path is printed out because it is in {}
        print(f"\n--- Loading: {file_path} ---")

        try:
            # Using pandas (pd) this reads the .csv file and stores the information in a data frame (df)
            df = pd.read_csv(file_path)
            print(df.head())  # Shows first rows
            print(df.info())  # Shows data types
        except Exception as error_message:
            print(f"Error loading {file_path}: {error_message}")
            # if the try fails then this will display the file path and assign the error to the variable 'error_message'

print("\n===== INSPECTION COMPLETE =====")
