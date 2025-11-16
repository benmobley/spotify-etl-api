import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import tracks

logger = logging.getLogger(__name__)

app = FastAPI(title="Spotify ETL API", version="1.0.0")

# CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def init_db():
    # Database schema is now managed by Alembic migrations
    # Run `python migrate.py` or `alembic upgrade head` before starting the API
    logger.info("API starting up - ensure database migrations are current")


app.include_router(tracks.router, prefix="/api")


@app.get("/health")
def health():
    return {"ok": True}
