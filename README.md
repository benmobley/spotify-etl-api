# Spotify ETL → Postgres → FastAPI

Complete data pipeline with CSV ETL, Postgres database, FastAPI endpoints, and production-ready features.

## ✨ Features

- **ETL Pipeline:** Validates & loads Spotify CSV data with error handling & logging
- **REST API:** FastAPI with filtering, pagination, and analytics endpoints
- **Database:** Alembic migrations, proper indexing, and data integrity
- **Production Ready:** Docker, CI/CD, structured logging, comprehensive error handling

## 🧱 Tech Stack

**Python 3.12** • **FastAPI** • **SQLAlchemy 2.x** • **Alembic** • **PostgreSQL 16** • **Docker**

## 🚀 Quick Start

### Local Setup

```bash
# 1. Setup
git clone <repo-url> && cd spotify-etl-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env

# 2. Start Postgres & create DB
brew services start postgresql@16
createdb spotify

# 3. Run migrations
python migrate.py

# 4. Load data
python -m app.etl.load_csv data/raw/spotify_kaggle.csv --replace

# 5. Start API
uvicorn app.api.main:app --reload
```

**API Docs:** http://localhost:8000/docs

### Docker Setup

```bash
# 1. Start services
docker compose up --build -d

# 2. Run migrations & load data
docker compose exec app python migrate.py
docker compose exec app python -m app.etl.load_csv data/raw/spotify_kaggle.csv --replace
```

**API Docs:** http://localhost:8000/docs  
**Stop:** `docker compose down -v`

## ⚙️ Configuration

**Environment Variables** (copy `.env.example` to `.env`):

```bash
# Local development
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/spotify

# Docker (use 'db' hostname)
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/spotify
```

## 🗄️ Database Migrations

**Alembic** manages database schema with version control and safe deployments.

```bash
# Run migrations
python migrate.py

# Check status
python migrate.py --check

# Create new migration
alembic revision --autogenerate -m "Description"

# Rollback
alembic downgrade -1
```

## 🛠️ ETL Features

**Error Handling:** File validation, data validation, database connectivity checks  
**Logging:** Structured logs with configurable levels (`--log-level DEBUG|INFO|WARNING|ERROR`)  
**Exit Codes:** Specific codes for different error types (file, data, database, etc.)  
**Batch Processing:** Chunks large datasets for memory efficiency

## 🧭 API Endpoints

**Base URL:** http://localhost:8000

| Endpoint                     | Description                           |
| ---------------------------- | ------------------------------------- |
| `GET /health`                | Health check                          |
| `GET /api/tracks`            | List tracks with filters & pagination |
| `GET /api/stats/summary`     | Overall statistics                    |
| `GET /api/stats/top-artists` | Most frequent artists                 |

**Query Parameters for `/api/tracks`:**

- `limit` (1-500), `offset` - Pagination
- `q` - Free text search (track/artist/album)
- `artist` - Filter by artist name
- `min_danceability` (0-1) - Filter by danceability
- `tempo_min`, `tempo_max` - Tempo range filter
- `sort` - Sort by `danceability|tempo|track_name`
- `order` - `asc|desc`

**Example Requests:**

```bash
# Health check
curl http://localhost:8000/health

# Get tracks
curl "http://localhost:8000/api/tracks?limit=5"

# Filter by artist
curl "http://localhost:8000/api/tracks?artist=Taylor%20Swift&limit=3"

# High danceability tracks
curl "http://localhost:8000/api/tracks?min_danceability=0.8&sort=danceability&order=desc"

# Get top artists
curl http://localhost:8000/api/stats/top-artists
```

## 🧪 Testing

```bash
# Run tests
pytest -q
# or
make test

# CI runs automatically on GitHub Actions
```

## 🛠️ Development

**Makefile shortcuts:**

```bash
make run          # Start API server
make test         # Run tests
make docker-up    # Start with Docker
make docker-down  # Stop Docker services
```

**ETL Options:**

```bash
# Basic load
python -m app.etl.load_csv data/raw/spotify_kaggle.csv

# Replace existing data
python -m app.etl.load_csv data/raw/spotify_kaggle.csv --replace

# Debug logging
python -m app.etl.load_csv data/raw/spotify_kaggle.csv --log-level DEBUG
```

## 📁 Project Structure

```
app/
├── api/          # FastAPI routes and schemas
├── db/           # Database models and operations
└── etl/          # CSV loading pipeline
data/raw/         # Input CSV files
tests/            # Test files
alembic/          # Database migration files
```

---

**🎯 This project demonstrates:** ETL pipelines, REST APIs, database management, error handling, testing, containerization, and CI/CD - all production-ready patterns for data engineering projects.
