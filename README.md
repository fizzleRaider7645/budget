# 🧾 Budget Logger

A CLI-based personal budgeting tool that parses recurring and spending CSV exports (e.g. from Rocket Money), categorizes them, and logs the data to a structured Google Sheets "Budget Log" tab by month and year.

---

## ✨ Features

- Parses **recurring** and **spending** CSVs into clean categories
- Logs data to **Google Sheets** dynamically using the API
- Supports:
  - ✅ `--dry-run`: preview without writing
  - ✅ `--replace`: overwrite existing tab
  - ✅ Custom category overrides during interactive edit
  - ✅ `.env` config and CLI overrides
  - ✅ Optional custom category config for editing session
- Automatically creates month/year log tabs like `March-Budget-25_Log`
- Auto-generates local folder structure at `~/Documents/budget/`
- Interactive `budget_edit.py` to modify vendor category/type

---

## 📁 File Structure

```
~/Documents/budget/
├── recurring/
│   └── march.csv
├── spending/
│   └── march.csv
vendor_map.json
.env
budget_parse.py
budget_edit.py
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

| Command        | Description                                               |
| -------------- | --------------------------------------------------------- |
| `make env`     | Create venv + install packages                            |
| `make run`     | Run the parser for the month/year you pass                |
| `make dry-run` | Preview parsed values (no write to sheet)                 |
| `make replace` | Wipe tab content and re-write clean data                  |
| `make edit`    | Launch `budget_edit.py` to update vendor categories/types |

Example:

```bash
make dry-run MONTH=april YEAR=2024
```

---

## 🧠 Editing Categories/Types

Run the edit tool:

```bash
python3 budget_edit.py
```

You can optionally pass a custom list of default categories:

```bash
python3 budget_edit.py --category-config=my_categories.json
```

The config should be a simple array:

```json
["Groceries", "Dining", "Travel", "Custom Category 1"]
```

Inside the tool:

- Navigate vendors
- Choose to edit **Category** or **Type**
- Select from defaults or set a custom category with `cust_cat=...`
- Set type to `recurring` or `spending` (or use numbers 1/2)
- Changes saved back to `vendor_map.json`

---

## 📊 Output

Each run appends (or replaces) a log tab in your Google Sheet with:

| Timestamp           | Month | Year | Name         | Amount | Category          | Type      |
| ------------------- | ----- | ---- | ------------ | ------ | ----------------- | --------- |
| 2025-04-06 15:25:00 | March | 2025 | Trader Joe's | 76.53  | Groceries         | spending  |
| 2025-04-06 15:25:01 | March | 2025 | Netflix      | 19.25  | Bills & Utilities | recurring |

---

## ✅ Categories Handled

Default categories include:

- Mortgage
- Car
- Utilities
- Subscriptions
- Childcare
- Health
- Groceries
- Dining & Drinks
- Shopping
- Entertainment
- Travel
- Software
- Insurance
- Medical
- Home
- Misc
- Bills & Utilities
- Auto & Transport
- Health & Wellness
- Entertainment & Rec.
- Software & Tech
- Home & Garden
- Travel & Vacation
- Uncategorized (fallback only)

You can override these in `budget_edit.py`.

---

## 🙌 License & Credits

Built with ❤️ by [You], powered by Python + gspread + pandas.
