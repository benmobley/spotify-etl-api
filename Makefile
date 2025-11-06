run:
	uvicorn app.api.main:app --reload

test:
	pytest -q

load-sample:
	python -m app.etl.load_csv data/raw/spotify_sample.csv
