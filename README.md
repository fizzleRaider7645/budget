# 🧾 Budget Logger

A CLI-based personal budgeting tool that parses recurring and spending CSV exports (e.g. from Rocket Money), categorizes them, and logs the data to a structured Google Sheets "Budget Log" tab by month and year.

---

## ✨ Features

- Parses **recurring** and **spending** CSVs into clean categories
- Logs data to **Google Sheets** dynamically using the API
- Supports:
  - ✅ `--dry-run`: preview without writing
  - ✅ `--replace`: overwrite existing tab
  - ✅ `.env` config and CLI overrides
- Automatically creates month/year log tabs like `March-Budget-25_Log`
- Auto-generates local folder structure at `~/Documents/budget/`

---

## 📁 File Structure

```
~/Documents/budget/
├── recurring/
│   └── march.csv
├── spending/
│   └── march.csv
.env
update_budget_log.py
parse_recurring_csv.py
parse_spending_csv.py
requirements.txt
Makefile
```

---

## ⚙️ Setup

1. Clone this repo
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or use the Makefile:

```bash
make setup
```

3. Create a `.env` file:

```env
GOOGLE_CREDS_PATH=/path/to/your/credentials.json
SPREADSHEET_NAME=Budget_Dynamic
```

4. Export your Rocket Money (or similar) data to CSV:

- Put recurring charges in `~/Documents/budget/recurring/march.csv`
- Put spending transactions in `~/Documents/budget/spending/march.csv`

---

## ▶️ Usage

### Basic example:

```bash
python3 update_budget_log.py march 2025
```

Or using Makefile:

```bash
make run
```

### Dry run (preview only):

```bash
python3 update_budget_log.py march 2025 --dry-run
# or
make dry-run
```

### Replace existing tab contents:

```bash
python3 update_budget_log.py march 2025 --replace
# or
make replace
```

---

## 📊 Output

Each run appends (or replaces) a log tab in your Google Sheet with:

| Timestamp           | Month | Year | Category  | Amount |
| ------------------- | ----- | ---- | --------- | ------ |
| 2025-04-06 15:25:00 | March | 2025 | Groceries | 476.57 |
| ...                 | ...   | ...  | ...       | ...    |

---

## ✅ Categories Handled

Recurring categories:

- Mortgage
- Car
- Utilities
- Subscriptions
- Daycare
- Health
- Miscellaneous

Spending categories:

- Auto & Transport
- Dining & Drinks
- Groceries
- Shopping
- Travel & Vacation
- Home & Garden
- Health & Wellness
- Entertainment & Rec.
- Medical
- Software & Tech
- Uncategorized

---

## 🙌 License & Credits

Built with ❤️ by [You], powered by Python + gspread + pandas.
