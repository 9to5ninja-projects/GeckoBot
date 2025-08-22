# dashboard.py
import streamlit as st
import pandas as pd
import os

# Define DATA_DIR
DATA_DIR = 'signal_bot/data'

st.title("Crypto Signal Dashboard")

tab1, tab2, tab3 = st.tabs(["Signals", "Anomalies", "Indicators"])

# Ensure files exist before trying to read
signals_path = os.path.join(DATA_DIR, "top10_signals.csv")
anomalies_dir = DATA_DIR
indicators_path = os.path.join(DATA_DIR, "top10_with_indicators.csv")

with tab1:
    st.subheader("Signal Feed (Top 10)")
    if os.path.exists(signals_path):
        try:
            signals = pd.read_csv(signals_path)
            st.dataframe(signals)
        except Exception as e:
            st.error(f"Error loading signals data: {e}")
    else:
        st.info(f"Signal data not found at {signals_path}. Run the main pipeline first.")

with tab2:
    st.subheader("Anomalies")
    anomaly_files = [f for f in os.listdir(anomalies_dir) if f.startswith('anomalies_') and f.endswith('.csv')]
    anomaly_files.sort(reverse=True)

    if anomaly_files:
        latest_anomaly_file = os.path.join(anomalies_dir, anomaly_files[0])
        st.info(f"Displaying latest anomalies from: {latest_anomaly_file}")
        try:
            anomalies = pd.read_csv(latest_anomaly_file)
            st.dataframe(anomalies)
        except Exception as e:
             st.error(f"Error loading anomalies data from {latest_anomaly_file}: {e}")
    else:
        st.info(f"No anomaly files found in {anomalies_dir}. Run the main pipeline with anomaly detection enabled.")

with tab3:
    st.subheader("Top 10 Indicators")
    if os.path.exists(indicators_path):
        try:
            indicators = pd.read_csv(indicators_path)
            chart_cols = ["rsi", "macd_diff"]
            available_chart_cols = [col for col in chart_cols if col in indicators.columns and pd.api.types.is_numeric_dtype(indicators[col])]

            if available_chart_cols:
                 st.subheader("Indicator Trends (RSI, MACD Diff)")
                 if not indicators[available_chart_cols].dropna().empty:
                      st.line_chart(indicators[available_chart_cols])
                 else:
                      st.info(f"Indicator data for charting ({available_chart_cols}) contains only NaN values or is empty. Cannot display chart.")
            elif chart_cols:
                 st.warning(f"Required numeric columns for charting not found or are not numeric: {chart_cols}")
            else:
                 st.info("No indicator data available for charting.")

            st.subheader("Full Indicator Data")
            st.dataframe(indicators)

        except Exception as e:
            st.error(f"Error loading indicators data: {e}")
    else:
        st.info(f"Indicator data not found at {indicators_path}. Run the main pipeline first.")

st.sidebar.subheader("How to run the dashboard:")
st.sidebar.markdown("1. Ensure you have Streamlit installed (`pip install streamlit`).")
st.sidebar.markdown("2. Run the main pipeline (`python -m signal_bot.main`) to generate data files.")
st.sidebar.markdown("3. Open a terminal in your project's root directory (`/content/` in Colab).")
st.sidebar.markdown("4. Run the command: `streamlit run signal_bot/dashboard.py`")
st.sidebar.markdown("5. A local URL will be provided to view the dashboard.")
