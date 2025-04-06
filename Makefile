setup:
	python3 -m venv budget_env
	source budget_env/bin/activate && pip install -r requirements.txt

run:
	python3 update_budget_log.py march 2025

dry-run:
	python3 update_budget_log.py march 2025 --dry-run

replace:
	python3 update_budget_log.py march 2025 --replace