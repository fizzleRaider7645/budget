import os
import json
import pandas as pd
import argparse
from dotenv import load_dotenv
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import calendar

# === Load .env ===
load_dotenv()

# === Constants ===
MAP_PATH = "vendor_map.json"
COLUMNS_TO_KEEP = [
    "Original Date", "Account Type", "Account Name", "Account Number",
    "Institution Name", "Name", "Amount", "Description", "Category"
]


def get_csv_path(base_dir: str, section: str, month: str) -> str:
    """Resolve CSV path from base dir, section, and month."""
    try:
        month_name = month.strip().capitalize()
        if month_name not in calendar.month_name:
            raise ValueError
    except ValueError:
        raise ValueError(f"Invalid month: {month}. Must be a valid full month name (e.g. March).")

    return os.path.expanduser(f"{base_dir}/{section}/{month.lower()}.csv")


def load_vendor_map() -> dict:
    if os.path.exists(MAP_PATH):
        with open(MAP_PATH) as f:
            return json.load(f)
    return {"recurring": {}, "spending": {}}


def save_vendor_map(vendor_map: dict) -> None:
    with open(MAP_PATH, "w") as f:
        json.dump(vendor_map, f, indent=2)
    print(f"\n✅ vendor_map.json updated with {sum(len(v) for v in vendor_map.values())} total vendors.")


def parse_csv(path: str, section: str, vendor_map: dict) -> list:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df = df[COLUMNS_TO_KEEP]
    df["Amount"] = df["Amount"].astype(str).str.replace(r"[$,]", "", regex=True).astype(float)
    df["Type"] = section

    new_transactions = []

    print(f"\n🔍 {section.capitalize()} Transactions:")
    for _, row in df.iterrows():
        name = str(row["Name"]).strip()
        amount = row["Amount"]
        vendor_data = {col: row[col] for col in COLUMNS_TO_KEEP if col in row}
        vendor_data["Type"] = section

        category = vendor_data.get("Category", "").strip()
        if not category:
            vendor_data["Category"] = "Uncategorized"
        print(f"✅ {name:40} → {vendor_data['Category']:15} (+${amount:.2f})")

        vendor_map[section][name] = vendor_data
        new_transactions.append({
            "Timestamp": datetime.now().isoformat(),
            "Vendor": name,
            "Amount": amount,
            "Type": section,
            "Category": vendor_data["Category"]
        })

    return new_transactions


def push_to_google_sheets(month: str, year: str, rows: list, replace: bool) -> None:
    tab_name = f"{month}-Budget-{year}"
    sheet_name = os.getenv("SPREADSHEET_NAME")
    credentials_file = os.getenv("GOOGLE_CREDS_PATH")

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
            print(f"⚠️ Tab '{tab_name}' already exists. No data was pushed. Use '--replace' to overwrite.")
            return
        worksheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=tab_name, rows="1000", cols="5")

    # Header
    header = ["Timestamp", "Vendor", "Amount", "Type", "Category"]
    worksheet.append_row(header)

    for row in rows:
        gsheet_row = [
            row.get("Timestamp", ""),
            row.get("Vendor", ""),
            f"{row.get('Amount', 0):.2f}",
            row.get("Type", ""),
            row.get("Category", "")
        ]
        worksheet.append_row(gsheet_row)

    print(f"\n✅ Google Sheet '{tab_name}' updated successfully.")


def main():
    parser = argparse.ArgumentParser(description="Parse and push budget data")
    parser.add_argument("month", help="Month to process (e.g. march)")
    parser.add_argument("year", help="Year to process (e.g. 2025)")
    parser.add_argument("--replace", action="store_true", help="Replace existing Google Sheet tab if exists")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without writing to Google Sheets")
    args = parser.parse_args()

    month = args.month.strip().capitalize()
    year = args.year.strip()
    dry_run = args.dry_run
    replace = args.replace

    vendor_map = load_vendor_map()
    all_transactions = []

    for section in ["recurring", "spending"]:
        try:
            path = get_csv_path("~/Documents/budget", section, month)
            if not os.path.exists(path):
                print(f"⚠️ {section.capitalize()} file not found: {path}")
                continue
            transactions = parse_csv(path, section, vendor_map)
            all_transactions.extend(transactions)
        except Exception as e:
            print(f"❌ Error processing {section} data: {e}")

    save_vendor_map(vendor_map)

    if not dry_run:
        push_to_google_sheets(month, year, all_transactions, replace=replace)
    else:
        print("\n🧪 Dry run enabled — no data was pushed to Google Sheets.")


if __name__ == "__main__":
    main()
