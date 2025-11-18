#!/bin/bash
set -e

echo "🚀 Setting up Spotify ETL API..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
until docker compose exec db pg_isready -U postgres > /dev/null 2>&1; do
    sleep 1
done

echo "📊 Running database migrations..."
docker compose exec app python migrate.py

echo "✅ Setup complete! The API is ready at http://localhost:8000"
echo ""
echo "Next steps:"
echo "  • Load sample data: make load-sample"
echo "  • View API docs: http://localhost:8000/docs"
echo "  • Load custom CSV: make load-custom CSV_FILE=data/your-file.csv"