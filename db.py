"""
db.py — shared database module for perfume catalog (read-only queries).
The catalog tables are populated by import_dataset.py.
"""

import os
import sqlite3

# Use /data volume on Fly.io, local file otherwise
DB_PATH = "/data/perfumes.db" if os.path.isdir("/data") else "perfumes.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_catalog_tables():
    """Create catalog tables if they don't exist yet."""
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS catalog_brands (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS catalog_perfumes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            brand_id INTEGER REFERENCES catalog_brands(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS catalog_notes (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS catalog_perfume_notes (
            perfume_id INTEGER REFERENCES catalog_perfumes(id),
            note_id    INTEGER REFERENCES catalog_notes(id),
            PRIMARY KEY (perfume_id, note_id)
        )
    """)

    conn.commit()
    conn.close()


def is_catalog_empty():
    """Return True if the catalog has no perfumes yet."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM catalog_perfumes")
    count = c.fetchone()[0]
    conn.close()
    return count == 0


def get_catalog_perfume(perfume_id: int) -> dict | None:
    """Return {id, name, brand} for a single catalog perfume by id."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT cp.id, cp.name, cb.name
        FROM catalog_perfumes cp
        JOIN catalog_brands cb ON cp.brand_id = cb.id
        WHERE cp.id = ?
    """, (perfume_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "name": row[1], "brand": row[2]}


def search_catalog(query: str, limit: int = 500) -> list[dict]:
    """
    Search catalog perfumes by name, brand, or note (Ukrainian or English).
    Returns list of dicts: {id, name, brand}.
    """
    conn = get_conn()
    c = conn.cursor()
    like = f"%{query}%"
    c.execute("""
        SELECT DISTINCT cp.id, cp.name, cb.name
        FROM catalog_perfumes cp
        JOIN catalog_brands cb ON cp.brand_id = cb.id
        LEFT JOIN catalog_perfume_notes cpn ON cpn.perfume_id = cp.id
        LEFT JOIN catalog_notes cn ON cpn.note_id = cn.id
        WHERE cp.name LIKE ? OR cb.name LIKE ? OR cn.name LIKE ? OR cn.name_uk LIKE ?
        LIMIT ?
    """, (like, like, like, like, limit))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "brand": r[2]} for r in rows]


def get_notes_for_perfume(perfume_id: int) -> list[str]:
    """Return list of note names (Ukrainian if available) for a given catalog perfume id."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT COALESCE(cn.name_uk, cn.name)
        FROM catalog_perfume_notes cpn
        JOIN catalog_notes cn ON cpn.note_id = cn.id
        WHERE cpn.perfume_id = ?
        ORDER BY COALESCE(cn.name_uk, cn.name)
    """, (perfume_id,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]


def suggest_by_notes(note_names: list[str], limit: int = 5) -> list[dict]:
    """
    Find catalog perfumes that share the most notes with the given list.
    Matches against Ukrainian note names (name_uk) if available, falling back to English (name).
    Returns list of dicts: {name, brand, shared}.
    """
    if not note_names:
        return []

    conn = get_conn()
    c = conn.cursor()

    placeholders = ",".join("?" * len(note_names))
    c.execute(f"""
        SELECT cp.name, cb.name, COUNT(*) AS shared
        FROM catalog_perfume_notes cpn
        JOIN catalog_notes cn ON cpn.note_id = cn.id
        JOIN catalog_perfumes cp ON cpn.perfume_id = cp.id
        JOIN catalog_brands cb ON cp.brand_id = cb.id
        WHERE cn.name_uk IN ({placeholders}) OR cn.name IN ({placeholders})
        GROUP BY cp.id
        ORDER BY shared DESC
        LIMIT ?
    """, (*note_names, *note_names, limit))

    rows = c.fetchall()
    conn.close()
    return [{"name": r[0], "brand": r[1], "shared": r[2]} for r in rows]
