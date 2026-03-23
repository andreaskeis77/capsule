# PROJECT_STATE – Capsule / Wardrobe Studio

Stand: 2026-03-23 (Europe/Berlin)

## 1. Zielbild

Capsule ist das zentrale Wardrobe-Management-System für Karen und perspektivisch weitere Nutzer. Das System verbindet:

- strukturierte Bestandsdaten
- Bilder und Dateiartefakte
- Ontologie-gestützte Klassifikation und Normalisierung
- Weboberfläche für Bedienung und Review
- API-Endpunkte für Integration in ChatGPT Custom GPT und weitere Clients
- klaren Engineering-, Testing-, Handoff- und Release-Rahmen

Das Ziel ist kein rein lokales Bastelsystem mehr, sondern ein kontrollierbar betriebenes, dokumentiertes und übergebbares System.

## 2. Aktueller Produkt- und Technikstand

### 2.1 Produktzugänge

Aktuell sind zwei primäre Nutzungswege vorgesehen:

1. **ChatGPT / Custom GPT**
   - ChatGPT nutzt definierte Actions gegen die Capsule-API.
   - Karen soll Capsule darüber direkt bedienen können, ohne lokalen Server auf ihrem Laptop.

2. **Weboberfläche**
   - Browserbasierter Zugriff auf die Capsule-Webseite / das Dashboard.
   - Die Website kann je nach Use Case serverseitig mit der OpenAI API kommunizieren.

### 2.2 Ziel für Karen

**Karen soll keinen lokalen Capsule-Server mehr auf ihrem Laptop betreiben müssen.**

Zielzustand:

- Betrieb auf zentralem Windows-VPS
- öffentlicher Zugriff über einen stabilen Tunnel / öffentlichen Endpoint
- Karen nutzt nur noch:
  - ChatGPT Custom GPT, oder
  - Browser / Website

## 3. Engineering- und Hardening-Stand

Zwischen 2026-03-22 und 2026-03-23 wurde das Repo in großen Hardening-Tranchen A–R überarbeitet. Alle Tranches wurden lokal mit denselben Quality Gates validiert.

### 3.1 Validierte Tranchengruppen

- **A** Quality Gates
- **B** API-v2 modularisiert
- **C** Ingest / Run Registry gehärtet
- **D** Dashboard / Category Map modularisiert
- **E** Ontology Runtime / Index entkoppelt
- **F** Runtime-Config / Entrypoints gehärtet
- **G** Tooling / Ops konsolidiert
- **H** Persistenz / DB / Schema-Migrationspfad gehärtet
- **I** GitHub-CI / Required Checks vorbereitet
- **J** Release-Governance / Branch-Protection / Release-Evidence
- **K** standardisierte lokale Task-/Developer-Entrypoints
- **L** Doku / Navigation gehärtet
- **M** Observability / Diagnose / Reporting gehärtet
- **N** Testarchitektur / Suite-Layering gehärtet
- **O** Performance-Baselines / Hot-Path-Messung
- **P** Security / Supply-Chain-Hygiene
- **Q** Packaging / Distribution / Release-Artefakte
- **R** Final Baseline / Normal Operations / Readiness

### 3.2 Validierungsstandard

Der aktuelle Entwicklungsstandard basiert auf:

- `python .\tools\run_quality_gates.py`
- Compile-/Lint-/Pytest-/Secret-Scan-/Live-Smoke-Gates
- dokumentierten ADRs
- dokumentierten Release-/Readiness-Artefakten
- lokalem und GitHub-seitigem Governance-Rahmen

## 4. Wichtige technische Komponenten

### 4.1 Laufzeit / Schnittstellen

- `src/api_main.py` – App Composition / Middleware / Mounting
- `src/api_v2.py` + Split-Module – API-v2-Fassade und spezialisierte Module
- `src/web_dashboard.py` + Split-Module – Weboberfläche
- `src/server_entry.py` – lokaler / serverseitiger Startpunkt
- `src/runtime_config.py`, `src/runtime_env.py`, `src/settings.py` – Konfigurationspfad

### 4.2 Fach- und Ingest-Kern

- `src/ingest_item_runner.py`
- `src/ingest_run_outcome.py`
- `src/run_registry.py`
- `src/run_registry_redaction.py`
- `src/run_registry_metrics.py`

### 4.3 Ontology Runtime

- `src/ontology_runtime.py`
- `src/ontology_runtime_manager.py`
- `src/ontology_runtime_index.py`
- `src/ontology_runtime_index_builders.py`
- `src/ontology_runtime_index_customization.py`
- `src/ontology_runtime_normalize.py`

### 4.4 Persistenz

- `src/db_schema.py`
- `src/db_schema_migrations.py`
- `src/db_sqlite.py`
- `src/database_manager.py`
- `src/update_db_schema.py`
- `src/check_db.py`
- `src/db_inspect.py`

### 4.5 Ops / Governance / Diagnostics

- `tools/run_quality_gates.py`
- `tools/secret_scan.py`
- `tools/handoff_make.py`
- `tools/release_evidence.py`
- `tools/final_repo_baseline.py`
- `tools/final_readiness_report.py`
- `tools/task_runner.py`

## 5. Aktueller Betriebsmodus

### 5.1 Lokal

Standard für lokale Entwicklung:

1. `.venv` aktivieren
2. Änderungen durchführen
3. `python .\tools\run_quality_gates.py`
4. bei Erfolg committen / pushen
5. relevante Doku aktualisieren

### 5.2 Ziel-Betrieb

Ziel ist ein zentraler Betrieb auf Windows-VPS mit:

- Capsule-App auf dem VPS
- öffentlichem Zugriff über ngrok oder später Reverse Proxy / festen Host
- Karen ohne lokalen App-Host
- OpenAI API Keys nur serverseitig

## 6. Wichtige Entscheidungen

### 6.1 Karen soll nicht mehr lokal hosten

Das ist eine zentrale Zielentscheidung. Karen soll die Lösung konsumieren, nicht hosten.

### 6.2 Ein kanonisches Backend

Custom GPT und Website sollen **dasselbe Backend** nutzen. Keine zweite, voneinander abweichende Logik.

### 6.3 OpenAI-Kommunikation serverseitig

Wenn die Webanwendung OpenAI nutzt, dann über serverseitige Logik. API-Keys gehören nicht in Browser-Clients.

## 7. Offene nächste Aufgaben

### Priorität 1 – Projektdoku und Handoff aktualisieren

- Projekt-Doku auf aktuellen A–R-Stand bringen
- Handoff-Standards für Chat-Sessions konsolidieren
- Engineering Manifest projektbezogen ergänzen

### Priorität 2 – VPS-Deployment

- aktuellen Stand auf den Windows-VPS bringen
- `.env` / Secrets / Datenpfade sauber definieren
- App-Start und ngrok-Start auf dem VPS stabilisieren
- Live-Smoke gegen öffentliche URL

### Priorität 3 – Betriebsmodell finalisieren

- entscheidet Karen primär über Custom GPT, Website oder beides?
- welche Flows gehen direkt auf Capsule-API?
- welche Flows gehen serverseitig zusätzlich über OpenAI API?

## 8. Bewusste Restschulden

- GitHub-seitige Branch Protection / Required Checks müssen real auf GitHub aktiviert werden
- reales VPS-Deployment ist noch nicht als produktionsnaher Zielzustand verifiziert
- finaler Betriebsmodus Custom GPT vs. Website vs. hybrid ist architektonisch definiert, aber noch nicht vollständig live umgesetzt
