from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import tracks
from app.db.session import engine, Base

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
    Base.metadata.create_all(engine)


app.include_router(tracks.router, prefix="/api")


@app.get("/health")
def health():
    return {"ok": True}
