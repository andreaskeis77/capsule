# FILE: src/export_db.py
import sqlite3
import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "03_database", "wardrobe.db")
EXPORT_PATH = os.path.join(BASE_DIR, "wardrobe_export.json")

def export_to_json():
    if not os.path.exists(DB_PATH):
        print("[-] Datenbank nicht gefunden!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    rows = cursor.execute("SELECT * FROM items").fetchall()
    conn.close()

    # In Liste von Dictionaries umwandeln
    items = [dict(row) for row in rows]

    with open(EXPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4, ensure_ascii=False)

    print(f"[OK] Datenbank exportiert nach: {EXPORT_PATH}")
    print(f"[*] Anzahl der Einträge: {len(items)}")

if __name__ == "__main__":
    export_to_json()