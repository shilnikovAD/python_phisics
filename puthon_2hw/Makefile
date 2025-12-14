.PHONY: lint-check format install run

install:
	pip install -r requirements.txt
	pip install ruff

lint-check:
	ruff check . --fix
	ruff format . --check

format:
	ruff format .

run:
	python run_server.py

test:
	python test_project.py

