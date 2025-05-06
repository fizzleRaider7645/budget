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

### 🪙 Coin Valuation

- Pulls **live gold/silver spot prices** using GoldAPI
- Evaluates melt value and premiums of any coin in `coin_spec.json`
- Supports one-off or batch valuation via CSV
- Supports price offered vs. price paid, with clear buy verdict
- Custom buyer **profiles** like `stacker`, `collector`, `investor`
- Fully editable `premium_profiles.json` with premium % per category
- Supports:
  - ✅ `--coin` (e.g. `peace_dollar`)
  - ✅ `--price` and/or `--paid`
  - ✅ `--profile` or persistent default
  - ✅ `--set-profile` to persist default
  - ✅ `--add-profile` to define new buyer profiles
  - ✅ `--profiles-path` for managing multiple profile sets

---

## 📁 File Structure

```
~/Documents/budget/
├── recurring/
│   └── march.csv
├── spending/
│   └── march.csv
vendor_map.json
premium_profiles.json
coin_spec.json
.env
budget_parse.py
budget_edit.py
coin_valuation.py
gold_api.py
requirements.txt
Makefile
```

---

## ⚙️ Setup

```bash
make setup
```

Create `.env` with:

```env
GOOGLE_CREDS_PATH=/path/to/your/credentials.json
SPREADSHEET_NAME=Budget_Dynamic
GOLDAPI_KEY=your_goldapi_key_here
```

---

## 🪙 Coin Valuation Usage

Evaluate one coin:

```bash
make coin-valuation coin=peace_dollar price=30.25
```

With price paid:

```bash
make coin-valuation coin=peace_dollar paid=29.00
```

Override profile:

```bash
make coin-valuation coin=peace_dollar price=30.25 profile=collector
```

Set default profile:

```bash
make set-profile name=investor
```

Add new profile:

```bash
make add-profile json='{"name": "reseller", "junk": 0.12, "bullion": 0.06, "sovereign": 0.08}'
```

Batch evaluate (CSV must have columns: `coin,price,profile`):

```bash
make coin-valuation-batch file=coins.csv
```

Use custom profile path:

```bash
PREMIUM_PROFILE_PATH=my_profiles.json make coin-valuation coin=peace_dollar price=30.25
```

---

## 📊 Budget Output Example

| Timestamp           | Month | Year | Name         | Amount | Category  | Type     |
| ------------------- | ----- | ---- | ------------ | ------ | --------- | -------- |
| 2025-04-06 15:25:00 | March | 2025 | Trader Joe's | 76.53  | Groceries | spending |

---

## 🪙 Coin Valuation Example

```bash
make coin-valuation coin=peace_dollar price=30.25
```

Outputs:

```
🔍 Coin: Peace Dollar (Silver, Junk)
Spot Price:       $33.05
Melt Value:       $25.56
Allowed Premium:  10.00%
Max Allowed:      $28.12
Profile:          stacker
Offered Price:    $30.25
Premium ($):      $4.69
Premium (%):      18.35%
Status:           ❌ Too Expensive
```

---

## 🙌 License & Credits

Built with ❤️ by [You], powered by Python, gspread, pandas, and GoldAPI.
