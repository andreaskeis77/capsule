# Architecture – Wardrobe Studio (CapsuleWardrobeRAG)

## High-Level
Ein lokales Wardrobe-Management-System mit:
- FastAPI (API v2 + Health)
- Flask Dashboard (UI) via WSGI-Mount (a2wsgi)
- Ontologie Runtime (Overrides + Color Lexicon + Ontology Markdown Parts)
- DB Layer (Model/Manager + Schema Updates)
- Optional: ngrok Public Access (feste Domain)

## Runtime Entry
- Startpunkt: `src/server_entry.py`
  - startet Uvicorn auf Port 5002
  - lädt `src/api_main.py` als ASGI-App

## ASGI App & Routing
- `src/api_main.py`
  - baut FastAPI App
  - mountet API v2 (`src/api_v2.py`)
  - mountet Flask Dashboard (`src/web_dashboard.py`) über `a2wsgi.WSGIMiddleware`
  - bietet Healthcheck `/healthz`

## API v2
- `src/api_v2.py`
  - enthält API v2 Endpoints
  - lädt Ontologie (über `src/ontology_runtime.py`)
  - verarbeitet Bilder (Pillow / PIL)

## Dashboard (UI)
- `src/web_dashboard.py`
  - Flask App
  - rendert Templates aus `templates/`
    - `templates/index.html` (Übersicht/Grid)
    - `templates/item_detail.html` (Detailansicht)
  - nutzt API/DB-Zugriff je nach Implementierung (siehe Code)

## Ontologie
- Ordner: `ontology/`
  - `ontology_overrides.yaml` (Runtime Overrides)
  - `color_lexicon.yaml` (Farblexikon)
  - `ontology_part_01...09_*.md` (Definition/Taxonomie/Attribute/Rules/Glossary)
- Runtime: `src/ontology_runtime.py`
  - lädt YAMLs
  - stellt Ontologie-Objekte/Lookups zur Verfügung

## DB / Models / Migration
- `src/models.py` – Datamodelle (Pydantic/ORM-ähnlich je nach Ausprägung)
- `src/database_manager.py` – DB Zugriffe, CRUD, Pfade
- `src/update_db_schema.py` – Schema Update/Migration
- `src/check_db.py` – DB Checks
- `src/export_db.py` – Export Funktionen
- `src/ingest_wardrobe.py` – Ingest/Import Workflow

## Logging
- `src/logging_config.py`, `src/logging_utils.py`
- Log Output/Rotation zusätzlich über `Wardrobe_Studio_Starten.bat` nach `logs/`

## Ops/Start
- `Wardrobe_Studio_Starten.bat`
  - startet Server via `.venv\Scripts\python.exe -m src.server_entry`
  - Readiness Polling über `/healthz`
  - optional: ngrok Start mit fester Domain

## Dateien & Ordner (wesentlich)
- `src/` Code
- `templates/` UI Templates
- `ontology/` Ontologie + YAML
- `logs/` runtime logs (rotated)
- `03_database/` lokale DB
- `02_wardrobe_images/` lokale Bilder
- `requirements.txt` Python dependencies (reproduzierbar)
- `tools/Test-WardrobeApi.ps1` – API Smoke/Manual testing (PowerShell)
