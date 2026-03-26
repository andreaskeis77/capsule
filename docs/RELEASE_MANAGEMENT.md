# Release Management
## Capsule Studio / Capsule Wardrobe Project

Stand: 2026-03-26

## 1. Purpose
Dieses Dokument definiert die Release-Logik des Projekts:
- wie Releases geschnitten werden
- wie Scope und Änderungen dokumentiert werden
- welche Nachweise erforderlich sind
- wie Tranchen Releases zugeordnet werden
- wie interne Test-/Ops-Tools als Teil des Projektgedächtnisses erhalten bleiben

## 2. Versioning Model
Das Projekt verwendet eine pragmatische, semantisch orientierte Versionierung:
- `MAJOR.MINOR.PATCH`

### 2.1 Bedeutungen
- **MAJOR**: signifikante Architekturänderungen, Breaking Changes, grundlegende Betriebsmodell-Änderungen
- **MINOR**: neue Funktionsblöcke oder deutlich sichtbare funktionale Erweiterungen
- **PATCH**: Bugfixes, Hardening, Stabilisierung, kleine nicht-breaking Verbesserungen

### 2.2 Release Policy
- Jede Änderung wird einem Zielrelease zugeordnet.
- Größere Änderungen werden in Tranchen umgesetzt.
- Ein Release ist nur dann gültig, wenn Scope, Änderungen und Nachweise dokumentiert wurden.

## 3. Release 1.0.0 Baseline

### 3.1 Definition
Der aktuelle dokumentierte Funktionsumfang wird als **Release 1.0.0** definiert.

### 3.2 Scope von Release 1.0.0
Release 1.0.0 umfasst mindestens:
- FastAPI API v2
- Flask Dashboard / Admin / Detail Views
- CRUD-Funktionalität für Items
- Kontext-/Review-/Notes-/Size-Metadaten
- mounted UI + API runtime
- SQLite + Filesystem Split
- Bildverwaltung
- Ingestion mit dry-run/fake-ai
- Ingestion Fingerprint / idempotence / quarantine
- Recovery-Tooling für Archive/DB Drift
- Run Registry
- Handoff-/Snapshot-Tooling
- Secret Redaction im Run Registry Kontext
- Secret Scanner
- UI Filter für context / needs_review
- dokumentierte Infrastruktur-Basis
- dokumentiertes Architektur- und Engineering-Regelwerk

## 4. Release Evidence Requirements

### 4.1 Pflichtbestandteile
- Zielrelease
- Scope
- Änderungsumfang
- betroffene Komponenten
- Testnachweise
- bekannte Einschränkungen
- relevante Handoff-/Snapshot-Verweise
- relevante Infrastruktur-/Betriebsänderungen

### 4.2 Testnachweise
Mindestens soweit relevant:
- `pytest`
- Secret Scan
- API-/Smoke-/Tool-Checks
- ggf. manuelle UI-/Ops-Nachweise

### 4.3 Dokumentationsnachweise
Vor Release müssen konsistent sein:
- ARD
- Manifest
- Release Management
- Release Notes
- relevante ADRs

## 5. Internal Engineering and Ops Tooling Inventory

Diese Werkzeuge sind Bestandteil des Projektgedächtnisses und müssen dokumentiert bleiben.

### 5.1 Test and Quality
- `pytest`
- `ruff`
- Secret Scan

### 5.2 Runtime / API / Smoke
- API-/Health-/Smoke-Skripte
- lokale Start- und Batch-Skripte

### 5.3 Handoff / Snapshot
- `tools/handoff_make.py`
- `tools/handoff_make_run.py`

### 5.4 Run / Report / Metrics
- `tools/runs_report.py`
- Repo-Metriken / Quality-Gate-/Metrics-Werkzeuge

### 5.5 Ingest / Recovery
- `src/ingest_wardrobe.py`
- `tools/ingest_recover.py`

Hinweis: Diese Liste ist lebendiger Projektbestand und bei Tooling-Änderungen zu aktualisieren.

## 6. Tranche-to-Release Mapping
### 6.1 Regel
Jede Tranche wird einem Zielrelease zugeordnet.

### 6.2 Dokumentationspflicht
Zu jeder Tranche gehören:
- Ziel
- Scope
- Zielrelease
- Testplan
- Doku-Impact

### 6.3 Keine releasefreien Änderungen
Änderungen ohne Zielrelease-Zuordnung gelten als unvollständig geplant.

## 7. Change Scope Rules
### 7.1 Patch Releases
Patch Releases dienen für:
- Bugfixes
- Hardening
- Stabilisierung
- Dokumentationskorrekturen ohne Scope-Erweiterung

### 7.2 Minor Releases
Minor Releases dienen für:
- neue Feature-Bausteine
- sichtbare UI-/Ops-Erweiterungen
- neue dokumentierte Capability-Bereiche

### 7.3 Major Releases
Major Releases sind für:
- Breaking Changes
- Architekturumbau
- neue Betriebsmodelle
- gravierende Contract-/Schemaänderungen

## 8. Release Notes Policy
Release Notes werden als eigenständiges Dokument geführt.

### 8.1 Jede Release-Fassung dokumentiert
- Version
- Datum
- Scope
- Included Capabilities
- Test-/Evidence-Stand
- bekannte offene Punkte
- Migrations-/Betriebshinweise

## 9. Rollback and Recovery Considerations
Releaseplanung muss berücksichtigen:
- Schema-/Persistenzrisiken
- Recoveryfähigkeit
- Quarantine-/Trash-/Repair-Mechaniken
- Handoff-Fähigkeit
- klare Nachvollziehbarkeit im Fehlerfall

## 10. Governance Rule

Releaseplanung ist verbindlicher Bestandteil des Engineering-Prozesses.

> Erweiterungen oder Verbesserungen werden in Tranchen geplant, mit umfangreichen Tests abgesichert und einem dokumentierten Zielrelease zugeordnet.

> Release-Dokumente müssen sowohl Endnutzer-relevanten Funktionsumfang als auch interne Engineering- und Betriebswerkzeuge ausreichend dokumentieren, damit das Projektwissen nicht verloren geht.
