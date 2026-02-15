import sqlite3
import os

# --- KONFIGURATION ---
BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, "03_database", "wardrobe.db")

def check_inventory():
    if not os.path.exists(DB_PATH):
        print(f"[-] Fehler: Datenbank nicht gefunden unter {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"[-] Datenbankfehler: {e}")
        conn.close()
        return
    
    print("\n" + "█"*100)
    print(f"  CAPSULE WARDROBE - VISION CHECK: {len(rows)} Teile erfasst")
    print("█"*100)

    for row in rows:
        # Fallback für leere Werte
        item = {k: (v if v is not None else "---") for k, v in dict(row).items()}
        
        print(f"\nID: {item['id']} | ARTIKEL: {item['name']}")
        print("-" * 100)
        
        # Basis-Daten
        print(f"MARKE:     {str(item['brand']):<20} | KAT:       {item['category']}")
        print(f"MODELL:    {str(item['model_name']):<20} | FARBE:     {item['color_primary']}")
        print(f"MATERIAL:  {item['material_main']}")
        print(f"PASSFORM:  {str(item['fit']):<20} | KRAGEN:    {item['collar']}")
        
        # Der neue Vision-Block (Expertise von GPT-5.2)
        print("\n[KI-VISION-ANALYSE]:")
        vision_text = item.get('vision_description', '---')
        # Wir rücken den Text etwas ein für bessere Lesbarkeit
        if vision_text != "---":
            print(f"> {vision_text[:500]}...") # Zeigt die ersten 500 Zeichen an
        else:
            print("> Keine Vision-Daten vorhanden.")
            
        print("-" * 100)
        print("█" * 100)

    conn.close()

if __name__ == "__main__":
    check_inventory()