import argparse
import json
import os
import csv
from gold_api import get_spot_prices
from colorama import Fore, Style, init

# Enable color output
init(autoreset=True)

# --- Load coin spec ---
print("📄 Loading coin_spec.json...")
with open("coin_spec.json") as f:
    COIN_SPEC = json.load(f)

# --- Load premium profiles ---
print("📄 Loading premium_profiles.json...")
with open("premium_profiles.json") as f:
    PROFILE_DATA = json.load(f)

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
    profile = profile_override or PROFILE_DATA["default_profile"]
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
            profile = row.get("profile", args.profile)
            result = calculate_values(coin, spot_prices, actual_price=price, profile_override=profile, paid_flag=False)
            if "error" in result:
                print(Fore.RED + result["error"])
            else:
                display_result(result)

def main():
    parser = argparse.ArgumentParser(description="Evaluate coin melt value and premiums.")
    parser.add_argument("--coin", help="Coin key from coin_spec.json")
    parser.add_argument("--price", type=float, help="Offered price for comparison")
    parser.add_argument("--paid", type=float, help="Price actually paid (takes precedence over --price)")
    parser.add_argument("--profile", help="Override buyer profile")
    parser.add_argument("--batch", help="CSV file with columns: coin,price,profile")
    args = parser.parse_args()

    if not args.coin and not args.batch:
        parser.error("❌ Must provide either --coin or --batch")

    spot_prices = get_spot_prices()

    if args.batch:
        evaluate_batch(args, spot_prices)
    elif args.coin:
        evaluate_single(args, spot_prices)

if __name__ == "__main__":
    main()
