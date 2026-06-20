.PHONY: install test lint format run docker-up docker-down db-upgrade

install:
	poetry install

test:
	poetry run pytest tests/ -v

lint:
	poetry run ruff check .
	poetry run mypy app/

format:
	poetry run ruff format .

run:
	poetry run flask run

db-upgrade:
	poetry run flask db upgrade

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
