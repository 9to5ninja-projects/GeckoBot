os.makedirs('signal_bot/signals', exist_ok=True)

generate_signals_content = """# signals/generate_signals.py
import pandas as pd

def generate_signal(df):
    signals = []
    # This is a basic signal function, find_signals is more developed
    if df.empty or 'rsi' not in df.columns or 'macd' not in df.columns or 'close' not in df.columns or 'ema_20' not in df.columns:
        df['signal'] = 'HOLD'
        return df[['signal']]

    latest_row = df.iloc[-1]

    sigs = []
    if latest_row["rsi"] < 30:
        sigs.append("BUY_RSI")
    # Add other basic signals if needed
    signals.append(", ".join(sigs) if sigs else "HOLD")

    df['signal'] = signals # Assign the generated signals (assuming single row for simplicity)
    return df[['signal']] # Return only the signal column as a DataFrame
"""
with open('signal_bot/signals/generate_signals.py', 'w') as f:
    f.write(generate_signals_content)
print("signal_bot/signals/generate_signals.py regenerated.")
