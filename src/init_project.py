import os
import json
from models import UserProfile, StyleGoals, PhysicalProfile

def setup_folders():
    # Wir legen die Struktur so an, dass sie später auf das Lenovo passt
    folders = [
        "01_raw_input",
        "02_wardrobe_images",
        "03_database",
        "04_user_data/karen/identity_images",
        "04_user_data/andreas/identity_images",
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Ordner erstellt: {folder}")

def create_initial_profiles():
    # Profil für Karen (mit ihren analytischen Zielen)
    karen = UserProfile(
        user_id="karen_01",
        name="Karen",
        physical=PhysicalProfile(color_type="Noch analysieren"),
        goals=StyleGoals(
            max_items_total=40, # Karens Ziel: Weniger ist mehr
            min_outfit_days=14,
            preferred_materials=["Bio-Baumwolle", "Leinen", "Wolle"]
        )
    )

    # Profil für Andreas
    andreas = UserProfile(
        user_id="andreas_01",
        name="Andreas",
        physical=PhysicalProfile(height_cm=193),
        goals=StyleGoals(max_items_total=60, min_outfit_days=7)
    )

    # Speichern als JSON in den jeweiligen User-Ordnern
    for user in [karen, andreas]:
        path = f"04_user_data/{user.name.lower()}/profile.json"
        with open(path, "w", encoding="utf-8") as f:
            f.write(user.model_dump_json(indent=4))
        print(f"Profil-Datei erstellt für: {user.name}")

if __name__ == "__main__":
    setup_folders()
    create_initial_profiles()
    print("\n--- Initialisierung abgeschlossen! ---")