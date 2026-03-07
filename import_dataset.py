"""
import_dataset.py — downloads the perfume dataset and imports it into SQLite.

Run once before starting the bot:
    python import_dataset.py

Dataset source: github.com/rdemarqui/perfume_recommender
File: database/perfume_database_cleaned.xlsx
Columns: brand | perfume | notes  (notes = comma-separated string)
"""

import os
import sqlite3
import requests
import pandas as pd
from db import init_catalog_tables, is_catalog_empty

DB_PATH = "perfumes.db"
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "perfume_database_cleaned.xlsx")
DOWNLOAD_URL = (
    "https://github.com/rdemarqui/perfume_recommender"
    "/raw/main/database/perfume_database_cleaned.xlsx"
)


def download_dataset():
    if os.path.exists(DATA_FILE):
        print(f"Dataset already exists at {DATA_FILE}, skipping download.")
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Downloading dataset from GitHub...")
    resp = requests.get(DOWNLOAD_URL, stream=True)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0

    with open(DATA_FILE, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"\r  {pct:.1f}%", end="", flush=True)

    print(f"\nSaved to {DATA_FILE}")


def import_data():
    print("Reading Excel file...")
    df = pd.read_excel(DATA_FILE, usecols=["brand", "perfume", "notes"])
    df = df.dropna(subset=["brand", "perfume", "notes"])
    df = df.astype(str).apply(lambda col: col.str.strip())
    print(f"Loaded {len(df)} perfumes.")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Cache brand name -> id to avoid redundant SELECTs
    brand_cache: dict[str, int] = {}

    def get_brand_id(brand_name: str) -> int:
        if brand_name in brand_cache:
            return brand_cache[brand_name]
        c.execute("INSERT OR IGNORE INTO catalog_brands (name) VALUES (?)", (brand_name,))
        c.execute("SELECT id FROM catalog_brands WHERE name = ?", (brand_name,))
        bid = c.fetchone()[0]
        brand_cache[brand_name] = bid
        return bid

    # Cache note name -> id
    note_cache: dict[str, int] = {}

    def get_note_id(note_name: str) -> int:
        if note_name in note_cache:
            return note_cache[note_name]
        c.execute("INSERT OR IGNORE INTO catalog_notes (name) VALUES (?)", (note_name,))
        c.execute("SELECT id FROM catalog_notes WHERE name = ?", (note_name,))
        nid = c.fetchone()[0]
        note_cache[note_name] = nid
        return nid

    print("Importing perfumes and notes...")
    for i, (_, row) in enumerate(df.iterrows(), 1):
        brand_id = get_brand_id(row["brand"])

        c.execute(
            "INSERT INTO catalog_perfumes (name, brand_id) VALUES (?, ?)",
            (row["perfume"], brand_id),
        )
        perfume_id = c.lastrowid

        # notes column is a comma-separated string like "rose, vanilla, musk"
        for raw_note in row["notes"].split(","):
            note = raw_note.strip().lower()
            if not note:
                continue
            note_id = get_note_id(note)
            c.execute(
                "INSERT OR IGNORE INTO catalog_perfume_notes (perfume_id, note_id) VALUES (?, ?)",
                (perfume_id, note_id),
            )

        if i % 1000 == 0:
            conn.commit()
            print(f"  {i}/{len(df)} done...")

    conn.commit()
    conn.close()
    print(f"Import complete. {len(df)} perfumes, {len(note_cache)} unique notes imported.")


if __name__ == "__main__":
    # 1. Create catalog tables if needed
    init_catalog_tables()

    # 2. Skip if already imported
    if not is_catalog_empty():
        print("Catalog already has data. Delete perfumes.db or catalog tables to re-import.")
    else:
        # 3. Download + import
        download_dataset()
        import_data()
