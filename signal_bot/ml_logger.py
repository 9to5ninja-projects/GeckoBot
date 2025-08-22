# ml_logger.py
import pandas as pd
import os
from datetime import datetime
from .logger import setup_logger, log_info, log_error # Import logger


def log_ml_features(indicator_csv, output_csv):
    """Append new features to ML training dataset."""
    setup_logger() # Ensure logger is setup
    log_info(f"Attempting to log ML features from {indicator_csv} to {output_csv}...")

    try:
        if not os.path.exists(indicator_csv):
            log_info(f"Warning: Input file for ML logging not found at {indicator_csv}. Skipping logging.")
            return pd.DataFrame() # Return empty DataFrame on error

        df = pd.read_csv(indicator_csv)
        log_info(f"Successfully read {indicator_csv} for ML logging. Columns: {df.columns.tolist()}")

        required_features = [
            "id", "timestamp", "current_price",
            "rsi", "ema_20", "macd_diff",
            "bb_upper", "bb_lower", "signal" # Added signal as a required feature
        ]

        # Check if all required features are in the DataFrame
        missing_features = [col for col in required_features if col not in df.columns]
        if missing_features:
            log_info(f"Warning: Missing required features for ML logging in {indicator_csv}: {missing_features}. Skipping logging for this file.")
            return pd.DataFrame() # Return empty DataFrame if features are missing

        features = df[required_features].copy()

        # Add a placeholder 'success' column for ML training.
        # In a real scenario, this would be populated by backtesting or manual labeling.
        if "signal" in features.columns and "BUY" in features["signal"].str.upper().str:
             # For simplicity, label any row with a BUY signal as needing potential backtest/labeling
             # A more sophisticated approach would look at future price movement
             features["success"] = pd.NA # Mark as needing labeling
        else:
             features["success"] = 0 # Assume not a successful trade if no BUY signal

        if os.path.exists(output_csv):
            existing = pd.read_csv(output_csv)
            # Ensure timestamp is datetime for proper merging/deduplication
            existing["timestamp"] = pd.to_datetime(existing["timestamp"])
            features["timestamp"] = pd.to_datetime(features["timestamp"])

            # Combine existing and new data, drop duplicates based on id and timestamp
            combined = pd.concat([existing, features]).drop_duplicates(subset=["id", "timestamp"]).reset_index(drop=True)
        else:
            combined = features

        combined.to_csv(output_csv, index=False)
        log_info(f"ML features logged successfully to {output_csv}. Total entries: {len(combined)}")
        return combined

    except Exception as e:
        log_error(f"Error during ML feature logging for {indicator_csv}: {e}. Skipping logging.")
        return pd.DataFrame() # Return empty DataFrame on error

