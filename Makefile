.PHONY: setup env run dry-run replace edit ensure-venv

VENV_DIR := budget_env
PYTHON := $(VENV_DIR)/bin/python

ensure-venv:
	@test -x "$(PYTHON)" || (echo "🔧 Creating virtual environment..." && python3 -m venv $(VENV_DIR) && $(PYTHON) -m pip install --upgrade pip && $(PYTHON) -m pip install -r requirements.txt)

# Create venv and install dependencies
setup: ensure-venv

# Alias for setup
env: setup

# Run the parser normally
run: ensure-venv
	$(PYTHON) budget_parse.py $(MONTH) $(YEAR)

# Dry run without writing to Google Sheets
dry-run: ensure-venv
	$(PYTHON) budget_parse.py $(MONTH) $(YEAR) --dry-run

# Replace existing tab in Google Sheets
replace: ensure-venv
	$(PYTHON) budget_parse.py $(MONTH) $(YEAR) --replace

# Edit vendor map with optional category config and specific month/year
edit: ensure-venv
	@if [ -n "$(CAT)" ]; then \
		echo "Using custom categories: $(CAT)"; \
		$(PYTHON) budget_edit.py --month=$(MONTH) --year=$(YEAR) --cat-config=$(CAT); \
	else \
		echo "Using default categories"; \
		$(PYTHON) budget_edit.py --month=$(MONTH) --year=$(YEAR); \
	fi
