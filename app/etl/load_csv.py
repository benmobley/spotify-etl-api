import sys
import argparse
import logging
import os
from pathlib import Path
from typing import Optional
import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.db.session import engine, Base
from app.db.models import Track


class ETLError(Exception):
    """Base exception for ETL operations"""
    pass


class FileValidationError(ETLError):
    """Raised when CSV file validation fails"""
    pass


class DataValidationError(ETLError):
    """Raised when data validation fails"""
    pass


class DatabaseError(ETLError):
    """Raised when database operations fail"""
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


TABLE_NAME = Track.__tablename__


def _read_csv(path: str) -> pd.DataFrame:
    """Read and validate CSV file with proper error handling"""
    try:
        # Validate file exists and is readable
        csv_path = Path(path)
        if not csv_path.exists():
            raise FileValidationError(f"CSV file not found: {path}")
        
        if not csv_path.is_file():
            raise FileValidationError(f"Path is not a file: {path}")
        
        if csv_path.stat().st_size == 0:
            raise FileValidationError(f"CSV file is empty: {path}")
        
        logger.info(f"Reading CSV file: {path} ({csv_path.stat().st_size} bytes)")
        
        # Read CSV with error handling
        df = pd.read_csv(path)
        
        if df.empty:
            raise DataValidationError("CSV file contains no data rows")
        
        logger.info(f"Successfully read {len(df)} rows from CSV")
        
        # Clean up unnamed index columns
        if df.columns[0].lower().startswith("unnamed"):
            df = df.drop(columns=[df.columns[0]], errors="ignore")
            logger.info("Removed unnamed index column")
        
        return df
        
    except pd.errors.EmptyDataError:
        raise DataValidationError(f"CSV file is empty or has no valid data: {path}")
    except pd.errors.ParserError as e:
        raise DataValidationError(f"Failed to parse CSV file: {e}")
    except FileNotFoundError:
        raise FileValidationError(f"CSV file not found: {path}")
    except PermissionError:
        raise FileValidationError(f"Permission denied reading CSV file: {path}")
    except Exception as e:
        raise ETLError(f"Unexpected error reading CSV file: {e}")


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and validate DataFrame with comprehensive error handling"""
    try:
        logger.info(f"Starting normalization of {len(df)} rows")
        
        # Validate required columns exist
        cols = {c.lower(): c for c in df.columns}
        required_cols = ["track_name", "artists", "album_name"]
        missing_cols = [col for col in required_cols if col not in cols]
        
        if missing_cols:
            available_cols = list(cols.keys())
            raise DataValidationError(
                f"Missing required columns: {missing_cols}. "
                f"Available columns: {available_cols}"
            )
        
        # Create normalized DataFrame with error handling
        out = pd.DataFrame(
            {
                "track_name": df[cols.get("track_name")],
                "artist": df[cols.get("artists")],
                "album": df[cols.get("album_name")],
                "popularity": pd.to_numeric(df[cols.get("popularity")], errors="coerce"),
                "duration_ms": pd.to_numeric(df[cols.get("duration_ms")], errors="coerce"),
                "explicit": df[cols.get("explicit")].astype(bool) if "explicit" in cols else False,
                "danceability": pd.to_numeric(df[cols.get("danceability")], errors="coerce"),
                "energy": pd.to_numeric(df[cols.get("energy")], errors="coerce"),
                "key": pd.to_numeric(df[cols.get("key")], errors="coerce"),
                "loudness": pd.to_numeric(df[cols.get("loudness")], errors="coerce"),
                "mode": pd.to_numeric(df[cols.get("mode")], errors="coerce"),
                "speechiness": pd.to_numeric(df[cols.get("speechiness")], errors="coerce"),
                "acousticness": pd.to_numeric(df[cols.get("acousticness")], errors="coerce"),
                "instrumentalness": pd.to_numeric(df[cols.get("instrumentalness")], errors="coerce"),
                "liveness": pd.to_numeric(df[cols.get("liveness")], errors="coerce"),
                "valence": pd.to_numeric(df[cols.get("valence")], errors="coerce"),
                "tempo": pd.to_numeric(df[cols.get("tempo")], errors="coerce"),
                "time_signature": pd.to_numeric(df[cols.get("time_signature")], errors="coerce"),
                "track_genre": df[cols.get("track_genre")].astype(str) if "track_genre" in cols else None,
            }
        )
        
    except KeyError as e:
        raise DataValidationError(f"Column mapping error: {e}")
    except Exception as e:
        raise ETLError(f"Unexpected error during normalization: {e}")

    out["track_name"] = out["track_name"].astype(str).str.strip()
    out["artist"] = (
        out["artist"]
        .astype(str)
        .str.strip("[]'\"")
        .str.replace(";", ",", regex=False)
        .str.split(",")
        .str[0]
        .str.strip()
    )
    out["album"] = out["album"].astype(str).str.strip()

    before = len(out)
    out = out[
        (out["track_name"].str.len() > 0)
        & (out["track_name"].str.lower() != "nan")
        & (out["artist"].str.len() > 0)
        & (out["artist"].str.lower() != "nan")
    ].copy()
    dropped = before - len(out)
    if dropped:
        logger.info(f"Dropped {dropped} rows with missing track_name/artist")

    # Remove duplicates based on unique constraint columns
    before_dedup = len(out)
    out = out.drop_duplicates(subset=['track_name', 'artist', 'album'], keep='first')
    dedup_dropped = before_dedup - len(out)
    if dedup_dropped:
        logger.info(f"Dropped {dedup_dropped} duplicate records based on (track_name, artist, album)")

    return out


def load_csv(path: str, replace: bool = False) -> None:
    """Load CSV data into database with comprehensive error handling"""
    try:
        logger.info(f"Starting ETL process for: {path}")
        
        # Test database connection
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection verified")
        except SQLAlchemyError as e:
            raise DatabaseError(f"Cannot connect to database: {e}")
        
        # Note: Database schema should be managed with Alembic migrations
        # Run: `alembic upgrade head` to ensure schema is up to date
        logger.info("Database schema should be managed with 'alembic upgrade head'")

        # Process data
        df = _normalize(_read_csv(path))
        step = 500
        total = len(df)
        
        if total == 0:
            raise DataValidationError("No valid data to load after normalization")
        
        logger.info(f"Starting database load of {total} rows in batches of {step}")

        try:
            with engine.begin() as conn:
                if replace:
                    conn.execute(text(f"TRUNCATE TABLE {TABLE_NAME} RESTART IDENTITY;"))
                    logger.info(f"Truncated table {TABLE_NAME}")

                processed = 0
                for start in range(0, total, step):
                    try:
                        chunk = df.iloc[start : start + step].copy()
                        _upsert_chunk(conn, chunk)
                        processed += len(chunk)
                        logger.info(f"Upserted rows {start}-{min(start + step, total)}")
                    except Exception as e:
                        logger.error(f"Failed to upsert chunk {start}-{min(start + step, total)}: {e}")
                        raise DatabaseError(f"Database upsert failed at row {start}: {e}")

            logger.info(f"✅ Successfully upserted {processed} rows into {TABLE_NAME}")
            
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database transaction failed: {e}")
            
    except (FileValidationError, DataValidationError, DatabaseError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ETL process: {e}")
        raise ETLError(f"ETL process failed: {e}")

def _upsert_chunk(conn, df_chunk: pd.DataFrame) -> None:
    """Upsert a chunk of data with error handling"""
    if df_chunk.empty:
        return

    try:
        table = Track.__table__
        records = df_chunk.to_dict(orient="records")
        
        # Validate records before inserting
        if not records:
            logger.warning("No records to upsert in chunk")
            return

        stmt = insert(table).values(records)

        update_cols = {
            c.name: getattr(stmt.excluded, c.name)
            for c in table.c
            if c.name != "id"
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=["track_name", "artist", "album"],
            set_=update_cols,
        )

        conn.execute(stmt)
        
    except IntegrityError as e:
        raise DatabaseError(f"Data integrity violation during upsert: {e}")
    except SQLAlchemyError as e:
        raise DatabaseError(f"Database error during upsert: {e}")
    except Exception as e:
        raise ETLError(f"Unexpected error during upsert: {e}")

def main(argv: list[str]) -> None:
    """Main entry point with comprehensive error handling"""
    parser = argparse.ArgumentParser(
        description="Load a Spotify CSV into the tracks table."
    )
    parser.add_argument(
        "csv_path",
        help="Path to the Spotify CSV file",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Truncate the tracks table before loading",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level",
    )

    try:
        args = parser.parse_args(argv)
        
        # Set log level
        logger.setLevel(getattr(logging, args.log_level))
        
        logger.info(f"Starting ETL with arguments: csv_path={args.csv_path}, replace={args.replace}")
        
        load_csv(args.csv_path, replace=args.replace)
        
        logger.info("ETL process completed successfully")
        
    except FileValidationError as e:
        logger.error(f"File validation error: {e}")
        sys.exit(1)
    except DataValidationError as e:
        logger.error(f"Data validation error: {e}")
        sys.exit(2)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        sys.exit(3)
    except ETLError as e:
        logger.error(f"ETL error: {e}")
        sys.exit(4)
    except KeyboardInterrupt:
        logger.info("ETL process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(5)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m app.etl.load_csv <csv> [--replace]")
    main(sys.argv[1:])
