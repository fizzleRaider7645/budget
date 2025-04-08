.PHONY: help parse dry-run edit clean

PYTHON := python3
SCRIPT := budget_parse.py
EDITOR := budget_edit.py

help:
	@echo "Usage:"
	@echo "  make parse MONTH=month YEAR=year        - Parse and sync data for a given month"
	@echo "  make dry-run MONTH=month YEAR=year      - Run the parser in dry-run mode (no write)"
	@echo "  make edit                               - Edit vendor map (category/type)"
	@echo "  make clean                              - Remove __pycache__ and temp files"

parse:
	$(PYTHON) $(SCRIPT) $(MONTH) $(YEAR) --replace

dry-run:
	$(PYTHON) $(SCRIPT) $(MONTH) $(YEAR) --dry-run

edit:
	$(PYTHON) $(EDITOR)

clean:
	find . -name '__pycache__' -type d -exec rm -r {} +
