VENV_DIR=budget-env
PYTHON=$(VENV_DIR)/bin/python3
PIP=$(VENV_DIR)/bin/pip

.PHONY: help init run dry-run replace edit clean

help:
	@echo "Available targets:"
	@echo "  init        Set up virtual environment and install dependencies"
	@echo "  run         Run budget_parse with default arguments (edit script manually)"
	@echo "  dry-run     Run budget_parse in dry-run mode (edit date in target)"
	@echo "  replace     Run budget_parse with --replace (edit date in target)"
	@echo "  edit        Edit the vendor_map.json (optionally add CAT=your_config.json)"
	@echo "  clean       Remove the virtual environment"

init:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) budget_parse.py march 2025

dry-run:
	$(PYTHON) budget_parse.py march 2025 --dry-run

replace:
	$(PYTHON) budget_parse.py march 2025 --replace

edit:
	@if [ -n "$(CAT)" ]; then \
		echo "Using custom categories: $(CAT)"; \
		$(PYTHON) budget_edit.py --cat-config=$(CAT); \
	else \
		echo "Using default categories"; \
		$(PYTHON) budget_edit.py; \
	fi

clean:
	rm -rf $(VENV_DIR)
