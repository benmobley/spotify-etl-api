#!/bin/bash
set -e

echo "🎵 Spotify ETL API - Quick Start"
echo "================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "🚀 Starting services..."
make setup

echo ""
echo "📊 Loading sample data (89K tracks)..."
make load-sample

echo ""
echo "🎉 All done! Your Spotify ETL API is ready!"
echo ""
echo "🌐 API Documentation: http://localhost:8000/docs"
echo "💻 API Base URL: http://localhost:8000/api"
echo ""
echo "📋 Quick test:"
echo "   curl http://localhost:8000/health"
echo "   curl 'http://localhost:8000/api/tracks?limit=3'"
echo ""
echo "🛠️  Useful commands:"
echo "   make logs        # View logs"
echo "   make down        # Stop services"
echo "   make load-custom CSV_FILE=data/your-file.csv  # Load custom data"