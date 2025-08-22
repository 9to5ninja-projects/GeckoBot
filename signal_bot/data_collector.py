# signal_bot/data_collector.py
import pandas as pd
import os
from .utils.coingecko_api import get_top_coins # Import get_top_coins
from .logger import setup_logger, log_info, log_error # Import logger

DATA_DIR = 'signal_bot/data'
os.makedirs(DATA_DIR, exist_ok=True)

def collect_data(limit=250):
    """
    Fetches a snapshot of market data for a specified number of top coins.

    Args:
        limit (int): The number of top coins to fetch data for.

    Returns:
        pd.DataFrame or None: DataFrame with market data if successful, None otherwise.
    """
    setup_logger() # Ensure logger is setup within the function
    log_info(f"Fetching market data for top {limit} coins...")
    try:
        data = get_top_coins(limit=limit)
        if data is not None:
            df = pd.DataFrame(data)
            df["timestamp"] = pd.Timestamp.utcnow()
            full_snapshot_path = os.path.join(DATA_DIR, "full_market_snapshot.csv")
            df.to_csv(full_snapshot_path, index=False)
            log_info(f"Full market snapshot fetched and saved to {full_snapshot_path}.")
            return df
        else:
            log_error("Failed to fetch market data for full snapshot.")
            return None
    except Exception as e:
        log_error(f"Error during market data collection: {e}")
        return None

if __name__ == '__main__':
    # Example of how to run the data collector as a script
    collect_data(limit=250) # Fetch data for top 250 coins for the snapshot
