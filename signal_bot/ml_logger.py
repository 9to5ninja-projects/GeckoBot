ml_logger_content = """# ml_logger.py
import pandas as pd
import os
from datetime import datetime

def log_ml_features(indicator_csv, output_csv):
    """Append new features to ML training dataset."""
    try:
        df = pd.read_csv(indicator_csv)

        required_features = [
            "id", "timestamp", "current_price",
            "rsi", "ema_20", "macd", # Use 'macd' as computed in ta_utils
            "bb_upper", "bb_lower"
        ]

        # Check if all required features are in the DataFrame and are numeric
        missing_features = [col for col in required_features if col not in df.columns]
        if missing_features:
            print(f"Warning: Missing required features for ML logging in {indicator_csv}: {missing_features}. Skipping logging for this file.")
            return pd.DataFrame()

        # Ensure numeric columns are numeric, handle potential errors
        numeric_cols = ["current_price", "rsi", "ema_20", "macd", "bb_upper", "bb_lower"]
        for col in numeric_cols:
             if col in df.columns:
                  df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows where essential numeric features could not be converted
        df = df.dropna(subset=[col for col in numeric_cols if col in df.columns])

        if df.empty:
            print(f"Warning: No valid numeric data remaining for ML logging from {indicator_csv} after cleaning. Skipping logging.")
            return pd.DataFrame()


        features = df[required_features].copy()

        if os.path.exists(output_csv):
            existing = pd.read_csv(output_csv)
            # Ensure timestamp is datetime for correct dropping duplicates
            existing['timestamp'] = pd.to_datetime(existing['timestamp'])
            features['timestamp'] = pd.to_datetime(features['timestamp'])

            combined = pd.concat([existing, features]).drop_duplicates(subset=["id", "timestamp"]).sort_values(by=["id", "timestamp"])
        else:
            combined = features

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else '.', exist_ok=True)

        combined.to_csv(output_csv, index=False)
        return combined

    except FileNotFoundError:
        print(f"Error: Input file for ML logging not found at {indicator_csv}. Skipping logging.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error during ML feature logging for {indicator_csv}: {e}. Skipping logging.")
        return pd.DataFrame()

# Example Usage (can be removed or commented out)
# if __name__ == '__main__':
#     # Assuming data/top10_with_indicators.csv exists
#     DATA_DIR = 'signal_bot/data'
#     indicators_path = os.path.join(DATA_DIR, 'top10_with_indicators.csv')
#     ml_output_path = os.path.join(DATA_DIR, 'ml_training.csv')
#     if os.path.exists(indicators_path):
#         log_ml_features(indicators_path, ml_output_path)
#     else:
#          print(f"Input file not found for ML logging: {indicators_path}")

"""
with open('signal_bot/ml_logger.py', 'w') as f:
    f.write(ml_logger_content)
print("signal_bot/ml_logger.py regenerated.")
