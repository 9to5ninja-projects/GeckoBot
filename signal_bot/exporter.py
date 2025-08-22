exporter_content = """# exporter.py
import pandas as pd
import os

def export_to_excel(csv_path, output_path):
    """Exports data from a CSV to an Excel file."""
    print(f"Attempting to export {csv_path} to Excel at {output_path}")
    try:
        df = pd.read_csv(csv_path)
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True) # Ensure output directory exists
        df.to_excel(output_path, index=False)
        print(f"Successfully exported {csv_path} to Excel at {output_path}")
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {csv_path} for Excel export.")
    except Exception as e:
        print(f"Error exporting to Excel from {csv_path}: {e}")


def export_to_html(csv_path, output_path):
    """Exports data from a CSV to an HTML file."""
    print(f"Attempting to export {csv_path} to HTML at {output_path}")
    try:
        df = pd.read_csv(csv_path)
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True) # Ensure output directory exists
        df.to_html(output_path, index=False)
        print(f"Successfully exported {csv_path} to HTML at {output_path}")
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {csv_path} for HTML export.")
    except Exception as e:
        print(f"Error exporting to HTML from {csv_path}: {e}")

# Example Usage (can be removed or commented out)
# if __name__ == '__main__':
#     # Assuming data/signal_backtest.csv exists after running main.py
#     DATA_DIR = 'signal_bot/data'
#     backtest_csv = os.path.join(DATA_DIR, 'signal_backtest.csv')
#     excel_output = os.path.join(DATA_DIR, 'signal_backtest.xlsx')
#     html_output = os.path.join(DATA_DIR, 'signal_backtest.html')
#
#     if os.path.exists(backtest_csv):
#          export_to_excel(backtest_csv, excel_output)
#          export_to_html(backtest_csv, html_output)
#     else:
#          print(f"Input file not found: {backtest_csv}")

"""
with open('signal_bot/exporter.py', 'w') as f:
    f.write(exporter_content)
print("signal_bot/exporter.py regenerated.")
