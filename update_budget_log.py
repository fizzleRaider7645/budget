import os
import argparse
from datetime import datetime
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import WorksheetNotFound
from parse_recurring_csv import get_category_totals as get_recurring_totals
from parse_spending_csv import parse_spending_csv as get_spending_totals

# === LOAD ENV ===
load_dotenv()
creds_path = os.getenv("GOOGLE_CREDS_PATH")
if not creds_path or not os.path.exists(creds_path):
    print("❌ Missing or invalid GOOGLE_CREDS_PATH in .env")
    exit(1)

# === ARGUMENTS ===
parser = argparse.ArgumentParser(description="Merge recurring and spending data and update Google Sheet.")
parser.add_argument("--month", required=True, help="Month name (e.g. 'March')")
parser.add_argument("--year", default=datetime.now().year, help="Year (e.g. 2025)")
parser.add_argument("--recurring", required=True, help="Path to recurring CSV")
parser.add_argument("--spending", required=True, help="Path to spending CSV")
args = parser.parse_args()

# === SETUP VARIABLES ===
month_name = args.month.strip().capitalize()
year_suffix = str(args.year)[-2:]  # "25" from "2025"
sheet_tab_name = f"{month_name}-Budget-{year_suffix}_Log"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# === PARSE CSVs ===
recurring_totals = get_recurring_totals(args.recurring)
spending_totals = get_spending_totals(args.spending)

# === MERGE INTO ONE DICTIONARY ===
merged_totals = recurring_totals.copy()
for category, amount in spending_totals.items():
    if category in merged_totals:
        merged_totals[category] += amount
    else:
        merged_totals[category] = amount

# === CONNECT TO GOOGLE SHEET ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

try:
    spreadsheet = client.open("Budget_Dynamic")
    try:
        log_sheet = spreadsheet.worksheet(sheet_tab_name)
        print(f"📄 Found existing tab: '{sheet_tab_name}'")
    except WorksheetNotFound:
        log_sheet = spreadsheet.add_worksheet(title=sheet_tab_name, rows="1000", cols="5")
        log_sheet.append_row(["Timestamp", "Month", "Year", "Category", "Amount"])
        print(f"🆕 Created new tab: '{sheet_tab_name}'")

except Exception as e:
    print(f"❌ Could not open Budget_Dynamic sheet or create tab: {e}")
    exit(1)

# === APPEND DATA ===
for category, amount in merged_totals.items():
    row = [timestamp, month_name, str(args.year), category, round(amount, 2)]
    log_sheet.append_row(row)

print(f"✅ Data successfully appended to '{sheet_tab_name}' for {month_name} {args.year}.")
