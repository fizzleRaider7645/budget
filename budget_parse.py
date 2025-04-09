import os
import json
import argparse
import pandas as pd
from dotenv import load_dotenv
import gspread
import calendar
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

MAP_PATH = "vendor_map.json"
REQUIRED_COLUMNS = ["Original Date", "Name", "Amount", "Category"]

def get_month_name(month):
    """
    Convert a numeric month or name to lowercase month name.
    Accepts integers, zero-padded strings, or full month names.
    """
    try:
        month_int = int(month)
        if 1 <= month_int <= 12:
            return calendar.month_name[month_int].lower()
    except ValueError:
        pass  # Try as name

    month_str = month.lower()
    months = {calendar.month_name[i].lower(): i for i in range(1, 13)}
    if month_str in months:
        return month_str

    raise ValueError("Invalid month value. Use '03' or 'march', etc.")

def load_vendor_map():
    if os.path.exists(MAP_PATH):
        with open(MAP_PATH) as f:
            return json.load(f)
    return {"recurring": {}, "spending": {}}

def save_vendor_map(vendor_map):
    with open(MAP_PATH, "w") as f:
        json.dump(vendor_map, f, indent=2)
    print(f"\n✅ vendor_map.json updated with {sum(len(v) for v in vendor_map.values())} total vendors.\n")

def load_csv(section, month_name, year):
    path = os.path.expanduser(f"~/Documents/budget/{section}/{year}/{month_name}.csv")
    if not os.path.exists(path):
        print(f"⚠️  {section.capitalize()} file not found: {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"❌ Missing required columns in {section} CSV: {missing}")
    df["Amount"] = df["Amount"].replace(r'[\$,]', '', regex=True).astype(float)
    df["Type"] = section
    return df

def process_section(section, df, vendor_map):
    if df.empty:
        return [], {}

    rows = []
    summary = {}

    print(f"\n🔍 {section.capitalize()} Transactions:")
    for _, row in df.iterrows():
        vendor = str(row["Name"]).strip()
        category = str(row.get("Category", "Uncategorized")).strip()
        if not category:
            category = "Uncategorized"

        amount = row["Amount"]
        timestamp = row["Original Date"]

        if vendor not in vendor_map[section]:
            vendor_map[section][vendor] = {
                "Category": category,
                "Sample": row.to_dict()
            }

        rows.append({
            "Timestamp": timestamp,
            "Vendor": vendor,
            "Amount": amount,
            "Type": section,
            "Category": category
        })

        summary[category] = summary.get(category, 0) + amount
        print(f"✅ {vendor:<40} → {category:<20} (+${amount:.2f})")

    return rows, summary

def push_to_google_sheets(month, year, all_transactions, replace=False):
    tab_name = f"{month.capitalize()}-Budget-{year}"
    sheet_name = os.getenv("SPREADSHEET_NAME", "Budget_Dynamic")
    credentials_file = os.getenv("GOOGLE_CREDS_PATH", "credentials.json")

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)

    try:
        sheet = client.open(sheet_name)
    except Exception as e:
        print(f"❌ Could not open Google Sheet '{sheet_name}': {e}")
        return

    try:
        worksheet = sheet.worksheet(tab_name)
        if not replace:
            print(f"⚠️ Tab '{tab_name}' already exists. Use --replace to overwrite.")
            return
        worksheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=tab_name, rows="1000", cols="5")

    # Prepare rows
    header = ["Timestamp", "Vendor", "Amount", "Type", "Category"]
    rows = [header] + [
        [
            tx.get("Timestamp", ""),
            tx.get("Vendor", ""),
            f"{tx.get('Amount', 0):.2f}",
            tx.get("Type", ""),
            tx.get("Category", "")
        ]
        for tx in all_transactions
    ]

    worksheet.append_rows(rows)
    print(f"\n✅ Google Sheet '{tab_name}' updated successfully.")

def main():
    parser = argparse.ArgumentParser(description="Parse budget CSVs and update Google Sheet")
    parser.add_argument("month", help="Month to process (e.g. '03' or 'March')")
    parser.add_argument("year", type=int, help="Year to process (e.g. 2025)")
    parser.add_argument("--replace", action="store_true", help="Replace Google Sheet tab if exists")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to sheet, just print")
    args = parser.parse_args()

    try:
        month_name = get_month_name(args.month)
    except ValueError as e:
        print(f"❌ {e}")
        return

    year = args.year
    replace = args.replace
    dry_run = args.dry_run

    vendor_map = load_vendor_map()

    recurring_df = load_csv("recurring", month_name, year)
    spending_df = load_csv("spending", month_name, year)

    recurring_rows, _ = process_section("recurring", recurring_df, vendor_map)
    spending_rows, _ = process_section("spending", spending_df, vendor_map)

    all_transactions = recurring_rows + spending_rows
    save_vendor_map(vendor_map)

    if dry_run:
        print("\n🧪 Dry run enabled — no data was pushed to Google Sheets.")
    else:
        push_to_google_sheets(month_name, year, all_transactions, replace=replace)

if __name__ == "__main__":
    main()
