"""Download COVID dataset and load it into SQLite for the database agent course."""

from pathlib import Path
import urllib.request

import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"
CSV_URL = "https://covidtracking.com/data/download/all-states-history.csv"
CSV_PATH = DATA_DIR / "all-states-history.csv"
DB_PATH = DB_DIR / "test.db"


def download_csv() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if CSV_PATH.exists():
        print(f"Dataset already exists at {CSV_PATH}")
        return CSV_PATH

    print(f"Downloading dataset from {CSV_URL} ...")
    request = urllib.request.Request(
        CSV_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; database-agent-course/1.0)"},
    )
    try:
        with urllib.request.urlopen(request) as response, open(CSV_PATH, "wb") as out_file:
            out_file.write(response.read())
        print(f"Saved to {CSV_PATH}")
    except urllib.error.URLError as exc:
        raise FileNotFoundError(
            f"Could not download dataset ({exc}). "
            f"Place all-states-history.csv manually at {CSV_PATH}"
        ) from exc
    return CSV_PATH


def load_to_sqlite(csv_path: Path = CSV_PATH) -> Path:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path).fillna(value=0)
    engine = create_engine(f"sqlite:///{DB_PATH}")
    df.to_sql("all_states_history", con=engine, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into {DB_PATH} (table: all_states_history)")
    return DB_PATH


def main() -> None:
    csv_path = download_csv()
    load_to_sqlite(csv_path)


if __name__ == "__main__":
    main()
