# utils/coingecko_api.py
import requests
import pandas as pd
import os
from ..logger import setup_logger, log_info, log_error # Import logger from parent directory

BASE_URL = "https://api.coingecko.com/api/v3"

def get_top_coins(limit=10):
    """Fetches market data for top N coins."""
    setup_logger() # Ensure logger is setup
    url = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": "true"
    }
    log_info(f"Fetching top {limit} coins from {url} with params {params}")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        log_info("Successfully fetched top coins.")
        return response.json()
    except requests.exceptions.RequestException as e:
        log_error(f"Error fetching top coins: {e}")
        if 'response' in locals() and response is not None:
             log_error(f"Response status code: {response.status_code}")
             log_error(f"Response text: {response.text}")
        return None

def get_coin_history(coin_id, days="30"):
    """Fetches historical market data for a specific coin."""
    setup_logger() # Ensure logger is setup
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    # Removing "interval": "hourly" as it's for Enterprise plan
    params = {"vs_currency": "usd", "days": days}
    log_info(f"Fetching historical data for {coin_id} from {url} with params: {params}")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        log_info(f"Successfully fetched historical data for {coin_id}. Response keys: {data.keys()}")
        return data
    except requests.exceptions.RequestException as e:
        log_error(f"Error fetching historical data for {coin_id}: {e}")
        if 'response' in locals() and response is not None:
             log_error(f"Response status code: {response.status_code}")
             log_error(f"Response text: {response.text}")
        return None