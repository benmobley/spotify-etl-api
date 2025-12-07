from typing import List, Optional
from pydantic import BaseModel, Field

class ErrorModel(BaseModel):
    detail: str

class TrackOut(BaseModel):
    id: int
    track_name: str
    artist: str
    album: Optional[str] = None
    popularity: Optional[int] = Field(None, ge=0, le=100)
    duration_ms: Optional[int] = None
    explicit: Optional[bool] = None
    danceability: Optional[float] = Field(None, ge=0, le=1)
    energy: Optional[float] = Field(None, ge=0, le=1)
    key: Optional[int] = Field(None, ge=0, le=11)
    loudness: Optional[float] = None
    mode: Optional[int] = Field(None, ge=0, le=1)
    speechiness: Optional[float] = Field(None, ge=0, le=1)
    acousticness: Optional[float] = Field(None, ge=0, le=1)
    instrumentalness: Optional[float] = Field(None, ge=0, le=1)
    liveness: Optional[float] = Field(None, ge=0, le=1)
    valence: Optional[float] = Field(None, ge=0, le=1)
    tempo: Optional[float] = None
    time_signature: Optional[int] = None
    track_genre: Optional[str] = None


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
    avg_energy: float
    avg_valence: float
    avg_tempo: float
    avg_loudness: float
    avg_acousticness: float
    avg_instrumentalness: float
    avg_speechiness: float
    avg_liveness: float
    avg_popularity: float
    avg_duration_ms: float
