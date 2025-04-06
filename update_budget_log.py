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

# === CLI ARGUMENTS ===
parser = argparse.ArgumentParser(description="Update budget log by month and year.")
parser.add_argument("month", help="Month name (e.g. 'march')")
parser.add_argument("year", type=int, help="Year (e.g. 2025)")
parser.add_argument("--dry-run", action="store_true", help="Print what would be written without modifying Google Sheet")
parser.add_argument("--replace", action="store_true", help="Replace existing log tab content instead of appending")
parser.add_argument("--creds", help="Path to credentials.json (overrides .env)")
parser.add_argument("--sheet", help="Google Sheet name (overrides .env)")
args = parser.parse_args()

# === SETUP ===
month_name = args.month.strip().capitalize()
year_suffix = str(args.year)[-2:]
sheet_tab_name = f"{month_name}-Budget-{year_suffix}_Log"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# === LOAD CONFIG FROM ENV / CLI ===
creds_path = args.creds or os.getenv("GOOGLE_CREDS_PATH")
sheet_name = args.sheet or os.getenv("SPREADSHEET_NAME", "Budget_Dynamic")

if not creds_path or not os.path.exists(creds_path):
    print(f"❌ Missing or invalid Google credentials at: {creds_path}")
    exit(1)

# === ENSURE FOLDER STRUCTURE EXISTS ===
base_path = os.path.expanduser("~/Documents/budget")
for subfolder in ["recurring", "spending"]:
    os.makedirs(os.path.join(base_path, subfolder), exist_ok=True)

recurring_path = f"{base_path}/recurring/{args.month.lower()}.csv"
spending_path = f"{base_path}/spending/{args.month.lower()}.csv"

# === VALIDATE FILES EXIST ===
for path in [recurring_path, spending_path]:
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        exit(1)

# === PARSE ===
recurring_totals = get_recurring_totals(recurring_path)
spending_totals = get_spending_totals(spending_path)

# === MERGE ===
merged_totals = recurring_totals.copy()
for category, amount in spending_totals.items():
    merged_totals[category] = merged_totals.get(category, 0) + amount

# === DRY RUN ===
if args.dry_run:
    print(f"🌱 [Dry Run] Would write to: '{sheet_tab_name}' in sheet '{sheet_name}'")
    print("📝 Data preview:")
    for category, amount in merged_totals.items():
        print(f" - {category:20} ${amount:,.2f}")
    print("✅ Dry run complete — no data written.\n")
    exit(0)

# === GOOGLE SHEETS AUTH ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# === LOAD SHEET ===
try:
    spreadsheet = client.open(sheet_name)
    try:
        log_sheet = spreadsheet.worksheet(sheet_tab_name)
        print(f"📄 Found existing tab: '{sheet_tab_name}'")
        if args.replace:
            log_sheet.clear()
            log_sheet.append_row(["Timestamp", "Month", "Year", "Category", "Amount"])
            print("♻️ Replaced tab contents with fresh data")
    except WorksheetNotFound:
        log_sheet = spreadsheet.add_worksheet(title=sheet_tab_name, rows="1000", cols="5")
        log_sheet.append_row(["Timestamp", "Month", "Year", "Category", "Amount"])
        print(f"🆕 Created new tab: '{sheet_tab_name}'")
except Exception as e:
    print(f"❌ Failed to open sheet '{sheet_name}': {e}")
    exit(1)

# === APPEND DATA ===
for category, amount in merged_totals.items():
    row = [timestamp, month_name, str(args.year), category, round(amount, 2)]
    log_sheet.append_row(row)

print(f"✅ Data {'replaced' if args.replace else 'appended'} to '{sheet_tab_name}' in '{sheet_name}'")