from __future__ import annotations

from pathlib import Path

from src import settings
from src.db_inspect import fetch_inventory_rows, summarize_row


def check_inventory(db_path: Path | None = None) -> None:
    target = Path(db_path) if db_path is not None else Path(settings.DB_PATH)
    if not target.exists():
        print(f"[-] Fehler: Datenbank nicht gefunden unter {target}")
        return

    try:
        rows = fetch_inventory_rows(target)
    except Exception as e:
        print(f"[-] Datenbankfehler: {e}")
        return

    print("\n" + "█" * 100)
    print(f" CAPSULE WARDROBE - VISION CHECK: {len(rows)} Teile erfasst")
    print("█" * 100)

    for row in rows:
        item = summarize_row(row)

        print(f"\nID: {item['id']} | ARTIKEL: {item['name']}")
        print("-" * 100)
        print(f"MARKE: {str(item['brand']):<20} | KAT: {item['category']}")
        print(f"FARBE: {item['color_primary']}")
        print(f"MATERIAL: {item['material_main']}")
        print(f"PASSFORM: {str(item['fit']):<20} | KRAGEN: {item['collar']}")
        print("\n[KI-VISION-ANALYSE]:")

        vision_text = str(item.get("vision_description", "---"))
        if vision_text != "---":
            print(f"> {vision_text[:500]}...")
        else:
            print("> Keine Vision-Daten vorhanden.")
        print("-" * 100)

    print("█" * 100)


if __name__ == "__main__":
    check_inventory()
