# Spotify ETL → Postgres → FastAPI

Working data pipeline that loads 89,348 unique Spotify tracks from CSV into PostgreSQL with FastAPI endpoints and production-ready features.

## ✨ Features

- **ETL Pipeline:** Loads 114K→89K unique tracks with deduplication, validation & comprehensive error handling
- **REST API:** FastAPI with search, filtering, pagination, and analytics endpoints  
- **Database:** PostgreSQL with proper constraints, migrations, and data integrity
- **Production Ready:** Docker, structured logging, batch processing, and robust error handling

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

# 2. Load sample data (89K unique tracks)
make load-sample
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

**Deduplication:** Removes 24,651 duplicate records based on (track_name, artist, album) constraint  
**Error Handling:** File validation, data validation, database connectivity checks  
**Logging:** Structured logs with progress tracking and detailed statistics  
**Batch Processing:** 500-record chunks with proper upsert handling for large datasets

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
make load-sample  # Load 89K unique tracks
make docker-up    # Start with Docker
make docker-down  # Stop Docker services
```

**ETL Options:**

```bash
# Load with deduplication (recommended)
make load-sample

# Direct load with replace flag
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

**🎯 This project demonstrates:** Complete ETL pipeline (114K→89K records), REST API with analytics, PostgreSQL with constraints, deduplication logic, error handling, Docker deployment - all production-ready data engineering patterns.
