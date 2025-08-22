import os

os.makedirs('signal_bot/utils', exist_ok=True)

coingecko_api_content = """# utils/coingecko_api.py
import requests

BASE_URL = "https://api.coingecko.com/api/v3"

def get_top_coins(limit=10):
    url = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": "true"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching top coins: {e}")
        return None

def get_coin_history(coin_id, days="30"):
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days} # Removed 'interval': 'hourly'
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical data for {coin_id}: {e}")
        if 'response' in locals() and response is not None:
             print(f"Response status code: {response.status_code}")
             print(f"Response text: {response.text}")
        return None
"""

with open('signal_bot/utils/coingecko_api.py', 'w') as f:
    f.write(coingecko_api_content)

print("signal_bot/utils/coingecko_api.py regenerated.")
