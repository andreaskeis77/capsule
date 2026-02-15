import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "03_database", "wardrobe.db")

def reset_database():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("[*] Alte DB gelöscht.")
        except PermissionError:
            print("[!] Fehler: DB gesperrt.")
            return

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            color_primary TEXT,
            color_variant TEXT,
            needs_review INTEGER DEFAULT 0,
            material_main TEXT,
            fit TEXT,
            collar TEXT,
            price TEXT,
            vision_description TEXT,
            image_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_user_id ON items(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_needs_review ON items(needs_review)")

    conn.commit()
    conn.close()
    print("[OK] Datenbank neu erstellt.")

if __name__ == "__main__":
    reset_database()
