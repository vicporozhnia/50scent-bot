import sqlite3

from db import DB_PATH, init_catalog_tables

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()


def init_user_db():
    """Create and migrate user tables."""
    try:
        cursor.execute("ALTER TABLE perfumes RENAME TO user_perfumes")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_perfumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        brand TEXT,
        name TEXT,
        season TEXT,
        mood TEXT,
        notes TEXT
    )
    """)
    try:
        cursor.execute("ALTER TABLE user_perfumes ADD COLUMN notes TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        catalog_id INTEGER NOT NULL,
        brand TEXT NOT NULL,
        name TEXT NOT NULL,
        UNIQUE(user_id, catalog_id)
    )
    """)
    conn.commit()

    init_catalog_tables()


init_user_db()
