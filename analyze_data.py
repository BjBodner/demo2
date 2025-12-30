import numpy as np
import pandas as pd


def load_data(file_path):    
    """Load data from a CSV file into a pandas DataFrame."""
    return pd.read_csv(file_path)

def clean_data_issues_from_db(df_raw):
    """Clean data by handling missing values and duplicates."""
    # Drop duplicate rows
    df = df_raw.drop_duplicates().copy()
    
    # Handle numeric columns: ensure positive values and fill missing values
    for column in df.select_dtypes(include=[np.number]).columns:
        # Convert negative values to positive
        df[column] = df[column].abs()
        # Fill missing values with the mean of the column
        df[column] = df[column].fillna(df[column].mean())
    
    # Fill missing values in categorical columns with the mode
    for column in df.select_dtypes(include=[object]).columns:
        mode_vals = df[column].mode()
        if not mode_vals.empty:
            df[column] = df[column].fillna(mode_vals[0])
    
    return df