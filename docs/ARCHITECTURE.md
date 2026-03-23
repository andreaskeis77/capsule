# Architecture Overview

## Zielbild

Capsule ist in Schichten organisiert, damit Fachlogik, Runtime, Persistenz und Betrieb getrennt geändert werden können.

## Hauptschichten

### 1. API / Presentation
- `src/api_v2.py`
- `src/api_v2_routes.py`
- `src/web_dashboard.py`
- `src/web_dashboard_routes.py`

### 2. Domain / Mapping / Ontology
- `src/category_map.py`
- `src/category_map_rules.py`
- `src/ontology_runtime.py`
- `src/ontology_runtime_manager.py`
- `src/ontology_runtime_index.py`

### 3. Ingest / Run-Orchestrierung
- `src/ingest_item_runner.py`
- `src/ingest_run_outcome.py`
- `src/run_registry.py`

### 4. Persistenz / DB
- `src/db_schema.py`
- `src/db_schema_migrations.py`
- `src/db_sqlite.py`
- `src/database_manager.py`

### 5. Runtime / Entrypoints
- `src/runtime_env.py`
- `src/runtime_config.py`
- `src/server_entry.py`
- `src/settings.py`

### 6. Tooling / Ops / Governance
- `tools/run_quality_gates.py`
- `tools/task_runner.py`
- `tools/release_evidence.py`
- `tools/handoff_make.py`
- `.github/workflows/*`

## Betriebsprinzip

Jede größere Änderung läuft gegen denselben Satz von Gates. Release und Handoff bauen auf denselben Artefakten auf statt auf manuellen Aussagen.
