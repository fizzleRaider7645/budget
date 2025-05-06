import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from colorama import Fore, Style, init
import argparse

# Enable colorama for terminal styling
init(autoreset=True)

# Load .env for GOLDAPI_KEY
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

def update_env(gold, silver, env_path=".env"):
    """Overwrite GOLD_SPOT and SILVER_SPOT in the .env file."""
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write("")

    with open(env_path, "r") as f:
        lines = f.readlines()

    # Remove old spot lines
    lines = [line for line in lines if not line.startswith("GOLD_SPOT=") and not line.startswith("SILVER_SPOT=")]

    lines.append(f"GOLD_SPOT={gold:.2f}\n")
    lines.append(f"SILVER_SPOT={silver:.2f}\n")

    with open(env_path, "w") as f:
        f.writelines(lines)

def update_spot_cache(gold, silver, cache_file=".cache/spot.json"):
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "gold": gold,
        "silver": silver
    }

    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(entry)

    with open(cache_file, "w") as f:
        json.dump(history, f, indent=2)

def load_last_cached_spot(cache_file=".cache/spot.json"):
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            history = json.load(f)
        if history:
            return history[-1]
    raise FileNotFoundError("No spot price history found.")

def parse_args():
    parser = argparse.ArgumentParser(description="Fetch and store gold/silver spot prices.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch prices but don't write to .env or cache.")
    parser.add_argument("--json", action="store_true", help="Output spot prices as JSON.")
    parser.add_argument("--from-cache", action="store_true", help="Use last saved spot prices from .cache/spot.json.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    try:
        if args.from_cache:
            spot = load_last_cached_spot()
            gold_price = spot["gold"]
            silver_price = spot["silver"]
            source_note = " (from cache)"
        else:
            gold_price = get_gold_price_usd()
            silver_price = get_silver_price_usd()
            source_note = ""

        if args.json:
            print(json.dumps({
                "gold": round(gold_price, 2),
                "silver": round(silver_price, 2),
                "source": "cache" if args.from_cache else "live"
            }, indent=2))
        else:
            print(Fore.YELLOW + Style.BRIGHT + f"Gold (XAU/USD):   ${gold_price:.2f}{source_note}")
            print(Fore.CYAN + Style.BRIGHT + f"Silver (XAG/USD): ${silver_price:.2f}{source_note}")

        if not args.from_cache and not args.dry_run:
            update_env(gold_price, silver_price)
            update_spot_cache(gold_price, silver_price)
            print(Fore.GREEN + "✅ Spot prices saved to .env and logged to .cache/spot.json")
        elif args.from_cache and not args.json:
            print(Fore.MAGENTA + "ℹ️ Loaded from cache: no API request made.")
        elif args.dry_run and not args.json:
            print(Fore.MAGENTA + "ℹ️ Dry run: no files were written.")

    except Exception as e:
        print(Fore.RED + f"Error: {e}")
