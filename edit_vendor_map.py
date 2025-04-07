import json
import os

# Use 'Misc' instead of 'Uncategorized' in menu options
DEFAULT_CATEGORIES = [
    "Mortgage", "Car", "Utilities", "Subscriptions", "Childcare",
    "Groceries", "Dining & Drinks", "Shopping", "Entertainment",
    "Health", "Medical", "Travel", "Auto & Transport", "Home & Garden",
    "Software & Tech", "Insurance", "Misc"
]

def load_vendor_map(path="vendor_map.json"):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_vendor_map(vendor_map, path="vendor_map.json"):
    with open(path, "w") as f:
        json.dump(vendor_map, f, indent=2)
    print(f"✅ Saved updated vendor map to {path}")

def show_category_menu():
    print("\n📚 Categories:")
    for i, cat in enumerate(DEFAULT_CATEGORIES, 1):
        print(f"  [{i}] {cat}")

def select_category():
    while True:
        choice = input("  → Select a category by number or type a custom name (Enter to skip): ").strip()
        if choice == "":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(DEFAULT_CATEGORIES):
            return DEFAULT_CATEGORIES[int(choice) - 1]
        return choice  # allow custom string

def edit_uncategorized_vendors():
    vendor_map = load_vendor_map()
    uncategorized = [v for v, cat in vendor_map.items() if cat == "Uncategorized"]

    if not uncategorized:
        print("✅ No Uncategorized vendors left!")
        return

    print(f"📝 Found {len(uncategorized)} Uncategorized vendors:")

    for vendor in uncategorized:
        print(f"\nVendor: {vendor}")
        show_category_menu()
        selected = select_category()
        if selected:
            vendor_map[vendor] = selected
            print(f"  ✅ Updated '{vendor}' → {selected}")
        else:
            print("  ↩️ Skipped.")

    save_vendor_map(vendor_map)

if __name__ == "__main__":
    edit_uncategorized_vendors()