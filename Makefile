.PHONY: setup env run dry-run replace edit

# Create and activate Python virtual environment
setup:
	python3 -m venv budget_env
	source budget_env/bin/activate && pip install -r requirements.txt

env:
	python3 -m venv budget_env
	source budget_env/bin/activate && pip install -r requirements.txt

# Run full update script for given month/year
run:
	python3 update_budget_log.py $(MONTH) $(YEAR)

# Run update script in dry-run mode
dry-run:
	python3 budget_parse.py $(MONTH) $(YEAR) --dry-run

# Run update script in replace mode
replace:
	python3 budget_parse.py $(MONTH) $(YEAR) --replace

# Edit vendor map with optional category config
edit:
	@if [ -n "$(CAT)" ]; then \
		echo "Using custom categories: $(CAT)"; \
		python3 budget_edit.py --cat-config=$(CAT); \
	else \
		echo "Using default categories"; \
		python3 budget_edit.py; \
	fi