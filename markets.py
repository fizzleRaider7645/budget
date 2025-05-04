# markets.py

import requests
import os
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Enable color on Windows and clean reset behavior
init(autoreset=True)

load_dotenv()
GOLDAPI_KEY = os.getenv("GOLDAPI_KEY")

if not GOLDAPI_KEY:
    raise EnvironmentError("GOLDAPI_KEY not found in environment variables.")

GOLDAPI_URL = "https://www.goldapi.io/api"
HEADERS = {
    "x-access-token": GOLDAPI_KEY,
    "Content-Type": "application/json"
}

def get_spot_price(metal: str = "XAU", currency: str = "USD") -> float:
    url = f"{GOLDAPI_URL}/{metal}/{currency}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()["price"]
    else:
        raise Exception(f"GoldAPI error {response.status_code}: {response.text}")

def get_gold_price_usd() -> float:
    return get_spot_price("XAU", "USD")

def get_silver_price_usd() -> float:
    return get_spot_price("XAG", "USD")

if __name__ == "__main__":
    try:
        gold_price = get_gold_price_usd()
        silver_price = get_silver_price_usd()

        print(Fore.YELLOW + Style.BRIGHT + f"Gold (XAU/USD):   ${gold_price:.2f}")
        print(Fore.CYAN + Style.BRIGHT + f"Silver (XAG/USD): ${silver_price:.2f}")

    except Exception as e:
        print(Fore.RED + f"Error: {e}")
