.PHONY: install test lint format typecheck run docker-up docker-down db-upgrade

install:
	poetry install

test:
	poetry run pytest tests/ -v

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

typecheck:
	poetry run mypy app/

run:
	poetry run flask run

db-upgrade:
	poetry run flask db upgrade

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
