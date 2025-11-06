from typing import List, Optional
from pydantic import BaseModel, Field

class TrackOut(BaseModel):
    id: int
    track_name: str
    artist: str
    album: Optional[str] = None
    danceability: Optional[float] = Field(None, ge=0, le=1)
    tempo: Optional[float] = None

class TracksPage(BaseModel):
    items: List[TrackOut]
    total: int
    next_offset: Optional[int] = None

class TopArtist(BaseModel):
    artist: str
    count: int

class Summary(BaseModel):
    total_tracks: int
    avg_danceability: float
    avg_tempo: float
