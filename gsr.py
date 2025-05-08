import json
from datetime import datetime
from gold_api import get_spot_prices
from colorama import Fore, Style, init
from config import load_user_config

init(autoreset=True)

CACHE_FILE = ".cache/gsr.json"


def save_gsr_to_cache(gsr):
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "gsr": gsr
    })

    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def check_gsr():
    config = load_user_config()
    thresholds = config.get("gsr_alerts", {"silver_to_gold": 55, "gold_to_silver": 85})
    spot = get_spot_prices()

    gold = spot["gold"]
    silver = spot["silver"]
    gsr = gold / silver
    gsr_rounded = round(gsr, 2)

    print(f"\n\U0001F4CA Gold-to-Silver Ratio: {gsr_rounded}")
    print(f"Gold Spot:   ${gold:.2f}")
    print(f"Silver Spot: ${silver:.2f}")

    save_gsr_to_cache(gsr_rounded)

    if gsr <= thresholds["silver_to_gold"]:
        print(Fore.BLUE + Style.BRIGHT + f"\n🔁 Suggestion: Consider trading silver for gold\nYou could convert {gsr_rounded:.2f} oz silver → 1 oz gold")
    elif gsr >= thresholds["gold_to_silver"]:
        print(Fore.YELLOW + Style.BRIGHT + f"\n🔁 Suggestion: Consider trading gold for silver\nYou could convert 1 oz gold → {gsr_rounded:.2f} oz silver")
    else:
        print(Fore.GREEN + Style.BRIGHT + "\n🟢 Suggestion: Hold – GSR within neutral range")


if __name__ == "__main__":
    check_gsr()
