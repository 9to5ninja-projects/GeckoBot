ml_model_trainer_content = """# ml_model_trainer.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os

def train_ml_model(training_csv):
    """
    Trains an ML model (RandomForestClassifier) on historical signal outcomes.

    Args:
        training_csv (str): Path to the CSV file containing training data
                            (e.g., backtest results with 'success' column).

    Returns:
        tuple: A tuple containing the trained model and the classification report (dict).
               Returns (None, None) if training fails or data is insufficient.
    """
    print("\\n--- Inside train_ml_model ---")
    try:
        if not os.path.exists(training_csv):
            print(f"Error: Training data file not found at {training_csv}.")
            print("--- Exiting train_ml_model ---\\n")
            return None, None

        df = pd.read_csv(training_csv)
        print(f"Successfully loaded training data from {training_csv}.")

        # Ensure required columns exist and are numeric
        required_features = ["rsi", "ema_20", "macd", "bb_upper", "bb_lower"] # Use 'macd' as computed
        required_label = "success"

        if not all(col in df.columns for col in required_features + [required_label]):
            missing = [col for col in required_features + [required_label] if col not in df.columns]
            print(f"Error: Missing required columns for training: {missing}. Skipping training.")
            print("--- Exiting train_ml_model ---\\n")
            return None, None

        # Ensure feature columns are numeric, coerce errors
        for col in required_features:
             df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows with NaN in required features or label
        df = df.dropna(subset=required_features + [required_label])

        if df.empty:
            print("Error: No valid data remaining after dropping NaNs for training. Skipping training.")
            print("--- Exiting train_ml_model ---\\n")
            return None, None

        print(f"Using {len(df)} valid rows for training.")


        # Define features (X) and label (y)
        X = df[required_features]
        y = df[required_label].astype(int) # Ensure label is integer


        # Check if there are at least two classes in the label (for classification)
        if y.nunique() < 2:
            print(f"Error: Training data contains only one class ({y.iloc[0]}) in the '{required_label}' column. Need at least two classes for classification. Skipping training.")
            print("--- Exiting train_ml_model ---\\n")
            return None, None

        # Check if there are enough samples for train/test split
        if len(df) < 2: # Need at least 2 samples for split
             print("Error: Not enough data points for train/test split (need at least 2). Skipping training.")
             print("--- Exiting train_ml_model ---\\n")
             return None, None

        # Perform train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y) # Use stratify if classes are imbalanced

        print(f"Training model on {len(X_train)} samples, testing on {len(X_test)} samples.")

        # Initialize and train the model
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)

        # Evaluate the model
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0) # Use zero_division=0 to handle cases with no predicted samples for a class

        print("ML model training successful.")
        print("--- Exiting train_ml_model ---\\n")
        return model, report

    except ValueError as ve:
        print(f"ValueError during ML training: {ve}. Skipping training.")
        print("--- Exiting train_ml_model ---\\n")
        return None, None
    except Exception as e:
        print(f"Error during ML training: {e}. Skipping training.")
        print("--- Exiting train_ml_model ---\\n")
        return None, None

# Example Usage (can be removed or commented out)
# if __name__ == '__main__':
#     # Assuming data/signal_backtest.csv exists with a 'success' column
#     DATA_DIR = 'signal_bot/data'
#     training_data_path = os.path.join(DATA_DIR, 'signal_backtest.csv')
#     if os.path.exists(training_data_path):
#         trained_model, training_report = train_ml_model(training_data_path)
#         if trained_model:
#             print("\\nTraining Report Summary:")
#             # Print classification report in a readable format
#             for label, metrics in training_report.items():
#                  if isinstance(metrics, dict):
#                       print(f"  {label}:")
#                       for metric, value in metrics.items():
#                            print(f"    {metric}: {value:.4f}")
#                  else:
#                       print(f"  {label}: {metrics:.4f}")
#     else:
#          print(f"Training data not found: {training_data_path}")

"""
with open('signal_bot/ml_model_trainer.py', 'w') as f:
    f.write(ml_model_trainer_content)
print("signal_bot/ml_model_trainer.py regenerated.")
