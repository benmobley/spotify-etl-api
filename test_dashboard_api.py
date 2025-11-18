#!/usr/bin/env python3
"""
Demo script to test the Spotify Dashboard API connectivity
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Test all the API endpoints that the dashboard uses"""
    
    print("🎵 Testing Spotify ETL API Endpoints")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health Check: PASSED")
        else:
            print("❌ Health Check: FAILED")
            return False
    except Exception as e:
        print(f"❌ Health Check: FAILED - {e}")
        return False
    
    # Test summary endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats/summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats Summary: PASSED")
            print(f"   📊 Total Tracks: {data['total_tracks']:,}")
            print(f"   💃 Avg Danceability: {data['avg_danceability']:.3f}")
            print(f"   🎵 Avg Tempo: {data['avg_tempo']:.1f} BPM")
        else:
            print("❌ Stats Summary: FAILED")
    except Exception as e:
        print(f"❌ Stats Summary: FAILED - {e}")
    
    # Test top artists endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/api/stats/top-artists?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Top Artists: PASSED")
            print("   🎤 Top 5 Artists:")
            for i, artist in enumerate(data[:5], 1):
                print(f"   {i}. {artist['artist']} ({artist['count']} tracks)")
        else:
            print("❌ Top Artists: FAILED")
    except Exception as e:
        print(f"❌ Top Artists: FAILED - {e}")
    
    # Test tracks endpoint with various filters
    try:
        response = requests.get(f"{API_BASE_URL}/api/tracks?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tracks Endpoint: PASSED")
            print(f"   📋 Sample: {len(data['items'])} tracks shown, {data['total']:,} total")
            if data['items']:
                track = data['items'][0]
                print(f"   🎶 First Track: '{track['track_name']}' by {track['artist']}")
        else:
            print("❌ Tracks Endpoint: FAILED")
    except Exception as e:
        print(f"❌ Tracks Endpoint: FAILED - {e}")
    
    # Test search functionality
    try:
        response = requests.get(f"{API_BASE_URL}/api/tracks?q=love&limit=3", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search Functionality: PASSED")
            print(f"   🔍 'love' search: {data['total']:,} matches")
        else:
            print("❌ Search Functionality: FAILED")
    except Exception as e:
        print(f"❌ Search Functionality: FAILED - {e}")
    
    # Test filtering by danceability
    try:
        response = requests.get(f"{API_BASE_URL}/api/tracks?min_danceability=0.8&limit=3", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Danceability Filter: PASSED")
            print(f"   💃 High danceability (>0.8): {data['total']:,} tracks")
        else:
            print("❌ Danceability Filter: FAILED")
    except Exception as e:
        print(f"❌ Danceability Filter: FAILED - {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing complete!")
    print("📊 Dashboard should be available at: http://localhost:8501")
    print("🔗 API docs available at: http://localhost:8000/docs")
    return True

if __name__ == "__main__":
    test_api_endpoints()