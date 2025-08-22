backtester_content = """# backtester.py
import pandas as pd
import os
import numpy as np # Import numpy for isna

def backtest_signals(signal_csv, price_csv, threshold=0.05, window=6):
    """
    Backtests trading signals against historical price data.

    Args:
        signal_csv (str): Path to the CSV file containing signals.
        price_csv (str): Path to the CSV file containing historical price data.
        threshold (float): The percentage price increase considered a successful BUY signal.
        window (int): The number of future price points (rows) to consider after a signal.

    Returns:
        pd.DataFrame: DataFrame containing backtest results.
    """
    print("\\n--- Inside backtest_signals ---")
    try:
        signals = pd.read_csv(signal_csv, parse_dates=["timestamp"])
        prices = pd.read_csv(price_csv, parse_dates=["timestamp"])
        print(f"Successfully loaded {signal_csv} and {price_csv} for backtesting.")

    except FileNotFoundError as e:
        print(f"Error loading data for backtesting: {e}")
        print("--- Exiting backtest_signals ---\\n")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading CSV files for backtesting: {e}")
        print("--- Exiting backtest_signals ---\\n")
        return pd.DataFrame()


    results = []
    # Ensure data is sorted for correct future price lookup
    signals = signals.sort_values("timestamp")
    prices = prices.sort_values("timestamp")

    # Filter for BUY signals using a more explicit method
    if 'signal' not in signals.columns:
         print("Warning: 'signal' column not found in signals CSV. Cannot backtest.")
         print("--- Exiting backtest_signals ---\\n")
         return pd.DataFrame()

    # Ensure the 'signal' column is treated as string
    signals['signal'] = signals['signal'].astype(str).fillna('') # Fill NaN with empty string for contains check

    # Use a boolean mask with apply and lambda for filtering
    buy_signals = signals[signals['signal'].apply(lambda x: 'BUY' in x)].copy()

    print(f"Found {len(buy_signals)} BUY signals for backtesting after filtering.")


    if buy_signals.empty:
        print("No BUY signals found for backtesting.")
        print("--- Exiting backtest_signals ---\\n")
        return pd.DataFrame()

    # Ensure prices DataFrame has necessary columns
    if "id" not in prices.columns or "timestamp" not in prices.columns or "current_price" not in prices.columns:
         print("Error: Required columns ('id', 'timestamp', 'current_price') missing in prices DataFrame for lookup.")
         print("--- Exiting backtest_signals ---\\n")
         return pd.DataFrame()


    # Iterate through BUY signals and find future prices
    for index, signal in buy_signals.iterrows():
        # print(f"Backtesting signal: {signal['signal']} at {signal['timestamp']}") # Debug print (can be verbose)
        coin_id = signal["id"]
        signal_time = signal["timestamp"]

        # Get the price at the signal time from the prices DataFrame
        price_at_signal_row = prices[
            (prices["id"] == coin_id) &
            (prices["timestamp"] == signal_time)
        ]
        if price_at_signal_row.empty:
             # This can happen if signals timestamp doesn't exactly match a price timestamp
             # Find the closest price point at or before the signal time as an alternative
             closest_price_row = prices[
                 (prices["id"] == coin_id) &
                 (prices["timestamp"] <= signal_time)
             ].sort_values("timestamp", ascending=False).head(1)

             if closest_price_row.empty:
                  # print(f"Warning: Price at or before signal time not found for {coin_id} at {signal_time}. Skipping.") # Debug print
                  continue # Skip this signal if no price found
             price_at_signal = closest_price_row.iloc[0]["current_price"]
             # print(f"Using closest price {price_at_signal} at {closest_price_row.iloc[0]['timestamp']} for signal at {signal_time}") # Debug print

        else:
             price_at_signal = price_at_signal_row.iloc[0]["current_price"]
             # print(f"Using exact price {price_at_signal} at {signal_time}") # Debug print


        # Filter for future prices of this coin within the window (next 'window' data points)
        # Find the index of the current signal in the sorted prices DataFrame for this coin
        price_indices_for_coin = prices[prices["id"] == coin_id].sort_values("timestamp").index
        signal_price_index_loc = price_indices_for_coin[price_indices_for_coin >= price_at_signal_row.index[0] if not price_at_signal_row.empty else price_indices_for_coin[price_indices_for_coin <= closest_price_row.index[0]].max()] # Find index of exact or closest price

        if pd.isna(signal_price_index_loc): # Handle case where closest price lookup failed
             # print(f"Warning: Could not find price index for signal at {signal_time}. Skipping.") # Debug print
             continue


        # Select the next 'window' rows starting from the row after the signal price index
        try:
            start_idx_in_full_prices = prices.index.get_loc(signal_price_index_loc) # Get the integer location in the full prices df
            future_prices = prices.iloc[start_idx_in_full_prices + 1 : start_idx_in_full_prices + 1 + window] # Get the next 'window' rows
            # print(f"Selected {len(future_prices)} future prices for window.") # Debug print
        except IndexError:
             # print(f"Warning: Not enough future data points within window for {coin_id} at index {signal_price_index_loc}. Skipping backtest for this signal.") # Debug print
             continue # Not enough future data


        if not future_prices.empty:
            # Find the maximum price within the future window
            if "current_price" not in future_prices.columns:
                 print("Error: 'current_price' column not found in future prices DataFrame subset.")
                 continue
            max_price = future_prices["current_price"].max()
            return_pct = (max_price - price_at_signal) / price_at_signal

            result = {
                "id": coin_id,
                "timestamp": signal_time,
                "signal": signal["signal"],
                "price_at_signal": price_at_signal,
                "max_future_price": max_price,
                "return_pct": return_pct,
                "success": return_pct >= threshold
            }
            results.append(result)
        # else: # No future prices found within the window (handled by continue in try block)
             # print(f"Warning: No future price data found within window for {coin_id} at {signal_time}. Skipping backtest for this signal.") # Debug print


    if not results:
         print("No backtest results generated (either no BUY signals processed or no successful trades based on criteria).")
         print("--- Exiting backtest_signals ---\\n")
         return pd.DataFrame()

    result_df = pd.DataFrame(results)
    output_path = "data/signal_backtest.csv"
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    try:
        result_df.to_csv(output_path, index=False)
        print(f"Backtest results saved to {output_path}")
    except Exception as e:
        print(f"Error saving backtest results to {output_path}: {e}")

    print("--- Exiting backtest_signals ---\\n")
    return result_df
"""
with open('signal_bot/backtester.py', 'w') as f:
    f.write(backtester_content)
print("signal_bot/backtester.py regenerated.")
