.PHONY: lint format typecheck pre-commit


run:
	poetry run uvicorn src.main:app --port 8001 --reload

test:
	PYTHONPATH=. poetry run pytest -x tests -v --cov=src --cov-branch --cov-fail-under=75

lint:
	poetry run ruff check . --force-exclude

format:
	poetry run ruff format . --force-exclude
	poetry run ruff check --fix . --force-exclude

typecheck:
	poetry run mypy src --explicit-package-bases

pre-commit:
	poetry run pre-commit run --all-files

# Всё сразу
check: format lint typecheck test

restart:
	docker compose up -d --build

migration:
	docker compose exec app alembic upgrade head

psql:
	docker compose exec postgres psql "dbname=mydatabase user=myuser password=mypassword"

%:
	@:
