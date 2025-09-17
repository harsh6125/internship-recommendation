# add_real_data.py

import pandas as pd
from database import internship_collection
import json

# --- IMPORTANT ---
# Make sure your 'internship_data.csv' file is in the same folder as this script.
CSV_FILE_PATH = 'internship_data.csv'

def clean_data(df):
    # Drop rows where essential information like Role or Company Name is missing
    df.dropna(subset=['Role', 'Company Name'], inplace=True)
    # Fill any other missing values with a placeholder
    df.fillna('Not specified', inplace=True)
    return df

def load_data_to_mongodb():
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        df = clean_data(df)
        
        # Clear the existing collection to avoid duplicates
        internship_collection.delete_many({})
        
        # Convert dataframe to a list of dictionaries (records)
        data_json = json.loads(df.to_json(orient='records'))
        
        # Insert data into the collection
        internship_collection.insert_many(data_json)
        
        print(f"✅ Successfully loaded {len(data_json)} internships from '{CSV_FILE_PATH}' into MongoDB.")
    
    except FileNotFoundError:
        print(f"❌ ERROR: The file '{CSV_FILE_PATH}' was not found.")
        print("   Please make sure the CSV file is in the same directory as this script.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    load_data_to_mongodb()