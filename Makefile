run:
	uvicorn app.api.main:app --reload

test:
	pytest -q

load-sample:
	python -m app.etl.load_csv data/raw/spotify_sample.csv

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down -v
