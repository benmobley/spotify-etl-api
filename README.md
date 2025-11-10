# Spotify ETL → Postgres → FastAPI (Portfolio Project)

A tiny but complete data project that proves end-to-end skills:

**CSV → clean/normalize → Postgres → API with filters/pagination → tests → Docker → CI**

---

## ✨ What this does

- **ETL:** Loads a Spotify-like CSV (e.g., Kaggle) into Postgres with light cleaning.
- **API:** Serves tracks and simple analytics via **FastAPI** (with typed responses).
- **Filters & Pagination:** Query by artist, danceability, tempo range; sort & paginate.
- **Tests:** `pytest` smoke tests.
- **Dev UX:** `.env.example`, Makefile shortcuts, CORS enabled, typed schemas, OpenAPI docs.
- **Ops:** Dockerfile + docker-compose to spin up Postgres + API. GitHub Actions CI.

---

## 🧱 Tech Stack

- **Python 3.12**, **FastAPI**, **Uvicorn**
- **SQLAlchemy 2.x**, **psycopg**
- **PostgreSQL 16**
- **pandas** (for CSV ETL)
- **pytest**, **GitHub Actions** (CI)
- **Docker** + **docker-compose**

---

## 📦 Repo Structure

.
├─ app/
│  ├─ api/
│  │  ├─ main.py        
│  │  ├─ tracks.py      
│  │  └─ schemas.py     
│  ├─ db/
│  │  ├─ crud.py        
│  │  ├─ models.py      
│  │  └─ session.py     
│  └─ etl/
│     └─ load_csv.py    
├─ data/
│  └─ raw/              
├─ tests/
│  └─ test_api.py       
├─ .env.example         
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ Makefile
└─ README.md

---

## 🚀 Quickstart (Local)

> Prereqs: Python 3.12, Postgres (e.g., Homebrew), `psql`, and optional pgAdmin.

1. **Clone & setup Python**

