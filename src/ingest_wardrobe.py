# FILE: src/ingest_wardrobe.py
import os
import shutil
import sqlite3
import json
import base64
import logging
import time
import gc
from openai import OpenAI
from dotenv import load_dotenv

# --- DEBUGGING & LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("WardrobeIngest")

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- KONFIGURATION ---
MODEL_VISION = "gpt-5.2"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "03_database", "wardrobe.db")
INPUT_DIR = os.path.join(BASE_DIR, "01_raw_input")
ARCHIVE_DIR = os.path.join(BASE_DIR, "02_wardrobe_images")
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.jfif', '.heic')

def encode_image(image_path):
    with open(image_path, "rb") as i_file:
        return base64.b64encode(i_file.read()).decode('utf-8')

def analyze_item_hybrid(image_paths, text_context):
    mode = "VISION+TEXT" if image_paths else "ONLY-TEXT"
    logger.info(f"      -> KI-Modus: {mode} ({len(image_paths)} Bilder, {len(text_context)} Zeichen Text)")
    
    prompt = f"""Analysiere dieses Kleidungsstück.
    TEXT-DATEN: '{text_context}'
    Nutze STRIKT die Mode-Ontologie IDs (cat_..., etc.).
    GIB NUR EIN VALIDES JSON ZURÜCK:
    {{
        "brand": "Marke", "category": "cat_...", "name": "Produktname",
        "color_primary": "Farbe", "material_main": "Material",
        "fit": "Passform", "collar": "Kragenform", "price": "Preis",
        "vision_description": "Detaillierte Analyse"
    }}"""

    content = [{"type": "text", "text": prompt}]
    for path in image_paths[:3]:
        ext = os.path.splitext(path)[1].lower().replace('.', '')
        if ext not in ['jpeg', 'jpg', 'png', 'webp']: ext = 'jpeg'
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/{ext};base64,{encode_image(path)}"}
        })

    try:
        response = client.chat.completions.create(
            model=MODEL_VISION,
            messages=[{"role": "user", "content": content}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"      [!] KI-Fehler: {str(e)}")
        return None

def robust_move(src, dst, retries=3, delay=1):
    """Versucht einen Ordner zu verschieben und fängt Windows-Sperren ab."""
    for i in range(retries):
        try:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.move(src, dst)
            return True
        except PermissionError:
            logger.warning(f"      [!] Zugriff gesperrt, versuche erneut ({i+1}/{retries})...")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"      [!] Schwerer Move-Fehler: {e}")
            break
    return False

def process_pipeline():
    logger.info("=== START HYBRID INGESTION (v3.2 - Robust Move) ===")
    
    if not os.path.exists(INPUT_DIR):
        logger.error(f"Input-Ordner fehlt: {INPUT_DIR}")
        return

    users = [d for d in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, d))]
    
    for user in users:
        u_path = os.path.join(INPUT_DIR, user)
        items = [d for d in os.listdir(u_path) if os.path.isdir(os.path.join(u_path, d))]
        
        for item_name in items:
            i_path = os.path.join(u_path, item_name)
            logger.info(f"  [*] Item: {item_name}")
            
            img_files = []
            txt_content = ""
            for root, _, filenames in os.walk(i_path):
                for f in filenames:
                    f_path = os.path.join(root, f)
                    if f.lower().endswith(VALID_EXTENSIONS):
                        img_files.append(f_path)
                    if f.lower().endswith(".txt"):
                        with open(f_path, "r", encoding="utf-8") as tf:
                            txt_content += tf.read() + "\n"

            if not img_files and not txt_content.strip():
                logger.warning(f"      -> SKIP: Kein Inhalt in '{item_name}'")
                continue

            data = analyze_item_hybrid(img_files, txt_content)
            
            if data:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute('''INSERT INTO items (user_id, name, brand, category, color_primary, material_main, fit, collar, price, vision_description, image_path)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                        (user, data.get('name', item_name), data.get('brand'), data.get('category'),
                         data.get('color_primary'), data.get('material_main'), data.get('fit'),
                         data.get('collar'), data.get('price'), data.get('vision_description'), f"{user}/{item_name}"))
                    conn.commit()
                    conn.close()
                    logger.info("      -> DB: Eintrag erstellt.")
                except Exception as e:
                    logger.error(f"      -> DB-Fehler: {e}")
                    continue

                # Garbage Collection erzwingen, um alle File-Handles freizugeben
                gc.collect()

                # Robustes Verschieben
                dest = os.path.join(ARCHIVE_DIR, user, item_name)
                if robust_move(i_path, dest):
                    logger.info(f"      -> ARCHIV: Erfolgreich verschoben.")
                else:
                    logger.error(f"      -> MOVE-FAIL: Ordner bleibt in 01_raw_input (bitte Explorer schließen!)")
            else:
                logger.error(f"      -> FAIL: Keine KI-Daten.")

    logger.info("=== PIPELINE BEENDET ===")

if __name__ == "__main__":
    process_pipeline()