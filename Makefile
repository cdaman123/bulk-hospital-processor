.PHONY: install test lint format run docker-up docker-down db-upgrade

install:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

lint:
	ruff check .
	mypy app/

format:
	black .

run:
	flask run

db-upgrade:
	flask db upgrade

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
