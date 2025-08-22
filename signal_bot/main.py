# main.py
import pandas as pd
import os
from .utils.coingecko_api import get_top_coins, get_coin_history
from .indicators.ta_utils import compute_indicators
# from .signals.generate_signals import generate_signal
from .signals.signal_finder import find_signals
from .anomaly_detector import detect_anomalies
from .ml_logger import log_ml_features
from .backtester import backtest_signals
from .ml_model_trainer import train_ml_model
from .logger import setup_logger, log_info, log_error
from .exporter import export_to_excel, export_to_html

DATA_DIR = 'signal_bot/data'
os.makedirs(DATA_DIR, exist_ok=True)

def main():
    setup_logger()
    log_info("Starting bot pipeline...")

    # --- Data Collection (using existing top 10 fetch for now) ---
    log_info("--- Top 10 Data Pipeline ---")
    print("Fetching top 10 coin data...")
    try:
        data = get_top_coins()
        if data is not None:
            df_top10 = pd.DataFrame(data)
            df_top10["timestamp"] = pd.Timestamp.utcnow()
            top10_market_data_path = os.path.join(DATA_DIR, "top10_market_data.csv")
            df_top10.to_csv(top10_market_data_path, index=False)
            log_info("Top 10 data fetched and saved.")

            log_info("Computing technical indicators for top 10 data...")
            df_top10["close"] = df_top10["current_price"]
            df_ind_top10 = compute_indicators(df_top10.copy())
            top10_indicators_path = os.path.join(DATA_DIR, "top10_with_indicators.csv")
            df_ind_top10.to_csv(top10_indicators_path, index=False)
            log_info("Indicators computed and saved for top 10 data.")

            log_info("Generating signals for top 10 snapshot data...")
            df_signals_top10 = find_signals(df_ind_top10.copy())
            top10_signals_path = os.path.join(DATA_DIR, "top10_signals.csv")
            df_signals_top10.to_csv(top10_signals_path, index=False)
            log_info("Signals generated and saved for top 10 snapshot data.")

            log_info("Logging ML features for top 10 data...")
            ml_log_path = os.path.join(DATA_DIR, "ml_training.csv")
            log_ml_features(top10_indicators_path, ml_log_path)
            log_info("ML features logged for top 10 data.")

        else:
            log_error("Failed to fetch top 10 coin data. Skipping subsequent steps for top 10.")
            df_signals_top10 = pd.DataFrame()

    except Exception as e:
        log_error(f"Error processing top 10 data pipeline: {e}. Skipping subsequent steps for top 10.")
        df_signals_top10 = pd.DataFrame()
    log_info("--- Top 10 Data Pipeline Finished ---")


    # --- Anomaly Detection ---
    log_info("\n--- Anomaly Detection Pipeline ---")
    print("Attempting to run Anomaly Detection...")
    full_snapshot_path = os.path.join(DATA_DIR, "full_market_snapshot.csv")
    anomalies_output_dir = DATA_DIR

    if os.path.exists(full_snapshot_path):
        try:
            log_info("Running Anomaly Detection...")
            path, anomalies = detect_anomalies(full_snapshot_path, anomalies_output_dir)
            log_info(f"Anomaly detection completed. Anomalies saved to {path}. Found {len(anomalies)} anomalies.")
            if not anomalies.empty:
                 print("Sample anomalies:")
                 print(anomalies.head().to_markdown(index=False))
            else:
                 print("No anomalies detected.")
        except Exception as e:
            log_error(f"Error during Anomaly Detection: {e}.")
    else:
        log_info(f"Warning: {full_snapshot_path} not found. Skipping Anomaly Detection.")
    log_info("--- Anomaly Detection Pipeline Finished ---")


    # --- Historical Data Processing ---
    log_info("\n--- Historical Data Pipeline ---")
    coin_id = "bitcoin"
    history_df_signals_display = pd.DataFrame()
    historical_price_data_path = os.path.join(DATA_DIR, f"{coin_id}_historical_price.csv")
    historical_signals_path = os.path.join(DATA_DIR, f"{coin_id}_historical_signals.csv")
    backtest_results_path = os.path.join(DATA_DIR, "signal_backtest.csv")


    print(f"Attempting to fetch and process historical data for {coin_id}...")
    try:
        history_data = get_coin_history(coin_id, days="30")
        if history_data is not None and "prices" in history_data:
            log_info("Historical data fetched.")
            history_df = pd.DataFrame(history_data["prices"], columns=["timestamp", "current_price"])
            history_df["timestamp"] = pd.to_datetime(history_df["timestamp"], unit="ms")
            history_df.to_csv(historical_price_data_path, index=False)
            log_info("Historical data processed and saved.")

            log_info(f"Computing technical indicators for {coin_id} historical data...")
            history_df["close"] = history_df["current_price"]
            history_df_ind = compute_indicators(history_df.copy())
            history_historical_indicators_path = os.path.join(DATA_DIR, f"{coin_id}_historical_with_indicators.csv")
            history_df_ind.to_csv(history_historical_indicators_path, index=False)
            log_info("Indicators computed and saved for historical data.")

            log_info(f"Generating signals for {coin_id} historical data...")
            history_df_signals = find_signals(history_df_ind.copy())
            history_signals_path = os.path.join(DATA_DIR, f"{coin_id}_historical_signals.csv")
            history_df_signals.to_csv(history_signals_path, index=False)
            log_info("Historical signals generated and saved.")
            history_df_signals_display = history_df_signals

            # --- Backtesting Historical Signals ---
            log_info(f"Attempting to backtest historical signals for {coin_id}...")
            backtest_results_df = backtest_signals(historical_signals_path, historical_price_data_path)
            log_info("Backtesting completed.")
            if not backtest_results_df.empty:
                print("Backtest Results (head):")
                print(backtest_results_df.head().to_markdown(index=False))

                # --- Export Backtest Results ---
                log_info("Exporting backtest results...")
                excel_output_path = os.path.join(DATA_DIR, "signal_backtest_report.xlsx")
                html_output_path = os.path.join(DATA_DIR, "signal_backtest_report.html")
                export_to_excel(backtest_results_path, excel_output_path)
                export_to_html(backtest_results_path, html_output_path)
                log_info(f"Backtest results exported to {excel_output_path} and {html_output_path}.")


                # --- ML Model Training ---
                log_info("Attempting to train ML model...")
                if os.path.exists(backtest_results_path):
                    try:
                        model, report = train_ml_model(backtest_results_path)
                        log_info("ML model training completed.")
                        print("Classification Report:")
                        for label, metrics in report.items():
                             if isinstance(metrics, dict):
                                  print(f"  {label}:")
                                  for metric, value in metrics.items():
                                       print(f"    {metric}: {value:.4f}")
                             else:
                                  print(f"  {label}: {metrics:.4f}")

                        # Optional: Save the trained model
                        # import joblib
                        # joblib.dump(model, os.path.join(DATA_DIR, 'ml_model.pkl'))
                        # log_info("ML model saved.")


                    except ValueError as ve:
                        log_error(f"Error during ML training: {ve}. Skipping training.")
                    except Exception as e:
                        log_error(f"Error during ML training: {e}. Skipping training.")
                else:
                    log_info(f"Warning: Backtest results file not found at {backtest_results_path}. Skipping ML model training.")


            else:
                log_info("No backtest results to display. Skipping ML model training.")


        else:
             log_info("Historical data fetching failed or 'prices' key not found. Skipping historical data processing and backtesting.")


    except Exception as e:
        log_error(f"Error processing historical data: {e}. Skipping historical signals.")
    log_info("--- Historical Data Pipeline Finished ---")


    # --- Display Results (for Top 10 snapshot) ---
    print("\n--- Results (Top 10 Snapshot) ---")
    if not df_signals_top10.empty:
        print(df_signals_top10.head().to_markdown(index=False))
    else:
        print("No top 10 snapshot signals generated due to processing errors or no data.")

    # --- Display Results (for Historical, if processed) ---
    print("\n--- Results (Historical Data) ---")
    if 'history_df_signals_display' in locals() and not history_df_signals_display.empty:
         print("Historical signals (tail):")
         print(history_df_signals_display.tail().to_markdown(index=False))
         print("
Historical signals (sample):")
         print(history_df_signals_display.sample(min(5, len(history_df_signals_display))).to_markdown(index=False))
    else:
         print("No historical signals generated or historical data processing skipped.")


    log_info("Bot pipeline finished.")


if __name__ == "__main__":
    main()
