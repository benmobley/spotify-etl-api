# Docker-first commands
up:
	docker compose up --build -d

setup: up
	@./scripts/setup.sh

down:
	docker compose down -v

logs:
	docker compose logs -f

# Data loading commands
load-sample:
	docker compose exec app python -m app.etl.load_csv data/raw/spotify_kaggle.csv

load-csv:
	docker compose exec app python -m app.etl.load_csv data/raw/spotify_kaggle.csv --replace

load-custom:
	@echo "Usage: make load-custom CSV_FILE=path/to/your/file.csv"
	@if [ -z "$(CSV_FILE)" ]; then \
		echo "Error: Please specify CSV_FILE=path/to/your/file.csv"; \
		exit 1; \
	fi
	docker compose exec app python -m app.etl.load_csv $(CSV_FILE)

# Database commands
migrate:
	docker compose exec app python migrate.py

db-shell:
	docker compose exec db psql -U postgres -d spotify

# Development commands
shell:
	docker compose exec app bash

test:
	docker compose exec app pytest -q

format:
	docker compose exec app black app tests

# Dashboard commands  
dashboard:
	@echo "🚀 Starting dashboard..."
	@echo "📊 Dashboard will be available at: http://localhost:8501"
	@echo "🎵 Make sure API is running first with: make setup"
	docker compose up dashboard --build -d

dashboard-logs:
	docker compose logs -f dashboard

# Legacy aliases (will be removed)
docker-up: up
docker-down: down
