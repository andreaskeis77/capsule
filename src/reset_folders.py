# FILE: src/reset_folders.py
import os
import shutil
import stat
import time

# --- KONFIGURATION (Absolut) ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCE_DIR = os.path.join(BASE_DIR, "02_wardrobe_images")
TARGET_DIR = os.path.join(BASE_DIR, "01_raw_input")

def remove_readonly(func, path, excinfo):
    """
    Fehlerbehandler für shutil.rmtree.
    Löscht den Schreibschutz und versucht den Löschvorgang erneut.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def reset_folders():
    print(f"[*] RESET-PROZESS: {SOURCE_DIR} -> {TARGET_DIR}")
    
    if not os.path.exists(SOURCE_DIR):
        print("[-] Quellverzeichnis nicht vorhanden. Nichts zu tun.")
        return

    users = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d))]
    
    for user in users:
        u_src = os.path.join(SOURCE_DIR, user)
        u_tgt = os.path.join(TARGET_DIR, user)
        os.makedirs(u_tgt, exist_ok=True)

        for item in os.listdir(u_src):
            i_src = os.path.join(u_src, item)
            i_tgt = os.path.join(u_tgt, item)

            if os.path.isdir(i_src):
                # Falls das Ziel bereits existiert, löschen wir es mit dem robusten Handler
                if os.path.exists(i_tgt):
                    try:
                        shutil.rmtree(i_tgt, onerror=remove_readonly)
                    except Exception as e:
                        print(f"[!] Konnte Zielordner nicht vor-reinigen: {item}. Fehler: {e}")
                        continue
                
                # Verschieben mit kurzem Delay gegen File-Locks
                try:
                    time.sleep(0.1) 
                    shutil.move(i_src, i_tgt)
                    print(f"[OK] {user}/{item}")
                except Exception as e:
                    print(f"[!] Fehler beim Verschieben von {item}: {e}")

    print("[*] Reset abgeschlossen.")

if __name__ == "__main__":
    reset_folders()