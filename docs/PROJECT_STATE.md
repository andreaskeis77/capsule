# PROJECT_STATE – Wardrobe Studio (RAG Wardrobe Projekt)

Stand: 2026-03-22 (Europe/Berlin)

## Ziel

Ein lokales Wardrobe-Management-System (Backend + Web-UI) für „Karen“ und später weitere Nutzer,
das reale Bestandsdaten, Bilder, Ontologie-gestützte Attribute und eine bedienbare Weboberfläche in
einem nachvollziehbaren Engineering-Rahmen zusammenführt.

## Aktueller Status (faktisch)

- Repo Root: `C:\CapsuleWardrobeRAG`
- Python: 3.12, virtuelle Umgebung: `.venv`
- Serverstart: `python -m src.server_entry`
- Lokaler Standard-Port: `5002`
- Dashboard: `http://127.0.0.1:5002/?user=karen`
- API-Health: `http://127.0.0.1:5002/api/v2/health`
- ngrok Fixed Domain: `https://wardrobe.ngrok-app.com.ngrok.app`
- Snapshot-/Handoff-Tooling vorhanden
- Test-Suite vorhanden
- Secret-Scan vorhanden
- Repo-Metrics / Hotspot-Analyse vorhanden

## Wesentliche Komponenten

- `src/api_main.py` – FastAPI App, Request-Middleware, Fehlervertrag, Mount API v2 + Flask-Dashboard
- `src/api_v2.py` – API-v2-Endpunkte und zentraler Applikations-Hotspot
- `src/web_dashboard.py` – Flask-Weboberfläche
- `src/ingest_item_runner.py` – Ingest-Orchestrierung
- `src/run_registry.py` – Run-bezogene Metadaten / KPIs
- `src/ontology_runtime*.py` – Runtime-Layer für Ontologie, Matching, Index, Loader
- `tools/secret_scan.py` – Secret-Hygiene
- `tools/project_sanity_check.py` – Live-Sanity gegen laufenden Server
- `tools/handoff_make.py` – Handoff-/Snapshot-Erzeugung

## Meilenstein 2026-03-22 – Tranche A (Quality Gates)

Tranche A führt einen ersten harten Gate-Rahmen ein, ohne den Runtime-Contract der Anwendung umzubauen.

Neu eingeführt:
- GitHub Actions Workflow für automatische Gates
- `requirements-dev.txt` für zusätzliche Dev-Tooling-Abhängigkeiten
- `tools/run_quality_gates.py` als gemeinsamer Gate-Runner
- `tools/run_quality_gates.ps1` als Windows-Einstiegspunkt
- optionaler Git-Hook für lokalen Commit-Schutz
- ADR für die Tranche-A-Entscheidung

Ziel von Tranche A:
- deterministischer Einstiegspunkt für Qualitätsprüfungen
- reproduzierbare Artefakte pro Gate-Lauf
- frühe, konkrete Fehlerzuordnung auf Schritt-Ebene
- Security Hygiene als Standardpfad

## Standard-Gates nach Tranche A

Stufe 1:
- `compileall`
- `ruff` (kritische Regeln: `E9,F63,F7,F82`)
- `pytest -q`
- `tools/secret_scan.py --mode tracked`

Stufe 1+ Runtime:
- lokaler Serverstart in isoliertem Port
- `tools/project_sanity_check.py` gegen `/healthz`, `/api/v2/health` und Selection-URL

Artefaktpfad:
- `docs/_ops/quality_gates/run_<timestamp>/`

## Nächste große Tranche

**Tranche B – API-v2-Hotspot-Zerlegung**
- `src/api_v2.py` in klarere Router-/Service-Schnitte trennen
- Contract-Stabilität bewahren
- Regressionen über bestehende Tests plus gezielte neue Tests absichern

## Operative Regeln

- keine Vermutungsfixes
- vollständige Dateien statt Diff-Schnipsel
- erst messen, dann ändern
- jede größere Änderung mit nachweisbarem Gate abschließen
