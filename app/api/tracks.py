from fastapi import APIRouter, Query
from typing import Optional
from app.db.crud import get_tracks, get_top_artists, get_summary

router = APIRouter()

@router.get("/tracks")
def list_tracks(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    q: Optional[str] = None,
    artist: Optional[str] = None,
    min_danceability: Optional[float] = Query(None, ge=0.0, le=1.0),
    tempo_min: Optional[float] = None,
    tempo_max: Optional[float] = None,
    sort: Optional[str] = Query(None, pattern="^(danceability|tempo|track_name)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
):
    return get_tracks(
        limit=limit,
        offset=offset,
        q=q,
        artist=artist,
        min_danceability=min_danceability,
        tempo_min=tempo_min,
        tempo_max=tempo_max,
        sort=sort,
        order=order,
    )

@router.get("/stats/top-artists")
def top_artists(limit: int = Query(10, ge=1, le=100)):
    return get_top_artists(limit=limit)

@router.get("/stats/summary")
def summary():
    return get_summary()
