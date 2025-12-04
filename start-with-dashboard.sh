#!/bin/bash

echo "🎵 Starting Spotify ETL API + Dashboard..."
echo "=========================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Start the services
echo "🐳 Starting services with Docker Compose..."
make setup

# Load sample data
echo "📊 Loading sample data (89K tracks)..."
make load-sample

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    sleep 2
    ATTEMPT=$((ATTEMPT + 1))
    echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS..."
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ API failed to start. Check logs with: make logs"
    exit 1
fi

# Start dashboard
echo "🚀 Starting Streamlit dashboard..."
make dashboard &

# Wait for dashboard to be ready
echo "⏳ Waiting for dashboard to be ready..."
sleep 10

# Final status
echo ""
echo "🎉 SUCCESS! All services are running:"
echo "=========================================="
echo "📊 Dashboard:  http://localhost:8501"
echo "🔗 API:        http://localhost:8000"
echo "📚 API Docs:   http://localhost:8000/docs"
echo ""
echo "🎯 Try the dashboard features:"
echo "   • Search and filter tracks"
echo "   • View top artists"
echo "   • Analyze track statistics"
echo "   • Interactive charts and data exploration"
echo ""
echo "🛠️  Useful commands:"
echo "   make logs           # View all service logs"
echo "   make dashboard-logs # View dashboard logs only"
echo "   make down          # Stop all services"
echo ""
echo "Press Ctrl+C to stop services or run 'make down' in another terminal"

# Keep the script running to show logs
wait