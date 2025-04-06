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
2. Install dependencies manually:

```bash
python3 -m venv budget_env
source budget_env/bin/activate
pip install -r requirements.txt
```

Or using the Makefile:

```bash
make env
```

3. Create a `.env` file:

```env
GOOGLE_CREDS_PATH=/path/to/your/credentials.json
SPREADSHEET_NAME=Budget_Dynamic
```

---

## ▶️ Usage

You must pass in the target month and year when using `make`:

```bash
make run MONTH=march YEAR=2025
```

### Other Makefile commands

| Command        | Description                                       |
| -------------- | ------------------------------------------------- |
| `make env`     | Create venv + install packages                    |
| `make run`     | Run the update script for the month/year you pass |
| `make dry-run` | Preview parsed values (no write to sheet)         |
| `make replace` | Wipe tab content and re-write clean data          |

Example:

```bash
make dry-run MONTH=april YEAR=2024
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
