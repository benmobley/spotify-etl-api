# 🎵 Spotify ETL → PostgreSQL → FastAPI + Dashboard

Fully dockerized data pipeline that loads 89,348 unique Spotify tracks from CSV into PostgreSQL with FastAPI endpoints **and interactive Streamlit dashboard**. **No Python setup required** - everything runs in Docker!

## ✨ Features

- **🐳 Fully Dockerized:** Zero local setup - just Docker required
- **📊 ETL Pipeline:** Loads 114K→89K unique tracks with automatic deduplication
- **🚀 REST API:** FastAPI with search, filtering, pagination, and analytics
- **📈 Interactive Dashboard:** Streamlit dashboard with charts, filters, and data exploration
- **🗄️ PostgreSQL:** Proper constraints, migrations, and data integrity
- **📁 Custom CSV Support:** Easy loading of your own Spotify CSV files

## 🧱 Tech Stack

**Docker** • **Python 3.12** • **FastAPI** • **SQLAlchemy 2.x** • **Alembic** • **PostgreSQL 16** • **Streamlit** • **Plotly**

## ⚡ Quick Start

**Prerequisites:** Docker Desktop running

### Option 1: Full Stack with Dashboard (Recommended)

```bash
git clone <repo-url> && cd spotify-etl-api
./start-with-dashboard.sh
```

This will:

1. 🚀 Start all services (PostgreSQL + FastAPI + Dashboard)
2. 🔄 Run database migrations
3. 📊 Load 89K sample tracks
4. 📈 Launch interactive dashboard at http://localhost:8501
5. ✅ API ready at http://localhost:8000/docs

### Option 2: API Only

```bash
git clone <repo-url> && cd spotify-etl-api
./start.sh
```

### Option 3: Step-by-Step

```bash
# 1. Clone and start services
git clone <repo-url> && cd spotify-etl-api
make setup

# 2. Load sample data
make load-sample

# 3. Start dashboard (optional)
make dashboard

# 4. Visit services
open http://localhost:8501    # Dashboard
open http://localhost:8000/docs  # API docs
```

## 📁 Loading Custom CSV Files

```bash
# 1. Place your CSV file in the data/ directory
cp ~/Downloads/my-spotify-data.csv data/

# 2. Load it
make load-custom CSV_FILE=data/my-spotify-data.csv

# 3. Or with replace flag
docker compose exec app python -m app.etl.load_csv data/my-spotify-data.csv --replace
```

**CSV Requirements:** Must have columns: `track_name`, `artists`, `album_name`, `danceability`, `tempo`

## 🛠️ ETL Features

- **🔄 Auto-Deduplication:** Removes 24,651 duplicate records automatically
- **✅ Data Validation:** File validation, column checking, data type conversion
- **📋 Batch Processing:** Handles large files in 500-record chunks
- **🔍 Progress Tracking:** Detailed logs with statistics and progress updates
- **⚠️ Error Handling:** Comprehensive error reporting with specific exit codes

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

## 📈 Interactive Dashboard Features

**Dashboard URL:** http://localhost:8501

### 🎯 Key Features:

- **📊 Analytics Tab:** Dataset overview, top artists chart, key metrics
- **🎵 Track Explorer:** Advanced filtering with interactive scatter plots
- **📈 Statistics Tab:** Distribution charts and statistical analysis

### 🔍 Interactive Filters:

- **Search:** Find tracks by name, artist, or album
- **Artist Filter:** Focus on specific artists
- **Danceability Slider:** Filter by danceability score (0-1)
- **Tempo Range:** Filter by BPM range
- **Sorting:** Sort by danceability, tempo, or track name

### 📊 Visualizations:

- **Top Artists Bar Chart:** Most prolific artists by track count
- **Danceability vs Tempo Scatter Plot:** Interactive track exploration
- **Distribution Histograms:** Data distribution analysis
- **Real-time Metrics:** Live statistics from the API

### ⚡ Dashboard Commands:

```bash
make dashboard       # Start dashboard service
make dashboard-logs  # View dashboard logs
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

## 🛠️ Commands

```bash
# Main commands
make setup           # Start services + run migrations
make load-sample     # Load 89K sample tracks
make load-custom CSV_FILE=data/file.csv  # Load your CSV
make dashboard       # Start interactive dashboard
make logs            # View service logs
make down            # Stop all services

# Development
make shell           # Access app container
make test            # Run tests
make dashboard-logs  # Dashboard logs only
make migrate         # Run database migrations
make db-shell        # PostgreSQL shell
```

## 🧪 Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Get tracks
curl "http://localhost:8000/api/tracks?limit=3"

# Search
curl "http://localhost:8000/api/tracks?q=taylor%20swift&limit=2"

# Stats
curl http://localhost:8000/api/stats/summary
```

## 📁 Project Structure

```
├── app/
│   ├── api/          # FastAPI routes and schemas
│   ├── db/           # Database models and operations
│   └── etl/          # CSV loading pipeline
├── data/
│   └── raw/          # Sample CSV file (place custom files here)
├── scripts/          # Setup and utility scripts
├── docker-compose.yml
├── Dockerfile
├── start.sh          # One-command setup
└── Makefile         # All commands
```

## 🎯 Why This Project?

Demonstrates **production-ready data engineering patterns**:

- 🐳 **Containerization:** Zero-setup deployment with Docker
- 📊 **ETL Pipeline:** Real data processing (114K→89K records) with deduplication
- 🚀 **REST API:** Search, filtering, pagination, analytics endpoints
- 🗄️ **Database Design:** Proper constraints, migrations, indexing
- 🛠️ **DevOps:** Health checks, logging, error handling, testing

Perfect for **data engineering portfolios** and **production deployments**!
