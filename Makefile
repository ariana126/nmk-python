.PHONY: install start-dev start-prod down restart status logs shell test bdd lint lint-fix format \
	migrate migration-create migrate-rollback migration-history

install:
	docker compose build

start-dev:
	docker compose up -d

start-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

down:
	docker compose down

restart:
	docker compose restart

status:
	docker compose ps

logs:
	docker compose logs -f app

shell:
	docker compose exec app bash

test:
	docker compose exec app pytest src/

bdd:
	docker compose exec app pytest features/ -v -m "not wip"

lint:
	docker compose exec app ruff check .

lint-fix:
	docker compose exec app ruff check . --fix

format:
	docker compose exec app ruff format .

migrate:
	docker compose exec app alembic upgrade head

migration-create:
	docker compose exec app alembic revision --autogenerate -m "$(m)"

migrate-rollback:
	docker compose exec app alembic downgrade -1

migration-history:
	docker compose exec app alembic history --verbose
