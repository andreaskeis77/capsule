# WORKSPACE CLEANUP INVENTORY

Dieses Paket erzeugt **nur eine Bestandsaufnahme**. Es verschiebt und löscht **nichts**.

## Zweck

Für euer lokales Arbeitsverzeichnis `C:\CapsuleWardrobeRAG` soll zuerst sauber sichtbar werden:

- welche Dateien und Ordner lokal existieren
- was `tracked` / `untracked` / `ignored` ist
- was typische Aufräumkandidaten sind
- wo sich Root-, `docs/`- und `logs/`-Ballast angesammelt hat

## Ausführung

```powershell
cd C:\CapsuleWardrobeRAG
.\.venv\Scripts\Activate.ps1
python .\tools\workspace_inventory.py
```

## Output

Standardziel:

```text
docs\_ops\workspace_inventory\run_<timestamp>\
```

Dort entstehen:

- `inventory_summary.md`
- `inventory_files.csv`
- `inventory_dirs.csv`
- `cleanup_candidates.csv`
- `inventory_tree_depth3.txt`
- `inventory_manifest.json`

## Nächster Schritt

Nach dem Lauf schickst du idealerweise:
- `inventory_summary.md`
- `cleanup_candidates.csv`

Dann bauen wir daraus das eigentliche **Move/Delete-Skript**.
