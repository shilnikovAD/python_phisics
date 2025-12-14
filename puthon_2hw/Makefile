.PHONY: lint-check format install run

install:
	pip install -r requirements.txt
	pip install ruff

lint-check:
	python -m ruff check . --fix
	python -m ruff format . --check

format:
	python -m ruff format .

run:
	python run_server.py

test:
	python test_project.py

