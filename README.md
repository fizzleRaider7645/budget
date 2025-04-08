# 💰 Budget Parser & Google Sheets Sync Tool

A command-line tool to parse personal finance exports (e.g. from Rocket Money), categorize them, update a vendor map, and sync the results to Google Sheets.

---

## 📦 Features

- ✅ Parse CSV exports with rich metadata:
  - `Original Date`, `Account Type`, `Name`, `Amount`, `Category`, etc.
- 🧠 Automatically categorize vendors and track new ones
- ✏️ Edit vendor categories and types with a terminal UI
- 📤 Push results to a Google Sheets doc:
  - Recurring and spending transactions
  - Includes transaction `Type` column
- 🔁 Supports `--dry-run` and `--replace` flags

---

## 📂 Directory Structure

```bash
.
├── budget_parse.py        # Main parser script
├── budget_edit.py         # CLI tool for editing vendor_map.json
├── vendor_map.json        # Persistent vendor categorization store
├── .env                   # Contains creds & sheet name
├── Makefile               # Handy command runner
└── Documents/
    └── budget/
        ├── recurring/
        │   └── march.csv
        └── spending/
            └── march.csv
```
