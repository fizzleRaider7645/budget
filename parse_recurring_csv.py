import pandas as pd

# === CONFIGURATION ===
CATEGORIES = {
    "Mortgage": ["MOVEMENT MTG PMT"],
    "Car": ["TOYOTA ACH LEASE"],
    "Utilities": ["Duquesne Light", "PEOPLES NATURAL", "PITTSBURGH WATER WEB", "VERIZON"],
    "Subscriptions": ["Spotify", "Netflix", "HULUPLUS", "Patreon", "APPLE.COM"],
    "Daycare": ["explorers", "brightwhl", "LITTLE EXPLO"],
    "Health": ["LA Fitness"],
}

def get_category_totals(csv_file_path: str) -> dict:
    df = pd.read_csv(csv_file_path)
    df.columns = df.columns.str.strip()
    df["Name"] = df["Name"].astype(str)
    df["Amount"] = (
        df["Amount"]
        .astype(str)
        .str.replace(r"[$,]", "", regex=True)
        .astype(float)
    )

    category_totals = {
        "Mortgage": 0.0,
        "Car": 0.0,
        "Utilities": 0.0,
        "Subscriptions": 0.0,
        "Daycare": 0.0,
        "Health": 0.0,
        "Miscellaneous": 0.0,
    }

    print("\n🔍 Categorizing transactions...\n")

    for _, row in df.iterrows():
        name_clean = row["Name"].strip().lower()
        matched = False
        for category, keywords in CATEGORIES.items():
            if any(k.lower() in name_clean for k in keywords):
                category_totals[category] += row["Amount"]
                print(f"✅ Matched '{row['Name']}' → {category} (+${row['Amount']:.2f})")
                matched = True
                break
        if not matched:
            category_totals["Miscellaneous"] += row["Amount"]
            print(f"⚠️  Unmatched: '{row['Name']}' → Miscellaneous (+${row['Amount']:.2f})")

    # === PRINT SUMMARY ===
    print("\n📊 Parsed Category Totals:")
    for category, amount in category_totals.items():
        print(f"{category:15}: ${amount:,.2f}")

    return category_totals

# === OPTIONAL: Run from CLI ===
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse Rocket Money CSV and print categorized totals.")
    parser.add_argument("csv_file", help="Path to Rocket Money CSV")
    args = parser.parse_args()

    get_category_totals(args.csv_file)
