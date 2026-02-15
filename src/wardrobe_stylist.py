import sqlite3
import json
import requests

# --- KONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"
DB_PATH = "03_database/wardrobe.db"

def get_wardrobe_context():
    """Holt alle Items aus der DB und bereitet sie als Text für die KI vor."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT brand, category, color_primary, material_main, fit, collar, name FROM items")
    rows = cursor.fetchall()
    conn.close()

    context = "Dies ist der Kleiderschrank des Nutzers:\n"
    for r in rows:
        context += f"- {r[0]} {r[1]} (Farbe: {r[2]}, Material: {r[3]}, Passform: {r[4]}, Kragen: {r[5]}, Name: {r[6]})\n"
    return context

def ask_stylist(question):
    wardrobe_info = get_wardrobe_context()
    
    prompt = f"""
    Du bist ein professioneller Stil-Berater. Du hast Zugriff auf den digitalen Kleiderschrank des Nutzers.
    
    DEIN WISSEN (KLEIDERSCHRANK):
    {wardrobe_info}
    
    AUFGABE: Beantworte die Frage des Nutzers basierend auf den vorhandenen Stücken. 
    Gib konkrete Empfehlungen, warum bestimmte Teile zusammenpassen (Farbenlehre, Stil-Etikette).
    
    FRAGE: {question}
    
    STIL-BERATUNG:
    """
    
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    try:
        print("\n[*] Stylist denkt nach...")
        response = requests.post(OLLAMA_URL, json=payload)
        return response.json().get("response", "")
    except Exception as e:
        return f"Fehler: {e}"

if __name__ == "__main__":
    print("--- DEIN KI-STILBERATER ---")
    while True:
        user_query = input("\nStelle eine Frage an deinen Kleiderschrank (oder 'exit'): ")
        if user_query.lower() == 'exit': break
        
        advice = ask_stylist(user_query)
        print("\n" + "="*50)
        print(advice)
        print("="*50)