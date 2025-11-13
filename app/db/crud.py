from typing import List, Dict, Optional
from sqlalchemy import select, func, desc, asc, or_
from .session import SessionLocal
from .models import Track


def _track_to_dict(t: Track) -> Dict:
    return {
        "id": t.id,
        "track_name": t.track_name,
        "artist": t.artist,
        "album": t.album,
        "danceability": t.danceability,
        "tempo": t.tempo,
    }


def get_tracks(
    limit: int = 50,
    offset: int = 0,
    q: Optional[str] = None,
    artist: Optional[str] = None,
    min_danceability: Optional[float] = None,
    tempo_min: Optional[float] = None,
    tempo_max: Optional[float] = None,
    sort: Optional[str] = None,  # "danceability" | "tempo" | "track_name"
    order: str = "desc",  # "asc" | "desc"
) -> Dict:
    with SessionLocal() as s:
        stmt = select(Track)

        # filters
        if q:
            pat = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Track.track_name.ilike(pat),
                    Track.artist.ilike(pat),
                    Track.album.ilike(pat),
                )
            )
        if artist:
            stmt = stmt.where(Track.artist.ilike(f"%{artist}%"))
        if min_danceability is not None:
            stmt = stmt.where(Track.danceability >= min_danceability)
        if tempo_min is not None:
            stmt = stmt.where(Track.tempo >= tempo_min)
        if tempo_max is not None:
            stmt = stmt.where(Track.tempo <= tempo_max)

        # total count with same filters
        total = s.scalar(select(func.count()).select_from(stmt.subquery())) or 0

        # sorting
        if sort in {"danceability", "tempo", "track_name"}:
            col = getattr(Track, sort)
            stmt = stmt.order_by(desc(col) if order == "desc" else asc(col))
        else:
            stmt = stmt.order_by(Track.id.asc())

        # page
        page = s.execute(stmt.offset(offset).limit(limit)).scalars().all()
        items = [_track_to_dict(t) for t in page]

        next_offset = offset + limit if (offset + limit) < total else None
        return {"items": items, "total": int(total), "next_offset": next_offset}


def get_top_artists(limit: int = 10) -> List[Dict]:
    with SessionLocal() as s:
        stmt = (
            select(Track.artist, func.count().label("count"))
            .group_by(Track.artist)
            .order_by(desc("count"))
            .limit(limit)
        )
        rows = s.execute(stmt).all()
        return [{"artist": a, "count": int(c)} for a, c in rows]


def get_summary() -> Dict:
    with SessionLocal() as s:
        total = s.scalar(select(func.count(Track.id)))
        avg_dance = s.scalar(select(func.avg(Track.danceability)))
        avg_tempo = s.scalar(select(func.avg(Track.tempo)))
        return {
            "total_tracks": int(total or 0),
            "avg_danceability": float(avg_dance or 0.0),
            "avg_tempo": float(avg_tempo or 0.0),
        }
