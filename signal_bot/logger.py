# signal_bot/logger.py
import logging
import sys

def setup_logger():
    """Sets up a basic logger to output to standard output."""
    # Ensure logger is not already configured
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            stream=sys.stdout)

def log_info(message):
    """Logs an informational message."""
    logging.info(message)

def log_error(message):
    """Logs an error message."""
    logging.error(message)
