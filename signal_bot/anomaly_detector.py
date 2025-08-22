# anomaly_detector.py
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime
import os
from .logger import setup_logger, log_info, log_error


def load_market_snapshot(snapshot_csv):
    """Load full market snapshot from CSV."""
    setup_logger()
    log_info(f"Loading market snapshot from {snapshot_csv} for anomaly detection.")
    try:
        df = pd.read_csv(snapshot_csv, parse_dates=["timestamp"])
        log_info("Market snapshot loaded successfully.")
        return df
    except FileNotFoundError:
        log_error(f"Error: Snapshot file not found at {snapshot_csv}.")
        return pd.DataFrame()
    except Exception as e:
        log_error(f"Error loading market snapshot from {snapshot_csv}: {e}")
        return pd.DataFrame()


def prepare_features(df):
    """Create features for anomaly detection (e.g., price % change)."""
    setup_logger()
    log_info("Preparing features for anomaly detection.")
    if df.empty:
        log_info("Input DataFrame is empty, cannot prepare features.")
        return pd.DataFrame()
    # Ensure required columns exist before accessing them
    required_cols = ["price_change_percentage_24h", "id", "symbol", "name", "timestamp"]
    if not all(col in df.columns for col in required_cols):
         missing = [col for col in required_cols if col not in df.columns]
         log_error(f"Missing required columns for feature preparation: {missing}. Cannot prepare features.")
         return pd.DataFrame()

    df["pct_change_24h"] = df["price_change_percentage_24h"].fillna(0)
    log_info("Features prepared.")
    return df[["id", "symbol", "name", "pct_change_24h", "timestamp"]].copy()


def run_isolation_forest(df, contamination=0.01):
    """Apply Isolation Forest to detect anomalies based on % change."""
    setup_logger()
    log_info("Running Isolation Forest for anomaly detection.")
    if df.empty or "pct_change_24h" not in df.columns:
        log_info("Input DataFrame is empty or missing 'pct_change_24h', skipping Isolation Forest.")
        return pd.DataFrame()

    try:
        # Ensure there's enough data points for IsolationForest (at least 2)
        if len(df) < 2:
             log_info(f"Not enough data points ({len(df)}) for Isolation Forest (requires at least 2). Skipping.")
             df["anomaly_score"] = 1 # Mark as not an anomaly if insufficient data
             return df

        # Fit and predict anomalies
        model = IsolationForest(contamination=contamination, random_state=42)
        df["anomaly_score"] = model.fit_predict(df[["pct_change_24h"]])
        log_info("Isolation Forest completed.")
        return df
    except Exception as e:
        log_error(f"Error running Isolation Forest: {e}")
        df["anomaly_score"] = 1 # Default to not an anomaly on error
        return df


def save_anomalies(df, output_dir="data"):
    """Save anomalies to timestamped CSV."""
    setup_logger()
    if df.empty or "anomaly_score" not in df.columns:
        log_info("Input DataFrame is empty or missing 'anomaly_score', skipping saving anomalies.")
        return None, pd.DataFrame()

    anomalies = df[df["anomaly_score"] == -1]
    if anomalies.empty:
        log_info("No anomalies detected to save.")
        return None, pd.DataFrame()

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(output_dir, f"anomalies_{timestamp}.csv")
    try:
        os.makedirs(output_dir, exist_ok=True)
        anomalies.to_csv(path, index=False)
        log_info(f"Anomalies saved to {path}. Found {len(anomalies)} anomalies.")
        return path, anomalies
    except Exception as e:
        log_error(f"Error saving anomalies to {path}: {e}")
        return None, pd.DataFrame()


def detect_anomalies(snapshot_csv, output_dir="data"):
    """End-to-end anomaly detection workflow."""
    setup_logger()
    log_info("Starting anomaly detection workflow.")
    df = load_market_snapshot(snapshot_csv)
    if df.empty:
        log_info("Anomaly detection workflow skipped due to empty data.")
        return None, pd.DataFrame()

    features = prepare_features(df)
    if features.empty:
        log_info("Anomaly detection workflow skipped due to empty features.")
        return None, pd.DataFrame()

    with_scores = run_isolation_forest(features)
    if with_scores.empty:
         log_info("Anomaly detection workflow skipped after Isolation Forest.")
         return None, pd.DataFrame()

    path, anomalies = save_anomalies(with_scores, output_dir)
    log_info("Anomaly detection workflow finished.")
    return path, anomalies
