include .env
export

.PHONY: run test lint format typecheck pre-commit check \
	infra-up infra-down infra-restart infra-logs \
	app-up app-down app-restart app-logs \
	compose-up compose-down compose-logs \
	migration psql

UVICORN_RELOAD :=
ifneq (,$(filter True true 1,$(DEBUG)))
UVICORN_RELOAD = --reload
endif

run:
	poetry run uvicorn src.main:app --port $(APP_PORT) $(UVICORN_RELOAD)

test:
	PYTHONPATH=. poetry run pytest -x tests -v --junitxml=junit.xml --cov=src --cov-branch --cov-report=term --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-fail-under=80

lint:
	poetry run ruff check . --force-exclude

format:
	poetry run ruff format . --force-exclude
	poetry run ruff check --fix . --force-exclude

typecheck:
	poetry run mypy src --explicit-package-bases

pre-commit:
	poetry run pre-commit run --all-files

check: format lint typecheck test

infra-up:
	docker compose up -d postgres redis

infra-down:
	docker compose stop postgres redis

infra-restart:
	docker compose restart postgres redis

infra-logs:
	docker compose logs -f postgres redis

compose-up:
	docker compose up -d --build

compose-down:
	docker compose down

compose-logs:
	docker compose logs -f

migration:
	docker compose exec app alembic upgrade head

psql:
	docker compose exec postgres psql "dbname=$(POSTGRES_DB) user=$(POSTGRES_USER) password=$(POSTGRES_PASSWORD)"

%:
	@:
