logger_content = """# logger.py
import logging
import os

DATA_DIR = 'signal_bot/data'
os.makedirs(DATA_DIR, exist_ok=True)

def setup_logger(log_file="bot.log"):
    """Sets up the root logger."""
    log_path = os.path.join(DATA_DIR, log_file)
    # Use basicConfig for simplicity, force=True allows reconfiguring in Colab
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True
    )
    # Add a handler to print logs to the console as well
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Avoid adding duplicate console handlers if basicConfig is called multiple times
    # Check if a StreamHandler is already attached to the root logger
    root_logger = logging.getLogger()
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
         root_logger.addHandler(console_handler)


def log_info(message):
    """Logs an informational message."""
    logging.info(message)

def log_error(message):
    """Logs an error message."""
    logging.error(message)

# Example usage (can be removed or commented out in final version)
# if __name__ == '__main__':
#     setup_logger()
#     log_info("Logger setup complete.")
#     log_error("This is a test error message.")
"""
with open('signal_bot/logger.py', 'w') as f:
    f.write(logger_content)
print("signal_bot/logger.py regenerated.")
