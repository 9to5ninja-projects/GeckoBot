data_collector_content = """# signal_bot/data_collector.py
import pandas as pd
import os
from .utils.coingecko_api import get_top_coins
from .dataset_manager import clean_and_normalize # Import clean_and_normalize
from .logger import setup_logger, log_info, log_error # Import logger

DATA_DIR = 'signal_bot/data'
os.makedirs(DATA_DIR, exist_ok=True)

def collect_data(limit=250):
    """
    Fetches a snapshot of market data for a specified number of top coins
    and saves it to full_market_snapshot.csv.

    Args:
        limit (int): The number of top coins to fetch data for. Note CoinGecko
                     /coins/markets has a per_page limit (typically 250).
                     Fetching more than the limit might require pagination.
                     Current implementation fetches up to 'limit' on page 1.

    Returns:
        pd.DataFrame or None: DataFrame with market data if successful, None otherwise.
    """
    # setup_logger() # Setup logger for this function if not setup globally

    log_info(f"Fetching market data for top {limit} coins for full snapshot...")
    try:
        data = get_top_coins(limit=limit)
        if data is not None:
            df = pd.DataFrame(data)

            # Add current timestamp to each row
            df["timestamp"] = pd.Timestamp.utcnow()

            # Clean and normalize the collected data
            df = clean_and_normalize(df)
            log_info("Data collected and cleaned.")

            # Ensure output directory exists (already done by DATA_DIR os.makedirs)
            full_snapshot_path = os.path.join(DATA_DIR, "full_market_snapshot.csv")

            # Append data to existing file or create new
            if os.path.exists(full_snapshot_path):
                 df.to_csv(full_snapshot_path, mode='a', header=False, index=False)
                 log_info(f"Market snapshot appended to {full_snapshot_path}.")
            else:
                 df.to_csv(full_snapshot_path, index=False)
                 log_info(f"New market snapshot created at {full_snapshot_path}.")

            return df
        else:
            log_error("Failed to fetch market data for full snapshot.")
            return None
    except Exception as e:
        log_error(f"Error during full market data collection: {e}")
        return None

# Example of how to run the data collector as a script
if __name__ == '__main__':
    # setup_logger() # Setup logger if running this script directly
    collect_data(limit=250) # Fetch data for top 250 coins for the snapshot
"""
with open('signal_bot/data_collector.py', 'w') as f:
    f.write(data_collector_content)
print("signal_bot/data_collector.py regenerated.")
