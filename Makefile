.PHONY: setup env run dry-run replace edit ensure-venv gold-api coin-valuation coin-valuation-batch coin-add coin-list coin-export coin-edit

VENV_DIR := budget_env
PYTHON := $(VENV_DIR)/bin/python
DEPS_MARKER := $(VENV_DIR)/.deps_installed

# --- Environment Setup ---
ensure-venv:
	@test -x "$(PYTHON)" || (echo "Creating virtual environment..." && python3 -m venv $(VENV_DIR))
	@if [ ! -f "$(DEPS_MARKER)" ] || [ requirements.txt -nt "$(DEPS_MARKER)" ]; then \
		echo "Installing or updating dependencies..."; \
		$(PYTHON) -m pip install --upgrade pip && \
		$(PYTHON) -m pip install -r requirements.txt && \
		touch $(DEPS_MARKER); \
	fi

setup: ensure-venv

# --- Utilities ---

help:
	@echo ""
	@echo "🧾 Budget & Coin Toolkit Help"
	@echo "-----------------------------"
	@echo "make setup                    # Create virtual environment and install dependencies"
	@echo "make run MONTH=may YEAR=2025 # Parse and upload budget data"
	@echo "make dry-run                 # Show parsed budget without writing"
	@echo "make replace                # Replace existing Google Sheets tab"
	@echo "make edit MONTH=may YEAR=2025 # Edit vendor map interactively"
	@echo ""
	@echo "💰 Coin Valuation"
	@echo "make coin-valuation coin=peace_dollar price=30.50 profile=stacker"
	@echo "make coin-valuation paid=28.25 coin=silver_eagle"
	@echo "make coin-valuation-batch file=coin_batch.csv"
	@echo ""
	@echo "📦 Coin Inventory"
	@echo "make coin-add coin=peace_dollar price=30.50 quantity=2 condition=AU date=2025-05-06 source=eBay notes='Toned'"
	@echo "make coin-edit id=<uuid> price=31.00 notes='Updated premium'"
	@echo "make coin-list"
	@echo "make coin-export format=csv"
	@echo ""
	@echo "⚖️  GSR Monitoring"
	@echo "make check-gsr              # Check gold/silver ratio and get trade advice"
	@echo ""

# --- Budget Parser ---
run: ensure-venv
	$(PYTHON) budget_parse.py $(MONTH) $(YEAR)

dry-run: ensure-venv
	$(PYTHON) budget_parse.py $(MONTH) $(YEAR) --dry-run

replace: ensure-venv
	$(PYTHON) budget_parse.py $(MONTH) $(YEAR) --replace

edit: ensure-venv
	@if [ -n "$(CAT)" ]; then \
		echo "Using custom categories: $(CAT)"; \
		$(PYTHON) budget_edit.py --months=$(MONTH) --years=$(YEAR) --cat-config=$(CAT); \
	else \
		echo "Using default categories"; \
		$(PYTHON) budget_edit.py --months=$(MONTH) --years=$(YEAR); \
	fi

# --- Spot Price ---
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

# --- Coin Valuation ---
coin-valuation: ensure-venv
	$(PYTHON) coin_valuation.py --coin $(coin) --price $(price) --paid $(paid) --profile $(profile)

coin-valuation-batch: ensure-venv
	$(PYTHON) coin_valuation.py --batch $(file)

# --- Coin Inventory ---
coin-add: ensure-venv
	$(PYTHON) coin_inventory.py add --coin $(coin) --price $(price) --quantity $(quantity) --condition $(condition) --date $(date) --source $(source) --notes "$(notes)"

coin-list: ensure-venv
	$(PYTHON) coin_inventory.py list

coin-export: ensure-venv
	$(PYTHON) coin_inventory.py export --format=$(format)

coin-edit: ensure-venv
	$(PYTHON) coin_inventory.py edit --id $(id) --price $(price) --quantity $(quantity) --condition $(condition) --date $(date) --source $(source) --notes "$(notes)"

# --- Gold to Silver Ratio ---
check-gsr: ensure-venv
	$(PYTHON) gsr.py

