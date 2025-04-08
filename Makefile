setup:
	python3 -m venv budget_env
	source budget_env/bin/activate && pip install -r requirements.txt

run:
<<<<<<< Updated upstream
	python3 update_budget_log.py $(MONTH) $(YEAR)

dry-run:
	python3 update_budget_log.py $(MONTH) $(YEAR) --dry-run

replace:
	python3 update_budget_log.py $(MONTH) $(YEAR) --replace
=======
	python3 budget_parse.py $(MONTH) $(YEAR)

dry-run:
	python3 budget_parse.py $(MONTH) $(YEAR) --dry-run

replace:
	python3 budget_parse.py $(MONTH) $(YEAR) --replace

edit:
	@if [ -n "$(CAT)" ]; then \
		echo "Using custom categories: $(CAT)"; \
		$(PYTHON) budget_edit.py --cat-config=$(CAT); \
	else \
		echo "Using default categories"; \
		$(PYTHON) budget_edit.py; \
	fi
>>>>>>> Stashed changes

env:
	python3 -m venv budget-env
	source budget-env/bin/activate && pip install -r requirements.txt
