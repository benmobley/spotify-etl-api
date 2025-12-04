# 🎵 Spotify ETL API + Dashboard

Full-stack data pipeline: CSV (114K→89K tracks) → PostgreSQL → FastAPI → Streamlit dashboard. Fully dockerized - just run `./start-with-dashboard.sh`

**Tech:** Docker • Python 3.12 • FastAPI • PostgreSQL 16 • Streamlit • Plotly

## ⚡ Quick Start

**Prerequisites:** Docker Desktop

```bash
# Full stack (Dashboard + API)
./start-with-dashboard.sh

# Or step-by-step
make setup && make load-sample && make dashboard
```

**URLs:** Dashboard: http://localhost:8501 | API: http://localhost:8000/docs

## 📁 Custom CSV

```bash
make load-custom CSV_FILE=data/your-file.csv
```

**Required columns:** `track_name`, `artists`, `album_name`, `danceability`, `tempo`

## 🧭 API Endpoints

| Endpoint                     | Description                     |
| ---------------------------- | ------------------------------- |
| `GET /api/tracks`            | Search, filter, paginate tracks |
| `GET /api/stats/summary`     | Dataset statistics              |
| `GET /api/stats/top-artists` | Top artists by track count      |

**Filters:** `q` (search), `artist`, `min_danceability`, `tempo_min/max`, `sort`, `order`

**Example:** `curl "http://localhost:8000/api/tracks?q=love&min_danceability=0.8&limit=5"`

## 📈 Dashboard

Interactive Streamlit dashboard with:

- 📊 Analytics: Top artists charts, key metrics
- 🎵 Track Explorer: Search, filters, scatter plots
- 📈 Statistics: Distribution analysis

**Start:** `make dashboard` | **URL:** http://localhost:8501

## 🛠️ Commands

```bash
make setup           # Start all services + load data
make dashboard       # Launch dashboard
make test            # Run tests
make down            # Stop everything
```

## 🎯 Why This Project?

Demonstrates **production-ready data engineering patterns**:

- 🐳 **Containerization:** Zero-setup deployment with Docker
- 📊 **ETL Pipeline:** Real data processing (114K→89K records) with deduplication
- 🚀 **REST API:** Search, filtering, pagination, analytics endpoints
- 🗄️ **Database Design:** Proper constraints, migrations, indexing
- 🛠️ **DevOps:** Health checks, logging, error handling, testing
