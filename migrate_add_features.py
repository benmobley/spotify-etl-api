#!/usr/bin/env python3
"""
Migration script to add all Spotify audio features to the tracks table.
Run this once to update the database schema.
"""

from sqlalchemy import text
from app.db.session import engine

def migrate():
    print("🔄 Starting database migration: Adding audio features...")
    
    migrations = [
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS popularity INTEGER;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS duration_ms INTEGER;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS explicit BOOLEAN;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS energy FLOAT;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS key INTEGER;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS loudness FLOAT;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS mode INTEGER;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS speechiness FLOAT;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS acousticness FLOAT;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS instrumentalness FLOAT;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS liveness FLOAT;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS valence FLOAT;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS time_signature INTEGER;",
        "ALTER TABLE tracks ADD COLUMN IF NOT EXISTS track_genre VARCHAR;",
    ]
    
    try:
        with engine.begin() as conn:
            for sql in migrations:
                print(f"  Executing: {sql}")
                conn.execute(text(sql))
        
        print("✅ Migration completed successfully!")
        print("💡 Now run: make load-sample  (to reload data with all features)")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate()
