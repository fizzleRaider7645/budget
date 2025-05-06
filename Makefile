.PHONY: setup ensure-venv run dry-run replace edit gold-api spot coin-valuation coin-valuation-batch

VENV_DIR := budget_env
PYTHON := $(VENV_DIR)/bin/python
DEPS_MARKER := $(VENV_DIR)/.deps_installed

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
		$(PYTHON) budget_edit.py --months=$(MONTH) --years=$(YEAR) --cat-config=$(CAT); \
	else \
		$(PYTHON) budget_edit.py --months=$(MONTH) --years=$(YEAR); \
	fi

gold-api: ensure-venv
	$(PYTHON) gold_api.py

spot: ensure-venv
	$(PYTHON) gold_api.py --json

set-profile: ensure-venv
	@if [ -z "$(name)" ]; then echo "❌ Must set name="; exit 1; fi; \
	$(PYTHON) coin_valuation.py --set-profile $(name)

add-profile: ensure-venv
	@if [ -z "$(json)" ]; then echo "❌ Must provide a json='{...}' string"; exit 1; fi; \
	$(PYTHON) coin_valuation.py --add-profile '$(json)

# Add or update a profile via JSON string
add-profile: ensure-venv
	@if [ -z "$(json)" ]; then echo "❌ Must provide a json='{...}' string"; exit 1; fi; \
	$(PYTHON) coin_valuation.py --add-profile '$(json)'

coin-valuation: ensure-venv
	@if [ -z "$(coin)" ]; then echo "❌ Must set coin="; exit 1; fi; \
	CMD="$(PYTHON) coin_valuation.py --coin $(coin)"; \
	if [ -n "$(price)" ]; then CMD="$$CMD --price $(price)"; fi; \
	if [ -n "$(paid)" ]; then CMD="$$CMD --paid $(paid)"; fi; \
	if [ -n "$(profile)" ]; then CMD="$$CMD --profile $(profile)"; fi; \
	echo "📈 Running: $$CMD"; \
	eval "$$CMD"

coin-valuation-batch: ensure-venv
	@if [ -z "$(file)" ]; then echo "❌ Must set file="; exit 1; fi; \
	$(PYTHON) coin_valuation.py --batch $(file)
