.PHONY: setup env run dry-run replace edit ensure-venv gold-api coin-valuation coin-valuation-batch

VENV_DIR := budget_env
PYTHON := $(VENV_DIR)/bin/python
DEPS_MARKER := $(VENV_DIR)/.deps_installed

# Create virtual environment and always install dependencies
ensure-venv:
	@test -x "$(PYTHON)" || (echo "Creating virtual environment..." && python3 -m venv $(VENV_DIR))
	@if [ ! -f "$(DEPS_MARKER)" ] || [ requirements.txt -nt "$(DEPS_MARKER)" ]; then \
		echo "Installing or updating dependencies..."; \
		$(PYTHON) -m pip install --upgrade pip && \
		$(PYTHON) -m pip install -r requirements.txt && \
		touch $(DEPS_MARKER); \
	fi

# Alias for setup
setup: ensure-venv

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
		$(PYTHON) budget_edit.py --months=$(MONTH) --years=$(YEAR) --cat-config=$(CAT); \
	else \
		echo "Using default categories"; \
		$(PYTHON) budget_edit.py --months=$(MONTH) --years=$(YEAR); \
	fi

# Gold API utility targets
gold-api: ensure-venv
	$(PYTHON) gold_api.py

gold-api-dry: ensure-venv
	$(PYTHON) gold_api.py --dry-run

gold-api-json: ensure-venv
	$(PYTHON) gold_api.py --json

gold-api-cache: ensure-venv
	$(PYTHON) gold_api.py --from-cache

gold-api-cache-json: ensure-venv
	$(PYTHON) gold_api.py --from-cache --json

gold-api-diff: ensure-venv
	$(PYTHON) gold_api.py --diff

gold-api-json-diff: ensure-venv
	$(PYTHON) gold_api.py --json --diff

# Spot shortcut
spot: ensure-venv
	$(PYTHON) gold_api.py --json

# Run single-coin valuation (paid is optional)
coin-valuation: ensure-venv
	@if [ -n "$(paid)" ] && [ -n "$(price)" ]; then \
		$(PYTHON) coin_valuation.py --coin $(coin) --price $(price) --paid $(paid) --profile $(profile); \
	elif [ -n "$(paid)" ]; then \
		$(PYTHON) coin_valuation.py --coin $(coin) --paid $(paid) --profile $(profile); \
	elif [ -n "$(price)" ]; then \
		$(PYTHON) coin_valuation.py --coin $(coin) --price $(price) --profile $(profile); \
	else \
		echo "❌ Must specify either price= or paid="; exit 1; \
	fi

# Run batch valuation (CSV must have coin,price[,profile])
coin-valuation-batch: ensure-venv
	$(PYTHON) coin_valuation.py --batch $(file)
