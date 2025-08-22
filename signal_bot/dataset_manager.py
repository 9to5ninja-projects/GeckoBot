dataset_manager_content = """# dataset_manager.py
import pandas as pd

def clean_and_normalize(df):
    """Clean and normalize DataFrame columns and data types."""
    if df.empty:
        print("Warning: Input DataFrame is empty for cleaning and normalization.")
        return df

    # Convert column names to lowercase and replace spaces with underscores
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]

    # Drop rows where essential columns are missing
    required_subset_cols = ["id", "current_price"]
    if not all(col in df.columns for col in required_subset_cols):
         print(f"Warning: Required columns for dropna subset missing: {required_subset_cols}. Skipping dropna subset.")
    else:
         df = df.dropna(subset=required_subset_cols)

    # Convert timestamp column to datetime, coerce errors to NaT
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
        # Optionally drop rows where timestamp conversion failed
        # df = df.dropna(subset=["timestamp"])
    else:
         print("Warning: 'timestamp' column not found for datetime conversion.")


    # Sort by id and timestamp
    if "id" in df.columns and "timestamp" in df.columns:
        df = df.sort_values(by=["id", "timestamp"])
    elif "id" in df.columns:
        df = df.sort_values(by="id")
    elif "timestamp" in df.columns:
        df = df.sort_values(by="timestamp")
    else:
        print("Warning: 'id' and 'timestamp' columns not found for sorting.")


    return df
"""
with open('signal_bot/dataset_manager.py', 'w') as f:
    f.write(dataset_manager_content)
print("signal_bot/dataset_manager.py regenerated.")
