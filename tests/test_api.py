import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.db.session import engine, SessionLocal
from app.db.models import Base, Track


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """
    Ensure the tracks table exists and has a few rows for tests.

    In CI, Postgres starts empty, so we can't rely on a pre-loaded DB.
    """
    # create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # seed a tiny dataset once
    with SessionLocal() as session:
        if not session.query(Track).first():
            session.add_all(
                [
                    Track(
                        track_name="Test Track 1",
                        artist="Artist A",
                        album="Album X",
                        danceability=0.9,
                        tempo=120.0,
                    ),
                    Track(
                        track_name="Chill Song",
                        artist="Quantic",
                        album="Album Y",
                        danceability=0.6,
                        tempo=85.0,
                    ),
                    Track(
                        track_name="Low Dance",
                        artist="Artist B",
                        album="Album Z",
                        danceability=0.3,
                        tempo=100.0,
                    ),
                ]
            )
            session.commit()

    yield


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_tracks_list_paginated():
    r = client.get("/api/tracks?limit=2")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "items" in data and isinstance(data["items"], list)
    assert "total" in data and isinstance(data["total"], int)
    assert len(data["items"]) <= 2


def test_tracks_filter_and_sort():
    r = client.get(
        "/api/tracks?min_danceability=0.1&tempo_min=40&tempo_max=300&sort=tempo&order=asc&limit=3"
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["items"], list)
    assert len(data["items"]) <= 3


def test_tracks_filter_min_danceability():
    threshold = 0.8
    r = client.get(f"/api/tracks?min_danceability={threshold}&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    for item in data["items"]:
        assert "danceability" in item
        assert item["danceability"] is None or item["danceability"] >= threshold


def test_top_artists():
    r = client.get("/api/stats/top-artists?limit=3")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert all("artist" in x and "count" in x for x in data)


def test_summary():
    r = client.get("/api/stats/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_tracks" in data
    assert "avg_danceability" in data
    assert "avg_tempo" in data
