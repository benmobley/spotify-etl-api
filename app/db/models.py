from sqlalchemy import Column, Integer, Float, String, Boolean, UniqueConstraint
from .session import Base


class Track(Base):
    __tablename__ = "tracks"
    __table_args__ = (UniqueConstraint('track_name', 'artist', 'album', name='tracks_unique_constraint'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    track_name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=True)
    popularity = Column(Integer)
    duration_ms = Column(Integer)
    explicit = Column(Boolean)
    danceability = Column(Float)
    energy = Column(Float)
    key = Column(Integer)
    loudness = Column(Float)
    mode = Column(Integer)
    speechiness = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    liveness = Column(Float)
    valence = Column(Float)
    tempo = Column(Float)
    time_signature = Column(Integer)
    track_genre = Column(String)
