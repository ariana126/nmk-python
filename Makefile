.PHONY: install dev start test lint format migrate migrate-create migrate-down migrate-history

install:
	pip install -e ".[dev]"

dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

start:
	uvicorn src.main:app --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

migrate:
	PYTHONPATH=src .venv/bin/alembic upgrade head

migration-create:
	PYTHONPATH=src .venv/bin/alembic revision --autogenerate -m "$(m)"

migrate-rollback:
	PYTHONPATH=src .venv/bin/alembic downgrade -1

migration-history:
	PYTHONPATH=src .venv/bin/alembic history --verbose