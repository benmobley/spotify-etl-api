from fastapi.testclient import TestClient
from app.api.main import app

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
    r = client.get("/api/tracks?min_danceability=0.1&tempo_min=40&tempo_max=300&sort=tempo&order=asc&limit=3")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["items"], list)
    assert len(data["items"]) <= 3

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
