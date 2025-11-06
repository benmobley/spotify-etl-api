from typing import List, Dict, Optional
from sqlalchemy import select, func, desc, or_
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

def get_tracks(limit: int = 50, offset: int = 0, q: Optional[str] = None) -> List[Dict]:
    from sqlalchemy import select
    with SessionLocal() as s:
        stmt = select(Track).offset(offset).limit(limit)
        if q:
            pat = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Track.track_name.ilike(pat),
                    Track.artist.ilike(pat),
                    Track.album.ilike(pat),
                )
            )
        rows = s.execute(stmt).scalars().all()
        return [_track_to_dict(t) for t in rows]

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
