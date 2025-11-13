import sys
import argparse
import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.db.session import engine, Base
from app.db.models import Track


TABLE_NAME = Track.__tablename__


def _read_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.columns[0].lower().startswith("unnamed"):
        df = df.drop(columns=[df.columns[0]], errors="ignore")
    return df


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    out = pd.DataFrame(
        {
            "track_name": df[cols.get("track_name")],
            "artist": df[cols.get("artists")],
            "album": df[cols.get("album_name")],
            "danceability": pd.to_numeric(
                df[cols.get("danceability")], errors="coerce"
            ),
            "tempo": pd.to_numeric(df[cols.get("tempo")], errors="coerce"),
        }
    )

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
        print(f"Dropped {dropped} rows with missing track_name/artist")

    return out


def load_csv(path: str, replace: bool = False) -> None:
    Base.metadata.create_all(engine)

    df = _normalize(_read_csv(path))
    step = 500
    total = len(df)

    with engine.begin() as conn:
        if replace:
            conn.execute(text(f"TRUNCATE TABLE {TABLE_NAME} RESTART IDENTITY;"))
            print(f"Truncated table {TABLE_NAME}")

        for start in range(0, total, step):
            chunk = df.iloc[start : start + step].copy()
            _upsert_chunk(conn, chunk)
            print(f"Upserted rows {start}-{min(start + step, total)}")

    print(f"✅ Upserted {total} rows into {TABLE_NAME}")

def _upsert_chunk(conn, df_chunk: pd.DataFrame) -> None:
    if df_chunk.empty:
        return

    table = Track.__table__
    records = df_chunk.to_dict(orient="records")

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

def main(argv: list[str]) -> None:
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

    args = parser.parse_args(argv)
    load_csv(args.csv_path, replace=args.replace)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m app.etl.load_csv <csv> [--replace]")
    main(sys.argv[1:])
