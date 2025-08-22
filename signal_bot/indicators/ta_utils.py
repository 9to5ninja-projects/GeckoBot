# indicators/ta_utils.py
import pandas as pd
import ta
from ..logger import setup_logger, log_info, log_error # Import logger from parent directory


def compute_indicators(df_or_path, output_csv=None):
    """
    Computes technical indicators (RSI, EMA, MACD, Bollinger Bands) for price data.

    Args:
        df_or_path (pd.DataFrame or str): Input data as a DataFrame or path to a CSV file.
        output_csv (str, optional): Path to save the DataFrame with indicators to CSV. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame with technical indicators added. Returns empty DataFrame on error.
    """
    setup_logger() # Ensure logger is setup

    try:
        if isinstance(df_or_path, pd.DataFrame):
            df = df_or_path.copy()
            log_info("Computing indicators on provided DataFrame.")
        elif isinstance(df_or_path, str) and os.path.exists(df_or_path):
            df = pd.read_csv(df_or_path, parse_dates=["timestamp"])
            log_info(f"Computing indicators on data loaded from {df_or_path}.")
        else:
            log_error(f"Invalid input: Expected a DataFrame or valid file path, got {type(df_or_path)}.")
            return pd.DataFrame()

        # Ensure close price exists and data is sorted by timestamp
        if "close" not in df.columns and "current_price" in df.columns:
             df["close"] = df["current_price"]
        elif "close" not in df.columns:
             log_error("Input DataFrame must contain a 'close' or 'current_price' column.")
             return pd.DataFrame()

        # Ensure timestamp is datetime and sort
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

        # Compute Indicators - Handle potential errors or insufficient data for windows
        if len(df) > 14: # Minimum required for RSI default window
            try:
                df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
            except Exception as e:
                 log_error(f"Error computing RSI: {e}")
                 df["rsi"] = pd.NA # Assign pandas NA on error or insufficient data

            if len(df) > 20: # Minimum required for EMA and BB default window
                 try:
                     df["ema_20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
                     bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
                     df["bb_upper"] = bb.bollinger_hband()
                     df["bb_lower"] = bb.bollinger_lband()
                 except Exception as e:
                      log_error(f"Error computing EMA or Bollinger Bands: {e}")
                      df["ema_20"] = pd.NA
                      df["bb_upper"] = pd.NA
                      df["bb_lower"] = pd.NA

                 try:
                    # MACD requires more data than the default window for meaningful values
                    # ta.trend.MACD default windows are (12, 26, 9). MACD_diff needs at least 26 data points.
                    if len(df) > 26:
                         df["macd_diff"] = ta.trend.MACD(df["close"]).macd_diff()
                    else:
                         log_info(f"Not enough data points ({len(df)}) for MACD calculation (requires > 26).")
                         df["macd_diff"] = pd.NA
                 except Exception as e:
                      log_error(f"Error computing MACD: {e}")
                      df["macd_diff"] = pd.NA


            else:
                 log_info(f"Not enough data points ({len(df)}) for EMA, MACD, or Bollinger Bands calculation (requires > 20).")
                 df["ema_20"] = pd.NA
                 df["bb_upper"] = pd.NA
                 df["bb_lower"] = pd.NA
                 df["macd_diff"] = pd.NA # Ensure MACD is also NA

        else:
            log_info(f"Not enough data points ({len(df)}) for any indicator calculation (requires > 14 for RSI).")
            # Assign NA to all indicator columns if not enough data for any
            df["rsi"] = pd.NA
            df["ema_20"] = pd.NA
            df["bb_upper"] = pd.NA
            df["bb_lower"] = pd.NA
            df["macd_diff"] = pd.NA

        df["processed_timestamp"] = pd.Timestamp.utcnow().isoformat()


        if output_csv:
            try:
                os.makedirs(os.path.dirname(output_csv), exist_ok=True)
                df.to_csv(output_csv, index=False)
                log_info(f"Indicators computed and saved to {output_csv}.")
            except Exception as e:
                log_error(f"Error saving indicators to {output_csv}: {e}")


        return df

    except Exception as e:
        log_error(f"An unexpected error occurred during indicator computation: {e}")
        return pd.DataFrame() # Return empty DataFrame on unexpected errors

