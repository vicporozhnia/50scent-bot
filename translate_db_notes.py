"""
translate_db_notes.py — Add Ukrainian note names to catalog_notes table.

Run once: python translate_db_notes.py

Adds name_uk column to catalog_notes and fills it using GoogleTranslator.
Caches translations to translations_cache.json so you can safely re-run
if interrupted — already-translated rows are skipped.
"""

import json
import sqlite3
import time
from pathlib import Path
from deep_translator import GoogleTranslator

DB_PATH = "perfumes.db"
CACHE_FILE = "translations_cache.json"

# Load cache
cache_path = Path(CACHE_FILE)
cache: dict[str, str] = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
print(f"Cache: {len(cache)} existing translations.")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Add column if missing
try:
    c.execute("ALTER TABLE catalog_notes ADD COLUMN name_uk TEXT")
    conn.commit()
    print("Added name_uk column.")
except Exception:
    print("name_uk column already exists.")

# Fetch notes that still need translation
c.execute("SELECT id, name FROM catalog_notes WHERE name_uk IS NULL")
rows = c.fetchall()
print(f"Notes to translate: {len(rows)}")

if not rows:
    print("Nothing to do.")
    conn.close()
    exit()

translator = GoogleTranslator(source="en", target="uk")
new_count = 0

for i, (note_id, name) in enumerate(rows, 1):
    if name in cache:
        name_uk = cache[name]
    else:
        try:
            name_uk = translator.translate(name)
            cache[name] = name_uk
            new_count += 1
            time.sleep(0.1)
        except Exception as e:
            print(f"  Error translating '{name}': {e} — keeping original")
            name_uk = name

    c.execute("UPDATE catalog_notes SET name_uk=? WHERE id=?", (name_uk, note_id))

    # Commit and save cache every 100 rows
    if i % 100 == 0:
        conn.commit()
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [{i}/{len(rows)}] saved ({new_count} new API calls)...")

conn.commit()
cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
conn.close()

print(f"\nDone. {new_count} new translations. All notes updated in DB.")
