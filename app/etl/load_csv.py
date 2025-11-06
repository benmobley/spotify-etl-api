import sys
import pandas as pd
from app.db.session import engine, Base
from app.db.models import Track

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map common Spotify/Kaggle column names into our schema:
      track_name, artist, album, danceability, tempo
    """
    mapping_options = [
        # Typical Kaggle export
        {
            "track_name": "name",
            "artist": "artists",
            "album": "album_name",
            "danceability": "danceability",
            "tempo": "tempo",
        },
        # Already in our desired schema
        {
            "track_name": "track_name",
            "artist": "artist",
            "album": "album",
            "danceability": "danceability",
            "tempo": "tempo",
        },
    ]

    lower = {c.lower(): c for c in df.columns}  # case-insensitive
    for mapping in mapping_options:
        try:
            cols = {}
            for target, source in mapping.items():
                src = lower.get(source.lower())
                if src is None:
                    raise KeyError(source)
                cols[target] = df[src]
            out = pd.DataFrame(cols)

            # If artists looks like "['A', 'B']" strings, take first
            if out["artist"].dtype == object:
                out["artist"] = (
                    out["artist"]
                    .astype(str)
                    .str.strip("[]'\"")
                    .str.split(",")
                    .str[0]
                    .str.strip()
                )
            return out
        except KeyError:
            continue
    raise SystemExit(
        "Could not map CSV columns. Expected something like: "
        "name/artists/album_name/danceability/tempo"
    )

def main(path: str):
    Base.metadata.create_all(engine)
    df = pd.read_csv(path)
    df = _normalize_columns(df)
    df.to_sql(Track.__tablename__, con=engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into {Track.__tablename__}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m app.etl.load_csv <path_to_csv>")
    main(sys.argv[1])
