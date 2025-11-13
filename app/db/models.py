from sqlalchemy import Column, Integer, Float, String
from .session import Base


class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    track_name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=True)
    danceability = Column(Float)
    tempo = Column(Float)
