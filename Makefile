.PHONY: setup env run dry-run replace edit ensure-venv gold-api coin-valuation coin-valuation-batch

VENV_DIR := budget_env
PYTHON := $(VENV_DIR)/bin/python
DEPS_MARKER := $(VENV_DIR)/.deps_installed

# Create virtual environment and install dependencies
ensure-venv:
	@test -x "$(PYTHON)" || (echo "Creating virtual environment..." && python3 -m venv $(VENV_DIR))
	@if [ ! -f "$(DEPS_MARKER)" ] || [ requirements.txt -nt "$(DEPS_MARKER)" ]; then \
		echo "Installing or updating dependencies..."; \
		$(PYTHON) -m pip install --upgrade pip && \
		$(PYTHON) -m pip install -r requirements.txt && \
		touch $(DEPS_MARKER); \
	fi

setup: ensure-venv

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

# --- Gold API targets ---
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

spot: ensure-venv
	$(PYTHON) gold_api.py --json

# --- Coin Valuation (single + set-profile) ---
coin-valuation: ensure-venv
	@if [ -n "$(profile_path)" ]; then PROFILE_PATH_ARG="--profile-path $(profile_path)"; else PROFILE_PATH_ARG=""; fi; \
	if [ -n "$(set-profile)" ]; then \
		echo "📝 Setting default profile..."; \
		$(PYTHON) coin_valuation.py --set-profile $(set-profile) $$PROFILE_PATH_ARG; \
	elif [ -n "$(coin)" ]; then \
		CMD="$(PYTHON) coin_valuation.py --coin $(coin)"; \
		if [ -n "$(price)" ]; then CMD="$$CMD --price $(price)"; fi; \
		if [ -n "$(paid)" ]; then CMD="$$CMD --paid $(paid)"; fi; \
		if [ -n "$(profile)" ]; then CMD="$$CMD --profile $(profile)"; fi; \
		CMD="$$CMD $$PROFILE_PATH_ARG"; \
		echo "📈 Running: $$CMD"; eval $$CMD; \
	else \
		echo "❌ Must provide either set-profile= or coin="; exit 1; \
	fi

# --- Coin Valuation (batch mode) ---
coin-valuation-batch: ensure-venv
	@if [ -n "$(profile_path)" ]; then PROFILE_PATH_ARG="--profile-path $(profile_path)"; else PROFILE_PATH_ARG=""; fi; \
	$(PYTHON) coin_valuation.py --batch $(file) $$PROFILE_PATH_ARG
