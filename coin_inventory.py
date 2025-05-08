import argparse
import json
import os
import uuid
from datetime import datetime
from tabulate import tabulate
from gold_api import get_spot_prices

INVENTORY_FILE = "coin_inventory.json"
USER_CONFIG_FILE = "user_config.json"

# Load COIN_SPEC from JSON
with open("coin_spec.json") as f:
    COIN_SPEC = json.load(f)

# Ensure inventory and config files exist
if not os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(USER_CONFIG_FILE):
    with open(USER_CONFIG_FILE, "w") as f:
        json.dump({
            "default_profile": "stacker",
            "profile_path": "premium_profiles.json",
            "user_profile_path": "user_profile.json",
            "preferred_currency": "USD",
            "notify_threshold_pct": 0.05,
            "track_gold_silver_ratio": true
        }, f, indent=2)

def load_user_config():
    with open(USER_CONFIG_FILE) as f:
        return json.load(f)

def load_inventory():
    with open(INVENTORY_FILE) as f:
        return json.load(f)

def save_inventory(inventory):
    with open(INVENTORY_FILE, "w") as f:
        json.dump(inventory, f, indent=2)

def calculate_melt_and_premium(coin_key, spot_prices, price_paid):
    if coin_key not in COIN_SPEC:
        raise ValueError(f"Coin '{coin_key}' not found in coin_spec.json")
    spec = COIN_SPEC[coin_key]
    spot_price = spot_prices[spec['type']]
    melt = spec['metal_content_oz'] * spot_price
    premium_dollar = price_paid - melt
    premium_pct = premium_dollar / melt if melt else 0
    return round(spot_price, 2), round(melt, 2), round(premium_dollar, 2), round(premium_pct, 4)

def add_coin(args):
    inventory = load_inventory()
    spot_prices = get_spot_prices()

    spot_price, melt, prem_dollar, prem_pct = calculate_melt_and_premium(
        args.coin, spot_prices, args.price)

    coin = COIN_SPEC[args.coin]

    entry = {
        "id": str(uuid.uuid4()),
        "coin": args.coin,
        "type": coin["type"],
        "category": coin["category"],
        "price_paid": args.price,
        "quantity": args.quantity,
        "condition": args.condition,
        "source": args.source,
        "date": args.date,
        "spot_price_at_purchase": spot_price,
        "melt_value": melt,
        "premium_dollar": prem_dollar,
        "premium_pct": prem_pct,
        "notes": args.notes or ""
    }
    inventory.append(entry)
    save_inventory(inventory)
    print("✅ Coin added to inventory.")

def list_inventory():
    inventory = load_inventory()
    if not inventory:
        print("📭 Inventory is empty.")
        return
    table = []
    for coin in inventory:
        table.append({
            "ID": coin["id"],
            "Date": coin["date"],
            "Coin": coin["coin"],
            "Qty": coin["quantity"],
            "Cond.": coin["condition"],
            "Paid": f"${coin['price_paid']:.2f}",
            "Prem %": f"{coin['premium_pct']*100:.2f}%",
            "Spot @ Buy": f"${coin['spot_price_at_purchase']:.2f}",
            "Source": coin["source"],
            "Notes": coin["notes"]
        })
    print("\n📦 Coin Inventory\n")
    print(tabulate(table, headers="keys", tablefmt="fancy_grid"))

def export_inventory(format):
    inventory = load_inventory()
    if format == "csv":
        import csv
        keys = inventory[0].keys() if inventory else []
        with open("coin_inventory_export.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(inventory)
        print("📤 Exported inventory to coin_inventory_export.csv")
    else:
        with open("coin_inventory_export.json", "w") as f:
            json.dump(inventory, f, indent=2)
        print("📤 Exported inventory to coin_inventory_export.json")

def edit_entry(args):
    inventory = load_inventory()
    entry = next((item for item in inventory if item["id"] == args.id), None)
    if not entry:
        print("❌ Entry not found.")
        return

    # Update only fields that were explicitly passed
    if hasattr(args, "price") and args.price is not None:
        entry["price_paid"] = args.price
    if hasattr(args, "quantity") and args.quantity is not None:
        entry["quantity"] = args.quantity
    if hasattr(args, "condition") and args.condition is not None:
        entry["condition"] = args.condition
    if hasattr(args, "date") and args.date is not None:
        entry["date"] = args.date
    if hasattr(args, "source") and args.source is not None:
        entry["source"] = args.source
    if hasattr(args, "notes") and args.notes is not None:
        entry["notes"] = args.notes

    # Recalculate premium
    spot_prices = get_spot_prices()
    spot_price, melt, prem_dollar, prem_pct = calculate_melt_and_premium(
        entry["coin"], spot_prices, entry["price_paid"])
    entry["spot_price_at_purchase"] = spot_price
    entry["melt_value"] = melt
    entry["premium_dollar"] = prem_dollar
    entry["premium_pct"] = prem_pct

    save_inventory(inventory)
    print("✏️ Entry updated.")

def main():
    parser = argparse.ArgumentParser(description="Manage coin inventory")
    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser("add")
    add.add_argument("--coin", required=True)
    add.add_argument("--price", type=float, required=True)
    add.add_argument("--quantity", type=int, default=1)
    add.add_argument("--condition", default="BU")
    add.add_argument("--date", required=True)
    add.add_argument("--source", default="Unknown")
    add.add_argument("--notes")

    list_cmd = subparsers.add_parser("list")

    export = subparsers.add_parser("export")
    export.add_argument("--format", choices=["csv", "json"], default="json")

    edit = subparsers.add_parser("edit")
    edit.add_argument("--id", required=True)
    edit.add_argument("--price", type=float)
    edit.add_argument("--quantity", type=int, nargs="?")
    edit.add_argument("--condition", nargs="?")
    edit.add_argument("--date", nargs="?")
    edit.add_argument("--source", nargs="?")
    edit.add_argument("--notes", nargs="?")

    args = parser.parse_args()

    if args.command == "add":
        add_coin(args)
    elif args.command == "list":
        list_inventory()
    elif args.command == "export":
        export_inventory(args.format)
    elif args.command == "edit":
        edit_entry(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