```bash
git clone <your-repo-url>
cd spotify-etl-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

brew services start postgresql@16

Create DB (only if it doesn't exist):

createdb spotify

3. (Optional) pgAdmin connection

• Host: localhost, Port: 5432, User: postgres, Password: postgres, DB: spotify

4. Load sample data or a Kaggle CSV

• Put your file at data/raw/spotify_kaggle.csv.
• The loader auto-maps common columns and drops bad rows with missing names.

Avoid duplicates if you re-run

psql -h localhost -U postgres -d spotify -c "TRUNCATE TABLE tracks;"

Load CSV → Postgres

python -m app.etl.load_csv data/raw/spotify_kaggle.csv

Expected output: multiple "Inserted rows ..." lines + final "Loaded N total rows"

5. Run the API
   uvicorn app.api.main:app --reload

or: make run

6. Open docs

• Swagger UI: http://127.0.0.1:8000/docs
• Health: http://127.0.0.1:8000/health

## 🐳 Quickstart (Docker Compose)

Spins up Postgres + API in one command.

docker compose up --build -d

App at http://127.0.0.1:8000/docs

Load data (pick one):
• From inside the app container (CSV is copied with the repo):
docker compose exec app python -m app.etl.load_csv data/raw/spotify_kaggle.csv
• From your host (connects to the mapped DB port):
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/spotify \
python -m app.etl.load_csv data/raw/spotify_kaggle.csv

Stop & clean:
docker compose down -v

## 🔌 Environment Variables

Create your .env from .env.example:

Local dev (host Postgres)

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/spotify

Docker compose (uncomment if you run app inside compose)

DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/spotify

## 🧪 Tests & CI

Run tests locally:
make test

or

pytest -q

CI (GitHub Actions):
• .github/workflows/ci.yml boots Postgres service and runs pytest on push/PR.

If you see ModuleNotFoundError: app, add a pytest.ini with:
[pytest]
pythonpath = .

## 🧭 API Endpoints (FastAPI)

Base URL: http://127.0.0.1:8000
• GET /health → {"ok": true}

• GET /api/stats/summary → overall stats
Response:
{ "total_tracks": 12345, "avg_danceability": 0.62, "avg_tempo": 118.3 }

• GET /api/stats/top-artists?limit=10 → most frequent artists
Response: [{ "artist": "Artist", "count": 42 }, ...]

• GET /api/tracks → tracks with pagination and filters.
Query params:
• limit (1–500, default 50)
• offset (default 0)
• q (free-text: track_name/artist/album, substring, case-insensitive)
• artist (substring match on artist)
• min_danceability (0–1)
• tempo_min, tempo_max
• sort (danceability|tempo|track_name)
• order (asc|desc, default desc)
Response:
{
"items": [
{
"id": 123,
"track_name": "Song",
"artist": "Artist",
"album": "Album",
"danceability": 0.73,
"tempo": 120.01
}
],
"total": 421,
"next_offset": 50
}

Curl Examples:

Health

curl "http://127.0.0.1:8000/health"

Summary

curl "http://127.0.0.1:8000/api/stats/summary"

Top artists

curl "http://127.0.0.1:8000/api/stats/top-artists?limit=5"

First 5 tracks

curl "http://127.0.0.1:8000/api/tracks?limit=5"

Free-text search

curl "http://127.0.0.1:8000/api/tracks?limit=5&q=tame"

Artist substring

curl "http://127.0.0.1:8000/api/tracks?limit=5&artist=Quantic"

Highly danceable, sorted

curl "http://127.0.0.1:8000/api/tracks?limit=5&min_danceability=0.8&sort=danceability&order=desc"

Tempo range, sorted asc

curl "http://127.0.0.1:8000/api/tracks?limit=5&tempo_min=60&tempo_max=90&sort=tempo&order=asc"

Next page (use "next_offset" from previous response)

curl "http://127.0.0.1:8000/api/tracks?limit=5&offset=5"

## 🧼 CSV Loader Details

Path: app/etl/load_csv.py
• Accepts common Spotify/Kaggle headers, e.g.:
track_name, artists, album_name, danceability, tempo
(Also handles name → track_name, drops unnamed index columns.)
• Cleans:
• artists: takes the first artist when multiple; converts ; to ,
• Coerces danceability and tempo to numeric
• Drops rows with empty track_name or artist (DB has NOT NULL on these)
• Chunked inserts: avoids giant SQL statements (500 row chunks)
• Re-run safe if you TRUNCATE TABLE tracks; first

Load data:
psql -h localhost -U postgres -d spotify -c "TRUNCATE TABLE tracks;"
python -m app.etl.load_csv data/raw/spotify_kaggle.csv

## ⚡ Performance (Optional)

Create indexes for faster queries on large datasets:
psql -h localhost -U postgres -d spotify -c "CREATE INDEX IF NOT EXISTS tracks_artist_idx ON tracks(artist);"
psql -h localhost -U postgres -d spotify -c "CREATE INDEX IF NOT EXISTS tracks_name_idx ON tracks(track_name);"

## 🛠 Makefile Shortcuts

make run # uvicorn app.api.main:app --reload
make test # pytest -q
make docker-up # docker compose up --build -d
make docker-down # docker compose down -v
make load-sample # load small sample CSV (if present)

## 🧩 Troubleshooting

• FATAL: role "postgres" does not exist
Create the role or use existing credentials; update DATABASE_URL accordingly.
• Connection refused / port in use
Ensure Postgres is running on localhost:5432 (or match your .env).
• Long SQL dump / IntegrityError
Caused by giant batch or null names. Fixed by chunked inserts + dropping rows with empty track_name/artist.
• ModuleNotFoundError: app in tests
Ensure pytest.ini has:
[pytest]
pythonpath = .

    •	Makefile “missing separator”

Make requires TABs, not spaces, before each command.
• VS Code yellow squiggles on imports
Select interpreter: Cmd+Shift+P → Python: Select Interpreter → ./.venv/bin/python.

⸻

## Screenshots

![FastAPI docs](docs/api-docs.png)

![Tracks endpoint example](docs/tracks-endpoint.png)

![Tracks row count](docs/tracks-count.png)


## 🗺️ Future Enhancements

• artist_exact=true or word-boundary filter
• More stats endpoints (tempo histograms, per-genre summaries)
• Auth (API key / OAuth) and rate limiting
• Frontend dashboard (React) consuming the API
• Alembic migrations
