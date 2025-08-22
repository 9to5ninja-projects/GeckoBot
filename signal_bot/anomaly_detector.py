anomaly_detector_content = """# anomaly_detector.py
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime
import os

def load_market_snapshot(snapshot_csv):
    """Load full market snapshot from CSV."""
    try:
        df = pd.read_csv(snapshot_csv, parse_dates=["timestamp"])
        return df
    except FileNotFoundError:
        print(f"Error: Market snapshot file not found at {snapshot_csv}.")
        return pd.DataFrame() # Return empty DataFrame on error
    except Exception as e:
        print(f"Error loading market snapshot from {snapshot_csv}: {e}")
        return pd.DataFrame() # Return empty DataFrame on other errors


def prepare_features(df):
    """Create features for anomaly detection (e.g., price % change)."""
    if df.empty or "price_change_percentage_24h" not in df.columns:
         print("Warning: DataFrame is empty or missing 'price_change_percentage_24h' for anomaly detection.")
         return pd.DataFrame() # Return empty if essential data is missing

    # Ensure the column is numeric, coerce errors to NaN
    df["price_change_percentage_24h"] = pd.to_numeric(df["price_change_percentage_24h"], errors='coerce')
    df = df.dropna(subset=["price_change_percentage_24h"]) # Drop rows where conversion failed

    if df.empty:
         print("Warning: No valid data remaining after cleaning for anomaly detection.")
         return pd.DataFrame() # Return empty if no valid data

    df["pct_change_24h"] = df["price_change_percentage_24h"].fillna(0) # Fill any remaining NaNs after dropna (unlikely here but safe)
    return df[["id", "symbol", "name", "pct_change_24h", "timestamp"]].copy()

def run_isolation_forest(df, contamination=0.01):
    """Apply Isolation Forest to detect anomalies based on % change."""
    if df.empty or "pct_change_24h" not in df.columns:
         print("Warning: No features available for Isolation Forest.")
         return pd.DataFrame() # Return empty if no features

    # Ensure contamination is valid
    if not (0 < contamination < 0.5):
         print(f"Warning: Invalid contamination value {contamination}. Using default (0.1) or adjusting.")
         # Adjust contamination if necessary, or use a default. Let's ensure it's between 0 and 0.5
         contamination = max(0.001, min(0.499, contamination)) # Clamp value if outside reasonable range


    # Ensure there are enough samples for Isolation Forest
    if len(df) < 2: # Isolation Forest needs at least 2 samples
         print("Warning: Not enough data points for Isolation Forest (need at least 2).")
         df["anomaly_score"] = 1 # Tag all as not anomaly or handle as appropriate
         return df


    model = IsolationForest(contamination=contamination, random_state=42)
    try:
        # Reshape the feature data for the model
        X = df[["pct_change_24h"]].values
        df["anomaly_score"] = model.fit_predict(X)
        return df
    except Exception as e:
         print(f"Error running Isolation Forest: {e}")
         df["anomaly_score"] = 1 # Tag all as not anomaly on error
         return df


def save_anomalies(df, output_dir="data"):
    """Save anomalies to timestamped CSV."""
    if df.empty or "anomaly_score" not in df.columns:
         print("Warning: No anomalies to save.")
         return None, pd.DataFrame()

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    anomalies = df[df["anomaly_score"] == -1].copy() # Use .copy() to avoid SettingWithCopyWarning
    if anomalies.empty:
         print("No anomalies found to save.")
         return None, pd.DataFrame()


    path = os.path.join(output_dir, f"anomalies_{timestamp}.csv")
    os.makedirs(output_dir, exist_ok=True)
    try:
        anomalies.to_csv(path, index=False)
        print(f"Anomalies saved to {path}")
        return path, anomalies
    except Exception as e:
        print(f"Error saving anomalies to {path}: {e}")
        return None, pd.DataFrame()


def detect_anomalies(snapshot_csv, output_dir="data"):
    """End-to-end anomaly detection workflow."""
    print(f"Starting anomaly detection from {snapshot_csv}")
    df = load_market_snapshot(snapshot_csv)
    if df.empty:
         print("Anomaly detection skipped due to no data.")
         return None, pd.DataFrame()

    features = prepare_features(df)
    if features.empty:
         print("Anomaly detection skipped due to no valid features.")
         return None, pd.DataFrame()

    with_scores = run_isolation_forest(features)
    if with_scores.empty: # Check if Isolation Forest returned empty
         print("Anomaly detection skipped after Isolation Forest due to no results.")
         return None, pd.DataFrame()

    path, anomalies = save_anomalies(with_scores, output_dir)

    # Return the path and the anomalies DataFrame
    return path, anomalies

# Example Usage (can be removed or commented out)
# if __name__ == '__main__':
#     # Assuming signal_bot/data/full_market_snapshot.csv exists
#     DATA_DIR = 'signal_bot/data'
#     snapshot_path = os.path.join(DATA_DIR, 'full_market_snapshot.csv')
#     if os.path.exists(snapshot_path):
#         anomaly_file_path, detected_anomalies = detect_anomalies(snapshot_path, DATA_DIR)
#         if anomaly_file_path:
#             print(f"Detected {len(detected_anomalies)} anomalies.")
#             # print(detected_anomalies.head().to_markdown(index=False))
#     else:
#          print(f"Input file not found for anomaly detection: {snapshot_path}")

"""
with open('signal_bot/anomaly_detector.py', 'w') as f:
    f.write(anomaly_detector_content)
print("signal_bot/anomaly_detector.py regenerated.")
