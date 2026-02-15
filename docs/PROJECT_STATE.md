@'
# PROJECT_STATE – Wardrobe Studio (RAG Wardrobe Projekt)

Stand: 2026-02-15 (Europe/Berlin)

## Ziel
Ein lokales Wardrobe-Management-System (Backend + Web-UI) für „Karen“ (und später weitere Nutzer), das:
- Items inkl. Bilder erfasst und speichert
- über Ontologie/Taxonomie konsistente Kategorien/Attribute nutzt
- per API (v2) von Custom GPT / Tools steuerbar ist
- eine nutzerfreundliche Web-Übersicht bietet (Filter nach Oberkategorien, Grid, Detailansicht)

## Aktueller Status (faktisch)
- Repo Root: `C:\CapsuleWardrobeRAG`
- Python: 3.12, virtuelle Umgebung: `.venv`
- Server: `python -m src.server_entry` (Uvicorn/FastAPI) läuft auf `http://127.0.0.1:5002`
- Dashboard: `http://127.0.0.1:5002/?user=karen`
- API Health: `http://127.0.0.1:5002/api/v2/health`
- ngrok: feste Domain `https://wardrobe.ngrok-app.com.ngrok.app`
- Start per Batch: `Wardrobe_Studio_Starten.bat` (Start Server + optional ngrok + Browser)
- Git: initialisiert; Commits vorhanden; Snapshot-Tool vorhanden.

## Wesentliche Komponenten (kurz)
- `src/api_main.py`: FastAPI App + Mount API v2 + Mount Flask Dashboard via a2wsgi
- `src/api_v2.py`: API v2 Endpoints (CRUD Items, Health, Ontology)
- `src/web_dashboard.py` + `templates/*.html`: Web-UI (Flask Templates)
- `src/ontology_runtime.py` + `ontology/*.md|yaml`: Ontologie/Overrides + Color-Lexicon
- `Wardrobe_Studio_Starten.bat`: robuster Start mit Logs unter `logs/`
- `tools/handoff_snapshot.ps1`: erzeugt `docs/_snapshot/latest.md`

## Ordnerstruktur (high-level)
- `src/` – Backend + Dashboard
- `templates/` – HTML Templates (`index.html`, `item_detail.html`)
- `ontology/` – Ontologie Markdown + YAML Lexika/Overrides
- `03_database/` – Datenbank
- `02_wardrobe_images/` – Bilder
- `04_user_data/` – userbezogene Daten
- `logs/` – server/ngrok/startup logs (rotierend)
- `docs/` – Architektur, Runbook, Working Agreement, Chat Handoff Template, Snapshots

## Arbeitsmodus (Kurzform)
- Schritt-für-Schritt: immer nur EIN Test-/Änderungsschritt pro Runde.
- Keine „Vermutungsfixes“: erst messen (Logs/Parser/Token), dann ändern.
- Bei Dateiänderungen: vollständigen Dateiinhalt liefern und danach verifizieren.
- Jede Änderung: lokaler Test → dann Commit.

## Nächste Meilensteine
1) Snapshot/Handoff-Standard finalisieren (inkl. Lessons Learned in docs).
2) Dashboard-UI verbessern:
   - Filter nach Oberkategorien (z.B. Hosen/Röcke/Schuhe/Handtaschen/Blusen/Kleider)
   - Grid mit kleineren Thumbnails
   - Click → Modal (größeres Bild)
   - optional „Details“-Button → eigene Detailseite

## Aktuelles TODO (kurz)
- `docs/WORKING_AGREEMENT.md`: Abschnitt „Lessons Learned / Debug-Regeln“ ergänzen (siehe Working Mode).
- Snapshot erweitern, damit er `PROJECT_STATE.md` und `WORKING_AGREEMENT.md` mit ausgibt (nur Auszug).
'@ | Set-Content -Encoding UTF8 .\docs\PROJECT_STATE.md
