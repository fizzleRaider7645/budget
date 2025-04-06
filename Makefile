setup:
	python3 -m venv budget_env
	source budget_env/bin/activate && pip install -r requirements.txt

run:
	python3 update_budget_log.py $(MONTH) $(YEAR)

dry-run:
	python3 update_budget_log.py $(MONTH) $(YEAR) --dry-run

replace:
	python3 update_budget_log.py $(MONTH) $(YEAR) --replace

env:
	python3 -m venv budget-env
	source budget-env/bin/activate && pip install -r requirements.txt
