#!/usr/bin/env python3
"""
Database migration script using Alembic.
Run this before starting the application or loading data.
"""

import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run Alembic migrations to update database schema"""
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        
        logger.info("Running database migrations...")
        
        # Run alembic upgrade head
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], cwd=script_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Database migrations completed successfully")
            if result.stdout:
                logger.info(f"Migration output: {result.stdout.strip()}")
        else:
            logger.error(f"❌ Migration failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Error output: {result.stderr.strip()}")
            if result.stdout:
                logger.error(f"Standard output: {result.stdout.strip()}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Unexpected error running migrations: {e}")
        sys.exit(1)


def check_migration_status():
    """Check current migration status"""
    try:
        script_dir = Path(__file__).parent
        
        logger.info("Checking migration status...")
        
        result = subprocess.run([
            sys.executable, "-m", "alembic", "current"
        ], cwd=script_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                logger.info(f"Current migration: {result.stdout.strip()}")
            else:
                logger.info("No migrations have been run yet")
        else:
            logger.warning("Could not check migration status")
            
    except Exception as e:
        logger.warning(f"Could not check migration status: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration management")
    parser.add_argument("--check", action="store_true", help="Check current migration status")
    parser.add_argument("--migrate", action="store_true", help="Run migrations")
    
    args = parser.parse_args()
    
    if args.check:
        check_migration_status()
    elif args.migrate:
        run_migrations()
    else:
        # Default action: check status then migrate
        check_migration_status()
        run_migrations()