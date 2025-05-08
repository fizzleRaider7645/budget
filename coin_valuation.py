import argparse
import json
import os
import csv
from gold_api import get_spot_prices
from colorama import Fore, Style, init
from config import load_user_config

# Enable color output
init(autoreset=True)

# --- Load config ---
config = load_user_config()
profile_path = config.get("profile_path", "premium_profiles.json")

# --- Load coin spec ---
print("\U0001F4C4 Loading coin_spec.json...")
with open("coin_spec.json") as f:
    COIN_SPEC = json.load(f)

# --- Parse args ---
parser = argparse.ArgumentParser(description="Evaluate coin melt value and premiums.")
parser.add_argument("--coin", help="Coin key from coin_spec.json")
parser.add_argument("--price", type=float, help="Offered price for comparison")
parser.add_argument("--paid", type=float, help="Price actually paid (takes precedence over --price)")
parser.add_argument("--profile", help="Override buyer profile for this run")
parser.add_argument("--set-profile", help="Set default buyer profile for future runs")
parser.add_argument("--add-profile", help="Add or update a premium profile (pass JSON string)")
parser.add_argument("--batch", help="CSV file with columns: coin,price,profile")
parser.add_argument("--profiles-path", default=profile_path, help="Path to premium_profiles.json")
args = parser.parse_args()

# --- Load premium profiles ---
print(f"\U0001F4C4 Loading {args.profiles_path}...")
with open(args.profiles_path) as f:
    PROFILE_DATA = json.load(f)

# --- Profile helpers ---
def get_default_profile():
    return config.get("default_profile", PROFILE_DATA.get("default_profile", "stacker"))

def set_default_profile(profile):
    config["default_profile"] = profile
    with open("user_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print(Fore.GREEN + f"✅ Default profile set to: {profile}")

def edit_premium_profile(profile_name, category_premiums):
    PROFILE_DATA["profiles"][profile_name] = category_premiums
    with open(args.profiles_path, "w") as f:
        json.dump(PROFILE_DATA, f, indent=2)
    print(Fore.GREEN + f"✅ Profile '{profile_name}' added/updated successfully.")

# --- Spot and valuation helpers ---
def get_spot_for_coin(coin, spot_prices):
    return spot_prices["gold"] if coin["type"] == "gold" else spot_prices["silver"]

def display_result(result):
    print("\n" + Fore.YELLOW + Style.BRIGHT + f"🔍 Coin: {result['coin'].replace('_', ' ').title()} ({result['type'].capitalize()}, {result['category']})")
    print(Fore.CYAN + f"Spot Price:       ${result['spot_price']:.2f}")
    print(Fore.CYAN + f"Melt Value:       ${result['melt_value']:.2f}")
    print(Fore.CYAN + f"Allowed Premium:  {result['allowed_premium_pct']*100:.2f}%")
    print(Fore.CYAN + f"Max Allowed:      ${result['max_allowed_price']:.2f}")
    print(Fore.CYAN + f"Profile:          {result['profile']}")

    if "actual_price" in result:
        label = "Paid" if result.get("paid_flag") else "Offered"
        print(Fore.MAGENTA + f"{label} Price:     ${result['actual_price']:.2f}")
        print(Fore.MAGENTA + f"Premium ($):      ${result['premium_dollar']:.2f}")
        print(Fore.MAGENTA + f"Premium (%):      {result['premium_pct']*100:.2f}%")
        status = ("✅ Good Buy" if result["within_threshold"] else "❌ Overpaid") if result.get("paid_flag") \
                 else ("✅ Fair Offer" if result["within_threshold"] else "❌ Too Expensive")
        color = Fore.GREEN if result["within_threshold"] else Fore.RED
        print(color + Style.BRIGHT + f"Status:           {status}")
    print()

def calculate_values(coin_key, spot_prices, actual_price=None, profile_override=None, paid_flag=False):
    if coin_key not in COIN_SPEC:
        return {"error": f"Coin '{coin_key}' not found in spec."}

    coin = COIN_SPEC[coin_key]
    profile = profile_override or get_default_profile()
    category = coin["category"]
    spot_price = get_spot_for_coin(coin, spot_prices)
    melt_value = coin["metal_content_oz"] * spot_price
    allowed_premium_pct = PROFILE_DATA["profiles"][profile][category]
    max_allowed_price = melt_value * (1 + allowed_premium_pct)

    result = {
        "coin": coin_key,
        "type": coin["type"],
        "category": category,
        "spot_price": round(spot_price, 2),
        "melt_value": round(melt_value, 2),
        "allowed_premium_pct": allowed_premium_pct,
        "max_allowed_price": round(max_allowed_price, 2),
        "profile": profile
    }

    if actual_price is not None:
        premium_dollar = actual_price - melt_value
        premium_pct = premium_dollar / melt_value if melt_value else 0
        result.update({
            "actual_price": round(actual_price, 2),
            "premium_dollar": round(premium_dollar, 2),
            "premium_pct": round(premium_pct, 4),
            "within_threshold": premium_pct <= allowed_premium_pct,
            "paid_flag": paid_flag
        })

    return result

def evaluate_single(args, spot_prices):
    paid = float(args.paid) if args.paid else None
    offered = float(args.price) if args.price else None
    price = paid if paid is not None else offered
    paid_flag = paid is not None

    if args.set_profile:
        set_default_profile(args.set_profile)
        return

    if args.add_profile:
        try:
            profile_dict = json.loads(args.add_profile)
            profile_name = profile_dict.pop("name")
            edit_premium_profile(profile_name, profile_dict)
        except Exception as e:
            print(Fore.RED + f"❌ Failed to add profile: {e}")
        return

    result = calculate_values(args.coin, spot_prices, actual_price=price, profile_override=args.profile, paid_flag=paid_flag)
    if "error" in result:
        print(Fore.RED + result["error"])
    else:
        display_result(result)

def evaluate_batch(args, spot_prices):
    with open(args.batch, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            coin = row["coin"]
            price = float(row["price"]) if "price" in row and row["price"] else None
            profile = row.get("profile", args.profile or get_default_profile())
            result = calculate_values(coin, spot_prices, actual_price=price, profile_override=profile, paid_flag=False)
            if "error" in result:
                print(Fore.RED + result["error"])
            else:
                display_result(result)

if __name__ == "__main__":
    if args.set_profile:
        set_default_profile(args.set_profile)
    elif args.add_profile:
        try:
            profile_dict = json.loads(args.add_profile)
            profile_name = profile_dict.pop("name")
            edit_premium_profile(profile_name, profile_dict)
        except Exception as e:
            print(Fore.RED + f"❌ Failed to add profile: {e}")
    elif args.batch:
        spot_prices = get_spot_prices()
        evaluate_batch(args, spot_prices)
    elif args.coin:
        spot_prices = get_spot_prices()
        evaluate_single(args, spot_prices)
    else:
        print(Fore.RED + "❌ Must provide either --coin or --batch or one of the management flags.")
