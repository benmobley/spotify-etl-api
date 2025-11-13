from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.db.crud import get_tracks, get_top_artists, get_summary
from .schemas import TracksPage, TopArtist, Summary, ErrorModel

router = APIRouter()


@router.get("/tracks", response_model=TracksPage)
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
    if tempo_min is not None and tempo_max is not None and tempo_min > tempo_max:
        raise HTTPException(
            status_code=422, detail="tempo_min cannot be greater than tempo_max"
        )
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


@router.get(
    "/stats/top-artists",
    response_model=List[TopArtist],
    responses={
        404: {"model": ErrorModel},
        422: {"model": ErrorModel},
    },
)
def top_artists(limit: int = Query(10, ge=1, le=100)):
    return get_top_artists(limit=limit)


@router.get(
    "/stats/summary",
    response_model=Summary,
    responses={
        404: {"model": ErrorModel},
        422: {"model": ErrorModel},
    },
)
def summary():
    return get_summary()
