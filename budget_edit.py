import json
import os

DEFAULT_CATEGORIES = [
    "Mortgage", "Car", "Utilities", "Subscriptions", "Childcare", "Health",
    "Groceries", "Dining & Drinks", "Shopping", "Entertainment", "Travel",
    "Software", "Insurance", "Medical", "Home", "Misc", "Bills & Utilities",
    "Auto & Transport", "Health & Wellness", "Entertainment & Rec.",
    "Software & Tech", "Home & Garden", "Travel & Vacation"
]

VENDOR_MAP_PATH = "vendor_map.json"

def load_vendor_map():
    if not os.path.exists(VENDOR_MAP_PATH):
        return {"recurring": {}, "spending": {}}
    with open(VENDOR_MAP_PATH) as f:
        return json.load(f)

def save_vendor_map(vendor_map):
    with open(VENDOR_MAP_PATH, "w") as f:
        json.dump(vendor_map, f, indent=2)
    print("\n✅ vendor_map.json saved.\n")

def show_category_menu():
    print("\n📚 Default Categories:")
    for i, cat in enumerate(DEFAULT_CATEGORIES, 1):
        print(f"  {i}) {cat}")
    print("")

def show_type_menu():
    print("\n🧾 Transaction Types:")
    print("  1) recurring")
    print("  2) spending\n")

def edit_category(entry):
    show_category_menu()
    print("➡️  Enter a number (e.g. 5), or use 'cust_cat=YourCustomCategory'")
    print("➡️  You may also combine with type override: type=recurring/spending")

    while True:
        choice = input("  → Your input (or 'back' to cancel): ").strip()
        if choice.lower() == "back":
            return None

        tokens = choice.split()
        selected_num = None
        custom_cat = None
        override_type = None

        for token in tokens:
            if token.lower().startswith("cust_cat="):
                custom_cat = token.split("=", 1)[1]
            elif token.lower().startswith("type="):
                override_type = token.split("=", 1)[1].lower()
            elif token.isdigit():
                selected_num = int(token)
            else:
                print(f"⚠️  Unrecognized input: '{token}'")

        if override_type and override_type not in ["recurring", "spending"]:
            print("⚠️  Invalid type. Use 'recurring' or 'spending'. Try again.")
            continue

        if selected_num and not (1 <= selected_num <= len(DEFAULT_CATEGORIES)):
            print("⚠️  Invalid number. Try again.")
            continue

        if custom_cat:
            entry["Category"] = custom_cat
        elif selected_num:
            entry["Category"] = DEFAULT_CATEGORIES[selected_num - 1]
        else:
            print("⚠️  You must select a number or pass 'cust_cat='. Try again.")
            continue

        if override_type:
            entry["Type"] = override_type

        return entry

def edit_type(entry):
    show_type_menu()
    while True:
        choice = input("  → Select type (number or name) or 'back' to cancel: ").strip().lower()
        if choice == "back":
            return None
        if choice == "1" or choice == "recurring":
            entry["Type"] = "recurring"
            return entry
        elif choice == "2" or choice == "spending":
            entry["Type"] = "spending"
            return entry
        else:
            print("⚠️  Invalid type. Please enter '1', '2', 'recurring', or 'spending'.")

def main():
    vendor_map = load_vendor_map()
    entries = []

    for type_key in ["recurring", "spending"]:
        for name, data in vendor_map.get(type_key, {}).items():
            entries.append({
                "Name": name,
                "Type": type_key,
                **(data if isinstance(data, dict) else {"Category": data})
            })

    if not entries:
        print("⚠️  Vendor map is empty.")
        return

    while True:
        print("\n🗂 Vendor Transactions:")
        for i, e in enumerate(entries, 1):
            print(f"{i}) {e['Name']:<40} Type: {e['Type']:<10} → {e['Category']}")

        print("\nSelect a number to edit, or type 'exit' to quit.")
        selection = input("→ ").strip()
        if selection.lower() == "exit":
            break
        if not selection.isdigit() or not (1 <= int(selection) <= len(entries)):
            print("⚠️  Invalid selection. Try again.")
            continue

        index = int(selection) - 1
        entry = entries[index]

        print(f"\n🔧 Editing '{entry['Name']}'")
        print("  1) Change Category")
        print("  2) Change Type")
        print("  3) Cancel")

        sub_choice = input("→ ").strip()
        if sub_choice == "1":
            updated = edit_category(entry)
        elif sub_choice == "2":
            updated = edit_type(entry)
        elif sub_choice == "3":
            continue
        else:
            print("⚠️  Invalid choice.")
            continue

        if updated:
            name = updated["Name"]
            vendor_map[entry["Type"]].pop(name, None)
            vendor_map[updated["Type"]][name] = {"Category": updated["Category"]}
            entries[index] = updated
            print(f"✅ Updated '{name}' successfully.")

    save_vendor_map(vendor_map)

if __name__ == "__main__":
    main()
